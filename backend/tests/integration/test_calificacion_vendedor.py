import pytest

pytestmark = pytest.mark.integration

import bcrypt
from flask_jwt_extended import create_access_token

from app import db
from app.models.anuncio import Anuncio
from app.models.calificacion import Calificacion
from app.models.contacto_log import ContactoLog
from app.models.transaccion import Transaccion
from app.models.usuario import Usuario


PASSWORD = "123456#P"


def crear_usuario(correo, rol="USER_ESTANDAR", estado="ACTIVO"):
    password_hash = bcrypt.hashpw(PASSWORD.encode("utf-8"), bcrypt.gensalt(rounds=10)).decode("utf-8")
    usuario = Usuario(
        nombre=f"Usuario {correo}",
        correo=correo,
        password_hash=password_hash,
        telefono=f"9{abs(hash(correo)) % 100000000:08d}",
        rol=rol,
        estado=estado,
    )
    db.session.add(usuario)
    db.session.commit()
    return usuario


def crear_anuncio(usuario, **overrides):
    anuncio = Anuncio(
        usuario_id=usuario.id,
        titulo="Ryzen 5 5600X",
        descripcion="Descripcion",
        categoria="COMPONENTES",
        subcategoria="PROCESADOR",
        condicion="USADO",
        precio="350.00",
        estado="ACTIVO",
        reactivaciones_count=0,
    )
    for campo, valor in overrides.items():
        setattr(anuncio, campo, valor)
    db.session.add(anuncio)
    db.session.commit()
    return anuncio


def crear_contacto(comprador, vendedor, anuncio):
    contacto = ContactoLog(
        comprador_id=comprador.id,
        vendedor_id=vendedor.id,
        anuncio_id=anuncio.id,
    )
    db.session.add(contacto)
    db.session.commit()
    return contacto


def crear_transaccion(vendedor, comprador, anuncio):
    anuncio.estado = "VENDIDO"
    anuncio.comprador_id = comprador.id
    transaccion = Transaccion(
        anuncio_id=anuncio.id,
        vendedor_id=vendedor.id,
        comprador_id=comprador.id,
        calificacion_vendedor_pending=True,
        calificacion_comprador_pending=True,
    )
    db.session.add(transaccion)
    db.session.commit()
    return transaccion


def token_para(usuario):
    return create_access_token(
        identity=str(usuario.id),
        additional_claims={"correo": usuario.correo, "rol": usuario.rol},
    )


def headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_calificar_vendedor_exitoso(client, app):
    with app.app_context():
        vendedor = crear_usuario("vendedor_hu15@gmail.com")
        comprador = crear_usuario("comprador_hu15@gmail.com")
        anuncio = crear_anuncio(vendedor)
        crear_contacto(comprador, vendedor, anuncio)
        transaccion = crear_transaccion(vendedor, comprador, anuncio)
        token = token_para(comprador)
        transaccion_id = transaccion.id
        vendedor_id = vendedor.id

    response = client.post(
        f"/api/v1/transacciones/{transaccion_id}/calificar/vendedor",
        json={
            "puntaje": 5,
            "comentario": "<b>Excelente</b> vendedor.\n",
        },
        headers=headers(token),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["transaccion_id"] == transaccion_id
    assert body["data"]["puntaje"] == 5
    assert body["data"]["comentario"] == "Excelente vendedor."
    assert body["data"]["calificado"]["id"] == vendedor_id
    assert body["data"]["calificado"]["calificacion_promedio"] == 5.0
    assert body["data"]["calificado"]["total_calificaciones"] == 1

    with app.app_context():
        vendedor_db = db.session.get(Usuario, vendedor_id)
        transaccion_db = db.session.get(Transaccion, transaccion_id)
        calificacion = Calificacion.query.filter_by(transaccion_id=transaccion_id).first()
        assert vendedor_db.total_calificaciones_vendedor == 1
        assert float(vendedor_db.calificacion_promedio_vendedor) == 5.0
        assert transaccion_db.calificacion_vendedor_pending is False
        assert calificacion is not None
        assert calificacion.tipo == "COMPRADOR_A_VENDEDOR"


def test_calificar_vendedor_solo_comprador_puede(client, app):
    with app.app_context():
        vendedor = crear_usuario("vendedor_forbidden@gmail.com")
        comprador = crear_usuario("comprador_forbidden@gmail.com")
        anuncio = crear_anuncio(vendedor)
        transaccion = crear_transaccion(vendedor, comprador, anuncio)
        token = token_para(vendedor)
        transaccion_id = transaccion.id

    response = client.post(
        f"/api/v1/transacciones/{transaccion_id}/calificar/vendedor",
        json={"puntaje": 4},
        headers=headers(token),
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == "FORBIDDEN"


def test_calificar_vendedor_no_permite_doble_calificacion(client, app):
    with app.app_context():
        vendedor = crear_usuario("vendedor_conflict@gmail.com")
        comprador = crear_usuario("comprador_conflict@gmail.com")
        anuncio = crear_anuncio(vendedor)
        transaccion = crear_transaccion(vendedor, comprador, anuncio)
        transaccion.calificacion_vendedor_pending = False
        db.session.commit()
        token = token_para(comprador)
        transaccion_id = transaccion.id

    response = client.post(
        f"/api/v1/transacciones/{transaccion_id}/calificar/vendedor",
        json={"puntaje": 4},
        headers=headers(token),
    )

    assert response.status_code == 409
    assert response.get_json()["error"] == "CONFLICT"


def test_calificar_vendedor_puntaje_fuera_rango_retorna_422(client, app):
    with app.app_context():
        vendedor = crear_usuario("vendedor_range@gmail.com")
        comprador = crear_usuario("comprador_range@gmail.com")
        anuncio = crear_anuncio(vendedor)
        transaccion = crear_transaccion(vendedor, comprador, anuncio)
        token = token_para(comprador)
        transaccion_id = transaccion.id

    response = client.post(
        f"/api/v1/transacciones/{transaccion_id}/calificar/vendedor",
        json={"puntaje": 6},
        headers=headers(token),
    )

    assert response.status_code == 422
    assert response.get_json()["error"] == "VALIDATION_ERROR"


def test_calificar_vendedor_comentario_muy_largo_retorna_422(client, app):
    with app.app_context():
        vendedor = crear_usuario("vendedor_long@gmail.com")
        comprador = crear_usuario("comprador_long@gmail.com")
        anuncio = crear_anuncio(vendedor)
        transaccion = crear_transaccion(vendedor, comprador, anuncio)
        token = token_para(comprador)
        transaccion_id = transaccion.id

    response = client.post(
        f"/api/v1/transacciones/{transaccion_id}/calificar/vendedor",
        json={"puntaje": 5, "comentario": "a" * 501},
        headers=headers(token),
    )

    assert response.status_code == 422
    assert response.get_json()["error"] == "VALIDATION_ERROR"


def test_calificar_vendedor_transaccion_inexistente_retorna_404(client, app):
    with app.app_context():
        comprador = crear_usuario("comprador_404@gmail.com")
        token = token_para(comprador)

    response = client.post(
        "/api/v1/transacciones/999/calificar/vendedor",
        json={"puntaje": 5},
        headers=headers(token),
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "NOT_FOUND"


def test_calificar_vendedor_cuenta_bloqueada_retorna_403(client, app):
    with app.app_context():
        vendedor = crear_usuario("vendedor_blocked@gmail.com")
        comprador = crear_usuario("comprador_blocked@gmail.com", estado="BLOQUEADO")
        anuncio = crear_anuncio(vendedor)
        transaccion = crear_transaccion(vendedor, comprador, anuncio)
        token = token_para(comprador)
        transaccion_id = transaccion.id

    response = client.post(
        f"/api/v1/transacciones/{transaccion_id}/calificar/vendedor",
        json={"puntaje": 5},
        headers=headers(token),
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == "FORBIDDEN"


def test_calificar_vendedor_requiere_puntaje(client, app):
    with app.app_context():
        vendedor = crear_usuario("vendedor_missing_score@gmail.com")
        comprador = crear_usuario("comprador_missing_score@gmail.com")
        anuncio = crear_anuncio(vendedor)
        transaccion = crear_transaccion(vendedor, comprador, anuncio)
        token = token_para(comprador)
        transaccion_id = transaccion.id

    response = client.post(
        f"/api/v1/transacciones/{transaccion_id}/calificar/vendedor",
        json={},
        headers=headers(token),
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "VALIDATION_ERROR"


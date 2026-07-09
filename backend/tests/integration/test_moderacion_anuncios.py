import pytest

pytestmark = pytest.mark.integration

from datetime import UTC, datetime, timedelta

import bcrypt
from flask_jwt_extended import create_access_token

from app import db
from app.models.anuncio import Anuncio
from app.models.moderacion_log import ModeracionLog
from app.models.reporte import Reporte
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


def crear_reporte(comprador, anuncio, motivo="FRAUDE", estado="PENDIENTE", created_at=None):
    reporte = Reporte(
        comprador_id=comprador.id,
        anuncio_id=anuncio.id,
        motivo=motivo,
        estado=estado,
        created_at=created_at or datetime.now(UTC).replace(tzinfo=None),
    )
    db.session.add(reporte)
    db.session.commit()
    return reporte


def token_para(usuario):
    return create_access_token(
        identity=str(usuario.id),
        additional_claims={"correo": usuario.correo, "rol": usuario.rol},
    )


def headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_reportar_anuncio_exitoso(client, app):
    with app.app_context():
        comprador = crear_usuario("comprador@gmail.com")
        vendedor = crear_usuario("vendedor@gmail.com")
        anuncio = crear_anuncio(vendedor)
        token = token_para(comprador)
        anuncio_id = anuncio.id

    response = client.post(
        f"/api/v1/anuncios/{anuncio_id}/reportar",
        json={"motivo": "fraude"},
        headers=headers(token),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["anuncio_id"] == anuncio_id
    assert body["data"]["motivo"] == "FRAUDE"
    assert body["data"]["estado"] == "PENDIENTE"


def test_reportar_anuncio_duplicado_en_mismo_ciclo_retorna_409(client, app):
    with app.app_context():
        comprador = crear_usuario("comprador2@gmail.com")
        vendedor = crear_usuario("vendedor2@gmail.com")
        anuncio = crear_anuncio(vendedor)
        crear_reporte(comprador, anuncio, estado="REVISADO")
        token = token_para(comprador)
        anuncio_id = anuncio.id

    response = client.post(
        f"/api/v1/anuncios/{anuncio_id}/reportar",
        json={"motivo": "FRAUDE"},
        headers=headers(token),
    )

    assert response.status_code == 409
    assert response.get_json()["error"] == "CONFLICT"


def test_reportar_anuncio_nuevo_ciclo_tras_desbloqueo_permitido(client, app):
    with app.app_context():
        comprador = crear_usuario("comprador3@gmail.com")
        vendedor = crear_usuario("vendedor3@gmail.com")
        admin = crear_usuario("admin@gmail.com", rol="ADMIN")
        anuncio = crear_anuncio(vendedor)
        token_comprador = token_para(comprador)
        token_admin = token_para(admin)
        anuncio_id = anuncio.id

    primer_reporte = client.post(
        f"/api/v1/anuncios/{anuncio_id}/reportar",
        json={"motivo": "FRAUDE"},
        headers=headers(token_comprador),
    )
    assert primer_reporte.status_code == 200

    bloqueo = client.patch(
        f"/api/v1/admin/anuncios/{anuncio_id}/bloquear",
        json={"motivo_admin": "Fraude confirmado."},
        headers=headers(token_admin),
    )
    assert bloqueo.status_code == 200

    desbloqueo = client.patch(
        f"/api/v1/admin/anuncios/{anuncio_id}/desbloquear",
        json={"motivo_admin": "Revisado nuevamente."},
        headers=headers(token_admin),
    )
    assert desbloqueo.status_code == 200

    segundo_reporte = client.post(
        f"/api/v1/anuncios/{anuncio_id}/reportar",
        json={"motivo": "OTRO"},
        headers=headers(token_comprador),
    )

    assert segundo_reporte.status_code == 200
    assert segundo_reporte.get_json()["data"]["motivo"] == "OTRO"


def test_reportar_propio_anuncio_retorna_409(client, app):
    with app.app_context():
        usuario = crear_usuario("propio@gmail.com")
        anuncio = crear_anuncio(usuario)
        token = token_para(usuario)
        anuncio_id = anuncio.id

    response = client.post(
        f"/api/v1/anuncios/{anuncio_id}/reportar",
        json={"motivo": "FRAUDE"},
        headers=headers(token),
    )

    assert response.status_code == 409
    assert response.get_json()["error"] == "CONFLICT"


def test_reportar_anuncio_inactivo_retorna_404(client, app):
    with app.app_context():
        comprador = crear_usuario("comprador4@gmail.com")
        vendedor = crear_usuario("vendedor4@gmail.com")
        anuncio = crear_anuncio(vendedor, estado="INACTIVO")
        token = token_para(comprador)
        anuncio_id = anuncio.id

    response = client.post(
        f"/api/v1/anuncios/{anuncio_id}/reportar",
        json={"motivo": "FRAUDE"},
        headers=headers(token),
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "NOT_FOUND"


def test_reportar_anuncio_supera_limite_diario_retorna_429(client, app):
    with app.app_context():
        comprador = crear_usuario("comprador5@gmail.com")
        vendedor = crear_usuario("vendedor5@gmail.com")
        anuncios = [crear_anuncio(vendedor, titulo=f"Anuncio {i}") for i in range(11)]
        now = datetime.now(UTC).replace(tzinfo=None)
        for anuncio in anuncios[:10]:
            crear_reporte(comprador, anuncio, created_at=now - timedelta(minutes=5))
        token = token_para(comprador)
        anuncio_id = anuncios[10].id

    response = client.post(
        f"/api/v1/anuncios/{anuncio_id}/reportar",
        json={"motivo": "OTRO"},
        headers=headers(token),
    )

    assert response.status_code == 429
    body = response.get_json()
    assert body["error"] == "RATE_LIMIT_REPORTES"
    assert "disponible_en" in body["data"]


def test_admin_lista_reportados_agrupa_pendientes(client, app):
    with app.app_context():
        admin = crear_usuario("admin2@gmail.com", rol="ADMIN")
        vendedor = crear_usuario("vendedor6@gmail.com", rol="TIENDA_VERIFICADA")
        comprador_a = crear_usuario("comprador6a@gmail.com")
        comprador_b = crear_usuario("comprador6b@gmail.com")
        anuncio = crear_anuncio(vendedor)
        crear_reporte(comprador_a, anuncio, motivo="FRAUDE")
        crear_reporte(comprador_b, anuncio, motivo="PRODUCTO_FALSO")
        token = token_para(admin)
        anuncio_id = anuncio.id

    response = client.get(
        "/api/v1/admin/anuncios/reportados?page=1&limit=20",
        headers=headers(token),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["total_pendientes"] == 1
    assert body["data"][0]["anuncio_id"] == anuncio_id
    assert body["data"][0]["total_reportes"] == 2
    assert set(body["data"][0]["motivos"]) == {"FRAUDE", "PRODUCTO_FALSO"}
    assert body["data"][0]["es_tienda_verificada"] is True


def test_admin_no_admin_retorna_403_en_lista_reportados(client, app):
    with app.app_context():
        usuario = crear_usuario("noadmin@gmail.com")
        token = token_para(usuario)

    response = client.get(
        "/api/v1/admin/anuncios/reportados",
        headers=headers(token),
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == "FORBIDDEN"


def test_admin_bloquear_anuncio_actualiza_estado_reportes_y_log(client, app):
    with app.app_context():
        admin = crear_usuario("admin3@gmail.com", rol="ADMIN")
        comprador = crear_usuario("comprador7@gmail.com")
        vendedor = crear_usuario("vendedor7@gmail.com")
        anuncio = crear_anuncio(vendedor)
        crear_reporte(comprador, anuncio, motivo="FRAUDE")
        token = token_para(admin)
        anuncio_id = anuncio.id

    response = client.patch(
        f"/api/v1/admin/anuncios/{anuncio_id}/bloquear",
        json={"motivo_admin": "Anuncio fraudulento confirmado."},
        headers=headers(token),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"]["estado"] == "BLOQUEADO"

    with app.app_context():
        anuncio_db = db.session.get(Anuncio, anuncio_id)
        reportes = Reporte.query.filter_by(anuncio_id=anuncio_id).all()
        log_entry = ModeracionLog.query.filter_by(anuncio_id=anuncio_id, accion="BLOQUEADO").first()
        assert anuncio_db.estado == "BLOQUEADO"
        assert reportes and all(reporte.estado == "REVISADO" for reporte in reportes)
        assert log_entry is not None
        assert log_entry.motivo_admin == "Anuncio fraudulento confirmado."


def test_admin_desbloquear_anuncio_retorna_activo_y_deja_auditoria(client, app):
    with app.app_context():
        admin = crear_usuario("admin4@gmail.com", rol="ADMIN")
        vendedor = crear_usuario("vendedor8@gmail.com")
        anuncio = crear_anuncio(vendedor, estado="BLOQUEADO")
        token = token_para(admin)
        anuncio_id = anuncio.id

    response = client.patch(
        f"/api/v1/admin/anuncios/{anuncio_id}/desbloquear",
        json={"motivo_admin": "Revisado, no se encontro infraccion."},
        headers=headers(token),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"]["estado"] == "ACTIVO"

    with app.app_context():
        anuncio_db = db.session.get(Anuncio, anuncio_id)
        log_entry = ModeracionLog.query.filter_by(anuncio_id=anuncio_id, accion="DESBLOQUEADO").first()
        assert anuncio_db.estado == "ACTIVO"
        assert log_entry is not None


def test_admin_bloquear_requiere_motivo_admin_no_vacio(client, app):
    with app.app_context():
        admin = crear_usuario("admin5@gmail.com", rol="ADMIN")
        vendedor = crear_usuario("vendedor9@gmail.com")
        anuncio = crear_anuncio(vendedor)
        token = token_para(admin)
        anuncio_id = anuncio.id

    response = client.patch(
        f"/api/v1/admin/anuncios/{anuncio_id}/bloquear",
        json={"motivo_admin": "   "},
        headers=headers(token),
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "VALIDATION_ERROR"


def test_historial_moderacion_admin_devuelve_eventos(client, app):
    with app.app_context():
        admin = crear_usuario("admin6@gmail.com", rol="ADMIN")
        vendedor = crear_usuario("vendedor10@gmail.com")
        anuncio = crear_anuncio(vendedor)
        token = token_para(admin)
        anuncio_id = anuncio.id

    bloqueo = client.patch(
        f"/api/v1/admin/anuncios/{anuncio_id}/bloquear",
        json={"motivo_admin": "Bloqueado por revision."},
        headers=headers(token),
    )
    assert bloqueo.status_code == 200

    response = client.get(
        "/api/v1/admin/moderacion/historial?page=1&limit=20",
        headers=headers(token),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"][0]["anuncio_id"] == anuncio_id
    assert body["data"][0]["accion"] == "BLOQUEADO"


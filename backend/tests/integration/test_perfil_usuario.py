import pytest

pytestmark = pytest.mark.integration

from datetime import UTC, datetime, timedelta

import bcrypt

from app import db
from app.models.anuncio import Anuncio
from app.models.media_anuncio import MediaAnuncio
from app.models.tienda import Tienda
from app.models.transaccion import Transaccion
from app.models.usuario import Usuario


PASSWORD = "123456#P"
PERFIL_URL = "/api/v1/usuarios"


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


def crear_tienda(usuario, estado="ACTIVO"):
    tienda = Tienda(
        usuario_id=usuario.id,
        nombre_comercial=f"Tienda {usuario.id}",
        ruc=f"{10000000000 + usuario.id}",
        direccion=f"Jr. Comercio {usuario.id}",
        documento_identidad=f"uploads/tiendas/{usuario.id}/dni.pdf",
        estado=estado,
    )
    db.session.add(tienda)
    db.session.commit()
    return tienda


def crear_anuncio(usuario, titulo, estado="ACTIVO", created_at=None):
    anuncio = Anuncio(
        usuario_id=usuario.id,
        titulo=titulo,
        descripcion=f"Descripcion {titulo}",
        categoria="COMPONENTES",
        subcategoria="PROCESADOR",
        condicion="USADO",
        precio="100.00",
        especificaciones={"socket": "AM4"},
        estado=estado,
        reactivaciones_count=0,
    )
    if created_at is not None:
        anuncio.created_at = created_at
        anuncio.updated_at = created_at
    db.session.add(anuncio)
    db.session.commit()
    return anuncio


def crear_imagen_principal(anuncio, nombre="principal.jpg"):
    media = MediaAnuncio(
        anuncio_id=anuncio.id,
        tipo_media="imagen",
        ruta_relativa=f"uploads/anuncios/{anuncio.id}/{nombre}",
        es_principal=True,
        orden=0,
    )
    db.session.add(media)
    db.session.commit()
    return media


def crear_transaccion(vendedor, comprador, anuncio):
    anuncio.estado = "VENDIDO"
    anuncio.comprador_id = comprador.id
    transaccion = Transaccion(
        anuncio_id=anuncio.id,
        vendedor_id=vendedor.id,
        comprador_id=comprador.id,
        calificacion_vendedor_pending=False,
        calificacion_comprador_pending=False,
    )
    db.session.add(transaccion)
    db.session.commit()
    return transaccion


def test_perfil_publico_usuario_estandar_con_reputacion_y_anuncios(client, app):
    with app.app_context():
        vendedor = crear_usuario("perfil@gmail.com")
        comprador = crear_usuario("comprador_perfil@gmail.com")
        vendedor.calificacion_promedio_vendedor = 4.8
        vendedor.total_calificaciones_vendedor = 23
        vendedor.calificacion_promedio_comprador = 4.6
        vendedor.total_calificaciones_comprador = 11
        db.session.commit()

        anuncio_activo = crear_anuncio(vendedor, "Activo reciente", created_at=datetime.now(UTC).replace(tzinfo=None))
        crear_anuncio(vendedor, "Inactivo", estado="INACTIVO")
        crear_imagen_principal(anuncio_activo, "foto.jpg")

        for i in range(18):
            anuncio_vendido = crear_anuncio(vendedor, f"Vendido {i}")
            crear_transaccion(vendedor, comprador, anuncio_vendido)

        for i in range(11):
            anuncio_compra = crear_anuncio(comprador, f"Compra {i}")
            crear_transaccion(comprador, vendedor, anuncio_compra)

        usuario_id = vendedor.id

    response = client.get(f"{PERFIL_URL}/{usuario_id}/perfil")

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["id"] == usuario_id
    assert body["data"]["es_tienda_verificada"] is False
    assert body["data"]["reputacion_vendedor"] == {
        "calificacion_promedio": 4.8,
        "total_calificaciones": 23,
        "total_ventas": 18,
    }
    assert body["data"]["reputacion_comprador"] == {
        "calificacion_promedio": 4.6,
        "total_calificaciones": 11,
        "total_compras": 11,
    }
    assert len(body["data"]["anuncios_activos"]) == 1
    assert body["data"]["anuncios_activos"][0]["titulo"] == "Activo reciente"
    assert body["data"]["anuncios_activos"][0]["imagen_principal"].endswith("foto.jpg")
    assert "tienda" not in body["data"]


def test_perfil_publico_tienda_verificada_incluye_tienda_y_limite_10_anuncios(client, app):
    with app.app_context():
        usuario = crear_usuario("tienda_perfil@gmail.com", rol="TIENDA_VERIFICADA")
        tienda = crear_tienda(usuario)
        usuario.calificacion_promedio_vendedor = 4.9
        usuario.total_calificaciones_vendedor = 87
        usuario.calificacion_promedio_comprador = 5.0
        usuario.total_calificaciones_comprador = 3
        db.session.commit()

        now = datetime.now(UTC).replace(tzinfo=None)
        for i in range(12):
            anuncio = crear_anuncio(
                usuario,
                f"Activo {i}",
                created_at=(now - timedelta(hours=i)),
            )
            if i == 0:
                crear_imagen_principal(anuncio, "principal.jpg")

        usuario_id = usuario.id
        direccion = tienda.direccion
        nombre_comercial = tienda.nombre_comercial

    response = client.get(f"{PERFIL_URL}/{usuario_id}/perfil")

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"]["es_tienda_verificada"] is True
    assert body["data"]["tienda"] == {
        "nombre_comercial": nombre_comercial,
        "direccion": direccion,
    }
    assert body["data"]["reputacion_vendedor"]["calificacion_promedio"] == 4.9
    assert body["data"]["reputacion_comprador"]["calificacion_promedio"] == 5.0
    assert body["data"]["total_anuncios_activos"] == 12
    assert len(body["data"]["anuncios_activos"]) == 10
    assert body["data"]["anuncios_activos"][0]["titulo"] == "Activo 0"
    assert body["data"]["anuncios_activos"][-1]["titulo"] == "Activo 9"


def test_perfil_publico_usuario_sin_actividad_retorna_nulls_y_listas_vacias(client, app):
    with app.app_context():
        usuario = crear_usuario("sin_actividad@gmail.com")
        usuario_id = usuario.id

    response = client.get(f"{PERFIL_URL}/{usuario_id}/perfil")

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"]["reputacion_vendedor"] == {
        "calificacion_promedio": None,
        "total_calificaciones": 0,
        "total_ventas": 0,
    }
    assert body["data"]["reputacion_comprador"] == {
        "calificacion_promedio": None,
        "total_calificaciones": 0,
        "total_compras": 0,
    }
    assert body["data"]["anuncios_activos"] == []
    assert body["data"]["total_anuncios_activos"] == 0


def test_perfil_publico_usuario_no_activo_retorna_404(client, app):
    with app.app_context():
        usuario = crear_usuario("bloqueado_perfil@gmail.com", estado="BLOQUEADO")
        usuario_id = usuario.id

    response = client.get(f"{PERFIL_URL}/{usuario_id}/perfil")

    assert response.status_code == 404
    assert response.get_json()["error"] == "NOT_FOUND"


def test_perfil_publico_usuario_inexistente_retorna_404(client):
    response = client.get(f"{PERFIL_URL}/999/perfil")

    assert response.status_code == 404
    assert response.get_json()["error"] == "NOT_FOUND"


def test_perfil_publico_usuario_id_invalido_retorna_400(client):
    response = client.get(f"{PERFIL_URL}/0/perfil")

    assert response.status_code == 400
    assert response.get_json()["error"] == "VALIDATION_ERROR"


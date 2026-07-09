import pytest

pytestmark = pytest.mark.integration

from datetime import UTC, datetime, timedelta

import bcrypt

from app import db
from app.models.anuncio import Anuncio
from app.models.media_anuncio import MediaAnuncio
from app.models.usuario import Usuario


PASSWORD = "123456#P"
FEED_URL = "/api/v1/anuncios"


def crear_usuario(correo="feed@gmail.com", rol="USER_ESTANDAR"):
    password_hash = bcrypt.hashpw(PASSWORD.encode("utf-8"), bcrypt.gensalt(rounds=10)).decode("utf-8")
    usuario = Usuario(
        nombre=f"Usuario {correo}",
        correo=correo,
        password_hash=password_hash,
        telefono=f"9{abs(hash(correo)) % 100000000:08d}",
        rol=rol,
        estado="ACTIVO",
    )
    db.session.add(usuario)
    db.session.commit()
    return usuario


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


def test_feed_publico_retorna_anuncios_activos_paginados(client, app):
    with app.app_context():
        vendedor = crear_usuario()
        vendedor_nombre = vendedor.nombre
        es_tienda_verificada = vendedor.rol == "TIENDA_VERIFICADA"
        reciente = crear_anuncio(vendedor, "Mas reciente", created_at=datetime.now(UTC).replace(tzinfo=None))
        medio = crear_anuncio(
            vendedor,
            "Intermedio",
            created_at=(datetime.now(UTC) - timedelta(days=1)).replace(tzinfo=None),
        )
        crear_anuncio(
            vendedor,
            "Inactivo",
            estado="INACTIVO",
            created_at=(datetime.now(UTC) - timedelta(days=2)).replace(tzinfo=None),
        )
        crear_anuncio(
            vendedor,
            "Vendido",
            estado="VENDIDO",
            created_at=(datetime.now(UTC) - timedelta(days=3)).replace(tzinfo=None),
        )
        crear_imagen_principal(reciente, "reciente.jpg")
        crear_imagen_principal(medio, "medio.jpg")

    response = client.get(f"{FEED_URL}?page=1&limit=20")

    assert response.status_code == 200
    body = response.get_json()
    assert [item["titulo"] for item in body["data"]] == ["Mas reciente", "Intermedio"]
    assert body["data"][0]["imagen_principal"].endswith("reciente.jpg")
    assert body["data"][0]["vendedor_nombre"] == vendedor_nombre
    assert body["data"][0]["categoria"] == "COMPONENTES"
    assert body["data"][0]["subcategoria"] == "PROCESADOR"
    assert body["data"][0]["es_tienda_verificada"] is es_tienda_verificada
    assert body["data"][0]["updated_at"] is not None
    assert "vendedor_rol" not in body["data"][0]
    assert body["paginacion"] == {
        "total": 2,
        "pagina_actual": 1,
        "total_paginas": 1,
        "limit": 20,
        "tiene_siguiente": False,
        "tiene_anterior": False,
    }


def test_feed_publico_page_fuera_de_rango_retorna_data_vacia(client, app):
    with app.app_context():
        vendedor = crear_usuario()
        crear_anuncio(vendedor, "Unico")

    response = client.get(f"{FEED_URL}?page=3&limit=20")

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"] == []
    assert body["paginacion"]["total"] == 1
    assert body["paginacion"]["pagina_actual"] == 3
    assert body["paginacion"]["total_paginas"] == 1


def test_feed_publico_limit_maximo_50(client, app):
    response = client.get(f"{FEED_URL}?page=1&limit=51")

    assert response.status_code == 400
    body = response.get_json()
    assert body["error"] == "VALIDATION_ERROR"


def test_feed_publico_page_invalido_retorna_400(client, app):
    response = client.get(f"{FEED_URL}?page=abc&limit=20")

    assert response.status_code == 400
    body = response.get_json()
    assert body["error"] == "VALIDATION_ERROR"


def test_feed_publico_limit_invalido_retorna_400(client, app):
    response = client.get(f"{FEED_URL}?page=1&limit=0")

    assert response.status_code == 400
    body = response.get_json()
    assert body["error"] == "VALIDATION_ERROR"


def test_feed_publico_imagen_principal_puede_ser_null(client, app):
    with app.app_context():
        vendedor = crear_usuario(rol="TIENDA_VERIFICADA")
        crear_anuncio(vendedor, "Sin imagen")

    response = client.get(FEED_URL)

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"][0]["imagen_principal"] is None
    assert body["data"][0]["es_tienda_verificada"] is True


import pytest

pytestmark = pytest.mark.integration

from datetime import UTC, datetime, timedelta

import bcrypt

from app import db
from app.models.anuncio import Anuncio
from app.models.media_anuncio import MediaAnuncio
from app.models.usuario import Usuario


BUSCAR_URL = "/api/v1/anuncios/buscar"
PASSWORD = "123456#P"


def _telefono_para(correo):
    base = abs(hash(correo)) % 100000000
    return f"9{base:08d}"


def crear_usuario(correo="busqueda@gmail.com", rol="USER_ESTANDAR"):
    password_hash = bcrypt.hashpw(PASSWORD.encode("utf-8"), bcrypt.gensalt(rounds=10)).decode("utf-8")
    usuario = Usuario(
        nombre=f"Usuario {correo}",
        correo=correo,
        password_hash=password_hash,
        telefono=_telefono_para(correo),
        rol=rol,
        estado="ACTIVO",
    )
    db.session.add(usuario)
    db.session.commit()
    return usuario


def crear_anuncio(
    usuario,
    titulo,
    *,
    precio="100.00",
    categoria="COMPONENTES",
    subcategoria="PROCESADOR",
    condicion="USADO",
    especificaciones=None,
    estado="ACTIVO",
    created_at=None,
):
    anuncio = Anuncio(
        usuario_id=usuario.id,
        titulo=titulo,
        descripcion=f"Descripcion {titulo}",
        categoria=categoria,
        subcategoria=subcategoria,
        condicion=condicion,
        precio=precio,
        especificaciones=especificaciones or {},
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


def test_busqueda_filtra_por_subcategoria_specs_y_precio(client, app):
    with app.app_context():
        vendedor = crear_usuario()
        match = crear_anuncio(
            vendedor,
            "Ryzen 5 5600X AM4",
            precio="450.00",
            condicion="COMO_NUEVO",
            especificaciones={"socket": "AM4", "nucleos": 6, "incluye_cooler": True},
        )
        crear_imagen_principal(match, "ryzen.jpg")
        crear_anuncio(
            vendedor,
            "Ryzen 7 7700X",
            precio="900.00",
            condicion="NUEVO",
            especificaciones={"socket": "AM5", "nucleos": 8, "incluye_cooler": False},
        )

    response = client.get(
        BUSCAR_URL,
        query_string={
            "subcategoria": "procesador",
            "precio_min": "400",
            "precio_max": "500",
            "specs[socket]": "AM4",
            "specs[nucleos]": "6",
            "specs[incluye_cooler]": "true",
        },
    )

    assert response.status_code == 200
    body = response.get_json()
    assert [item["titulo"] for item in body["data"]] == ["Ryzen 5 5600X AM4"]
    assert body["data"][0]["imagen_principal"].endswith("ryzen.jpg")
    assert body["filtros_aplicados"] == {
        "order_by": "reciente",
        "subcategoria": "PROCESADOR",
        "precio_min": "400",
        "precio_max": "500",
        "specs": {
            "socket": "AM4",
            "nucleos": "6",
            "incluye_cooler": "true",
        },
    }
    assert body["paginacion"]["total"] == 1


def test_busqueda_q_escapa_wildcards_y_no_hace_match_amplio(client, app):
    with app.app_context():
        vendedor = crear_usuario()
        crear_anuncio(vendedor, "Ryzen AM%4 especial")
        crear_anuncio(vendedor, "Ryzen AMX4 comun")

    response = client.get(BUSCAR_URL, query_string={"q": "AM%4"})

    assert response.status_code == 200
    body = response.get_json()
    assert [item["titulo"] for item in body["data"]] == ["Ryzen AM%4 especial"]
    assert body["filtros_aplicados"]["q"] == "AM%4"


def test_busqueda_order_by_precio_asc_y_paginacion(client, app):
    with app.app_context():
        vendedor = crear_usuario()
        base_time = datetime.now(UTC).replace(tzinfo=None)
        crear_anuncio(vendedor, "Caro", precio="900.00", created_at=base_time)
        crear_anuncio(vendedor, "Barato", precio="100.00", created_at=base_time - timedelta(days=1))
        crear_anuncio(vendedor, "Medio", precio="500.00", created_at=base_time - timedelta(days=2))

    response = client.get(
        BUSCAR_URL,
        query_string={"order_by": "precio_asc", "page": "1", "limit": "2"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert [item["titulo"] for item in body["data"]] == ["Barato", "Medio"]
    assert body["paginacion"] == {
        "total": 3,
        "pagina_actual": 1,
        "total_paginas": 2,
        "limit": 2,
        "tiene_siguiente": True,
        "tiene_anterior": False,
    }


def test_busqueda_usuario_tienda_transforma_rol_a_bandera_publica(client, app):
    with app.app_context():
        vendedor = crear_usuario("tienda@gmail.com", rol="TIENDA_VERIFICADA")
        crear_anuncio(vendedor, "Monitor gamer")

    response = client.get(BUSCAR_URL)

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"][0]["es_tienda_verificada"] is True
    assert "rol" not in body["data"][0]


def test_busqueda_precio_min_mayor_precio_max_retorna_400(client):
    response = client.get(BUSCAR_URL, query_string={"precio_min": "500", "precio_max": "100"})

    assert response.status_code == 400
    body = response.get_json()
    assert body["error"] == "VALIDATION_ERROR"
    assert "precio_min" in body["data"]


def test_busqueda_q_menor_a_dos_caracteres_retorna_400(client):
    response = client.get(BUSCAR_URL, query_string={"q": "a"})

    assert response.status_code == 400
    assert response.get_json()["error"] == "VALIDATION_ERROR"


def test_busqueda_order_by_invalido_retorna_422(client):
    response = client.get(BUSCAR_URL, query_string={"order_by": "popular"})

    assert response.status_code == 422
    assert response.get_json()["error"] == "VALIDATION_ERROR"


def test_busqueda_spec_key_invalida_retorna_422(client):
    response = client.get(BUSCAR_URL, query_string={"specs[socket-drop]": "AM4"})

    assert response.status_code == 422
    body = response.get_json()
    assert body["error"] == "VALIDATION_ERROR"
    assert "specs" in body["data"]


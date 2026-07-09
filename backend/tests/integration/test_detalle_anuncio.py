import pytest

pytestmark = pytest.mark.integration

from datetime import UTC, datetime

import bcrypt
from flask_jwt_extended import create_access_token

from app import db
from app.models.anuncio import Anuncio
from app.models.media_anuncio import MediaAnuncio
from app.models.tienda import Tienda
from app.models.usuario import Usuario


DETAIL_URL = "/api/v1/anuncios"
PASSWORD = "123456#P"


def _telefono_para(correo):
    base = abs(hash(correo)) % 100000000
    return f"9{base:08d}"


def crear_usuario(correo="detalle@gmail.com", rol="USER_ESTANDAR"):
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


def crear_tienda(usuario, nombre_comercial="TechStore Ayacucho"):
    tienda = Tienda(
        usuario_id=usuario.id,
        nombre_comercial=nombre_comercial,
        ruc=f"20{abs(hash(nombre_comercial)) % 1000000000:09d}",
        direccion="Jr. Lima 123, Ayacucho",
        documento_identidad="uploads/tiendas/doc.png",
        estado="ACTIVO",
    )
    db.session.add(tienda)
    db.session.commit()
    return tienda


def crear_anuncio(usuario, **overrides):
    anuncio = Anuncio(
        usuario_id=usuario.id,
        titulo="Ryzen 5 5600X casi nuevo",
        descripcion="Procesador en excelente estado.",
        categoria="COMPONENTES",
        subcategoria="PROCESADOR",
        condicion="COMO_NUEVO",
        precio="450.00",
        especificaciones={"socket": "AM4", "nucleos": 6},
        estado="ACTIVO",
        reactivaciones_count=0,
    )
    for campo, valor in overrides.items():
        setattr(anuncio, campo, valor)
    db.session.add(anuncio)
    db.session.commit()
    return anuncio


def crear_media(anuncio, tipo_media="imagen", nombre="archivo.jpg", es_principal=False, orden=None):
    media = MediaAnuncio(
        anuncio_id=anuncio.id,
        tipo_media=tipo_media,
        ruta_relativa=f"uploads/anuncios/{anuncio.id}/{nombre}",
        es_principal=es_principal,
        orden=orden,
    )
    db.session.add(media)
    db.session.commit()
    return media


def token_para(usuario):
    return create_access_token(
        identity=str(usuario.id),
        additional_claims={"correo": usuario.correo, "rol": usuario.rol},
    )


def headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_detalle_publico_visitante_oculta_telefono_y_muestra_media(client, app):
    with app.app_context():
        vendedor = crear_usuario()
        anuncio = crear_anuncio(vendedor, updated_at=None)
        crear_media(anuncio, "imagen", "principal.jpg", True, 0)
        crear_media(anuncio, "imagen", "segunda.jpg", False, 1)
        crear_media(anuncio, "video", "demo.mp4", False, None)
        anuncio_id = anuncio.id

    response = client.get(f"{DETAIL_URL}/{anuncio_id}")

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"]["id"] == anuncio_id
    assert body["data"]["es_propietario"] is False
    assert body["data"]["vendedor"]["telefono"] is None
    assert body["data"]["vendedor"]["es_tienda_verificada"] is False
    assert "tienda" not in body["data"]["vendedor"]
    assert [item["tipo_media"] for item in body["data"]["media"]] == ["imagen", "imagen", "video"]
    assert body["data"]["updated_at"] is not None
    assert "estado_propietario" not in body["data"]


def test_detalle_autenticado_muestra_telefono_y_tienda_si_corresponde(client, app):
    with app.app_context():
        vendedor = crear_usuario("tienda@gmail.com", rol="TIENDA_VERIFICADA")
        tienda = crear_tienda(vendedor)
        anuncio = crear_anuncio(
            vendedor,
            titulo="RTX 4070 SUPER nueva",
            subcategoria="GPU",
            condicion="NUEVO",
            precio="2800.00",
            especificaciones={"vram_gb": 12, "tipo_memoria": "GDDR6X", "tdp_w": 220},
            created_at=datetime.now(UTC).replace(tzinfo=None),
        )
        crear_media(anuncio, "imagen", "principal.jpg", True, 0)
        visitante = crear_usuario("visitante@gmail.com")
        token = token_para(visitante)
        anuncio_id = anuncio.id
        vendedor_telefono = vendedor.telefono
        tienda_data = {
            "nombre_comercial": tienda.nombre_comercial,
            "direccion": tienda.direccion,
        }

    response = client.get(f"{DETAIL_URL}/{anuncio_id}", headers=headers(token))

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"]["es_propietario"] is False
    assert body["data"]["vendedor"]["telefono"] == vendedor_telefono
    assert body["data"]["vendedor"]["es_tienda_verificada"] is True
    assert body["data"]["vendedor"]["tienda"] == tienda_data


def test_detalle_propietario_puede_ver_inactivo_con_estado_propietario(client, app):
    with app.app_context():
        vendedor = crear_usuario()
        anuncio = crear_anuncio(vendedor, estado="INACTIVO", reactivaciones_count=1)
        token = token_para(vendedor)
        anuncio_id = anuncio.id
        vendedor_telefono = vendedor.telefono

    response = client.get(f"{DETAIL_URL}/{anuncio_id}", headers=headers(token))

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"]["es_propietario"] is True
    assert body["data"]["estado_propietario"] == {
        "estado": "INACTIVO",
        "reactivaciones_restantes": 2,
    }
    assert body["data"]["vendedor"]["telefono"] == vendedor_telefono


def test_detalle_propietario_con_reactivaciones_nulas_no_falla(client, app):
    with app.app_context():
        vendedor = crear_usuario()
        anuncio = crear_anuncio(vendedor, estado="INACTIVO", reactivaciones_count=None)
        token = token_para(vendedor)
        anuncio_id = anuncio.id

    response = client.get(f"{DETAIL_URL}/{anuncio_id}", headers=headers(token))

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"]["estado_propietario"] == {
        "estado": "INACTIVO",
        "reactivaciones_restantes": 3,
    }


def test_detalle_inactivo_para_tercero_retorna_404(client, app):
    with app.app_context():
        vendedor = crear_usuario()
        anuncio = crear_anuncio(vendedor, estado="INACTIVO")
        tercero = crear_usuario("tercero@gmail.com")
        token = token_para(tercero)
        anuncio_id = anuncio.id

    response = client.get(f"{DETAIL_URL}/{anuncio_id}", headers=headers(token))

    assert response.status_code == 404
    assert response.get_json()["error"] == "NOT_FOUND"


def test_detalle_vendido_y_bloqueado_ocultos_incluso_para_propietario(client, app):
    with app.app_context():
        vendedor = crear_usuario()
        vendido = crear_anuncio(vendedor, estado="VENDIDO")
        bloqueado = crear_anuncio(vendedor, estado="BLOQUEADO", titulo="Bloqueado")
        token = token_para(vendedor)
        vendido_id = vendido.id
        bloqueado_id = bloqueado.id

    response_vendido = client.get(f"{DETAIL_URL}/{vendido_id}", headers=headers(token))
    response_bloqueado = client.get(f"{DETAIL_URL}/{bloqueado_id}", headers=headers(token))

    assert response_vendido.status_code == 404
    assert response_bloqueado.status_code == 404


def test_detalle_anuncio_id_invalido_retorna_400(client):
    response = client.get(f"{DETAIL_URL}/0")

    assert response.status_code == 400
    assert response.get_json()["error"] == "VALIDATION_ERROR"


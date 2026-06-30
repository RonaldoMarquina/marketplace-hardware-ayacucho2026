from datetime import UTC, datetime, timedelta
from urllib.parse import parse_qs, urlparse

import bcrypt
from flask_jwt_extended import create_access_token

from app import db
from app.models.anuncio import Anuncio
from app.models.contacto_log import ContactoLog
from app.models.tienda import Tienda
from app.models.usuario import Usuario


CONTACTO_URL = "/api/v1/anuncios"
PASSWORD = "123456#P"


def _telefono_para(correo):
    base = abs(hash(correo)) % 100000000
    return f"9{base:08d}"


def crear_usuario(correo="comprador@gmail.com", rol="USER_ESTANDAR", estado="ACTIVO", telefono=None):
    password_hash = bcrypt.hashpw(PASSWORD.encode("utf-8"), bcrypt.gensalt(rounds=10)).decode("utf-8")
    usuario = Usuario(
        nombre=f"Usuario {correo}",
        correo=correo,
        password_hash=password_hash,
        telefono=telefono if telefono is not None else _telefono_para(correo),
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
        ruc=f"20{usuario.id:09d}",
        direccion="Jr. Lima 123, Ayacucho",
        documento_identidad="uploads/tiendas/doc.png",
        estado=estado,
    )
    db.session.add(tienda)
    db.session.commit()
    return tienda


def crear_anuncio(usuario, **overrides):
    anuncio = Anuncio(
        usuario_id=usuario.id,
        titulo='Ryzen "Elite"\n5600X',
        descripcion="Descripcion",
        categoria="COMPONENTES",
        subcategoria="PROCESADOR",
        condicion="COMO_NUEVO",
        precio="450.00",
        especificaciones={"socket": "AM4"},
        estado="ACTIVO",
        reactivaciones_count=0,
    )
    for campo, valor in overrides.items():
        setattr(anuncio, campo, valor)
    db.session.add(anuncio)
    db.session.commit()
    return anuncio


def crear_contacto(comprador, vendedor, anuncio, created_at):
    contacto = ContactoLog(
        comprador_id=comprador.id,
        vendedor_id=vendedor.id,
        anuncio_id=anuncio.id,
        created_at=created_at,
    )
    db.session.add(contacto)
    db.session.commit()
    return contacto


def token_para(usuario):
    return create_access_token(
        identity=str(usuario.id),
        additional_claims={"correo": usuario.correo, "rol": usuario.rol},
    )


def headers(token):
    return {"Authorization": f"Bearer {token}"}


def _ahora_local():
    return (datetime.now(UTC) - timedelta(hours=5)).replace(tzinfo=None)


def test_contacto_whatsapp_exitoso_loguea_y_oculta_telefono_directo(client, app):
    with app.app_context():
        comprador = crear_usuario()
        vendedor = crear_usuario("vendedor@gmail.com")
        anuncio = crear_anuncio(vendedor)
        token = token_para(comprador)
        anuncio_id = anuncio.id
        vendedor_nombre = vendedor.nombre
        titulo = anuncio.titulo

    response = client.get(f"{CONTACTO_URL}/{anuncio_id}/contacto", headers=headers(token))

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["vendedor_nombre"] == vendedor_nombre
    assert body["data"]["anuncio_titulo"] == titulo
    assert f"51{_telefono_para('vendedor@gmail.com')}" in body["data"]["whatsapp_url"]
    parsed = urlparse(body["data"]["whatsapp_url"])
    mensaje = parse_qs(parsed.query)["text"][0]
    assert '"Ryzen Elite5600X"' in mensaje
    assert "'Ryzen" not in mensaje
    assert "\n" not in mensaje

    with app.app_context():
        log = ContactoLog.query.one()
        assert log.comprador_id == comprador.id
        assert log.vendedor_id == vendedor.id
        assert log.anuncio_id == anuncio_id


def test_contacto_sin_jwt_retorna_401(client, app):
    with app.app_context():
        vendedor = crear_usuario("vendedor@gmail.com")
        anuncio = crear_anuncio(vendedor)
        anuncio_id = anuncio.id

    response = client.get(f"{CONTACTO_URL}/{anuncio_id}/contacto")

    assert response.status_code == 401
    assert response.get_json()["error"] == "UNAUTHORIZED"


def test_contacto_autocontacto_retorna_409(client, app):
    with app.app_context():
        vendedor = crear_usuario("dueno@gmail.com")
        anuncio = crear_anuncio(vendedor)
        token = token_para(vendedor)
        anuncio_id = anuncio.id

    response = client.get(f"{CONTACTO_URL}/{anuncio_id}/contacto", headers=headers(token))

    assert response.status_code == 409
    assert response.get_json()["error"] == "CONFLICT"


def test_contacto_vendedor_sin_telefono_retorna_422(client, app):
    with app.app_context():
        comprador = crear_usuario()
        vendedor = crear_usuario("sinfono@gmail.com", telefono=None)
        vendedor.telefono = None
        db.session.commit()
        anuncio = crear_anuncio(vendedor)
        token = token_para(comprador)
        anuncio_id = anuncio.id

    response = client.get(f"{CONTACTO_URL}/{anuncio_id}/contacto", headers=headers(token))

    assert response.status_code == 422
    assert response.get_json()["error"] == "SELLER_WITHOUT_PHONE"


def test_contacto_comprador_tienda_en_revision_retorna_403(client, app):
    with app.app_context():
        comprador = crear_usuario("tienda@gmail.com", rol="TIENDA_VERIFICADA")
        crear_tienda(comprador, estado="EN_REVISION")
        vendedor = crear_usuario("vendedor@gmail.com")
        anuncio = crear_anuncio(vendedor)
        token = token_para(comprador)
        anuncio_id = anuncio.id

    response = client.get(f"{CONTACTO_URL}/{anuncio_id}/contacto", headers=headers(token))

    assert response.status_code == 403
    assert response.get_json()["error"] == "FORBIDDEN"


def test_contacto_mismo_anuncio_en_ultima_hora_retorna_429(client, app):
    with app.app_context():
        comprador = crear_usuario()
        vendedor = crear_usuario("vendedor@gmail.com")
        anuncio = crear_anuncio(vendedor)
        crear_contacto(comprador, vendedor, anuncio, _ahora_local() - timedelta(minutes=30))
        token = token_para(comprador)
        anuncio_id = anuncio.id

    response = client.get(f"{CONTACTO_URL}/{anuncio_id}/contacto", headers=headers(token))

    assert response.status_code == 429
    body = response.get_json()
    assert body["error"] == "RATE_LIMIT_ANUNCIO"
    assert "disponible_en" in body["data"]


def test_contacto_limite_diario_20_vendedores_distintos_retorna_429(client, app):
    with app.app_context():
        comprador = crear_usuario()
        ahora = _ahora_local()
        for i in range(20):
            vendedor = crear_usuario(f"vendedor{i}@gmail.com")
            anuncio = crear_anuncio(vendedor, titulo=f"Anuncio {i}")
            crear_contacto(comprador, vendedor, anuncio, ahora - timedelta(minutes=5))

        vendedor_extra = crear_usuario("extra@gmail.com")
        anuncio_extra = crear_anuncio(vendedor_extra, titulo="Extra")
        token = token_para(comprador)
        anuncio_extra_id = anuncio_extra.id

    response = client.get(f"{CONTACTO_URL}/{anuncio_extra_id}/contacto", headers=headers(token))

    assert response.status_code == 429
    body = response.get_json()
    assert body["error"] == "RATE_LIMIT_DIARIO"
    assert "disponible_en" in body["data"]


def test_contacto_anuncio_inactivo_retorna_404(client, app):
    with app.app_context():
        comprador = crear_usuario()
        vendedor = crear_usuario("vendedor@gmail.com")
        anuncio = crear_anuncio(vendedor, estado="INACTIVO")
        token = token_para(comprador)
        anuncio_id = anuncio.id

    response = client.get(f"{CONTACTO_URL}/{anuncio_id}/contacto", headers=headers(token))

    assert response.status_code == 404
    assert response.get_json()["error"] == "NOT_FOUND"

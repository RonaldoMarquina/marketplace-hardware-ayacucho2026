from io import BytesIO

import bcrypt

from app import db
from app.models.tienda import Tienda
from app.models.usuario import Usuario


REGISTER_TIENDA_URL = "/api/v1/auth/register/tienda"
PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR"
    b"\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde"
)


def datos_tienda(**overrides):
    data = {
        "nombre_comercial": "TechStore Ayacucho",
        "ruc": "20601234567",
        "direccion": "Jr. Lima 123, Ayacucho",
        "telefono": "987654321",
        "correo": "tienda@gmail.com",
        "password": "123456#P",
        "documento_identidad": (BytesIO(PNG_BYTES), "documento.png"),
    }
    data.update(overrides)
    return data


def post_tienda(client, **overrides):
    return client.post(
        REGISTER_TIENDA_URL,
        data=datos_tienda(**overrides),
        content_type="multipart/form-data",
    )


def test_registro_tienda_exitoso_retorna_201_y_crea_usuario_tienda(client, app):
    response = post_tienda(client)

    assert response.status_code == 201
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["nombre_comercial"] == "TechStore Ayacucho"
    assert body["data"]["ruc"] == "20601234567"
    assert body["data"]["correo"] == "tienda@gmail.com"
    assert body["data"]["rol"] == "TIENDA_VERIFICADA"
    assert body["data"]["estado"] == "EN_REVISION"
    assert "password" not in str(body)
    assert "password_hash" not in str(body)

    with app.app_context():
        usuario = Usuario.query.filter_by(correo="tienda@gmail.com").first()
        tienda = Tienda.query.filter_by(ruc="20601234567").first()

        assert usuario is not None
        assert tienda is not None
        assert tienda.usuario_id == usuario.id
        assert usuario.rol == "TIENDA_VERIFICADA"
        assert usuario.estado == "PENDIENTE_VERIFICACION"
        assert tienda.estado == "EN_REVISION"
        assert tienda.documento_identidad.startswith("uploads/tiendas/")
        assert "documento.png" not in tienda.documento_identidad
        assert bcrypt.checkpw(
            "123456#P".encode("utf-8"),
            usuario.password_hash.encode("utf-8"),
        )


def test_registro_tienda_ruc_duplicado_retorna_409(client):
    post_tienda(client)

    response = post_tienda(
        client,
        nombre_comercial="Hardware Center",
        correo="hardware@gmail.com",
        telefono="987654322",
    )

    assert response.status_code == 409
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "CONFLICT"
    assert "ruc" in body["message"].lower()


def test_registro_tienda_correo_duplicado_retorna_409(client):
    post_tienda(client)

    response = post_tienda(
        client,
        nombre_comercial="Hardware Center",
        ruc="20601234568",
        telefono="987654322",
    )

    assert response.status_code == 409
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "CONFLICT"
    assert "correo" in body["message"].lower()


def test_registro_tienda_ruc_invalido_retorna_422(client):
    response = post_tienda(client, ruc="123")

    assert response.status_code == 422
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "VALIDATION_ERROR"
    assert "ruc" in body["data"]


def test_registro_tienda_sin_documento_retorna_400(client):
    data = datos_tienda()
    data.pop("documento_identidad")

    response = client.post(
        REGISTER_TIENDA_URL,
        data=data,
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "MISSING_FILE"


def test_registro_tienda_archivo_invalido_retorna_415(client):
    response = post_tienda(
        client,
        documento_identidad=(BytesIO(b"contenido falso"), "documento.gif"),
    )

    assert response.status_code == 415
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "INVALID_FILE_TYPE"


def test_registro_tienda_documento_mayor_a_5mb_retorna_413(client):
    archivo_grande = BytesIO(PNG_BYTES + (b"0" * (5 * 1024 * 1024 + 1)))

    response = post_tienda(
        client,
        documento_identidad=(archivo_grande, "documento.png"),
    )

    assert response.status_code == 413
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "FILE_TOO_LARGE"


def test_registro_tienda_rollback_no_deja_registro_huerfano(client, app):
    post_tienda(client)
    post_tienda(
        client,
        nombre_comercial="Hardware Center",
        correo="hardware@gmail.com",
        telefono="987654322",
    )

    with app.app_context():
        assert db.session.query(Usuario).count() == 1
        assert db.session.query(Tienda).count() == 1

import pytest

pytestmark = pytest.mark.integration

import bcrypt

from app import db
from app.models.usuario import Usuario


REGISTER_URL = "/api/v1/auth/register"


def datos_usuario(**overrides):
    data = {
        "nombre": "Pablo Perez",
        "correo": "pablo@gmail.com",
        "password": "123456#P",
        "telefono": "987653215",
    }
    data.update(overrides)
    return data


def test_registro_usuario_exitoso_retorna_201_y_guarda_hash(client, app):
    response = client.post(REGISTER_URL, json=datos_usuario())

    assert response.status_code == 201
    body = response.get_json()
    assert body["success"] is True
    assert body["message"] == "Revisa tu correo para activar tu cuenta."
    assert body["data"]["nombre"] == "Pablo Perez"
    assert body["data"]["correo"] == "pablo@gmail.com"
    assert body["data"]["rol"] == "USER_ESTANDAR"
    assert body["data"]["estado"] == "PENDIENTE_VERIFICACION"
    assert "password" not in str(body)
    assert "password_hash" not in str(body)

    with app.app_context():
        usuario = Usuario.query.filter_by(correo="pablo@gmail.com").first()
        assert usuario is not None
        assert usuario.estado == "PENDIENTE_VERIFICACION"
        assert usuario.password_hash != "123456#P"
        assert bcrypt.checkpw(
            "123456#P".encode("utf-8"),
            usuario.password_hash.encode("utf-8"),
        )


def test_registro_usuario_campos_faltantes_retorna_400(client):
    response = client.post(
        REGISTER_URL,
        json={"correo": "pablo@gmail.com"},
    )

    assert response.status_code == 400
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "VALIDATION_ERROR"
    assert "nombre" in body["data"]
    assert "password" in body["data"]
    assert "telefono" in body["data"]


def test_registro_usuario_con_datos_invalidos_retorna_422(client):
    response = client.post(
        REGISTER_URL,
        json=datos_usuario(correo="correo-invalido", telefono="123", password="abcdefg#"),
    )

    assert response.status_code == 422
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "VALIDATION_ERROR"
    assert "correo" in body["data"]
    assert "telefono" in body["data"]
    assert "password" in body["data"]


def test_registro_usuario_correo_duplicado_retorna_409(client):
    client.post(REGISTER_URL, json=datos_usuario())

    response = client.post(
        REGISTER_URL,
        json=datos_usuario(nombre="Juan Gomez", telefono="987654321"),
    )

    assert response.status_code == 409
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "CONFLICT"
    assert "correo" in body["message"].lower()


def test_registro_usuario_telefono_duplicado_retorna_409(client):
    client.post(REGISTER_URL, json=datos_usuario())

    response = client.post(
        REGISTER_URL,
        json=datos_usuario(nombre="Juan Gomez", correo="juan@gmail.com"),
    )

    assert response.status_code == 409
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "CONFLICT"
    assert "telefono" in body["message"].lower()


def test_registro_usuario_nombre_duplicado_no_retorna_conflicto(client, app):
    client.post(REGISTER_URL, json=datos_usuario())

    response = client.post(
        REGISTER_URL,
        json=datos_usuario(correo="juan@gmail.com", telefono="987654321"),
    )

    assert response.status_code == 201

    with app.app_context():
        usuarios = Usuario.query.filter_by(nombre="Pablo Perez").all()
        assert len(usuarios) == 2


def test_registro_usuario_no_deja_registros_duplicados(client, app):
    client.post(REGISTER_URL, json=datos_usuario())
    client.post(
        REGISTER_URL,
        json=datos_usuario(nombre="Juan Gomez", telefono="987654321"),
    )

    with app.app_context():
        assert db.session.query(Usuario).count() == 1


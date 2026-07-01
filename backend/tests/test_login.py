from datetime import UTC, datetime, timedelta

import bcrypt
from flask_jwt_extended import decode_token

from app import db
from app.models.usuario import Usuario


LOGIN_URL = "/api/v1/auth/login"
PASSWORD = "123456#P"


def crear_usuario(correo="juan@gmail.com", estado="ACTIVO", rol="USER_ESTANDAR"):
    password_hash = bcrypt.hashpw(
        PASSWORD.encode("utf-8"),
        bcrypt.gensalt(rounds=10),
    ).decode("utf-8")
    usuario = Usuario(
        nombre=f"Usuario {estado} {rol}",
        correo=correo,
        password_hash=password_hash,
        telefono="987654321",
        rol=rol,
        estado=estado,
    )
    db.session.add(usuario)
    db.session.commit()
    return usuario


def post_login(client, correo="juan@gmail.com", password=PASSWORD):
    return client.post(
        LOGIN_URL,
        json={"correo": correo, "password": password},
    )


def test_login_exitoso_retorna_200_y_jwt(client, app):
    with app.app_context():
        usuario = crear_usuario()
        usuario_id = usuario.id

    response = post_login(client)

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["rol"] == "USER_ESTANDAR"
    assert body["data"]["nombre"].startswith("Usuario")
    assert body["data"]["correo"] == "juan@gmail.com"
    assert body["data"]["es_tienda_verificada"] is False
    assert body["data"]["estado"] == "ACTIVO"
    assert body["data"]["expira_en"] == "8h"
    assert "token" in body["data"]
    assert "password" not in str(body)
    assert "password_hash" not in str(body)

    with app.app_context():
        decoded = decode_token(body["data"]["token"])
        assert decoded["sub"] == str(usuario_id)
        assert decoded["correo"] == "juan@gmail.com"
        assert decoded["rol"] == "USER_ESTANDAR"


def test_login_campos_invalidos_retorna_400(client):
    response = client.post(LOGIN_URL, json={"correo": "correo-invalido"})

    assert response.status_code == 400
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "VALIDATION_ERROR"
    assert "correo" in body["data"]
    assert "password" in body["data"]


def test_login_correo_invalido_retorna_422(client):
    response = client.post(
        LOGIN_URL,
        json={"correo": "correo-invalido", "password": PASSWORD},
    )

    assert response.status_code == 422
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "VALIDATION_ERROR"
    assert "correo" in body["data"]


def test_login_correo_inexistente_retorna_401_mensaje_generico(client):
    response = post_login(client, correo="nadie@gmail.com")

    assert response.status_code == 401
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "INVALID_CREDENTIALS"
    assert body["message"] == "Credenciales invalidas."


def test_login_password_incorrecto_retorna_401_mismo_mensaje(client, app):
    with app.app_context():
        crear_usuario()

    response = post_login(client, password="Password#Incorrecto1")

    assert response.status_code == 401
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "INVALID_CREDENTIALS"
    assert body["message"] == "Credenciales invalidas."

    with app.app_context():
        usuario = Usuario.query.filter_by(correo="juan@gmail.com").first()
        assert usuario.intentos_fallidos == 1
        assert usuario.bloqueado_hasta is None


def test_login_cuenta_pendiente_retorna_403(client, app):
    with app.app_context():
        crear_usuario(estado="PENDIENTE_VERIFICACION")

    response = post_login(client)

    assert response.status_code == 403
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "ACCOUNT_PENDING"
    assert body["data"]["puede_reenviar"] is True


def test_login_cuenta_bloqueada_retorna_403(client, app):
    with app.app_context():
        crear_usuario(estado="BLOQUEADO")

    response = post_login(client)

    assert response.status_code == 403
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "ACCOUNT_BLOCKED"
    assert body["data"]["puede_reenviar"] is False


def test_login_cuenta_en_revision_retorna_403(client, app):
    with app.app_context():
        crear_usuario(estado="EN_REVISION", rol="TIENDA_VERIFICADA")

    response = post_login(client)

    assert response.status_code == 403
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "ACCOUNT_IN_REVIEW"
    assert body["data"]["puede_reenviar"] is False


def test_login_rate_limit_tras_5_intentos_fallidos(client, app):
    with app.app_context():
        crear_usuario()

    for _ in range(4):
        response = post_login(client, password="Password#Incorrecto1")
        assert response.status_code == 401

    response = post_login(client, password="Password#Incorrecto1")

    assert response.status_code == 429
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "RATE_LIMIT_LOGIN"
    assert "disponible_en" in body["data"]

    with app.app_context():
        usuario = Usuario.query.filter_by(correo="juan@gmail.com").first()
        assert usuario.estado == "BLOQUEADO_TEMP"
        assert usuario.intentos_fallidos == 5
        assert usuario.bloqueado_hasta is not None

    response = post_login(client)
    assert response.status_code == 429
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "RATE_LIMIT_LOGIN"
    assert "disponible_en" in body["data"]


def test_login_bloqueo_temporal_expirado_se_libera_y_permite_login(client, app):
    with app.app_context():
        usuario = crear_usuario(estado="BLOQUEADO_TEMP")
        usuario.intentos_fallidos = 5
        usuario.bloqueado_hasta = (
            datetime.now(UTC).replace(tzinfo=None) - timedelta(minutes=1)
        )
        db.session.commit()

    response = post_login(client)

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True

    with app.app_context():
        usuario = Usuario.query.filter_by(correo="juan@gmail.com").first()
        assert usuario.estado == "ACTIVO"
        assert usuario.intentos_fallidos == 0
        assert usuario.bloqueado_hasta is None

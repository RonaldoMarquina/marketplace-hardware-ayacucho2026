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


def test_login_cuenta_pendiente_retorna_403(client, app):
    with app.app_context():
        crear_usuario(estado="PENDIENTE_VERIFICACION")

    response = post_login(client)

    assert response.status_code == 403
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "ACCOUNT_PENDING"


def test_login_cuenta_bloqueada_retorna_403(client, app):
    with app.app_context():
        crear_usuario(estado="BLOQUEADO")

    response = post_login(client)

    assert response.status_code == 403
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "ACCOUNT_BLOCKED"


def test_login_rate_limit_tras_5_intentos_fallidos(client):
    for _ in range(5):
        response = post_login(client, correo="nadie@gmail.com")
        assert response.status_code == 401

    response = post_login(client, correo="nadie@gmail.com")

    assert response.status_code == 429
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "RATE_LIMIT"

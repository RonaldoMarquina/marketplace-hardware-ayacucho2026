import pytest

pytestmark = pytest.mark.integration

from datetime import UTC, datetime, timedelta

import bcrypt
from flask_jwt_extended import create_access_token

from app import db
from app.models.token_verificacion import TokenVerificacion
from app.models.usuario import Usuario
from app.services.auth_service import AuthService


FORGOT_URL = "/api/v1/auth/password/forgot"
RESET_URL = "/api/v1/auth/password/reset"
PASSWORD = "123456#P"
NEW_PASSWORD = "NuevaPass123!"


def crear_usuario(correo="reset@gmail.com", estado="ACTIVO", telefono="987654321"):
    password_hash = bcrypt.hashpw(
        PASSWORD.encode("utf-8"),
        bcrypt.gensalt(rounds=10),
    ).decode("utf-8")
    usuario = Usuario(
        nombre="Usuario Reset",
        correo=correo,
        password_hash=password_hash,
        telefono=telefono,
        rol="USER_ESTANDAR",
        estado=estado,
    )
    db.session.add(usuario)
    db.session.commit()
    return usuario


def crear_token_reset(usuario, token="reset-token", usado=False, expira_en=None):
    token_reset = TokenVerificacion(
        usuario_id=usuario.id,
        token=token,
        tipo="PASSWORD_RESET",
        expira_en=expira_en or (datetime.now(UTC).replace(tzinfo=None) + timedelta(hours=1)),
        usado=usado,
        created_at=datetime.now(UTC).replace(tzinfo=None),
    )
    db.session.add(token_reset)
    db.session.commit()
    return token_reset


def test_forgot_password_activo_crea_token_e_invalida_anteriores(client, app):
    with app.app_context():
        usuario = crear_usuario()
        usuario_id = usuario.id
        crear_token_reset(usuario, token="viejo-token")

    response = client.post(FORGOT_URL, json={"correo": "reset@gmail.com"})

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert len(app.extensions["mail_outbox"]) == 1
    correo = app.extensions["mail_outbox"][0]
    assert correo["kind"] == "password_reset"
    assert correo["to"] == "reset@gmail.com"
    assert "/reset-password?token=" in correo["link"]

    with app.app_context():
        tokens = TokenVerificacion.query.filter_by(
            usuario_id=usuario_id,
            tipo="PASSWORD_RESET",
        ).order_by(TokenVerificacion.id.asc()).all()
        assert len(tokens) == 2
        assert tokens[0].usado is True
        assert tokens[1].usado is False
        assert tokens[1].expira_en > tokens[1].created_at
        raw_token = correo["link"].split("token=", 1)[1]
        assert tokens[1].token != raw_token


def test_forgot_password_correo_inexistente_retorna_200_generico(client):
    response = client.post(FORGOT_URL, json={"correo": "nadie@gmail.com"})

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert "recibiras un enlace" in body["message"].lower()


def test_forgot_password_no_envia_correo_si_cuenta_no_es_activa(client, app):
    with app.app_context():
        crear_usuario(correo="blocked@gmail.com", estado="BLOQUEADO", telefono="987654399")

    response = client.post(FORGOT_URL, json={"correo": "blocked@gmail.com"})

    assert response.status_code == 200
    assert app.extensions["mail_outbox"] == []


def test_forgot_password_cuenta_no_activa_no_crea_token(client, app):
    estados = [
        "PENDIENTE_VERIFICACION",
        "EN_REVISION",
        "BLOQUEADO",
        "RECHAZADO",
    ]

    with app.app_context():
        for index, estado in enumerate(estados, start=1):
            crear_usuario(
                correo=f"estado{index}@gmail.com",
                estado=estado,
                telefono=f"98765432{index}",
            )

    for index in range(1, 5):
        response = client.post(FORGOT_URL, json={"correo": f"estado{index}@gmail.com"})
        assert response.status_code == 200
        assert response.get_json()["success"] is True

    with app.app_context():
        total_tokens = TokenVerificacion.query.filter_by(tipo="PASSWORD_RESET").count()
        assert total_tokens == 0


def test_forgot_password_rate_limit_retorna_429(client, app):
    with app.app_context():
        crear_usuario(correo="rate@gmail.com", telefono="987654322")

    for _ in range(3):
        response = client.post(FORGOT_URL, json={"correo": "rate@gmail.com"})
        assert response.status_code == 200

    response = client.post(FORGOT_URL, json={"correo": "rate@gmail.com"})

    assert response.status_code == 429
    body = response.get_json()
    assert body["error"] == "RATE_LIMIT_PASSWORD_RESET"
    assert "disponible_en" in body["data"]


def test_reset_password_campos_invalidos_y_password_debil(client):
    response = client.post(RESET_URL, json={"token": ""})
    assert response.status_code == 400
    assert response.get_json()["error"] == "VALIDATION_ERROR"

    response = client.post(
        RESET_URL,
        json={"token": "token-valido", "password": "12345678"},
    )
    assert response.status_code == 422
    assert response.get_json()["error"] == "VALIDATION_ERROR"


def test_reset_password_token_inexistente_usado_y_expirado(client, app):
    response = client.post(RESET_URL, json={"token": "no-existe", "password": NEW_PASSWORD})
    assert response.status_code == 404
    assert response.get_json()["error"] == "NOT_FOUND"

    with app.app_context():
        usuario = crear_usuario(correo="used@gmail.com", telefono="987654323")
        crear_token_reset(usuario, token="token-usado", usado=True)
        crear_token_reset(
            usuario,
            token="token-expirado",
            expira_en=datetime.now(UTC).replace(tzinfo=None) - timedelta(minutes=1),
        )

    response = client.post(RESET_URL, json={"token": "token-usado", "password": NEW_PASSWORD})
    assert response.status_code == 409
    assert response.get_json()["error"] == "TOKEN_USED"

    response = client.post(RESET_URL, json={"token": "token-expirado", "password": NEW_PASSWORD})
    assert response.status_code == 410
    assert response.get_json()["error"] == "TOKEN_EXPIRED"


def test_reset_password_falla_si_estado_no_permitido(client, app):
    with app.app_context():
        usuario = crear_usuario(correo="blocked@gmail.com", estado="BLOQUEADO", telefono="987654324")
        crear_token_reset(usuario, token="token-bloqueado")

    response = client.post(
        RESET_URL,
        json={"token": "token-bloqueado", "password": NEW_PASSWORD},
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == "FORBIDDEN"


def test_reset_password_falla_si_nueva_password_es_igual(client, app):
    with app.app_context():
        usuario = crear_usuario(correo="same@gmail.com", telefono="987654325")
        crear_token_reset(usuario, token="token-same")

    response = client.post(
        RESET_URL,
        json={"token": "token-same", "password": PASSWORD},
    )

    assert response.status_code == 409
    assert response.get_json()["error"] == "CONFLICT"


def test_reset_password_exitoso_actualiza_hash_e_invalida_tokens(client, app):
    with app.app_context():
        usuario = crear_usuario(correo="ok@gmail.com", telefono="987654326")
        usuario.intentos_fallidos = 5
        usuario.bloqueado_hasta = datetime.now(UTC).replace(tzinfo=None) + timedelta(minutes=10)
        usuario.estado = "BLOQUEADO_TEMP"
        db.session.commit()
        crear_token_reset(usuario, token="token-ok")
        crear_token_reset(usuario, token="token-extra")
        usuario_id = usuario.id

    response = client.post(
        RESET_URL,
        json={"token": "token-ok", "password": NEW_PASSWORD},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["usuario_id"] == usuario_id

    with app.app_context():
        usuario = db.session.get(Usuario, usuario_id)
        assert usuario.estado == "ACTIVO"
        assert usuario.intentos_fallidos == 0
        assert usuario.bloqueado_hasta is None
        assert bcrypt.checkpw(
            NEW_PASSWORD.encode("utf-8"),
            usuario.password_hash.encode("utf-8"),
        )
        tokens = TokenVerificacion.query.filter_by(
            usuario_id=usuario_id,
            tipo="PASSWORD_RESET",
        ).all()
        assert all(token.usado is True for token in tokens)


def test_reset_password_revoca_jwt_emitido_antes_del_cambio(client, app):
    with app.app_context():
        usuario = crear_usuario(correo="jwt@gmail.com", telefono="987654327")
        usuario_id = usuario.id
        access_token = create_access_token(
            identity=str(usuario.id),
            additional_claims={
                "correo": usuario.correo,
                "rol": usuario.rol,
                "pwd_sig": AuthService.password_claim_signature(usuario.password_hash),
            },
            expires_delta=timedelta(hours=8),
        )
        crear_token_reset(usuario, token="token-jwt")

    reset_response = client.post(
        RESET_URL,
        json={"token": "token-jwt", "password": NEW_PASSWORD},
    )

    assert reset_response.status_code == 200

    panel_response = client.get(
        "/api/v1/usuarios/me/panel",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert panel_response.status_code == 401
    assert (
        panel_response.get_json()["message"]
        == "Token JWT revocado por cambio de credenciales."
    )

    with app.app_context():
        usuario = db.session.get(Usuario, usuario_id)
        assert bcrypt.checkpw(
            NEW_PASSWORD.encode("utf-8"),
            usuario.password_hash.encode("utf-8"),
        )


def test_reset_password_confirm_rate_limit_retorna_429(client):
    for _ in range(10):
        response = client.post(
            RESET_URL,
            json={"token": "no-existe", "password": NEW_PASSWORD},
        )
        assert response.status_code == 404
        assert response.get_json()["error"] == "NOT_FOUND"

    response = client.post(
        RESET_URL,
        json={"token": "no-existe", "password": NEW_PASSWORD},
    )

    assert response.status_code == 429
    body = response.get_json()
    assert body["error"] == "RATE_LIMIT_PASSWORD_RESET_CONFIRM"
    assert "disponible_en" in body["data"]


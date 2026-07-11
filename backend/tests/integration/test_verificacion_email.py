import pytest

pytestmark = pytest.mark.integration

from datetime import UTC, datetime, timedelta
from io import BytesIO

from app import db
from app.models.tienda import Tienda
from app.models.token_verificacion import TokenVerificacion
from app.models.usuario import Usuario


REGISTER_URL = "/api/v1/auth/register"
REGISTER_TIENDA_URL = "/api/v1/auth/register/tienda"
VERIFY_URL = "/api/v1/auth/verify-email"
RESEND_URL = "/api/v1/auth/verify-email/resend"
PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR"
    b"\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde"
)


def datos_usuario(**overrides):
    data = {
        "nombre": "Luis Flores",
        "correo": "luis@gmail.com",
        "password": "123456#P",
        "telefono": "987654320",
    }
    data.update(overrides)
    return data


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


def registrar_usuario(client, **overrides):
    return client.post(REGISTER_URL, json=datos_usuario(**overrides))


def registrar_tienda(client, **overrides):
    return client.post(
        REGISTER_TIENDA_URL,
        data=datos_tienda(**overrides),
        content_type="multipart/form-data",
    )


def obtener_token(correo):
    usuario = Usuario.query.filter_by(correo=correo).first()
    return TokenVerificacion.query.filter_by(usuario_id=usuario.id).first()


def test_registro_crea_token_verificacion_activo(client, app):
    response = registrar_usuario(client)

    assert response.status_code == 201
    assert len(app.extensions["mail_outbox"]) == 1
    correo = app.extensions["mail_outbox"][0]
    assert correo["kind"] == "email_verification"
    assert correo["to"] == "luis@gmail.com"
    assert "/verificar?token=" in correo["link"]

    with app.app_context():
        token = obtener_token("luis@gmail.com")
        assert token is not None
        assert len(token.token) == 64
        assert token.tipo == "EMAIL_VERIFICATION"
        assert token.usado is False
        assert token.expira_en > datetime.now(UTC).replace(tzinfo=None)


def test_verificar_correo_token_valido_activa_usuario(client, app):
    registrar_usuario(client)

    with app.app_context():
        token = obtener_token("luis@gmail.com").token

    response = client.get(f"{VERIFY_URL}?token={token}")

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["estado"] == "ACTIVO"
    assert body["message"] == "Correo verificado. Tu cuenta esta activa, ya puedes iniciar sesion."

    with app.app_context():
        usuario = Usuario.query.filter_by(correo="luis@gmail.com").first()
        token_verificacion = TokenVerificacion.query.filter_by(token=token).first()
        assert usuario.estado == "ACTIVO"
        assert token_verificacion.usado is True


def test_verificar_correo_tienda_mantiene_en_revision(client, app):
    registrar_tienda(client)

    with app.app_context():
        token = obtener_token("tienda@gmail.com").token

    response = client.get(f"{VERIFY_URL}?token={token}")

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["estado"] == "EN_REVISION"
    assert body["message"] == (
        "Correo verificado. Tu solicitud de tienda esta siendo revisada por un administrador."
    )

    with app.app_context():
        usuario = Usuario.query.filter_by(correo="tienda@gmail.com").first()
        tienda = Tienda.query.filter_by(ruc="20601234567").first()
        assert usuario.estado == "EN_REVISION"
        assert tienda.estado == "EN_REVISION"


def test_verificar_correo_token_inexistente_retorna_404(client):
    response = client.get(f"{VERIFY_URL}?token=no-existe")

    assert response.status_code == 404
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "NOT_FOUND"


def test_verificar_correo_token_usado_retorna_409(client, app):
    registrar_usuario(client)

    with app.app_context():
        token = obtener_token("luis@gmail.com").token

    client.get(f"{VERIFY_URL}?token={token}")
    response = client.get(f"{VERIFY_URL}?token={token}")

    assert response.status_code == 409
    body = response.get_json()
    assert body["error"] == "TOKEN_USED"


def test_verificar_correo_token_expirado_retorna_410(client, app):
    registrar_usuario(client)

    with app.app_context():
        token = obtener_token("luis@gmail.com")
        token.expira_en = datetime.now(UTC).replace(tzinfo=None) - timedelta(minutes=1)
        db.session.commit()
        token_value = token.token

    response = client.get(f"{VERIFY_URL}?token={token_value}")

    assert response.status_code == 410
    body = response.get_json()
    assert body["error"] == "TOKEN_EXPIRED"


def test_reenviar_verificacion_invalida_token_anterior_y_crea_nuevo(client, app):
    registrar_usuario(client)
    app.extensions["mail_outbox"].clear()

    with app.app_context():
        token_anterior = obtener_token("luis@gmail.com").token

    response = client.post(RESEND_URL, json={"correo": "luis@gmail.com"})

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["message"] == "Correo de verificacion reenviado. Revisa tu bandeja de entrada."
    assert "expira_en" in body["data"]
    assert len(app.extensions["mail_outbox"]) == 1
    assert app.extensions["mail_outbox"][0]["kind"] == "email_verification"

    with app.app_context():
        tokens = TokenVerificacion.query.join(Usuario).filter(
            Usuario.correo == "luis@gmail.com"
        ).order_by(TokenVerificacion.id.asc()).all()
        assert len(tokens) == 2
        assert tokens[0].token == token_anterior
        assert tokens[0].usado is True
        assert tokens[1].usado is False


def test_reenviar_verificacion_tienda_en_revision_retorna_200(client):
    registrar_tienda(client)

    response = client.post(RESEND_URL, json={"correo": "tienda@gmail.com"})

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert "expira_en" in body["data"]


def test_reenviar_verificacion_cuenta_activa_retorna_409(client, app):
    registrar_usuario(client)

    with app.app_context():
        token = obtener_token("luis@gmail.com").token

    client.get(f"{VERIFY_URL}?token={token}")
    response = client.post(RESEND_URL, json={"correo": "luis@gmail.com"})

    assert response.status_code == 409
    body = response.get_json()
    assert body["error"] == "CONFLICT"


def test_reenviar_verificacion_rate_limit_retorna_429(client):
    registrar_usuario(client)

    for _ in range(3):
        response = client.post(RESEND_URL, json={"correo": "luis@gmail.com"})
        assert response.status_code == 200

    response = client.post(RESEND_URL, json={"correo": "luis@gmail.com"})

    assert response.status_code == 429
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "RATE_LIMIT_REENVIO"
    assert "disponible_en" in body["data"]


def test_reenviar_verificacion_rate_limit_sin_token_inicial_en_ventana_retorna_429(client, app):
    registrar_usuario(client)

    with app.app_context():
        usuario = Usuario.query.filter_by(correo="luis@gmail.com").first()
        primer_token = TokenVerificacion.query.filter_by(usuario_id=usuario.id).first()
        primer_token.created_at = datetime.now(UTC).replace(tzinfo=None) - timedelta(minutes=16)
        db.session.commit()

    for _ in range(3):
        response = client.post(RESEND_URL, json={"correo": "luis@gmail.com"})
        assert response.status_code == 200

    response = client.post(RESEND_URL, json={"correo": "luis@gmail.com"})

    assert response.status_code == 429
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "RATE_LIMIT_REENVIO"


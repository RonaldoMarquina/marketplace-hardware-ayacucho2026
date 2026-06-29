from datetime import UTC, datetime, timedelta

from app import db
from app.models.token_verificacion import TokenVerificacion
from app.models.usuario import Usuario


REGISTER_URL = "/api/v1/auth/register"
VERIFY_URL = "/api/v1/auth/verify-email"
RESEND_URL = "/api/v1/auth/verify-email/resend"


def datos_usuario(**overrides):
    data = {
        "nombre": "Luis Flores",
        "correo": "luis@gmail.com",
        "password": "123456#P",
        "telefono": "987654320",
    }
    data.update(overrides)
    return data


def registrar_usuario(client, **overrides):
    return client.post(REGISTER_URL, json=datos_usuario(**overrides))


def obtener_token(correo):
    usuario = Usuario.query.filter_by(correo=correo).first()
    return TokenVerificacion.query.filter_by(usuario_id=usuario.id).first()


def test_registro_crea_token_verificacion_activo(client, app):
    response = registrar_usuario(client)

    assert response.status_code == 201
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
    assert body["data"]["correo"] == "luis@gmail.com"

    with app.app_context():
        usuario = Usuario.query.filter_by(correo="luis@gmail.com").first()
        token_verificacion = TokenVerificacion.query.filter_by(token=token).first()
        assert usuario.estado == "ACTIVO"
        assert token_verificacion.usado is True


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

    with app.app_context():
        token_anterior = obtener_token("luis@gmail.com").token

    response = client.post(RESEND_URL, json={"correo": "luis@gmail.com"})

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True

    with app.app_context():
        tokens = TokenVerificacion.query.join(Usuario).filter(
            Usuario.correo == "luis@gmail.com"
        ).order_by(TokenVerificacion.id.asc()).all()
        assert len(tokens) == 2
        assert tokens[0].token == token_anterior
        assert tokens[0].usado is True
        assert tokens[1].usado is False


def test_reenviar_verificacion_cuenta_activa_retorna_409(client, app):
    registrar_usuario(client)

    with app.app_context():
        token = obtener_token("luis@gmail.com").token

    client.get(f"{VERIFY_URL}?token={token}")
    response = client.post(RESEND_URL, json={"correo": "luis@gmail.com"})

    assert response.status_code == 409
    body = response.get_json()
    assert body["error"] == "CONFLICT"

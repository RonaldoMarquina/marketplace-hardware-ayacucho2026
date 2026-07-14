import pytest

from app import create_app
from app.services.email_service import EmailService


pytestmark = pytest.mark.unit


def test_create_app_falla_si_public_production_no_tiene_smtp(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("FLASK_APP_SECRET", "x" * 48)
    monkeypatch.setenv("JWT_SECRET_KEY", "y" * 48)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("EMAIL_PUBLIC_PRODUCTION", "true")
    monkeypatch.setenv("EMAIL_DELIVERY_MODE", "log")

    with pytest.raises(RuntimeError, match="produccion publica requiere EMAIL_DELIVERY_MODE=smtp, resend_api o brevo_api"):
        create_app()


def test_create_app_acepta_public_production_con_smtp_configurado(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("FLASK_APP_SECRET", "x" * 48)
    monkeypatch.setenv("JWT_SECRET_KEY", "y" * 48)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("EMAIL_PUBLIC_PRODUCTION", "true")
    monkeypatch.setenv("EMAIL_DELIVERY_MODE", "smtp")
    monkeypatch.setenv("EMAIL_FROM", "no-reply@example.com")
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_USERNAME", "user")
    monkeypatch.setenv("SMTP_PASSWORD", "pass")

    app = create_app()

    assert app.config["EMAIL_DELIVERY_MODE"] == "smtp"
    assert app.config["EMAIL_PUBLIC_PRODUCTION"] is True


def test_create_app_acepta_public_production_con_resend_api(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("FLASK_APP_SECRET", "x" * 48)
    monkeypatch.setenv("JWT_SECRET_KEY", "y" * 48)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("EMAIL_PUBLIC_PRODUCTION", "true")
    monkeypatch.setenv("EMAIL_DELIVERY_MODE", "resend_api")
    monkeypatch.setenv("EMAIL_FROM", "soporte@mail.hardwareayacucho.shop")
    monkeypatch.setenv("RESEND_API_KEY", "re_test_123")

    app = create_app()

    assert app.config["EMAIL_DELIVERY_MODE"] == "resend_api"
    assert app.config["EMAIL_PUBLIC_PRODUCTION"] is True


def test_email_service_envia_por_resend_api(app, monkeypatch):
    captured = {}

    class _FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def _fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        captured["headers"] = dict(req.header_items())
        captured["body"] = req.data.decode("utf-8")
        captured["timeout"] = timeout
        return _FakeResponse()

    app.config.update(
        {
            "EMAIL_DELIVERY_MODE": "resend_api",
            "EMAIL_FROM": "soporte@mail.hardwareayacucho.shop",
            "RESEND_API_KEY": "re_test_123",
            "RESEND_API_BASE_URL": "https://api.resend.com/emails",
        }
    )
    monkeypatch.setattr("app.services.email_service.request.urlopen", _fake_urlopen)

    EmailService.send_verification_email(app, "alumno@example.com", "token-demo")

    assert captured["url"] == "https://api.resend.com/emails"
    assert captured["timeout"] == 15
    assert "Bearer re_test_123" in captured["headers"]["Authorization"]
    assert '"to": ["alumno@example.com"]' in captured["body"]


def test_create_app_acepta_public_production_con_brevo_api(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("FLASK_APP_SECRET", "x" * 48)
    monkeypatch.setenv("JWT_SECRET_KEY", "y" * 48)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("EMAIL_PUBLIC_PRODUCTION", "true")
    monkeypatch.setenv("EMAIL_DELIVERY_MODE", "brevo_api")
    monkeypatch.setenv("EMAIL_FROM", "Soporte HardwareAyacucho <soporte.sistemasha@gmail.com>")
    monkeypatch.setenv("BREVO_API_KEY", "xkeysib-demo")

    app = create_app()

    assert app.config["EMAIL_DELIVERY_MODE"] == "brevo_api"
    assert app.config["EMAIL_PUBLIC_PRODUCTION"] is True


def test_email_service_envia_por_brevo_api(app, monkeypatch):
    captured = {}

    class _FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def _fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        captured["headers"] = dict(req.header_items())
        captured["body"] = req.data.decode("utf-8")
        captured["timeout"] = timeout
        return _FakeResponse()

    app.config.update(
        {
            "EMAIL_DELIVERY_MODE": "brevo_api",
            "EMAIL_FROM": "Soporte HardwareAyacucho <soporte.sistemasha@gmail.com>",
            "BREVO_API_KEY": "xkeysib-demo",
            "BREVO_API_BASE_URL": "https://api.brevo.com/v3/smtp/email",
        }
    )
    monkeypatch.setattr("app.services.email_service.request.urlopen", _fake_urlopen)

    EmailService.send_verification_email(app, "alumno@example.com", "token-demo")

    normalized_headers = {key.lower(): value for key, value in captured["headers"].items()}

    assert captured["url"] == "https://api.brevo.com/v3/smtp/email"
    assert captured["timeout"] == 15
    assert normalized_headers["api-key"] == "xkeysib-demo"
    assert '"email": "soporte.sistemasha@gmail.com"' in captured["body"]
    assert '"email": "alumno@example.com"' in captured["body"]


def test_create_app_falla_si_cloudinary_queda_incompleto(monkeypatch):
    monkeypatch.setenv("FLASK_APP_SECRET", "x" * 48)
    monkeypatch.setenv("JWT_SECRET_KEY", "y" * 48)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("CLOUDINARY_CLOUD_NAME", "demo-cloud")
    monkeypatch.setenv("CLOUDINARY_API_KEY", "")
    monkeypatch.setenv("CLOUDINARY_API_SECRET", "")

    with pytest.raises(RuntimeError, match="La configuracion de Cloudinary es incompleta"):
        create_app()


def test_create_app_acepta_cloudinary_completo(monkeypatch):
    monkeypatch.setenv("FLASK_APP_SECRET", "x" * 48)
    monkeypatch.setenv("JWT_SECRET_KEY", "y" * 48)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("CLOUDINARY_CLOUD_NAME", "demo-cloud")
    monkeypatch.setenv("CLOUDINARY_API_KEY", "123456789")
    monkeypatch.setenv("CLOUDINARY_API_SECRET", "secret-value")
    monkeypatch.setenv("CLOUDINARY_FOLDER", "hardware-ayacucho/anuncios")

    app = create_app()

    assert app.config["CLOUDINARY_ENABLED"] is True
    assert app.config["CLOUDINARY_CLOUD_NAME"] == "demo-cloud"
    assert app.config["CLOUDINARY_API_KEY"] == "123456789"
    assert app.config["CLOUDINARY_FOLDER"] == "hardware-ayacucho/anuncios"

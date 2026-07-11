import pytest

from app import create_app


pytestmark = pytest.mark.unit


def test_create_app_falla_si_public_production_no_tiene_smtp(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("FLASK_APP_SECRET", "x" * 48)
    monkeypatch.setenv("JWT_SECRET_KEY", "y" * 48)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("EMAIL_PUBLIC_PRODUCTION", "true")
    monkeypatch.setenv("EMAIL_DELIVERY_MODE", "log")

    with pytest.raises(RuntimeError, match="produccion publica requiere EMAIL_DELIVERY_MODE=smtp"):
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

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.services.auth_service import AuthService


@pytest.fixture(scope="function")
def app(tmp_path):
    AuthService._login_attempts.clear()
    AuthService._password_reset_attempts.clear()
    AuthService._password_reset_confirm_attempts.clear()
    flask_app = create_app(
        {
            "TESTING": True,
            "EMAIL_DELIVERY_MODE": "testing",
            "EMAIL_PUBLIC_PRODUCTION": False,
            "EMAIL_FROM": "test@hardwareayacucho.local",
            "EMAIL_SUBJECT_PREFIX": "[Test]",
            "JWT_SECRET_KEY": "test-jwt-secret-for-hs256-32-bytes-minimum",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "UPLOAD_FOLDER": str(tmp_path / "uploads"),
            "CLOUDINARY_CLOUD_NAME": None,
            "CLOUDINARY_API_KEY": None,
            "CLOUDINARY_API_SECRET": None,
            "CLOUDINARY_FOLDER": "hardware-ayacucho/test",
        }
    )

    with flask_app.app_context():
        flask_app.extensions["mail_outbox"] = []
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        AuthService._login_attempts.clear()
        AuthService._password_reset_attempts.clear()
        AuthService._password_reset_confirm_attempts.clear()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()

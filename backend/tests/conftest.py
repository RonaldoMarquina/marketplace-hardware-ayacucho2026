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
    flask_app = create_app(
        {
            "TESTING": True,
            "JWT_SECRET_KEY": "test-jwt-secret-for-hs256-32-bytes-minimum",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "UPLOAD_FOLDER": str(tmp_path / "uploads"),
        }
    )

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()
        AuthService._login_attempts.clear()
        AuthService._password_reset_attempts.clear()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()

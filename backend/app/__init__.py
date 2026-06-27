import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
migrate = Migrate()


def create_app(test_config=None):
    # Carga el .env del backend de forma estable, sin depender de la carpeta
    # desde donde ejecutes Flask, PyTest o scripts manuales.
    backend_dir = Path(__file__).resolve().parent.parent
    load_dotenv(backend_dir / ".env")

    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["JWT_SECRET_KEY"] = os.getenv(
        "JWT_SECRET_KEY",
        os.getenv("JWT_SECRET"),
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)

    from app.routes.auth import auth_bp

    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")

    return app

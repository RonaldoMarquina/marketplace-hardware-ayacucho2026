import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify
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
    app.config["UPLOAD_FOLDER"] = os.getenv(
        "UPLOAD_FOLDER",
        str(backend_dir / "uploads"),
    )
    app.config["MAX_DOCUMENT_SIZE"] = 5 * 1024 * 1024

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)

    _registrar_manejadores_jwt(jwt)

    from app.routes.admin import admin_bp
    from app.routes.anuncios import anuncios_bp
    from app.routes.auth import auth_bp
    from app.routes.transacciones import transacciones_bp
    from app.routes.usuarios import usuarios_bp

    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(anuncios_bp, url_prefix="/api/v1/anuncios")
    app.register_blueprint(admin_bp, url_prefix="/api/v1/admin")
    app.register_blueprint(transacciones_bp, url_prefix="/api/v1/transacciones")
    app.register_blueprint(usuarios_bp, url_prefix="/api/v1/usuarios")

    return app


def _registrar_manejadores_jwt(jwt_manager):
    @jwt_manager.unauthorized_loader
    def jwt_faltante(reason):
        return jsonify({
            "success": False,
            "data": {},
            "error": "UNAUTHORIZED",
            "message": "Token JWT requerido.",
        }), 401

    @jwt_manager.invalid_token_loader
    def jwt_invalido(reason):
        return jsonify({
            "success": False,
            "data": {},
            "error": "UNAUTHORIZED",
            "message": "Token JWT invalido.",
        }), 401

    @jwt_manager.expired_token_loader
    def jwt_expirado(jwt_header, jwt_payload):
        return jsonify({
            "success": False,
            "data": {},
            "error": "UNAUTHORIZED",
            "message": "Token JWT expirado.",
        }), 401

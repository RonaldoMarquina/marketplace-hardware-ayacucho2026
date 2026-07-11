import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect


db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
migrate = Migrate()
csrf = CSRFProtect()


def _env_flag(env_name, default=False):
    value = os.getenv(env_name)
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


def _resolve_app_secret(*env_names, allow_ephemeral=False):
    for env_name in env_names:
        secret_value = os.getenv(env_name)
        if secret_value:
            return secret_value

    if allow_ephemeral:
        return secrets.token_urlsafe(48)

    joined_names = ", ".join(env_names)
    raise RuntimeError(
        f"Debes definir al menos una de estas variables para iniciar la aplicacion: {joined_names}."
    )


def create_app(test_config=None):
    # Carga el .env del backend de forma estable, sin depender de la carpeta
    # desde donde ejecutes Flask, PyTest o scripts manuales.
    backend_dir = Path(__file__).resolve().parent.parent
    load_dotenv(backend_dir / ".env")
    testing_mode = bool(test_config and test_config.get("TESTING"))
    production_mode = os.getenv("FLASK_ENV", "").lower() == "production"

    app = Flask(__name__)
    # La app usa JWT en el header Authorization y no autenticacion basada en
    # cookies del navegador; por eso endurecemos cookies de sesion y evitamos
    # depender de formularios server-rendered con estado compartido.
    app.secret_key = _resolve_app_secret(
        "FLASK_APP_SECRET",
        "JWT_SECRET",
        allow_ephemeral=testing_mode,
    )
    app.config["JWT_SECRET_KEY"] = (
        os.getenv("JWT_SECRET_KEY")
        or os.getenv("JWT_SECRET")
        or _resolve_app_secret(
            "JWT_APP_SECRET",
            "FLASK_APP_SECRET",
            allow_ephemeral=testing_mode,
        )
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["BCRYPT_ROUNDS"] = int(os.getenv("BCRYPT_ROUNDS", "12"))
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = production_mode
    app.config["UPLOAD_FOLDER"] = os.getenv(
        "UPLOAD_FOLDER",
        str(backend_dir / "uploads"),
    )
    app.config["MAX_DOCUMENT_SIZE"] = 5 * 1024 * 1024
    app.config["FRONTEND_URL"] = os.getenv("FRONTEND_URL", "http://localhost:5173")
    app.config["EMAIL_DELIVERY_MODE"] = os.getenv(
        "EMAIL_DELIVERY_MODE",
        "testing" if testing_mode else "log",
    ).strip().lower()
    app.config["EMAIL_PUBLIC_PRODUCTION"] = _env_flag("EMAIL_PUBLIC_PRODUCTION", False)
    app.config["EMAIL_FROM"] = os.getenv("EMAIL_FROM", "no-reply@hardwareayacucho.local")
    app.config["EMAIL_SUBJECT_PREFIX"] = os.getenv(
        "EMAIL_SUBJECT_PREFIX",
        "[HardwareAyacucho]",
    )
    app.config["SMTP_HOST"] = os.getenv("SMTP_HOST")
    app.config["SMTP_PORT"] = int(os.getenv("SMTP_PORT", "587"))
    app.config["SMTP_USERNAME"] = os.getenv("SMTP_USERNAME")
    app.config["SMTP_PASSWORD"] = os.getenv("SMTP_PASSWORD")
    app.config["SMTP_USE_TLS"] = _env_flag("SMTP_USE_TLS", True)
    app.config["SMTP_USE_SSL"] = _env_flag("SMTP_USE_SSL", False)
    app.config["SMTP_TIMEOUT_SECONDS"] = int(os.getenv("SMTP_TIMEOUT_SECONDS", "15"))

    if test_config:
        app.config.update(test_config)

    app.extensions.setdefault("mail_outbox", [])
    _validate_email_config(app)

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

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
    # Las blueprints del proyecto exponen una API JSON autenticada con JWT en
    # el header Authorization, no formularios basados en cookie/sesion.
    csrf.exempt(auth_bp)
    csrf.exempt(anuncios_bp)
    csrf.exempt(admin_bp)
    csrf.exempt(transacciones_bp)
    csrf.exempt(usuarios_bp)

    @app.route("/uploads/<path:filename>")
    def servir_upload(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    return app


def _validate_email_config(app):
    email_mode = app.config.get("EMAIL_DELIVERY_MODE", "log")
    supported_modes = {"testing", "log", "smtp"}
    if email_mode not in supported_modes:
        raise RuntimeError(
            "EMAIL_DELIVERY_MODE debe ser uno de: testing, log, smtp."
        )

    if email_mode != "smtp" and app.config.get("EMAIL_PUBLIC_PRODUCTION"):
        raise RuntimeError(
            "La produccion publica requiere EMAIL_DELIVERY_MODE=smtp con configuracion real de correo."
        )

    if email_mode != "smtp":
        return

    missing = [
        key
        for key in ("SMTP_HOST", "SMTP_USERNAME", "SMTP_PASSWORD", "EMAIL_FROM")
        if not app.config.get(key)
    ]
    if missing:
        raise RuntimeError(
            "Falta configuracion SMTP obligatoria: " + ", ".join(missing) + "."
        )

    if app.config.get("SMTP_USE_TLS") and app.config.get("SMTP_USE_SSL"):
        raise RuntimeError("SMTP_USE_TLS y SMTP_USE_SSL no pueden estar activos a la vez.")


def _registrar_manejadores_jwt(jwt_manager):
    @jwt_manager.unauthorized_loader
    def jwt_faltante(_reason):
        return jsonify({
            "success": False,
            "data": {},
            "error": "UNAUTHORIZED",
            "message": "Token JWT requerido.",
        }), 401

    @jwt_manager.invalid_token_loader
    def jwt_invalido(_reason):
        return jsonify({
            "success": False,
            "data": {},
            "error": "UNAUTHORIZED",
            "message": "Token JWT invalido.",
        }), 401

    @jwt_manager.expired_token_loader
    def jwt_expirado(_jwt_header, _jwt_payload):
        return jsonify({
            "success": False,
            "data": {},
            "error": "UNAUTHORIZED",
            "message": "Token JWT expirado.",
        }), 401

    @jwt_manager.token_in_blocklist_loader
    def jwt_revocado(_jwt_header, jwt_payload):
        password_signature = jwt_payload.get("pwd_sig")
        if not password_signature:
            return False

        from app.models.usuario import Usuario
        from app.services.auth_service import AuthService

        try:
            usuario_id = int(jwt_payload["sub"])
        except (KeyError, TypeError, ValueError):
            return True

        usuario = db.session.get(Usuario, usuario_id)
        if not usuario:
            return True

        return (
            AuthService.password_claim_signature(usuario.password_hash)
            != password_signature
        )

    @jwt_manager.revoked_token_loader
    def jwt_token_revocado(_jwt_header, _jwt_payload):
        return jsonify({
            "success": False,
            "data": {},
            "error": "UNAUTHORIZED",
            "message": "Token JWT revocado por cambio de credenciales.",
        }), 401

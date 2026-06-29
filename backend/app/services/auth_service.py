from pathlib import Path
from datetime import UTC, datetime, timedelta
import secrets
import threading

import bcrypt
from flask import current_app
from flask_jwt_extended import create_access_token
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app import db
from app.models.tienda import Tienda
from app.models.token_verificacion import TokenVerificacion
from app.models.usuario import Usuario
from app.repositories.auth_repository import AuthRepository
from app.utils.file_validation import FileValidationError, validate_store_document


class AuthService:
    # Rate limit simple para MVP: guarda intentos fallidos por IP en memoria.
    # En produccion con varios procesos convendria mover esto a Redis.
    _login_attempts = {}
    _max_login_attempts = 5
    _login_block_minutes = 15

    @staticmethod
    def registrar_usuario(data):
        usuario_existente = Usuario.query.filter(
            or_(
                Usuario.correo == data["correo"],
                Usuario.telefono == data["telefono"],
                Usuario.nombre == data["nombre"],
            )
        ).first()

        if usuario_existente:
            if usuario_existente.correo == data["correo"]:
                mensaje = "El correo ya se encuentra registrado."
            elif usuario_existente.telefono == data["telefono"]:
                mensaje = "El telefono ya se encuentra registrado."
            else:
                mensaje = "El nombre ya se encuentra registrado."

            return {
                "success": False,
                "data": {},
                "error": "CONFLICT",
                "message": mensaje,
            }

        password_hash = bcrypt.hashpw(
            data["password"].encode("utf-8"),
            bcrypt.gensalt(rounds=10),
        ).decode("utf-8")

        usuario = Usuario(
            nombre=data["nombre"],
            correo=data["correo"],
            password_hash=password_hash,
            telefono=data["telefono"],
            rol="USER_ESTANDAR",
            estado="PENDIENTE_VERIFICACION",
        )

        try:
            db.session.add(usuario)
            db.session.flush()
            token_verificacion = AuthService._crear_token_verificacion(usuario)
            db.session.add(token_verificacion)
            db.session.commit()
            AuthService._enviar_correo_verificacion_async(usuario, token_verificacion.token)
            return {
                "success": True,
                "data": usuario.to_public_dict(),
                "error": None,
                "message": "Usuario registrado correctamente.",
            }
        except IntegrityError:
            db.session.rollback()
            return {
                "success": False,
                "data": {},
                "error": "CONFLICT",
                "message": "El correo, telefono o nombre ya se encuentra registrado.",
            }
        except SQLAlchemyError:
            db.session.rollback()
            return {
                "success": False,
                "data": {},
                "error": "DATABASE_ERROR",
                "message": "No se pudo registrar el usuario.",
            }

    @staticmethod
    def registrar_tienda(data, documento_identidad):
        conflicto = AuthService._validar_conflictos_tienda(data)
        if conflicto:
            return conflicto

        upload_folder = current_app.config.get("UPLOAD_FOLDER")
        if not upload_folder:
            upload_folder = Path(current_app.root_path).parent / "uploads"

        max_size_bytes = current_app.config.get("MAX_DOCUMENT_SIZE", 5 * 1024 * 1024)
        try:
            ruta_relativa, ruta_absoluta = validate_store_document(
                documento_identidad,
                upload_folder,
                max_size_bytes,
            )
        except FileValidationError as error:
            return {
                "success": False,
                "data": {},
                "error": error.error_code,
                "message": error.message,
            }

        password_hash = bcrypt.hashpw(
            data["password"].encode("utf-8"),
            bcrypt.gensalt(rounds=10),
        ).decode("utf-8")

        usuario = Usuario(
            nombre=data["nombre_comercial"],
            correo=data["correo"],
            password_hash=password_hash,
            telefono=data["telefono"],
            rol="TIENDA_VERIFICADA",
            estado="PENDIENTE_VERIFICACION",
        )

        tienda = Tienda(
            usuario=usuario,
            nombre_comercial=data["nombre_comercial"],
            ruc=data["ruc"],
            direccion=data["direccion"],
            documento_identidad=ruta_relativa,
            estado="EN_REVISION",
        )

        try:
            AuthRepository.agregar_usuario(usuario)
            AuthRepository.agregar_tienda(tienda)
            AuthRepository.flush()
            token_verificacion = AuthService._crear_token_verificacion(usuario)
            AuthRepository.agregar_token_verificacion(token_verificacion)
            AuthRepository.commit()
            AuthService._enviar_correo_verificacion_async(usuario, token_verificacion.token)
            return {
                "success": True,
                "data": tienda.to_public_dict(),
                "error": None,
                "message": "Tienda registrada correctamente.",
            }
        except IntegrityError:
            AuthRepository.rollback()
            AuthService._eliminar_archivo_si_existe(ruta_absoluta)
            return {
                "success": False,
                "data": {},
                "error": "CONFLICT",
                "message": "El correo, telefono, nombre comercial o RUC ya se encuentra registrado.",
            }
        except SQLAlchemyError:
            AuthRepository.rollback()
            AuthService._eliminar_archivo_si_existe(ruta_absoluta)
            return {
                "success": False,
                "data": {},
                "error": "DATABASE_ERROR",
                "message": "No se pudo registrar la tienda.",
            }

    @staticmethod
    def login(data, ip_address=None):
        # HU-04 exige que correo inexistente y password incorrecto respondan
        # igual. Asi evitamos enumeracion de usuarios.
        ip_key = ip_address or "unknown"
        if AuthService._ip_bloqueada(ip_key):
            return {
                "success": False,
                "data": {},
                "error": "RATE_LIMIT",
                "message": "Demasiados intentos fallidos. Intenta nuevamente en 15 minutos.",
            }

        usuario = AuthRepository.buscar_usuario_por_correo(data["correo"])
        if not usuario or not AuthService._password_valido(usuario, data["password"]):
            AuthService._registrar_intento_fallido(ip_key)
            return AuthService._respuesta_credenciales_invalidas()

        if usuario.estado == "PENDIENTE_VERIFICACION":
            return {
                "success": False,
                "data": {},
                "error": "ACCOUNT_PENDING",
                "message": "La cuenta esta pendiente de verificacion.",
            }

        if usuario.estado == "BLOQUEADO":
            return {
                "success": False,
                "data": {},
                "error": "ACCOUNT_BLOCKED",
                "message": "La cuenta se encuentra bloqueada.",
            }

        AuthService._limpiar_intentos_login(ip_key)
        access_token = create_access_token(
            identity=str(usuario.id),
            additional_claims={
                "correo": usuario.correo,
                "rol": usuario.rol,
            },
            expires_delta=timedelta(hours=8),
        )

        return {
            "success": True,
            "data": {
                "token": access_token,
                "rol": usuario.rol,
                "nombre": usuario.nombre,
                "expira_en": "8h",
            },
            "error": None,
            "message": "Login exitoso.",
        }

    @staticmethod
    def verificar_correo(token):
        token_verificacion = AuthRepository.buscar_token_verificacion(token)
        if not token_verificacion:
            return {
                "success": False,
                "data": {},
                "error": "NOT_FOUND",
                "message": "Token invalido o inexistente.",
            }

        if token_verificacion.usado:
            return {
                "success": False,
                "data": {},
                "error": "TOKEN_USED",
                "message": "El token ya fue usado.",
            }

        if token_verificacion.expira_en <= AuthService._utcnow():
            return {
                "success": False,
                "data": {},
                "error": "TOKEN_EXPIRED",
                "message": "El token ha expirado.",
            }

        try:
            token_verificacion.usuario.estado = "ACTIVO"
            token_verificacion.usado = True
            AuthRepository.commit()
            return {
                "success": True,
                "data": token_verificacion.usuario.to_public_dict(),
                "error": None,
                "message": "Correo verificado correctamente.",
            }
        except SQLAlchemyError:
            AuthRepository.rollback()
            return {
                "success": False,
                "data": {},
                "error": "DATABASE_ERROR",
                "message": "No se pudo verificar el correo.",
            }

    @staticmethod
    def reenviar_verificacion(data):
        usuario = AuthRepository.buscar_usuario_por_correo(data["correo"])
        if not usuario:
            return {
                "success": False,
                "data": {},
                "error": "NOT_FOUND",
                "message": "Usuario no encontrado.",
            }

        if usuario.estado == "ACTIVO":
            return {
                "success": False,
                "data": {},
                "error": "CONFLICT",
                "message": "La cuenta ya se encuentra activa.",
            }

        if usuario.estado != "PENDIENTE_VERIFICACION":
            return {
                "success": False,
                "data": {},
                "error": "CONFLICT",
                "message": "La cuenta no permite reenvio de verificacion.",
            }

        try:
            for token_anterior in AuthRepository.buscar_tokens_activos_usuario(usuario.id):
                token_anterior.usado = True

            token_verificacion = AuthService._crear_token_verificacion(usuario)
            AuthRepository.agregar_token_verificacion(token_verificacion)
            AuthRepository.commit()
            AuthService._enviar_correo_verificacion_async(usuario, token_verificacion.token)
            return {
                "success": True,
                "data": {"correo": usuario.correo},
                "error": None,
                "message": "Correo de verificacion reenviado correctamente.",
            }
        except SQLAlchemyError:
            AuthRepository.rollback()
            return {
                "success": False,
                "data": {},
                "error": "DATABASE_ERROR",
                "message": "No se pudo reenviar el correo de verificacion.",
            }

    @staticmethod
    def _password_valido(usuario, password):
        return bcrypt.checkpw(
            password.encode("utf-8"),
            usuario.password_hash.encode("utf-8"),
        )

    @staticmethod
    def _respuesta_credenciales_invalidas():
        return {
            "success": False,
            "data": {},
            "error": "INVALID_CREDENTIALS",
            "message": "Credenciales invalidas.",
        }

    @staticmethod
    def _ip_bloqueada(ip_key):
        intento = AuthService._login_attempts.get(ip_key)
        if not intento:
            return False

        bloqueado_hasta = intento.get("blocked_until")
        if bloqueado_hasta and bloqueado_hasta > AuthService._utcnow():
            return True

        if bloqueado_hasta:
            AuthService._limpiar_intentos_login(ip_key)
        return False

    @staticmethod
    def _registrar_intento_fallido(ip_key):
        ahora = AuthService._utcnow()
        intento = AuthService._login_attempts.setdefault(
            ip_key,
            {"count": 0, "blocked_until": None},
        )
        intento["count"] += 1

        if intento["count"] >= AuthService._max_login_attempts:
            intento["blocked_until"] = ahora + timedelta(minutes=AuthService._login_block_minutes)

    @staticmethod
    def _limpiar_intentos_login(ip_key):
        AuthService._login_attempts.pop(ip_key, None)

    @staticmethod
    def _utcnow():
        return datetime.now(UTC).replace(tzinfo=None)

    @staticmethod
    def _crear_token_verificacion(usuario):
        return TokenVerificacion(
            usuario=usuario,
            token=secrets.token_hex(32),
            tipo="EMAIL_VERIFICATION",
            expira_en=AuthService._utcnow() + timedelta(hours=24),
            usado=False,
        )

    @staticmethod
    def _enviar_correo_verificacion_async(usuario, token):
        if current_app.config.get("TESTING"):
            return

        app = current_app._get_current_object()
        thread = threading.Thread(
            target=AuthService._enviar_correo_verificacion,
            args=(app, usuario.correo, token),
            daemon=True,
        )
        thread.start()

    @staticmethod
    def _enviar_correo_verificacion(app, correo, token):
        try:
            frontend_url = app.config.get("FRONTEND_URL") or "http://localhost:5173"
            enlace = f"{frontend_url}/verificar?token={token}"
            app.logger.info("Enlace de verificacion para %s: %s", correo, enlace)
        except Exception:
            app.logger.exception("No se pudo enviar correo de verificacion")

    @staticmethod
    def _validar_conflictos_tienda(data):
        if AuthRepository.buscar_usuario_por_correo(data["correo"]):
            return {
                "success": False,
                "data": {},
                "error": "CONFLICT",
                "message": "El correo ya se encuentra registrado.",
            }

        if AuthRepository.buscar_usuario_por_telefono(data["telefono"]):
            return {
                "success": False,
                "data": {},
                "error": "CONFLICT",
                "message": "El telefono ya se encuentra registrado.",
            }

        if AuthRepository.buscar_usuario_por_nombre(data["nombre_comercial"]):
            return {
                "success": False,
                "data": {},
                "error": "CONFLICT",
                "message": "El nombre comercial ya se encuentra registrado.",
            }

        if AuthRepository.buscar_tienda_por_ruc(data["ruc"]):
            return {
                "success": False,
                "data": {},
                "error": "CONFLICT",
                "message": "El RUC ya se encuentra registrado.",
            }

        return None

    @staticmethod
    def _eliminar_archivo_si_existe(ruta_absoluta):
        try:
            Path(ruta_absoluta).unlink(missing_ok=True)
        except OSError:
            current_app.logger.exception("No se pudo eliminar archivo de rollback")

from pathlib import Path
from datetime import UTC, datetime, timedelta
import secrets
import threading

import bcrypt
from flask import current_app
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app import db
from app.models.tienda import Tienda
from app.models.token_verificacion import TokenVerificacion
from app.models.usuario import Usuario
from app.repositories.auth_repository import AuthRepository
from app.utils.file_validation import (
    FileValidationError,
    persist_store_document,
    validate_store_document,
)


class AuthService:
    _login_attempts = {}
    _max_login_attempts = 5
    _login_block_minutes = 15
    _resend_limit = 3
    _resend_window_minutes = 15
    _password_reset_limit = 3
    _password_reset_window_minutes = 15
    _password_reset_attempts = {}

    @staticmethod
    def registrar_usuario(data):
        usuario_existente = AuthRepository.buscar_usuario_por_correo_o_telefono(
            data["correo"],
            data["telefono"],
        )

        if usuario_existente:
            if usuario_existente.correo == data["correo"]:
                mensaje = "El correo ya se encuentra registrado."
            else:
                mensaje = "El telefono ya se encuentra registrado."

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
                "message": "Revisa tu correo para activar tu cuenta.",
            }
        except IntegrityError:
            db.session.rollback()
            return {
                "success": False,
                "data": {},
                "error": "CONFLICT",
                "message": "El correo o telefono ya se encuentra registrado.",
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
            estado="EN_REVISION",
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
            persist_store_document(documento_identidad, ruta_absoluta)
            AuthService._enviar_correo_verificacion_async(usuario, token_verificacion.token)
            return {
                "success": True,
                "data": tienda.to_public_dict(),
                "error": None,
                "message": "Revisa tu correo para verificar tu cuenta. Tu solicitud de tienda sera revisada por un administrador.",
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
        except OSError:
            current_app.logger.exception("No se pudo guardar documento de tienda")
            return {
                "success": True,
                "data": tienda.to_public_dict(),
                "error": None,
                "message": "Revisa tu correo para verificar tu cuenta. Tu solicitud de tienda sera revisada por un administrador.",
            }

    @staticmethod
    def login(data, ip_address=None):
        usuario = AuthRepository.buscar_usuario_por_correo(data["correo"])
        if not usuario:
            AuthService._registrar_evento_login(None, ip_address, exitoso=False)
            return AuthService._respuesta_credenciales_invalidas()

        bloqueo_temp = AuthService._resolver_bloqueo_temporal(usuario)
        if bloqueo_temp:
            AuthService._registrar_evento_login(usuario.id, ip_address, exitoso=False)
            return bloqueo_temp

        if not AuthService._password_valido(usuario, data["password"]):
            AuthService._registrar_evento_login(usuario.id, ip_address, exitoso=False)
            return AuthService._registrar_fallo_login(usuario)

        if usuario.estado == "PENDIENTE_VERIFICACION":
            AuthService._registrar_evento_login(usuario.id, ip_address, exitoso=False)
            return {
                "success": False,
                "data": {"puede_reenviar": True},
                "error": "ACCOUNT_PENDING",
                "message": "Debes verificar tu correo antes de iniciar sesion.",
            }

        if usuario.estado == "EN_REVISION":
            AuthService._registrar_evento_login(usuario.id, ip_address, exitoso=False)
            return {
                "success": False,
                "data": {"puede_reenviar": False},
                "error": "ACCOUNT_IN_REVIEW",
                "message": "Tu solicitud de tienda esta siendo revisada por un administrador.",
            }

        if usuario.estado == "RECHAZADO":
            AuthService._registrar_evento_login(usuario.id, ip_address, exitoso=False)
            return {
                "success": False,
                "data": {"puede_reenviar": False},
                "error": "ACCOUNT_REJECTED",
                "message": "Tu solicitud de tienda fue rechazada. Debes registrarte nuevamente.",
            }

        if usuario.estado == "BLOQUEADO":
            AuthService._registrar_evento_login(usuario.id, ip_address, exitoso=False)
            return {
                "success": False,
                "data": {"puede_reenviar": False},
                "error": "ACCOUNT_BLOCKED",
                "message": "Tu cuenta ha sido suspendida. Contacta al administrador.",
            }

        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None
        AuthRepository.commit()
        access_token = create_access_token(
            identity=str(usuario.id),
            additional_claims={
                "correo": usuario.correo,
                "rol": usuario.rol,
            },
            expires_delta=timedelta(hours=8),
        )
        AuthService._registrar_evento_login(usuario.id, ip_address, exitoso=True)

        return {
            "success": True,
            "data": {
                "token": access_token,
                "correo": usuario.correo,
                "rol": usuario.rol,
                "nombre": usuario.nombre,
                "es_tienda_verificada": usuario.rol == "TIENDA_VERIFICADA",
                "estado": usuario.estado,
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
            usuario = token_verificacion.usuario
            if usuario.rol == "TIENDA_VERIFICADA":
                usuario.estado = "EN_REVISION"
                mensaje = (
                    "Correo verificado. Tu solicitud de tienda esta siendo revisada por un administrador."
                )
            else:
                usuario.estado = "ACTIVO"
                mensaje = "Correo verificado. Tu cuenta esta activa, ya puedes iniciar sesion."

            token_verificacion.usado = True
            AuthRepository.commit()
            return {
                "success": True,
                "data": {
                    "estado": usuario.estado,
                },
                "error": None,
                "message": mensaje,
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

        if usuario.estado not in {"PENDIENTE_VERIFICACION", "EN_REVISION"}:
            return {
                "success": False,
                "data": {},
                "error": "CONFLICT",
                "message": "La cuenta no permite reenvio de verificacion.",
            }

        ventana = AuthService._utcnow() - timedelta(minutes=AuthService._resend_window_minutes)
        reenvios_recientes = AuthRepository.contar_tokens_recientes_usuario(
            usuario.id,
            ventana,
        )
        primer_token = AuthRepository.buscar_primer_token_usuario(usuario.id)
        descuento_registro = 0
        if primer_token and primer_token.created_at >= ventana:
            descuento_registro = 1

        reenvios_efectivos = max(reenvios_recientes - descuento_registro, 0)
        if reenvios_efectivos >= AuthService._resend_limit:
            disponible_en = ventana + timedelta(minutes=AuthService._resend_window_minutes)
            tokens_recientes = sorted(
                [
                    token.created_at
                    for token in usuario.tokens_verificacion
                    if token.created_at >= ventana
                ]
            )
            if tokens_recientes:
                disponible_en = tokens_recientes[0] + timedelta(minutes=AuthService._resend_window_minutes)
            return {
                "success": False,
                "data": {
                    "disponible_en": disponible_en.isoformat(timespec="seconds"),
                },
                "error": "RATE_LIMIT_REENVIO",
                "message": "Demasiados intentos. Espera 15 minutos antes de solicitar otro correo.",
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
                "data": {
                    "expira_en": token_verificacion.expira_en.isoformat(timespec="seconds"),
                },
                "error": None,
                "message": "Correo de verificacion reenviado. Revisa tu bandeja de entrada.",
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
    def solicitar_reset_password(data, ip_address=None):
        correo = data["correo"]
        ahora = AuthService._utcnow()
        rate_limit = AuthService._validar_rate_limit_reset(correo, ip_address, ahora)
        if rate_limit:
            return rate_limit

        usuario = AuthRepository.buscar_usuario_por_correo(correo)
        respuesta_generica = {
            "success": True,
            "data": {},
            "error": None,
            "message": "Si el correo esta registrado y la cuenta esta activa, recibiras un enlace en los proximos minutos.",
        }

        if not usuario or usuario.estado != "ACTIVO":
            AuthService._registrar_solicitud_reset(correo, ip_address, ahora)
            return respuesta_generica

        try:
            for token_anterior in AuthRepository.buscar_tokens_activos_usuario(
                usuario.id,
                tipo="PASSWORD_RESET",
            ):
                token_anterior.usado = True

            token_reset = AuthService._crear_token_password_reset(usuario, ahora)
            AuthRepository.agregar_token_verificacion(token_reset)
            AuthRepository.commit()
            AuthService._registrar_solicitud_reset(correo, ip_address, ahora)
            AuthService._enviar_correo_reset_password_async(usuario, token_reset.token)
            return respuesta_generica
        except SQLAlchemyError:
            AuthRepository.rollback()
            return {
                "success": False,
                "data": {},
                "error": "DATABASE_ERROR",
                "message": "No se pudo procesar la solicitud de recuperacion.",
            }

    @staticmethod
    def confirmar_reset_password(data, ip_address=None):
        token_verificacion = AuthRepository.buscar_token_por_valor_y_tipo(
            data["token"],
            "PASSWORD_RESET",
        )
        if not token_verificacion:
            return {
                "success": False,
                "data": {},
                "error": "NOT_FOUND",
                "message": "El token no existe.",
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

        usuario = token_verificacion.usuario
        if usuario.estado not in {"ACTIVO", "BLOQUEADO_TEMP"}:
            return {
                "success": False,
                "data": {},
                "error": "FORBIDDEN",
                "message": "La cuenta no permite restablecer la contrasena en este momento.",
            }

        if AuthService._password_valido(usuario, data["password"]):
            return {
                "success": False,
                "data": {},
                "error": "CONFLICT",
                "message": "La nueva contrasena debe ser diferente a la actual.",
            }

        try:
            usuario.password_hash = bcrypt.hashpw(
                data["password"].encode("utf-8"),
                bcrypt.gensalt(rounds=10),
            ).decode("utf-8")
            usuario.intentos_fallidos = 0
            usuario.bloqueado_hasta = None
            if usuario.estado == "BLOQUEADO_TEMP":
                usuario.estado = "ACTIVO"

            token_verificacion.usado = True
            for token_activo in AuthRepository.buscar_tokens_activos_usuario(
                usuario.id,
                tipo="PASSWORD_RESET",
            ):
                token_activo.usado = True

            AuthRepository.commit()
            current_app.logger.info(
                "Password reset usuario_id=%s ip=%s accion=PASSWORD_RESET",
                usuario.id,
                ip_address or "unknown",
            )
            return {
                "success": True,
                "data": {"usuario_id": usuario.id},
                "error": None,
                "message": "Contrasena actualizada correctamente. Ya puedes iniciar sesion.",
            }
        except SQLAlchemyError:
            AuthRepository.rollback()
            return {
                "success": False,
                "data": {},
                "error": "DATABASE_ERROR",
                "message": "No se pudo actualizar la contrasena.",
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
    def _registrar_fallo_login(usuario):
        ahora = AuthService._utcnow()
        usuario.intentos_fallidos = (usuario.intentos_fallidos or 0) + 1

        if usuario.intentos_fallidos >= AuthService._max_login_attempts:
            usuario.estado = "BLOQUEADO_TEMP"
            usuario.bloqueado_hasta = ahora + timedelta(minutes=AuthService._login_block_minutes)
            AuthRepository.commit()
            return {
                "success": False,
                "data": {
                    "disponible_en": usuario.bloqueado_hasta.isoformat(timespec="seconds"),
                },
                "error": "RATE_LIMIT_LOGIN",
                "message": "Demasiados intentos fallidos. Cuenta bloqueada temporalmente.",
            }

        AuthRepository.commit()
        return AuthService._respuesta_credenciales_invalidas()

    @staticmethod
    def _resolver_bloqueo_temporal(usuario):
        if usuario.estado != "BLOQUEADO_TEMP":
            return None

        ahora = AuthService._utcnow()
        if usuario.bloqueado_hasta and usuario.bloqueado_hasta > ahora:
            return {
                "success": False,
                "data": {
                    "disponible_en": usuario.bloqueado_hasta.isoformat(timespec="seconds"),
                },
                "error": "RATE_LIMIT_LOGIN",
                "message": "Demasiados intentos fallidos. Cuenta bloqueada temporalmente.",
            }

        usuario.estado = "ACTIVO"
        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None
        AuthRepository.commit()
        return None

    @staticmethod
    def _validar_rate_limit_reset(correo, ip_address, ahora):
        ventana = ahora - timedelta(minutes=AuthService._password_reset_window_minutes)
        request_key = AuthService._password_reset_key(correo, ip_address)
        intentos = [
            ts for ts in AuthService._password_reset_attempts.get(request_key, [])
            if ts >= ventana
        ]
        AuthService._password_reset_attempts[request_key] = intentos
        if len(intentos) >= AuthService._password_reset_limit:
            disponible_en = intentos[0] + timedelta(
                minutes=AuthService._password_reset_window_minutes
            )
            return {
                "success": False,
                "data": {
                    "disponible_en": disponible_en.isoformat(timespec="seconds"),
                },
                "error": "RATE_LIMIT_PASSWORD_RESET",
                "message": "Demasiadas solicitudes. Espera 15 minutos antes de intentar de nuevo.",
            }

        usuario = AuthRepository.buscar_usuario_por_correo(correo)
        if usuario and usuario.estado == "ACTIVO":
            tokens_recientes = AuthRepository.listar_tokens_recientes_usuario(
                usuario.id,
                ventana,
                "PASSWORD_RESET",
            )
            if len(tokens_recientes) >= AuthService._password_reset_limit:
                disponible_en = tokens_recientes[0].created_at + timedelta(
                    minutes=AuthService._password_reset_window_minutes
                )
                return {
                    "success": False,
                    "data": {
                        "disponible_en": disponible_en.isoformat(timespec="seconds"),
                    },
                    "error": "RATE_LIMIT_PASSWORD_RESET",
                    "message": "Demasiadas solicitudes. Espera 15 minutos antes de intentar de nuevo.",
                }

        return None

    @staticmethod
    def _registrar_solicitud_reset(correo, ip_address, timestamp):
        request_key = AuthService._password_reset_key(correo, ip_address)
        intentos = AuthService._password_reset_attempts.setdefault(request_key, [])
        intentos.append(timestamp)

    @staticmethod
    def _password_reset_key(correo, ip_address):
        return f"{(ip_address or 'unknown').strip()}::{correo.strip().lower()}"

    @staticmethod
    def _registrar_evento_login(usuario_id, ip_address, exitoso):
        current_app.logger.info(
            "Login usuario_id=%s ip=%s exitoso=%s",
            usuario_id,
            ip_address or "unknown",
            exitoso,
        )

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
            created_at=AuthService._utcnow(),
        )

    @staticmethod
    def _crear_token_password_reset(usuario, ahora=None):
        timestamp = ahora or AuthService._utcnow()
        return TokenVerificacion(
            usuario=usuario,
            token=secrets.token_hex(32),
            tipo="PASSWORD_RESET",
            expira_en=timestamp + timedelta(hours=1),
            usado=False,
            created_at=timestamp,
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
    def _enviar_correo_reset_password_async(usuario, token):
        if current_app.config.get("TESTING"):
            return

        app = current_app._get_current_object()
        thread = threading.Thread(
            target=AuthService._enviar_correo_reset_password,
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
    def _enviar_correo_reset_password(app, correo, token):
        try:
            frontend_url = app.config.get("FRONTEND_URL") or "http://localhost:5173"
            enlace = f"{frontend_url}/reset-password?token={token}"
            app.logger.info("Enlace de reset password para %s: %s", correo, enlace)
        except Exception:
            app.logger.exception("No se pudo enviar correo de reset password")

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

        if AuthRepository.buscar_tienda_por_nombre_comercial(data["nombre_comercial"]):
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

from flask import current_app, jsonify, request
from marshmallow import RAISE, Schema, ValidationError, fields

from app.schemas.tienda_schema import RegistroTiendaSchema
from app.schemas.usuario_schema import LoginUsuarioSchema, RegistroUsuarioSchema
from app.services.auth_service import AuthService


class ReenvioVerificacionSchema(Schema):
    correo = fields.Email(required=True)


def registrar_usuario_controller():
    request_data = request.get_json(silent=True) or {}
    schema = RegistroUsuarioSchema()

    try:
        datos_validados = schema.load(request_data, unknown=RAISE)
    except ValidationError as error:
        return jsonify({
            "success": False,
            "data": error.messages,
            "error": "VALIDATION_ERROR",
            "message": "Campos invalidos.",
        }), 400

    try:
        respuesta = AuthService.registrar_usuario(datos_validados)
    except Exception:
        current_app.logger.exception("Error inesperado en AuthService")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": "Error interno del servidor.",
        }), 500

    if respuesta.get("success"):
        return jsonify(respuesta), 201

    if respuesta.get("error") == "CONFLICT":
        return jsonify(respuesta), 409

    return jsonify(respuesta), 500


def registrar_tienda_controller():
    schema = RegistroTiendaSchema()

    try:
        datos_validados = schema.load(request.form, unknown=RAISE)
    except ValidationError as error:
        status_code = 422 if "ruc" in error.messages or "password" in error.messages else 400
        return jsonify({
            "success": False,
            "data": error.messages,
            "error": "VALIDATION_ERROR",
            "message": "Campos invalidos.",
        }), status_code

    documento_identidad = request.files.get("documento_identidad")

    try:
        respuesta = AuthService.registrar_tienda(
            datos_validados,
            documento_identidad,
        )
    except Exception:
        current_app.logger.exception("Error inesperado en AuthService")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": "Error interno del servidor.",
        }), 500

    if respuesta.get("success"):
        return jsonify(respuesta), 201

    status_by_error = {
        "CONFLICT": 409,
        "MISSING_FILE": 400,
        "FILE_TOO_LARGE": 413,
        "INVALID_FILE_TYPE": 415,
        "DATABASE_ERROR": 500,
    }
    return jsonify(respuesta), status_by_error.get(respuesta.get("error"), 500)


def login_controller():
    # El controller solo valida la forma del request y delega la autenticacion
    # al service. Asi evitamos mezclar HTTP con reglas de negocio.
    request_data = request.get_json(silent=True) or {}
    schema = LoginUsuarioSchema()

    try:
        datos_validados = schema.load(request_data, unknown=RAISE)
    except ValidationError as error:
        return jsonify({
            "success": False,
            "data": error.messages,
            "error": "VALIDATION_ERROR",
            "message": "Campos invalidos.",
        }), 400

    try:
        respuesta = AuthService.login(datos_validados, request.remote_addr)
    except Exception:
        current_app.logger.exception("Error inesperado en login")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": "Error interno del servidor.",
        }), 500

    status_by_error = {
        "INVALID_CREDENTIALS": 401,
        "ACCOUNT_PENDING": 403,
        "ACCOUNT_BLOCKED": 403,
        "RATE_LIMIT": 429,
    }
    return jsonify(respuesta), 200 if respuesta.get("success") else status_by_error.get(respuesta.get("error"), 500)


def verificar_correo_controller():
    token = request.args.get("token", "").strip()
    if not token:
        return jsonify({
            "success": False,
            "data": {},
            "error": "VALIDATION_ERROR",
            "message": "El token es obligatorio.",
        }), 400

    try:
        respuesta = AuthService.verificar_correo(token)
    except Exception:
        current_app.logger.exception("Error inesperado al verificar correo")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": "Error interno del servidor.",
        }), 500

    status_by_error = {
        "NOT_FOUND": 404,
        "TOKEN_USED": 409,
        "TOKEN_EXPIRED": 410,
        "DATABASE_ERROR": 500,
    }
    return jsonify(respuesta), 200 if respuesta.get("success") else status_by_error.get(respuesta.get("error"), 500)


def reenviar_verificacion_controller():
    request_data = request.get_json(silent=True) or {}
    schema = ReenvioVerificacionSchema()

    try:
        datos_validados = schema.load(request_data, unknown=RAISE)
    except ValidationError as error:
        return jsonify({
            "success": False,
            "data": error.messages,
            "error": "VALIDATION_ERROR",
            "message": "Campos invalidos.",
        }), 400

    try:
        respuesta = AuthService.reenviar_verificacion(datos_validados)
    except Exception:
        current_app.logger.exception("Error inesperado al reenviar verificacion")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": "Error interno del servidor.",
        }), 500

    status_by_error = {
        "NOT_FOUND": 404,
        "CONFLICT": 409,
        "DATABASE_ERROR": 500,
    }
    return jsonify(respuesta), 200 if respuesta.get("success") else status_by_error.get(respuesta.get("error"), 500)

from flask import current_app, jsonify
from flask import request
from flask_jwt_extended import get_jwt_identity

from app.schemas.usuario_schema import HistorialTransaccionesSchema
from app.services.transaccion_service import TransaccionService
from app.services.usuario_service import UsuarioService


def perfil_publico_usuario_controller(usuario_id):
    try:
        usuario_id_int = _parse_positive_int(usuario_id, "usuario_id")
        respuesta = UsuarioService.obtener_perfil_publico(usuario_id_int)
    except ValueError as error:
        return jsonify({
            "success": False,
            "data": {},
            "error": "VALIDATION_ERROR",
            "message": str(error),
        }), 400
    except Exception:
        current_app.logger.exception("Error inesperado al obtener perfil publico")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": "Error interno del servidor.",
        }), 500

    return jsonify(respuesta), _status_for_usuario_response(respuesta, success_status=200)


def historial_transacciones_me_controller():
    schema = HistorialTransaccionesSchema()

    try:
        page = _parse_positive_int(request.args.get("page", "1"), "page")
        limit = _parse_positive_int(request.args.get("limit", "10"), "limit")
    except ValueError as error:
        return jsonify({
            "success": False,
            "data": {},
            "error": "VALIDATION_ERROR",
            "message": str(error),
        }), 400

    if limit > 20:
        return jsonify({
            "success": False,
            "data": {},
            "error": "VALIDATION_ERROR",
            "message": "El parametro limit no puede superar 20.",
        }), 400

    try:
        datos_validados = schema.load({"tipo": request.args.get("tipo", "ambas")})
        usuario_id = int(get_jwt_identity())
        respuesta = TransaccionService.obtener_historial_usuario(
            usuario_id,
            datos_validados["tipo"],
            page,
            limit,
        )
    except Exception as error:
        from marshmallow import ValidationError
        if isinstance(error, ValidationError):
            return jsonify({
                "success": False,
                "data": error.messages,
                "error": "VALIDATION_ERROR",
                "message": "Parametros invalidos.",
            }), 422
        current_app.logger.exception("Error inesperado al obtener historial de transacciones")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": "Error interno del servidor.",
        }), 500

    return jsonify(respuesta), _status_for_usuario_response(respuesta, success_status=200)


def panel_usuario_me_controller():
    try:
        usuario_id = int(get_jwt_identity())
        respuesta = UsuarioService.obtener_panel_usuario(usuario_id)
    except Exception:
        current_app.logger.exception("Error inesperado al obtener panel del usuario")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": "Error interno del servidor.",
        }), 500

    return jsonify(respuesta), _status_for_usuario_response(respuesta, success_status=200)


def _status_for_usuario_response(respuesta, success_status):
    if respuesta.get("success"):
        return success_status

    status_by_error = {
        "FORBIDDEN": 403,
        "NOT_FOUND": 404,
        "VALIDATION_ERROR": 422,
    }
    return status_by_error.get(respuesta.get("error"), 500)


def _parse_positive_int(raw_value, param_name):
    try:
        value = int(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"El parametro {param_name} debe ser un entero positivo.") from exc

    if value <= 0:
        raise ValueError(f"El parametro {param_name} debe ser un entero positivo.")

    return value

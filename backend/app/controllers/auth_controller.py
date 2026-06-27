from flask import current_app, jsonify, request
from marshmallow import RAISE, ValidationError

from app.schemas.usuario_schema import RegistroUsuarioSchema
from app.services.auth_service import AuthService


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
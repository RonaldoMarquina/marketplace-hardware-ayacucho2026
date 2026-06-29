from flask import current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import RAISE, ValidationError

from app.schemas.anuncio_schema import CrearAnuncioSchema
from app.services.anuncio_service import AnuncioService


def publicar_anuncio_controller():
    # Controller delgado: valida HTTP/JSON y delega reglas de negocio al service.
    request_data = request.get_json(silent=True) or {}
    schema = CrearAnuncioSchema()

    try:
        datos_validados = schema.load(request_data, unknown=RAISE)
    except ValidationError as error:
        status_code = 400 if _hay_campos_obligatorios(error.messages) else 422
        return jsonify({
            "success": False,
            "data": error.messages,
            "error": "VALIDATION_ERROR",
            "message": "Campos invalidos.",
        }), status_code

    try:
        usuario_id = int(get_jwt_identity())
        respuesta = AnuncioService.publicar_anuncio(usuario_id, datos_validados)
    except Exception:
        current_app.logger.exception("Error inesperado al publicar anuncio")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": "Error interno del servidor.",
        }), 500

    if respuesta.get("success"):
        return jsonify(respuesta), 201

    status_by_error = {
        "FORBIDDEN": 403,
        "NOT_FOUND": 404,
        "DATABASE_ERROR": 500,
    }
    return jsonify(respuesta), status_by_error.get(respuesta.get("error"), 500)


def _hay_campos_obligatorios(messages):
    texto = str(messages).lower()
    return "obligatori" in texto or "missing" in texto or "required" in texto



from flask import current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import RAISE, ValidationError

from app.schemas.anuncio_schema import CrearAnuncioSchema, EditarAnuncioSchema, ReordenarMediaSchema
from app.services.anuncio_service import AnuncioService


EDITABLE_FIELDS = {
    "titulo",
    "categoria",
    "subcategoria",
    "descripcion",
    "condicion",
    "precio",
    "especificaciones",
}


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

    return jsonify(respuesta), _status_for_anuncio_response(respuesta, success_status=201)


def editar_anuncio_controller(anuncio_id):
    request_data = request.get_json(silent=True)
    filtered_data = _solo_campos_editables(request_data)
    schema = EditarAnuncioSchema()

    try:
        datos_validados = schema.load(filtered_data, unknown=RAISE)
    except ValidationError as error:
        return jsonify({
            "success": False,
            "data": error.messages,
            "error": "VALIDATION_ERROR",
            "message": "Campos invalidos.",
        }), 422

    try:
        usuario_id = int(get_jwt_identity())
        respuesta = AnuncioService.editar_anuncio(anuncio_id, usuario_id, datos_validados)
    except Exception:
        current_app.logger.exception("Error inesperado al editar anuncio")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": "Error interno del servidor.",
        }), 500

    return jsonify(respuesta), _status_for_anuncio_response(respuesta, success_status=200)


def desactivar_anuncio_controller(anuncio_id):
    try:
        usuario_id = int(get_jwt_identity())
        respuesta = AnuncioService.desactivar_anuncio(anuncio_id, usuario_id)
    except Exception:
        current_app.logger.exception("Error inesperado al desactivar anuncio")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": "Error interno del servidor.",
        }), 500

    return jsonify(respuesta), _status_for_anuncio_response(respuesta, success_status=200)


def reactivar_anuncio_controller(anuncio_id):
    try:
        usuario_id = int(get_jwt_identity())
        respuesta = AnuncioService.reactivar_anuncio(anuncio_id, usuario_id)
    except Exception:
        current_app.logger.exception("Error inesperado al reactivar anuncio")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": "Error interno del servidor.",
        }), 500

    return jsonify(respuesta), _status_for_anuncio_response(respuesta, success_status=200)


def subir_media_controller(anuncio_id):
    # Los archivos llegan por multipart/form-data. El controller solo los toma
    # y el service valida propiedad, limites, mimetype real y persistencia.
    files = request.files.getlist("media") or request.files.getlist("files")

    try:
        usuario_id = int(get_jwt_identity())
        respuesta = AnuncioService.subir_media(
            anuncio_id,
            usuario_id,
            files,
            current_app.config["UPLOAD_FOLDER"],
        )
    except Exception:
        current_app.logger.exception("Error inesperado al cargar media")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": "Error interno del servidor.",
        }), 500

    return jsonify(respuesta), _status_for_anuncio_response(respuesta, success_status=201)


def reordenar_media_controller(anuncio_id):
    request_data = request.get_json(silent=True) or {}
    schema = ReordenarMediaSchema()

    try:
        datos_validados = schema.load(request_data, unknown=RAISE)
    except ValidationError as error:
        return jsonify({
            "success": False,
            "data": error.messages,
            "error": "VALIDATION_ERROR",
            "message": "Campos invalidos.",
        }), 422

    try:
        usuario_id = int(get_jwt_identity())
        respuesta = AnuncioService.reordenar_media(anuncio_id, usuario_id, datos_validados["orden"])
    except Exception:
        current_app.logger.exception("Error inesperado al reordenar media")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": "Error interno del servidor.",
        }), 500

    return jsonify(respuesta), _status_for_anuncio_response(respuesta, success_status=200)


def eliminar_media_controller(anuncio_id, media_id):
    try:
        usuario_id = int(get_jwt_identity())
        respuesta = AnuncioService.eliminar_media(
            anuncio_id,
            media_id,
            usuario_id,
            current_app.config["UPLOAD_FOLDER"],
        )
    except Exception:
        current_app.logger.exception("Error inesperado al eliminar media")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": "Error interno del servidor.",
        }), 500

    return jsonify(respuesta), _status_for_anuncio_response(respuesta, success_status=200)


def reemplazar_media_controller(anuncio_id, media_id):
    file_storage = request.files.get("media") or request.files.get("file")

    try:
        usuario_id = int(get_jwt_identity())
        respuesta = AnuncioService.reemplazar_media(
            anuncio_id,
            media_id,
            usuario_id,
            file_storage,
            current_app.config["UPLOAD_FOLDER"],
        )
    except Exception:
        current_app.logger.exception("Error inesperado al reemplazar media")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": "Error interno del servidor.",
        }), 500

    return jsonify(respuesta), _status_for_anuncio_response(respuesta, success_status=200)


def _hay_campos_obligatorios(messages):
    texto = str(messages).lower()
    return "obligatori" in texto or "missing" in texto or "required" in texto


def _solo_campos_editables(request_data):
    if not isinstance(request_data, dict):
        return {}
    return {campo: valor for campo, valor in request_data.items() if campo in EDITABLE_FIELDS}


def _status_for_anuncio_response(respuesta, success_status):
    if respuesta.get("success"):
        return success_status

    status_by_error = {
        "EMPTY_BODY": 400,
        "MISSING_FILE": 400,
        "FORBIDDEN": 403,
        "NOT_FOUND": 404,
        "CONFLICT": 409,
        "FILE_TOO_LARGE": 413,
        "INVALID_FILE_TYPE": 422,
        "TOO_MANY_FILES": 422,
        "VALIDATION_ERROR": 422,
        "FILE_DELETE_ERROR": 500,
        "DATABASE_ERROR": 500,
    }
    return status_by_error.get(respuesta.get("error"), 500)

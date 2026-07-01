from flask import current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from marshmallow import RAISE, ValidationError

from app.schemas.anuncio_schema import (
    BuscarAnunciosSchema,
    CrearAnuncioSchema,
    EditarAnuncioSchema,
    ReportarAnuncioSchema,
    ReordenarMediaSchema,
)
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

MAX_SPECS_BUSQUEDA = 10


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


def feed_anuncios_controller():
    try:
        page = _parse_positive_int(request.args.get("page", "1"), "page")
        limit = _parse_positive_int(request.args.get("limit", "20"), "limit")
    except ValueError as error:
        return jsonify({
            "success": False,
            "data": {},
            "error": "VALIDATION_ERROR",
            "message": str(error),
        }), 400

    if limit > 50:
        return jsonify({
            "success": False,
            "data": {},
            "error": "VALIDATION_ERROR",
            "message": "El parametro limit no puede superar 50.",
        }), 400

    try:
        respuesta = AnuncioService.obtener_feed_publico(page, limit)
    except Exception:
        current_app.logger.exception("Error inesperado al obtener feed publico")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": "Error interno del servidor.",
        }), 500

    return jsonify(respuesta), 200


def buscar_anuncios_controller():
    request_data = _extraer_query_busqueda(request.args)
    schema = BuscarAnunciosSchema()

    try:
        datos_validados = schema.load(request_data, unknown=RAISE)
    except ValidationError as error:
        return jsonify({
            "success": False,
            "data": error.messages,
            "error": "VALIDATION_ERROR",
            "message": "Parametros de busqueda invalidos.",
        }), _status_for_search_validation(error.messages)

    specs_error = _validar_specs_query(request.args)
    if specs_error:
        return jsonify(specs_error), 422

    datos_validados["specs"] = _extraer_specs_query(request.args)

    try:
        respuesta = AnuncioService.buscar_anuncios_publicos(datos_validados)
    except Exception:
        current_app.logger.exception("Error inesperado al buscar anuncios")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": "Error interno del servidor.",
        }), 500

    return jsonify(respuesta), 200


def detalle_anuncio_controller(anuncio_id):
    try:
        anuncio_id_int = _parse_positive_int(anuncio_id, "anuncio_id")
    except ValueError as error:
        return jsonify({
            "success": False,
            "data": {},
            "error": "VALIDATION_ERROR",
            "message": str(error),
        }), 400

    try:
        verify_jwt_in_request(optional=True)
        jwt_identity = get_jwt_identity()
        viewer_user_id = int(jwt_identity) if jwt_identity is not None else None
        respuesta = AnuncioService.obtener_detalle_anuncio(anuncio_id_int, viewer_user_id)
    except Exception:
        current_app.logger.exception("Error inesperado al obtener detalle de anuncio")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": "Error interno del servidor.",
        }), 500

    return jsonify(respuesta), _status_for_anuncio_response(respuesta, success_status=200)


def contacto_anuncio_controller(anuncio_id):
    try:
        anuncio_id_int = _parse_positive_int(anuncio_id, "anuncio_id")
        usuario_id = int(get_jwt_identity())
        respuesta = AnuncioService.obtener_contacto_whatsapp(anuncio_id_int, usuario_id)
    except Exception:
        current_app.logger.exception("Error inesperado al obtener contacto de anuncio")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": "Error interno del servidor.",
        }), 500

    return jsonify(respuesta), _status_for_anuncio_response(respuesta, success_status=200)


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


def marcar_vendido_controller(anuncio_id):
    try:
        usuario_id = int(get_jwt_identity())
        respuesta = AnuncioService.marcar_anuncio_vendido(anuncio_id, usuario_id)
    except Exception:
        current_app.logger.exception("Error inesperado al marcar anuncio como vendido")
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


def reportar_anuncio_controller(anuncio_id):
    request_data = request.get_json(silent=True) or {}
    schema = ReportarAnuncioSchema()

    try:
        datos_validados = schema.load(request_data, unknown=RAISE)
        anuncio_id_int = _parse_positive_int(anuncio_id, "anuncio_id")
        usuario_id = int(get_jwt_identity())
        respuesta = AnuncioService.reportar_anuncio(anuncio_id_int, usuario_id, datos_validados["motivo"])
    except ValidationError as error:
        return jsonify({
            "success": False,
            "data": error.messages,
            "error": "VALIDATION_ERROR",
            "message": "Campos invalidos.",
        }), 422
    except ValueError as error:
        return jsonify({
            "success": False,
            "data": {},
            "error": "VALIDATION_ERROR",
            "message": str(error),
        }), 400
    except Exception:
        current_app.logger.exception("Error inesperado al reportar anuncio")
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
        "SELLER_WITHOUT_PHONE": 422,
        "INVALID_FILE_TYPE": 422,
        "TOO_MANY_FILES": 422,
        "VALIDATION_ERROR": 422,
        "RATE_LIMIT_DIARIO": 429,
        "RATE_LIMIT_ANUNCIO": 429,
        "RATE_LIMIT_REPORTES": 429,
        "FILE_DELETE_ERROR": 500,
        "DATABASE_ERROR": 500,
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


def _extraer_query_busqueda(args):
    data = {}
    for key in args.keys():
        if not key.startswith("specs["):
            data[key] = args.get(key)
    return data


def _extraer_specs_query(args):
    specs = {}
    for key in args.keys():
        if not key.startswith("specs[") or not key.endswith("]"):
            continue

        spec_key = key[6:-1]
        specs[spec_key] = (args.get(key) or "").strip()
    return specs


def _validar_specs_query(args):
    specs = _extraer_specs_query(args)
    if len(specs) > MAX_SPECS_BUSQUEDA:
        return {
            "success": False,
            "data": {"specs": ["No se permiten mas de 10 specs simultaneas."]},
            "error": "VALIDATION_ERROR",
            "message": "Parametros de busqueda invalidos.",
        }

    for spec_key in specs:
        if not spec_key or len(spec_key) > 50 or not spec_key.replace("_", "").isalnum():
            return {
                "success": False,
                "data": {"specs": [f"La clave de spec '{spec_key}' es invalida."]},
                "error": "VALIDATION_ERROR",
                "message": "Parametros de busqueda invalidos.",
            }

    return None


def _status_for_search_validation(messages):
    texto = str(messages).lower()
    if "precio_min no puede ser mayor que precio_max" in texto:
        return 400
    if "q" in messages:
        return 400
    return 422

from flask import current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import RAISE, ValidationError

from app.schemas.anuncio_schema import MotivoAdminSchema
from app.services.anuncio_service import AnuncioService


def listar_anuncios_reportados_controller():
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
        respuesta = AnuncioService.listar_anuncios_reportados(page, limit)
    except Exception:
        current_app.logger.exception("Error inesperado al listar anuncios reportados")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": "Error interno del servidor.",
        }), 500

    return jsonify(respuesta), _status_for_admin_response(respuesta, success_status=200)


def bloquear_anuncio_admin_controller(anuncio_id):
    return _ejecutar_accion_moderacion(
        anuncio_id,
        accion_service=AnuncioService.bloquear_anuncio_admin,
        log_message="Error inesperado al bloquear anuncio",
    )


def desbloquear_anuncio_admin_controller(anuncio_id):
    return _ejecutar_accion_moderacion(
        anuncio_id,
        accion_service=AnuncioService.desbloquear_anuncio_admin,
        log_message="Error inesperado al desbloquear anuncio",
    )


def historial_moderacion_controller():
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
        respuesta = AnuncioService.listar_historial_moderacion(page, limit)
    except Exception:
        current_app.logger.exception("Error inesperado al obtener historial de moderacion")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": "Error interno del servidor.",
        }), 500

    return jsonify(respuesta), _status_for_admin_response(respuesta, success_status=200)


def _ejecutar_accion_moderacion(anuncio_id, accion_service, log_message):
    request_data = request.get_json(silent=True) or {}
    schema = MotivoAdminSchema()

    try:
        datos_validados = schema.load(request_data, unknown=RAISE)
        anuncio_id_int = _parse_positive_int(anuncio_id, "anuncio_id")
        admin_id = int(get_jwt_identity())
        respuesta = accion_service(anuncio_id_int, admin_id, datos_validados["motivo_admin"])
    except ValidationError as error:
        return jsonify({
            "success": False,
            "data": error.messages,
            "error": "VALIDATION_ERROR",
            "message": "Campos invalidos.",
        }), 400
    except ValueError as error:
        return jsonify({
            "success": False,
            "data": {},
            "error": "VALIDATION_ERROR",
            "message": str(error),
        }), 400
    except Exception:
        current_app.logger.exception(log_message)
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": "Error interno del servidor.",
        }), 500

    return jsonify(respuesta), _status_for_admin_response(respuesta, success_status=200)


def _status_for_admin_response(respuesta, success_status):
    if respuesta.get("success"):
        return success_status

    status_by_error = {
        "FORBIDDEN": 403,
        "NOT_FOUND": 404,
        "CONFLICT": 409,
        "RATE_LIMIT_REPORTES": 429,
        "VALIDATION_ERROR": 422,
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

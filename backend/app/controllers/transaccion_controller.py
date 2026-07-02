from flask import current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import RAISE, ValidationError

from app.schemas.anuncio_schema import CalificarUsuarioSchema
from app.services.transaccion_service import TransaccionService


def calificar_vendedor_controller(transaccion_id):
    request_data = request.get_json(silent=True) or {}
    schema = CalificarUsuarioSchema()

    try:
        datos_validados = schema.load(request_data, unknown=RAISE)
        transaccion_id_int = _parse_positive_int(transaccion_id, "transaccion_id")
        usuario_id = int(get_jwt_identity())
        respuesta = TransaccionService.calificar_vendedor(
            transaccion_id_int,
            usuario_id,
            datos_validados["puntaje"],
            datos_validados.get("comentario"),
        )
    except ValidationError as error:
        status_code = 400 if _hay_campos_obligatorios(error.messages) else 422
        return jsonify({
            "success": False,
            "data": error.messages,
            "error": "VALIDATION_ERROR",
            "message": "Campos invalidos.",
        }), status_code
    except ValueError as error:
        return jsonify({
            "success": False,
            "data": {},
            "error": "VALIDATION_ERROR",
            "message": str(error),
        }), 400
    except Exception:
        current_app.logger.exception("Error inesperado al calificar vendedor")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": "Error interno del servidor.",
        }), 500

    return jsonify(respuesta), _status_for_transaccion_response(respuesta, success_status=200)


def calificar_comprador_controller(transaccion_id):
    request_data = request.get_json(silent=True) or {}
    schema = CalificarUsuarioSchema()

    try:
        datos_validados = schema.load(request_data, unknown=RAISE)
        transaccion_id_int = _parse_positive_int(transaccion_id, "transaccion_id")
        usuario_id = int(get_jwt_identity())
        respuesta = TransaccionService.calificar_comprador(
            transaccion_id_int,
            usuario_id,
            datos_validados["puntaje"],
            datos_validados.get("comentario"),
        )
    except ValidationError as error:
        status_code = 400 if _hay_campos_obligatorios(error.messages) else 422
        return jsonify({
            "success": False,
            "data": error.messages,
            "error": "VALIDATION_ERROR",
            "message": "Campos invalidos.",
        }), status_code
    except ValueError as error:
        return jsonify({
            "success": False,
            "data": {},
            "error": "VALIDATION_ERROR",
            "message": str(error),
        }), 400
    except Exception:
        current_app.logger.exception("Error inesperado al calificar comprador")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": "Error interno del servidor.",
        }), 500

    return jsonify(respuesta), _status_for_transaccion_response(respuesta, success_status=200)


def _status_for_transaccion_response(respuesta, success_status):
    if respuesta.get("success"):
        return success_status

    status_by_error = {
        "FORBIDDEN": 403,
        "NOT_FOUND": 404,
        "CONFLICT": 409,
        "VALIDATION_ERROR": 422,
        "DATABASE_ERROR": 500,
    }
    return status_by_error.get(respuesta.get("error"), 500)


def _hay_campos_obligatorios(messages):
    texto = str(messages).lower()
    return "obligatori" in texto or "missing" in texto or "required" in texto


def _parse_positive_int(raw_value, param_name):
    try:
        value = int(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"El parametro {param_name} debe ser un entero positivo.") from exc

    if value <= 0:
        raise ValueError(f"El parametro {param_name} debe ser un entero positivo.")

    return value

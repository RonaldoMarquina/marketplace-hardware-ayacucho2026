from flask import current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import RAISE, ValidationError

from app.schemas.anuncio_schema import MotivoAdminSchema
from app.schemas.usuario_schema import (
    AdminUsuariosFiltroSchema,
    MotivoAdminUsuarioSchema,
    ResolverApelacionAdminSchema,
)
from app.services.anuncio_service import AnuncioService
from app.services.admin_user_service import AdminUserService

INVALID_FIELDS_MESSAGE = "Campos invalidos."
INTERNAL_ERROR_MESSAGE = "Error interno del servidor."
LIMIT_EXCEEDED_MESSAGE = "El parametro limit no puede superar 50."


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
            "message": LIMIT_EXCEEDED_MESSAGE,
        }), 400

    try:
        respuesta = AnuncioService.listar_anuncios_reportados(page, limit)
    except Exception:
        current_app.logger.exception("Error inesperado al listar anuncios reportados")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": INTERNAL_ERROR_MESSAGE,
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


def detalle_anuncio_reportado_controller(anuncio_id):
    try:
        anuncio_id_int = _parse_positive_int(anuncio_id, "anuncio_id")
        respuesta = AnuncioService.obtener_detalle_anuncio_reportado(anuncio_id_int)
    except ValueError as error:
        return jsonify({
            "success": False,
            "data": {},
            "error": "VALIDATION_ERROR",
            "message": str(error),
        }), 400
    except Exception:
        current_app.logger.exception("Error inesperado al obtener detalle de anuncio reportado")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": INTERNAL_ERROR_MESSAGE,
        }), 500

    return jsonify(respuesta), _status_for_admin_response(respuesta, success_status=200)


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
            "message": LIMIT_EXCEEDED_MESSAGE,
        }), 400

    try:
        respuesta = AnuncioService.listar_historial_moderacion(page, limit)
    except Exception:
        current_app.logger.exception("Error inesperado al obtener historial de moderacion")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": INTERNAL_ERROR_MESSAGE,
        }), 500

    return jsonify(respuesta), _status_for_admin_response(respuesta, success_status=200)


def listar_apelaciones_pendientes_controller():
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
            "message": LIMIT_EXCEEDED_MESSAGE,
        }), 400

    try:
        respuesta = AnuncioService.listar_apelaciones_pendientes(page, limit)
    except Exception:
        current_app.logger.exception("Error inesperado al listar apelaciones pendientes")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": INTERNAL_ERROR_MESSAGE,
        }), 500

    return jsonify(respuesta), _status_for_admin_response(respuesta, success_status=200)


def resolver_apelacion_controller(apelacion_id):
    schema = ResolverApelacionAdminSchema()
    request_data = request.get_json(silent=True) or {}

    try:
        apelacion_id_int = _parse_positive_int(apelacion_id, "apelacion_id")
        datos_validados = schema.load(request_data)
        admin_id = int(get_jwt_identity())
        respuesta = AnuncioService.resolver_apelacion_admin(
            apelacion_id_int,
            admin_id,
            datos_validados["decision"],
            datos_validados["motivo_admin"],
        )
    except ValidationError as error:
        return jsonify({
            "success": False,
            "data": error.messages,
            "error": "VALIDATION_ERROR",
            "message": INVALID_FIELDS_MESSAGE,
        }), 422
    except ValueError as error:
        return jsonify({
            "success": False,
            "data": {},
            "error": "VALIDATION_ERROR",
            "message": str(error),
        }), 400
    except Exception:
        current_app.logger.exception("Error inesperado al resolver apelacion")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": INTERNAL_ERROR_MESSAGE,
        }), 500

    return jsonify(respuesta), _status_for_admin_response(respuesta, success_status=200)


def listar_usuarios_admin_controller():
    schema = AdminUsuariosFiltroSchema()
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
            "message": LIMIT_EXCEEDED_MESSAGE,
        }), 400

    try:
        filtros = schema.load({
            "estado": request.args.get("estado"),
            "rol": request.args.get("rol"),
            "q": request.args.get("q"),
        })
        respuesta = AdminUserService.listar_usuarios(page, limit, **filtros)
    except ValidationError as error:
        return jsonify({
            "success": False,
            "data": error.messages,
            "error": "VALIDATION_ERROR",
            "message": "Parametros invalidos.",
        }), 422
    except Exception:
        current_app.logger.exception("Error inesperado al listar usuarios admin")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": INTERNAL_ERROR_MESSAGE,
        }), 500

    return jsonify(respuesta), _status_for_admin_response(respuesta, success_status=200)


def detalle_usuario_admin_controller(usuario_id):
    try:
        usuario_id_int = _parse_positive_int(usuario_id, "usuario_id")
        respuesta = AdminUserService.obtener_detalle_usuario(usuario_id_int)
    except ValueError as error:
        return jsonify({
            "success": False,
            "data": {},
            "error": "VALIDATION_ERROR",
            "message": str(error),
        }), 400
    except Exception:
        current_app.logger.exception("Error inesperado al obtener detalle de usuario admin")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": INTERNAL_ERROR_MESSAGE,
        }), 500

    return jsonify(respuesta), _status_for_admin_response(respuesta, success_status=200)


def activar_usuario_admin_controller(usuario_id):
    try:
        usuario_id_int = _parse_positive_int(usuario_id, "usuario_id")
        admin_id = int(get_jwt_identity())
        respuesta = AdminUserService.activar_usuario(usuario_id_int, admin_id)
    except ValueError as error:
        return jsonify({
            "success": False,
            "data": {},
            "error": "VALIDATION_ERROR",
            "message": str(error),
        }), 400
    except Exception:
        current_app.logger.exception("Error inesperado al activar usuario")
        return jsonify({
            "success": False,
            "data": {},
            "error": "INTERNAL_ERROR",
            "message": INTERNAL_ERROR_MESSAGE,
        }), 500

    return jsonify(respuesta), _status_for_admin_response(respuesta, success_status=200)


def rechazar_usuario_admin_controller(usuario_id):
    return _ejecutar_accion_admin_usuario(
        usuario_id,
        accion_service=AdminUserService.rechazar_tienda,
        log_message="Error inesperado al rechazar tienda",
    )


def bloquear_usuario_admin_controller(usuario_id):
    return _ejecutar_accion_admin_usuario(
        usuario_id,
        accion_service=AdminUserService.bloquear_usuario,
        log_message="Error inesperado al bloquear usuario",
    )


def desbloquear_usuario_admin_controller(usuario_id):
    return _ejecutar_accion_admin_usuario(
        usuario_id,
        accion_service=AdminUserService.desbloquear_usuario,
        log_message="Error inesperado al desbloquear usuario",
    )


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
            "message": INVALID_FIELDS_MESSAGE,
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
            "message": INTERNAL_ERROR_MESSAGE,
        }), 500

    return jsonify(respuesta), _status_for_admin_response(respuesta, success_status=200)


def _ejecutar_accion_admin_usuario(usuario_id, accion_service, log_message):
    request_data = request.get_json(silent=True) or {}
    schema = MotivoAdminUsuarioSchema()

    try:
        datos_validados = schema.load(request_data, unknown=RAISE)
        usuario_id_int = _parse_positive_int(usuario_id, "usuario_id")
        admin_id = int(get_jwt_identity())
        respuesta = accion_service(usuario_id_int, admin_id, datos_validados["motivo"])
    except ValidationError as error:
        return jsonify({
            "success": False,
            "data": error.messages,
            "error": "VALIDATION_ERROR",
            "message": INVALID_FIELDS_MESSAGE,
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
            "message": INTERNAL_ERROR_MESSAGE,
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

from math import ceil

from sqlalchemy.exc import SQLAlchemyError

from app.models.admin_log import AdminLog
from app.repositories.usuario_repository import UsuarioRepository


class AdminUserService:
    @staticmethod
    def listar_usuarios(page, limit, estado=None, rol=None, q=None):
        offset = (page - 1) * limit
        registros, total = UsuarioRepository.listar_usuarios_admin(
            estado=estado,
            rol=rol,
            q=q,
            offset=offset,
            limit=limit,
        )

        data = []
        for usuario, nombre_comercial, ruc in registros:
            data.append({
                "id": usuario.id,
                "nombre": usuario.nombre,
                "correo": usuario.correo,
                "telefono": usuario.telefono,
                "rol": usuario.rol,
                "estado": usuario.estado,
                "nombre_comercial": nombre_comercial,
                "ruc": ruc,
                "created_at": usuario.created_at.isoformat() if usuario.created_at else None,
            })

        total_paginas = ceil(total / limit) if total else 0
        return {
            "success": True,
            "data": data,
            "error": None,
            "message": "Usuarios obtenidos correctamente.",
            "paginacion": {
                "total": total,
                "pagina_actual": page,
                "total_paginas": total_paginas,
                "limit": limit,
                "tiene_siguiente": page < total_paginas,
                "tiene_anterior": page > 1 and total > 0,
            },
        }

    @staticmethod
    def obtener_detalle_usuario(usuario_id):
        registro = UsuarioRepository.buscar_usuario_admin_detalle(usuario_id)
        if not registro:
            return _error_response("NOT_FOUND", "Usuario no encontrado.")

        usuario, tienda = registro
        historial = UsuarioRepository.listar_historial_admin_usuario(usuario_id, limit=5)
        total_ventas = UsuarioRepository.contar_ventas(usuario_id)
        total_compras = UsuarioRepository.contar_compras(usuario_id)

        data = {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "correo": usuario.correo,
            "telefono": usuario.telefono,
            "rol": usuario.rol,
            "estado": usuario.estado,
            "miembro_desde": usuario.created_at.isoformat() if usuario.created_at else None,
            "reputacion_vendedor": {
                "calificacion_promedio": _float_or_none(usuario.calificacion_promedio_vendedor),
                "total_calificaciones": usuario.total_calificaciones_vendedor,
                "total_ventas": total_ventas,
            },
            "reputacion_comprador": {
                "calificacion_promedio": _float_or_none(usuario.calificacion_promedio_comprador),
                "total_calificaciones": usuario.total_calificaciones_comprador,
                "total_compras": total_compras,
            },
            "historial_admin": [
                {
                    "accion": item.accion,
                    "motivo": item.motivo,
                    "admin_id": item.admin_id,
                    "created_at": item.created_at.isoformat() if item.created_at else None,
                }
                for item in historial
            ],
        }

        if usuario.rol == "TIENDA_VERIFICADA" and tienda is not None:
            data["tienda"] = {
                "nombre_comercial": tienda.nombre_comercial,
                "ruc": tienda.ruc,
                "direccion": tienda.direccion,
                "documento_identidad": tienda.documento_identidad,
            }

        return {
            "success": True,
            "data": data,
            "error": None,
            "message": "Detalle de usuario obtenido correctamente.",
        }

    @staticmethod
    def activar_usuario(usuario_id, admin_id):
        registro = UsuarioRepository.buscar_usuario_admin_detalle(usuario_id)
        if not registro:
            return _error_response("NOT_FOUND", "Usuario no encontrado.")
        usuario, tienda = registro
        if usuario.estado != "EN_REVISION":
            return _error_response("CONFLICT", "El usuario no se encuentra en revision.")
        if usuario.rol != "TIENDA_VERIFICADA":
            return _error_response("VALIDATION_ERROR", "Solo una tienda en revision puede activarse.")

        try:
            usuario.estado = "ACTIVO"
            if tienda is not None:
                tienda.estado = "ACTIVO"
            log_entry = AdminLog(
                admin_id=admin_id,
                usuario_id=usuario_id,
                anuncio_id=None,
                accion="USUARIO_ACTIVADO",
                motivo=None,
            )
            UsuarioRepository.agregar_admin_log(log_entry)
            UsuarioRepository.commit()
            return {
                "success": True,
                "data": {
                    "usuario_id": usuario.id,
                    "nombre_comercial": tienda.nombre_comercial if tienda is not None else None,
                    "estado": usuario.estado,
                    "accion": "USUARIO_ACTIVADO",
                    "admin_id": admin_id,
                    "updated_at": usuario.updated_at.isoformat() if usuario.updated_at else None,
                },
                "error": None,
                "message": "Usuario activado correctamente.",
            }
        except SQLAlchemyError:
            UsuarioRepository.rollback()
            return _error_response("DATABASE_ERROR", "No se pudo activar el usuario.")

    @staticmethod
    def rechazar_tienda(usuario_id, admin_id, motivo):
        registro = UsuarioRepository.buscar_usuario_admin_detalle(usuario_id)
        if not registro:
            return _error_response("NOT_FOUND", "Usuario no encontrado.")
        usuario, tienda = registro
        if usuario.estado != "EN_REVISION":
            return _error_response("CONFLICT", "El usuario no se encuentra en revision.")
        if usuario.rol != "TIENDA_VERIFICADA":
            return _error_response("VALIDATION_ERROR", "Solo una tienda en revision puede rechazarse.")

        try:
            usuario.estado = "RECHAZADO"
            if tienda is not None:
                tienda.estado = "RECHAZADO"
            log_entry = AdminLog(
                admin_id=admin_id,
                usuario_id=usuario_id,
                anuncio_id=None,
                accion="TIENDA_RECHAZADA",
                motivo=motivo,
            )
            UsuarioRepository.agregar_admin_log(log_entry)
            UsuarioRepository.commit()
            return {
                "success": True,
                "data": {
                    "usuario_id": usuario.id,
                    "nombre_comercial": tienda.nombre_comercial if tienda is not None else None,
                    "estado": usuario.estado,
                    "motivo": motivo,
                    "accion": "TIENDA_RECHAZADA",
                    "admin_id": admin_id,
                    "updated_at": usuario.updated_at.isoformat() if usuario.updated_at else None,
                },
                "error": None,
                "message": "Tienda rechazada correctamente.",
            }
        except SQLAlchemyError:
            UsuarioRepository.rollback()
            return _error_response("DATABASE_ERROR", "No se pudo rechazar la tienda.")

    @staticmethod
    def bloquear_usuario(usuario_id, admin_id, motivo):
        registro = UsuarioRepository.buscar_usuario_admin_detalle(usuario_id)
        if not registro:
            return _error_response("NOT_FOUND", "Usuario no encontrado.")
        usuario, _ = registro
        if usuario.estado != "ACTIVO":
            return _error_response("CONFLICT", "Solo se puede bloquear un usuario activo.")
        if usuario.rol == "ADMIN":
            return _error_response("VALIDATION_ERROR", "No se puede bloquear a un administrador.")
        if usuario.id == admin_id:
            return _error_response("VALIDATION_ERROR", "No puedes bloquear tu propia cuenta.")

        try:
            usuario.estado = "BLOQUEADO"
            anuncios_desactivados = UsuarioRepository.desactivar_anuncios_activos_usuario(usuario_id)
            log_entry = AdminLog(
                admin_id=admin_id,
                usuario_id=usuario_id,
                anuncio_id=None,
                accion="USUARIO_BLOQUEADO",
                motivo=motivo,
            )
            UsuarioRepository.agregar_admin_log(log_entry)
            UsuarioRepository.commit()
            return {
                "success": True,
                "data": {
                    "usuario_id": usuario.id,
                    "nombre": usuario.nombre,
                    "estado": usuario.estado,
                    "anuncios_desactivados": anuncios_desactivados,
                    "motivo": motivo,
                    "accion": "USUARIO_BLOQUEADO",
                    "admin_id": admin_id,
                    "updated_at": usuario.updated_at.isoformat() if usuario.updated_at else None,
                },
                "error": None,
                "message": "Usuario bloqueado correctamente.",
            }
        except SQLAlchemyError:
            UsuarioRepository.rollback()
            return _error_response("DATABASE_ERROR", "No se pudo bloquear el usuario.")

    @staticmethod
    def desbloquear_usuario(usuario_id, admin_id, motivo):
        registro = UsuarioRepository.buscar_usuario_admin_detalle(usuario_id)
        if not registro:
            return _error_response("NOT_FOUND", "Usuario no encontrado.")
        usuario, _ = registro
        if usuario.estado != "BLOQUEADO":
            return _error_response("CONFLICT", "Solo se puede desbloquear un usuario bloqueado.")

        try:
            usuario.estado = "ACTIVO"
            log_entry = AdminLog(
                admin_id=admin_id,
                usuario_id=usuario_id,
                anuncio_id=None,
                accion="USUARIO_DESBLOQUEADO",
                motivo=motivo,
            )
            UsuarioRepository.agregar_admin_log(log_entry)
            UsuarioRepository.commit()
            return {
                "success": True,
                "data": {
                    "usuario_id": usuario.id,
                    "nombre": usuario.nombre,
                    "estado": usuario.estado,
                    "motivo": motivo,
                    "accion": "USUARIO_DESBLOQUEADO",
                    "admin_id": admin_id,
                    "updated_at": usuario.updated_at.isoformat() if usuario.updated_at else None,
                },
                "error": None,
                "message": "Usuario desbloqueado correctamente.",
            }
        except SQLAlchemyError:
            UsuarioRepository.rollback()
            return _error_response("DATABASE_ERROR", "No se pudo desbloquear el usuario.")


def _float_or_none(value):
    return float(value) if value is not None else None


def _error_response(error_code, message, data=None):
    return {
        "success": False,
        "data": data or {},
        "error": error_code,
        "message": message,
    }

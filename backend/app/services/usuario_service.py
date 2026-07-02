from app.repositories.usuario_repository import UsuarioRepository


MAX_ANUNCIOS_ACTIVOS_USER_ESTANDAR = 25


class UsuarioService:
    @staticmethod
    def obtener_perfil_publico(usuario_id):
        registro = UsuarioRepository.buscar_usuario_y_tienda(usuario_id)
        if not registro:
            return _error_response("NOT_FOUND", "Usuario no encontrado.")

        usuario, tienda = registro
        if usuario.estado != "ACTIVO":
            return _error_response("NOT_FOUND", "Usuario no encontrado.")

        anuncios_activos = UsuarioRepository.listar_anuncios_activos_publicos(usuario_id, limit=10)
        total_anuncios_activos = UsuarioRepository.contar_anuncios_activos(usuario_id)
        total_ventas = UsuarioRepository.contar_ventas(usuario_id)
        total_compras = UsuarioRepository.contar_compras(usuario_id)

        data = {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "es_tienda_verificada": usuario.rol == "TIENDA_VERIFICADA",
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
            "anuncios_activos": [
                {
                    "id": item.id,
                    "titulo": item.titulo,
                    "precio": float(item.precio) if hasattr(item.precio, "as_tuple") else item.precio,
                    "categoria": item.categoria,
                    "subcategoria": item.subcategoria,
                    "condicion": item.condicion,
                    "imagen_principal": item.imagen_principal,
                    "created_at": item.created_at.isoformat() if item.created_at else None,
                    "updated_at": item.updated_at.isoformat() if item.updated_at else None,
                }
                for item in anuncios_activos
            ],
            "total_anuncios_activos": total_anuncios_activos,
        }

        if usuario.rol == "TIENDA_VERIFICADA" and tienda is not None:
            data["tienda"] = {
                "nombre_comercial": tienda.nombre_comercial,
                "direccion": tienda.direccion,
            }

        return {
            "success": True,
            "data": data,
            "error": None,
            "message": "Perfil publico obtenido correctamente.",
        }

    @staticmethod
    def obtener_panel_usuario(usuario_id):
        registro = UsuarioRepository.buscar_usuario_y_tienda(usuario_id)
        if not registro:
            return _error_response("FORBIDDEN", "La cuenta debe estar activa para ver el panel.")

        usuario, tienda = registro
        if usuario.estado != "ACTIVO":
            return _error_response("FORBIDDEN", "La cuenta debe estar activa para ver el panel.")

        conteos = UsuarioRepository.contar_anuncios_por_estado(usuario_id)
        total_activos = conteos.get("ACTIVO", 0)
        total_inactivos = conteos.get("INACTIVO", 0)
        total_vendidos = conteos.get("VENDIDO", 0)
        total_ventas = UsuarioRepository.contar_ventas(usuario_id)
        total_compras = UsuarioRepository.contar_compras(usuario_id)
        calificaciones_pendientes = UsuarioRepository.contar_calificaciones_pendientes(usuario_id)

        perfil = {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "correo": usuario.correo,
            "telefono": usuario.telefono,
            "es_tienda_verificada": usuario.rol == "TIENDA_VERIFICADA",
            "estado": usuario.estado,
            "miembro_desde": usuario.created_at.isoformat() if usuario.created_at else None,
        }
        if usuario.rol == "TIENDA_VERIFICADA" and tienda is not None:
            perfil["tienda"] = {
                "nombre_comercial": tienda.nombre_comercial,
                "ruc": tienda.ruc,
                "direccion": tienda.direccion,
            }

        limite_maximo = None if usuario.rol == "TIENDA_VERIFICADA" else MAX_ANUNCIOS_ACTIVOS_USER_ESTANDAR
        disponibles = None if limite_maximo is None else max(0, limite_maximo - total_activos)

        return {
            "success": True,
            "data": {
                "perfil": perfil,
                "anuncios": {
                    "activos": {
                        "total": total_activos,
                        "limite_maximo": limite_maximo,
                        "disponibles": disponibles,
                    },
                    "inactivos": {
                        "total": total_inactivos,
                    },
                    "vendidos": {
                        "total": total_vendidos,
                    },
                },
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
                "calificaciones_pendientes": calificaciones_pendientes,
            },
            "error": None,
            "message": "Panel del usuario obtenido correctamente.",
        }


def _float_or_none(value):
    return float(value) if value is not None else None


def _error_response(error_code, message, data=None):
    return {
        "success": False,
        "data": data or {},
        "error": error_code,
        "message": message,
    }

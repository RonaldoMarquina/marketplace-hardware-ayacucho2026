import re
from datetime import UTC, datetime
from decimal import Decimal, ROUND_HALF_UP
from math import ceil

from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from app.models.calificacion import Calificacion
from app.repositories.transaccion_repository import TransaccionRepository


class TransaccionService:
    @staticmethod
    def calificar_vendedor(transaccion_id, usuario_id, puntaje, comentario):
        usuario = TransaccionRepository.buscar_usuario_por_id(usuario_id)
        if not usuario or usuario.estado != "ACTIVO":
            return _error_response("FORBIDDEN", "La cuenta debe estar activa para calificar transacciones.")

        transaccion = TransaccionRepository.buscar_transaccion_por_id(transaccion_id)
        if not transaccion:
            return _error_response("NOT_FOUND", "Transaccion no encontrada.")

        if transaccion.comprador_id != usuario_id:
            return _error_response("FORBIDDEN", "Solo el comprador de la transaccion puede calificar al vendedor.")

        if not transaccion.calificacion_vendedor_pending:
            return _error_response("CONFLICT", "El vendedor ya fue calificado en esta transaccion.")

        comentario_sanitizado = _sanitizar_comentario(comentario)
        created_at = _utcnow_naive()

        try:
            calificacion = Calificacion(
                transaccion_id=transaccion_id,
                calificador_id=usuario_id,
                calificado_id=transaccion.vendedor_id,
                tipo="COMPRADOR_A_VENDEDOR",
                puntaje=puntaje,
                comentario=comentario_sanitizado,
                created_at=created_at,
            )
            TransaccionRepository.agregar_calificacion(calificacion)
            transaccion.calificacion_vendedor_pending = False

            vendedor = TransaccionRepository.buscar_usuario_por_id(transaccion.vendedor_id)
            promedio, total = _recalcular_reputacion_desde_tabla(
                vendedor,
                tipo="COMPRADOR_A_VENDEDOR",
                promedio_attr="calificacion_promedio_vendedor",
                total_attr="total_calificaciones_vendedor",
            )

            TransaccionRepository.commit()
            current_app.logger.info(
                "HU-15 calificar_vendedor comprador_id=%s vendedor_id=%s transaccion_id=%s puntaje=%s",
                usuario_id,
                transaccion.vendedor_id,
                transaccion_id,
                puntaje,
            )
            return {
                "success": True,
                "data": {
                    "calificacion_id": calificacion.id,
                    "transaccion_id": transaccion_id,
                    "calificado": {
                        "id": vendedor.id,
                        "nombre": vendedor.nombre,
                        "es_tienda_verificada": vendedor.rol == "TIENDA_VERIFICADA",
                        "calificacion_promedio": promedio,
                        "total_calificaciones": total,
                    },
                    "puntaje": calificacion.puntaje,
                    "comentario": calificacion.comentario,
                    "created_at": calificacion.created_at.isoformat() if calificacion.created_at else None,
                },
                "error": None,
                "message": "Vendedor calificado correctamente.",
            }
        except SQLAlchemyError:
            TransaccionRepository.rollback()
            return _error_response("DATABASE_ERROR", "No se pudo registrar la calificacion.")

    @staticmethod
    def calificar_comprador(transaccion_id, usuario_id, puntaje, comentario):
        usuario = TransaccionRepository.buscar_usuario_por_id(usuario_id)
        if not usuario or usuario.estado != "ACTIVO":
            return _error_response("FORBIDDEN", "La cuenta debe estar activa para calificar transacciones.")

        transaccion = TransaccionRepository.buscar_transaccion_por_id(transaccion_id)
        if not transaccion:
            return _error_response("NOT_FOUND", "Transaccion no encontrada.")

        if transaccion.vendedor_id != usuario_id:
            return _error_response("FORBIDDEN", "Solo el vendedor de la transaccion puede calificar al comprador.")

        if not transaccion.calificacion_comprador_pending:
            return _error_response("CONFLICT", "El comprador ya fue calificado en esta transaccion.")

        comentario_sanitizado = _sanitizar_comentario(comentario)
        created_at = _utcnow_naive()

        try:
            calificacion = Calificacion(
                transaccion_id=transaccion_id,
                calificador_id=usuario_id,
                calificado_id=transaccion.comprador_id,
                tipo="VENDEDOR_A_COMPRADOR",
                puntaje=puntaje,
                comentario=comentario_sanitizado,
                created_at=created_at,
            )
            TransaccionRepository.agregar_calificacion(calificacion)
            transaccion.calificacion_comprador_pending = False

            comprador = TransaccionRepository.buscar_usuario_por_id(transaccion.comprador_id)
            promedio, total = _recalcular_reputacion_desde_tabla(
                comprador,
                tipo="VENDEDOR_A_COMPRADOR",
                promedio_attr="calificacion_promedio_comprador",
                total_attr="total_calificaciones_comprador",
            )

            TransaccionRepository.commit()
            current_app.logger.info(
                "HU-16 calificar_comprador vendedor_id=%s comprador_id=%s transaccion_id=%s puntaje=%s",
                usuario_id,
                transaccion.comprador_id,
                transaccion_id,
                puntaje,
            )
            return {
                "success": True,
                "data": {
                    "calificacion_id": calificacion.id,
                    "transaccion_id": transaccion_id,
                    "calificado": {
                        "id": comprador.id,
                        "nombre": comprador.nombre,
                        "es_tienda_verificada": comprador.rol == "TIENDA_VERIFICADA",
                        "calificacion_promedio": promedio,
                        "total_calificaciones": total,
                    },
                    "puntaje": calificacion.puntaje,
                    "comentario": calificacion.comentario,
                    "created_at": calificacion.created_at.isoformat() if calificacion.created_at else None,
                },
                "error": None,
                "message": "Comprador calificado correctamente.",
            }
        except SQLAlchemyError:
            TransaccionRepository.rollback()
            return _error_response("DATABASE_ERROR", "No se pudo registrar la calificacion.")

    @staticmethod
    def obtener_historial_usuario(usuario_id, tipo, page, limit):
        usuario = TransaccionRepository.buscar_usuario_por_id(usuario_id)
        if not usuario or usuario.estado != "ACTIVO":
            return _error_response("FORBIDDEN", "La cuenta debe estar activa para ver transacciones.")

        offset = (page - 1) * limit
        registros, total = TransaccionRepository.listar_historial_usuario(usuario_id, tipo, offset, limit)
        total_ventas = TransaccionRepository.contar_ventas_usuario(usuario_id)
        total_compras = TransaccionRepository.contar_compras_usuario(usuario_id)
        calificaciones_pendientes = TransaccionRepository.contar_calificaciones_pendientes_usuario(usuario_id)

        data = []
        for (
            transaccion,
            anuncio_titulo,
            anuncio_categoria,
            anuncio_subcategoria,
            anuncio_precio,
            imagen_principal,
            vendedor_public_id,
            vendedor_nombre,
            vendedor_rol,
            comprador_public_id,
            comprador_nombre,
            comprador_rol,
            calificacion_puntaje,
            calificacion_comentario,
            calificacion_created_at,
        ) in registros:
            es_venta = transaccion.vendedor_id == usuario_id
            contraparte_id = comprador_public_id if es_venta else vendedor_public_id
            contraparte_nombre = comprador_nombre if es_venta else vendedor_nombre
            contraparte_rol = comprador_rol if es_venta else vendedor_rol
            calificacion_pendiente = (
                transaccion.calificacion_comprador_pending
                if es_venta
                else transaccion.calificacion_vendedor_pending
            )

            data.append({
                "transaccion_id": transaccion.id,
                "tipo": "venta" if es_venta else "compra",
                "anuncio": {
                    "id": transaccion.anuncio_id,
                    "titulo": anuncio_titulo,
                    "categoria": anuncio_categoria,
                    "subcategoria": anuncio_subcategoria,
                    "imagen_principal": imagen_principal,
                },
                "contraparte": {
                    "id": contraparte_id,
                    "nombre": contraparte_nombre,
                    "es_tienda_verificada": contraparte_rol == "TIENDA_VERIFICADA",
                },
                "monto": float(anuncio_precio) if hasattr(anuncio_precio, "as_tuple") else anuncio_precio,
                "created_at": transaccion.created_at.isoformat() if transaccion.created_at else None,
                "calificacion_pendiente": bool(calificacion_pendiente),
                "calificacion_emitida": (
                    {
                        "puntaje": calificacion_puntaje,
                        "comentario": calificacion_comentario,
                        "created_at": calificacion_created_at.isoformat() if calificacion_created_at else None,
                    }
                    if calificacion_puntaje is not None
                    else None
                ),
            })

        total_paginas = ceil(total / limit) if total else 0
        return {
            "success": True,
            "data": data,
            "error": None,
            "message": "Historial de transacciones obtenido correctamente.",
            "resumen": {
                "total_ventas": total_ventas,
                "total_compras": total_compras,
                "calificaciones_pendientes": calificaciones_pendientes,
            },
            "paginacion": {
                "total": total,
                "pagina_actual": page,
                "total_paginas": total_paginas,
                "limit": limit,
                "tiene_siguiente": page < total_paginas,
                "tiene_anterior": page > 1 and total > 0,
            },
        }


def _recalcular_reputacion_desde_tabla(usuario, tipo, promedio_attr, total_attr):
    promedio_db, total = TransaccionRepository.obtener_resumen_calificaciones(usuario.id, tipo)
    promedio = None
    if total:
        promedio = Decimal(str(promedio_db)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    setattr(usuario, promedio_attr, promedio)
    setattr(usuario, total_attr, total)
    return (float(promedio) if promedio is not None else None), total


def _sanitizar_comentario(comentario):
    if comentario is None:
        return None

    sin_tags = re.sub(r"<[^>]*>", "", comentario)
    sin_control = "".join(char for char in sin_tags if char >= " " or char in "\n\t")
    limpio = sin_control.strip()
    return limpio or None


def _utcnow_naive():
    return datetime.now(UTC).replace(tzinfo=None)


def _error_response(error_code, message, data=None):
    return {
        "success": False,
        "data": data or {},
        "error": error_code,
        "message": message,
    }

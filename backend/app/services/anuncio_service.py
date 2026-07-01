from copy import deepcopy
from datetime import UTC, datetime, timedelta
from math import ceil
from pathlib import Path
import threading
from urllib.parse import quote
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from flask import current_app
from sqlalchemy import String, cast, func, or_
from sqlalchemy.exc import SQLAlchemyError

from app.models.anuncio import SUBCATEGORIAS_POR_CATEGORIA, Anuncio
from app.models.contacto_log import ContactoLog
from app.models.media_anuncio import MediaAnuncio
from app.models.moderacion_log import ModeracionLog
from app.models.reporte import Reporte
from app.repositories.anuncio_repository import AnuncioRepository
from app.utils.media_validation import MediaValidationError, classify_media, validate_and_store_media


EDITABLE_FIELDS = {
    "titulo",
    "categoria",
    "subcategoria",
    "descripcion",
    "condicion",
    "precio",
    "especificaciones",
}

MAX_REACTIVACIONES = 3
MAX_ANUNCIOS_ACTIVOS_USER_ESTANDAR = 25
MAX_IMAGENES_POR_ANUNCIO = 8
MAX_VIDEOS_POR_ANUNCIO = 1
MAX_CONTACTOS_DIARIOS = 20
CONTACTO_RETRY_MINUTES = 60
MAX_REPORTES_DIARIOS = 10
try:
    PERU_TIMEZONE = ZoneInfo("America/Lima")
except ZoneInfoNotFoundError:
    PERU_TIMEZONE = None
ORDER_BY_BUSQUEDA = {
    "reciente": (Anuncio.created_at.desc(), Anuncio.id.desc()),
    "precio_asc": (Anuncio.precio.asc(), Anuncio.id.desc()),
    "precio_desc": (Anuncio.precio.desc(), Anuncio.id.desc()),
}


class AnuncioService:
    @staticmethod
    def obtener_feed_publico(page, limit):
        offset = (page - 1) * limit
        total = AnuncioRepository.contar_anuncios_publicos()
        registros = AnuncioRepository.listar_feed_publico(offset, limit)

        data = []
        for item in registros:
            precio = item.precio
            if hasattr(precio, "as_tuple"):
                precio = float(precio)

            data.append({
                "id": item.id,
                "titulo": item.titulo,
                "precio": precio,
                "categoria": item.categoria,
                "subcategoria": item.subcategoria,
                "condicion": item.condicion,
                "imagen_principal": item.imagen_principal,
                "vendedor_nombre": item.vendedor_nombre,
                "es_tienda_verificada": item.vendedor_rol == "TIENDA_VERIFICADA",
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None,
            })

        total_paginas = ceil(total / limit) if total else 0
        return {
            "data": data,
            "paginacion": {
                "total": total,
                "pagina_actual": page,
                "total_paginas": total_paginas,
                "limit": limit,
                "tiene_siguiente": page < total_paginas,
                "tiene_anterior": page > 1,
            },
        }

    @staticmethod
    def buscar_anuncios_publicos(filters):
        page = filters["page"]
        limit = filters["limit"]
        offset = (page - 1) * limit

        query = AnuncioRepository.construir_query_publica_base()

        if filters.get("categoria"):
            query = query.filter(Anuncio.categoria == filters["categoria"])

        if filters.get("subcategoria"):
            query = query.filter(func.lower(Anuncio.subcategoria) == filters["subcategoria"].lower())

        if filters.get("condicion"):
            query = query.filter(Anuncio.condicion == filters["condicion"])

        if filters.get("precio_min") is not None:
            query = query.filter(Anuncio.precio >= filters["precio_min"])

        if filters.get("precio_max") is not None:
            query = query.filter(Anuncio.precio <= filters["precio_max"])

        for spec_key, spec_value in filters.get("specs", {}).items():
            query = query.filter(_build_spec_filter(spec_key, spec_value))

        if filters.get("q"):
            pattern = f"%{_escape_like(filters['q'].lower())}%"
            query = query.filter(or_(
                func.lower(Anuncio.titulo).like(pattern, escape="\\"),
                func.lower(Anuncio.descripcion).like(pattern, escape="\\"),
                func.lower(Anuncio.subcategoria).like(pattern, escape="\\"),
            ))

        query = query.order_by(*ORDER_BY_BUSQUEDA[filters["order_by"]])
        total = AnuncioRepository.contar_query_publica(query)
        registros = AnuncioRepository.listar_query_publica(query, offset, limit)

        data = [_serialize_public_listing(item) for item in registros]
        total_paginas = ceil(total / limit) if total else 0
        return {
            "data": data,
            "filtros_aplicados": _build_applied_filters(filters),
            "paginacion": {
                "total": total,
                "pagina_actual": page,
                "total_paginas": total_paginas,
                "limit": limit,
                "tiene_siguiente": page < total_paginas,
                "tiene_anterior": page > 1,
            },
        }

    @staticmethod
    def obtener_detalle_anuncio(anuncio_id, viewer_user_id=None):
        detalle = AnuncioRepository.buscar_detalle_anuncio(anuncio_id)
        if not detalle:
            return _error_response("NOT_FOUND", "Anuncio no encontrado.")

        anuncio, vendedor, tienda = detalle
        es_propietario = viewer_user_id == anuncio.usuario_id if viewer_user_id is not None else False

        if anuncio.estado != "ACTIVO":
            if not es_propietario or anuncio.estado in {"VENDIDO", "BLOQUEADO"}:
                return _error_response("NOT_FOUND", "Anuncio no encontrado.")

        media = AnuncioRepository.listar_media_detalle(anuncio_id)
        current_app.logger.info(
            "HU-11 detalle anuncio_id=%s viewer=%s",
            anuncio_id,
            "autenticado" if viewer_user_id is not None else "visitante",
        )
        return {
            "success": True,
            "data": _serialize_detail_listing(
                anuncio=anuncio,
                vendedor=vendedor,
                tienda=tienda,
                media=media,
                viewer_user_id=viewer_user_id,
                es_propietario=es_propietario,
            ),
            "error": None,
            "message": "Detalle de anuncio obtenido correctamente.",
        }

    @staticmethod
    def obtener_contacto_whatsapp(anuncio_id, comprador_id):
        comprador = AnuncioRepository.buscar_usuario_por_id(comprador_id)
        if not comprador:
            return _error_response("NOT_FOUND", "Usuario no encontrado.")

        permiso_error = _validar_estado_comprador_contacto(comprador)
        if permiso_error:
            return permiso_error

        anuncio = AnuncioRepository.buscar_anuncio_por_id(anuncio_id)
        if not anuncio or anuncio.estado != "ACTIVO":
            return _error_response("NOT_FOUND", "Anuncio no encontrado.")

        if comprador.id == anuncio.usuario_id:
            return _error_response("CONFLICT", "No puedes contactarte a ti mismo por este anuncio.")

        vendedor = AnuncioRepository.buscar_usuario_por_id(anuncio.usuario_id)
        if not vendedor or not vendedor.telefono:
            return _error_response("SELLER_WITHOUT_PHONE", "El vendedor no tiene telefono registrado.")

        ahora_local = _now_local_naive()
        day_start = ahora_local.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        contactos_hoy = AnuncioRepository.contar_contactos_distintos_hoy(comprador.id, day_start, day_end)
        if contactos_hoy >= MAX_CONTACTOS_DIARIOS:
            return {
                "success": False,
                "data": {
                    "disponible_en": day_end.isoformat(),
                },
                "error": "RATE_LIMIT_DIARIO",
                "message": f"Alcanzaste el limite de {MAX_CONTACTOS_DIARIOS} contactos por dia.",
            }

        ultimo_contacto = AnuncioRepository.buscar_ultimo_contacto_anuncio(comprador.id, anuncio.id)
        if ultimo_contacto and ultimo_contacto.created_at > ahora_local - timedelta(minutes=CONTACTO_RETRY_MINUTES):
            disponible_en = ultimo_contacto.created_at + timedelta(minutes=CONTACTO_RETRY_MINUTES)
            return {
                "success": False,
                "data": {
                    "disponible_en": disponible_en.isoformat(),
                },
                "error": "RATE_LIMIT_ANUNCIO",
                "message": "Ya contactaste este anuncio recientemente. Intenta en 1 hora.",
            }

        titulo_sanitizado = _sanitize_contact_title(anuncio.titulo)
        mensaje = (
            f'Hola, vi tu anuncio "{titulo_sanitizado}" en HardwareAyacucho y me interesa. '
            "¿Sigue disponible?"
        )
        mensaje_codificado = quote(mensaje, safe="")
        whatsapp_url = f"https://wa.me/51{vendedor.telefono}?text={mensaje_codificado}"

        AnuncioService._registrar_contacto_async(
            comprador_id=comprador.id,
            vendedor_id=vendedor.id,
            anuncio_id=anuncio.id,
            created_at=ahora_local,
        )
        return {
            "success": True,
            "data": {
                "whatsapp_url": whatsapp_url,
                "vendedor_nombre": vendedor.nombre,
                "anuncio_titulo": anuncio.titulo,
            },
            "error": None,
            "message": "Contacto generado correctamente.",
        }

    @staticmethod
    def publicar_anuncio(usuario_id, data):
        # El usuario_id viene del JWT, nunca del body. Esta regla evita que un
        # cliente publique anuncios a nombre de otra cuenta.
        usuario = AnuncioRepository.buscar_usuario_por_id(usuario_id)
        if not usuario:
            return _error_response("NOT_FOUND", "Usuario no encontrado.")

        if usuario.estado != "ACTIVO":
            return _error_response("FORBIDDEN", "La cuenta debe estar activa para publicar anuncios.")

        if usuario.rol == "TIENDA_VERIFICADA":
            tienda = getattr(usuario, "tienda", None)
            if tienda and tienda.estado != "ACTIVO":
                return _error_response("FORBIDDEN", "La tienda debe estar activa para publicar anuncios.")

        if usuario.rol == "USER_ESTANDAR":
            activos = AnuncioRepository.contar_anuncios_activos(usuario.id)
            if activos >= MAX_ANUNCIOS_ACTIVOS_USER_ESTANDAR:
                return _error_response(
                    "FORBIDDEN",
                    f"El usuario estandar alcanzo el limite de {MAX_ANUNCIOS_ACTIVOS_USER_ESTANDAR} anuncios activos.",
                )

        anuncio = Anuncio(
            usuario_id=usuario.id,
            titulo=data["titulo"],
            descripcion=data["descripcion"],
            categoria=data["categoria"],
            subcategoria=data["subcategoria"],
            condicion=data["condicion"],
            precio=data["precio"],
            especificaciones=data.get("especificaciones"),
            estado="ACTIVO",
            reactivaciones_count=0,
        )

        try:
            AnuncioRepository.agregar(anuncio)
            AnuncioRepository.commit()
            return {
                "success": True,
                "data": anuncio.to_public_dict(),
                "error": None,
                "message": "Anuncio publicado correctamente.",
            }
        except SQLAlchemyError:
            AnuncioRepository.rollback()
            return _error_response("DATABASE_ERROR", "No se pudo publicar el anuncio.")

    @staticmethod
    def editar_anuncio(anuncio_id, usuario_id, data):
        anuncio = AnuncioRepository.buscar_anuncio_por_id(anuncio_id)
        if not anuncio:
            return _error_response("NOT_FOUND", "Anuncio no encontrado.")

        ownership_error = _validar_propietario(anuncio, usuario_id)
        if ownership_error:
            return ownership_error

        status_error = _validar_estado_edicion(anuncio)
        if status_error:
            return status_error

        cambios = {campo: valor for campo, valor in data.items() if campo in EDITABLE_FIELDS}
        if not cambios:
            return _error_response("EMPTY_BODY", "Debe enviar al menos un campo editable.")

        if "categoria" in cambios and "subcategoria" not in cambios:
            return _error_response(
                "VALIDATION_ERROR",
                "La categoria requiere subcategoria en el mismo request.",
                {"subcategoria": ["La subcategoria es obligatoria al cambiar categoria."]},
            )

        categoria_objetivo = cambios.get("categoria", anuncio.categoria)
        subcategoria_objetivo = cambios.get("subcategoria", anuncio.subcategoria)
        if "subcategoria" in cambios and subcategoria_objetivo not in SUBCATEGORIAS_POR_CATEGORIA.get(categoria_objetivo, ()):
            return _error_response(
                "VALIDATION_ERROR",
                "La subcategoria no corresponde a la categoria seleccionada.",
                {"subcategoria": ["La subcategoria no corresponde a la categoria seleccionada."]},
            )

        if "especificaciones" in cambios:
            cambios["especificaciones"] = _json_merge_patch(anuncio.especificaciones, cambios["especificaciones"])

        try:
            campos_modificados = []
            for campo, valor in cambios.items():
                setattr(anuncio, campo, valor)
                campos_modificados.append(campo)

            AnuncioRepository.commit()
            current_app.logger.info(
                "HU-07 editar anuncio usuario_id=%s anuncio_id=%s campos=%s",
                usuario_id,
                anuncio_id,
                ",".join(campos_modificados),
            )
            return {
                "success": True,
                "data": anuncio.to_public_dict(),
                "error": None,
                "message": "Anuncio actualizado correctamente.",
            }
        except SQLAlchemyError:
            AnuncioRepository.rollback()
            return _error_response("DATABASE_ERROR", "No se pudo actualizar el anuncio.")

    @staticmethod
    def marcar_anuncio_vendido(anuncio_id, usuario_id):
        anuncio = AnuncioRepository.buscar_anuncio_por_id(anuncio_id)
        if not anuncio:
            return _error_response("NOT_FOUND", "Anuncio no encontrado.")

        ownership_error = _validar_propietario(anuncio, usuario_id)
        if ownership_error:
            return ownership_error

        status_error = _validar_estado_para_vendido(anuncio)
        if status_error:
            return status_error

        estado_anterior = anuncio.estado
        try:
            anuncio.estado = "VENDIDO"
            AnuncioRepository.commit()
            current_app.logger.info(
                "HU-08 cambio_estado usuario_id=%s anuncio_id=%s estado_anterior=%s estado_nuevo=%s",
                usuario_id,
                anuncio_id,
                estado_anterior,
                anuncio.estado,
            )
            return {
                "success": True,
                "data": {
                    "id": anuncio.id,
                    "estado": anuncio.estado,
                    "updated_at": anuncio.updated_at.isoformat() if anuncio.updated_at else None,
                },
                "error": None,
                "message": "Tu anuncio ha sido marcado como vendido exitosamente.",
            }
        except SQLAlchemyError:
            AnuncioRepository.rollback()
            return _error_response("DATABASE_ERROR", "No se pudo marcar el anuncio como vendido.")

    @staticmethod
    def desactivar_anuncio(anuncio_id, usuario_id):
        anuncio = AnuncioRepository.buscar_anuncio_por_id(anuncio_id)
        if not anuncio:
            return _error_response("NOT_FOUND", "Anuncio no encontrado.")

        ownership_error = _validar_propietario(anuncio, usuario_id)
        if ownership_error:
            return ownership_error

        status_error = _validar_estado_para_desactivar(anuncio)
        if status_error:
            return status_error

        estado_anterior = anuncio.estado
        try:
            anuncio.estado = "INACTIVO"
            AnuncioRepository.commit()
            current_app.logger.info(
                "HU-08 cambio_estado usuario_id=%s anuncio_id=%s estado_anterior=%s estado_nuevo=%s",
                usuario_id,
                anuncio_id,
                estado_anterior,
                anuncio.estado,
            )
            return {
                "success": True,
                "data": {
                    "id": anuncio.id,
                    "estado": anuncio.estado,
                    "updated_at": anuncio.updated_at.isoformat() if anuncio.updated_at else None,
                },
                "error": None,
                "message": "Anuncio desactivado correctamente.",
            }
        except SQLAlchemyError:
            AnuncioRepository.rollback()
            return _error_response("DATABASE_ERROR", "No se pudo desactivar el anuncio.")

    @staticmethod
    def reactivar_anuncio(anuncio_id, usuario_id):
        anuncio = AnuncioRepository.buscar_anuncio_por_id(anuncio_id)
        if not anuncio:
            return _error_response("NOT_FOUND", "Anuncio no encontrado.")

        ownership_error = _validar_propietario(anuncio, usuario_id)
        if ownership_error:
            return ownership_error

        status_error = _validar_estado_para_reactivar(anuncio)
        if status_error:
            return status_error

        usuario = AnuncioRepository.buscar_usuario_por_id(usuario_id)
        if usuario and usuario.rol == "USER_ESTANDAR":
            activos = AnuncioRepository.contar_anuncios_activos(usuario_id)
            if activos >= MAX_ANUNCIOS_ACTIVOS_USER_ESTANDAR:
                return _error_response(
                    "FORBIDDEN",
                    f"El usuario estandar alcanzo el limite de {MAX_ANUNCIOS_ACTIVOS_USER_ESTANDAR} anuncios activos.",
                )

        if anuncio.reactivaciones_count >= MAX_REACTIVACIONES:
            return _error_response("FORBIDDEN", "El anuncio alcanzo el limite de 3 reactivaciones.")

        estado_anterior = anuncio.estado
        try:
            anuncio.estado = "ACTIVO"
            anuncio.reactivaciones_count += 1
            AnuncioRepository.commit()
            current_app.logger.info(
                "HU-08 cambio_estado usuario_id=%s anuncio_id=%s estado_anterior=%s estado_nuevo=%s reactivaciones_count=%s",
                usuario_id,
                anuncio_id,
                estado_anterior,
                anuncio.estado,
                anuncio.reactivaciones_count,
            )
            return {
                "success": True,
                "data": {
                    "id": anuncio.id,
                    "estado": anuncio.estado,
                    "reactivaciones_count": anuncio.reactivaciones_count,
                    "reactivaciones_restantes": MAX_REACTIVACIONES - anuncio.reactivaciones_count,
                    "updated_at": anuncio.updated_at.isoformat() if anuncio.updated_at else None,
                },
                "error": None,
                "message": "Anuncio reactivado correctamente.",
            }
        except SQLAlchemyError:
            AnuncioRepository.rollback()
            return _error_response("DATABASE_ERROR", "No se pudo reactivar el anuncio.")

    @staticmethod
    def reportar_anuncio(anuncio_id, comprador_id, motivo):
        usuario = AnuncioRepository.buscar_usuario_por_id(comprador_id)
        if not usuario or usuario.estado != "ACTIVO":
            return _error_response("FORBIDDEN", "La cuenta debe estar activa para reportar anuncios.")

        anuncio = AnuncioRepository.buscar_anuncio_por_id(anuncio_id)
        if not anuncio or anuncio.estado != "ACTIVO":
            return _error_response("NOT_FOUND", "Anuncio no encontrado.")

        if anuncio.usuario_id == comprador_id:
            return _error_response("CONFLICT", "No puedes reportar tu propio anuncio.")

        ultimo_desbloqueo = AnuncioRepository.buscar_ultimo_desbloqueo_anuncio(anuncio_id)
        created_at_min = ultimo_desbloqueo.created_at if ultimo_desbloqueo else None
        reporte_duplicado = AnuncioRepository.buscar_reporte_duplicado_en_ciclo(
            comprador_id,
            anuncio_id,
            created_at_min=created_at_min,
        )
        if reporte_duplicado:
            return _error_response(
                "CONFLICT",
                "Ya reportaste este anuncio en su ciclo activo actual.",
            )

        day_start, day_end = _day_bounds_peru()
        reportes_hoy = AnuncioRepository.contar_reportes_usuario_hoy(comprador_id, day_start, day_end)
        if reportes_hoy >= MAX_REPORTES_DIARIOS:
            return _error_response(
                "RATE_LIMIT_REPORTES",
                "Alcanzaste el limite de 10 reportes por dia.",
                {"disponible_en": day_end.isoformat()},
            )

        try:
            reporte = Reporte(
                comprador_id=comprador_id,
                anuncio_id=anuncio_id,
                motivo=motivo,
                estado="PENDIENTE",
                created_at=_utcnow_naive(),
            )
            AnuncioRepository.agregar_reporte(reporte)
            AnuncioRepository.commit()
            return {
                "success": True,
                "data": {
                    "reporte_id": reporte.id,
                    "anuncio_id": anuncio_id,
                    "motivo": reporte.motivo,
                    "estado": reporte.estado,
                    "created_at": reporte.created_at.isoformat() if reporte.created_at else None,
                },
                "error": None,
                "message": "Reporte registrado correctamente.",
            }
        except SQLAlchemyError:
            AnuncioRepository.rollback()
            return _error_response("DATABASE_ERROR", "No se pudo registrar el reporte.")

    @staticmethod
    def listar_anuncios_reportados(page, limit):
        offset = (page - 1) * limit
        registros, total = AnuncioRepository.listar_anuncios_reportados(offset, limit)

        data = []
        for item in registros:
            data.append({
                "anuncio_id": item.anuncio_id,
                "titulo": item.titulo,
                "categoria": item.categoria,
                "subcategoria": item.subcategoria,
                "estado_anuncio": item.estado_anuncio,
                "vendedor_id": item.vendedor_id,
                "vendedor_nombre": item.vendedor_nombre,
                "es_tienda_verificada": item.vendedor_rol == "TIENDA_VERIFICADA",
                "total_reportes": item.total_reportes,
                "motivos": item.motivos.split(",") if item.motivos else [],
                "ultimo_reporte": item.ultimo_reporte.isoformat() if item.ultimo_reporte else None,
            })

        total_paginas = ceil(total / limit) if total else 0
        return {
            "success": True,
            "data": data,
            "error": None,
            "message": "Anuncios reportados obtenidos correctamente.",
            "total_pendientes": total,
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
    def bloquear_anuncio_admin(anuncio_id, admin_id, motivo_admin):
        anuncio = AnuncioRepository.buscar_anuncio_por_id(anuncio_id)
        if not anuncio:
            return _error_response("NOT_FOUND", "Anuncio no encontrado.")
        if anuncio.estado != "ACTIVO":
            return _error_response("CONFLICT", "Solo se puede bloquear un anuncio activo.")

        try:
            anuncio.estado = "BLOQUEADO"
            AnuncioRepository.marcar_reportes_revisados(anuncio_id)
            log_entry = ModeracionLog(
                admin_id=admin_id,
                anuncio_id=anuncio_id,
                accion="BLOQUEADO",
                motivo_admin=motivo_admin,
                created_at=_utcnow_naive(),
            )
            AnuncioRepository.agregar_moderacion_log(log_entry)
            AnuncioRepository.commit()
            return {
                "success": True,
                "data": {
                    "anuncio_id": anuncio.id,
                    "estado": anuncio.estado,
                    "motivo_admin": motivo_admin,
                    "admin_id": admin_id,
                    "updated_at": anuncio.updated_at.isoformat() if anuncio.updated_at else None,
                },
                "error": None,
                "message": "Anuncio bloqueado correctamente.",
            }
        except SQLAlchemyError:
            AnuncioRepository.rollback()
            return _error_response("DATABASE_ERROR", "No se pudo bloquear el anuncio.")

    @staticmethod
    def desbloquear_anuncio_admin(anuncio_id, admin_id, motivo_admin):
        anuncio = AnuncioRepository.buscar_anuncio_por_id(anuncio_id)
        if not anuncio:
            return _error_response("NOT_FOUND", "Anuncio no encontrado.")
        if anuncio.estado != "BLOQUEADO":
            return _error_response("CONFLICT", "Solo se puede desbloquear un anuncio bloqueado.")

        try:
            anuncio.estado = "ACTIVO"
            log_entry = ModeracionLog(
                admin_id=admin_id,
                anuncio_id=anuncio_id,
                accion="DESBLOQUEADO",
                motivo_admin=motivo_admin,
                created_at=_utcnow_naive(),
            )
            AnuncioRepository.agregar_moderacion_log(log_entry)
            AnuncioRepository.commit()
            return {
                "success": True,
                "data": {
                    "anuncio_id": anuncio.id,
                    "estado": anuncio.estado,
                    "motivo_admin": motivo_admin,
                    "admin_id": admin_id,
                    "updated_at": anuncio.updated_at.isoformat() if anuncio.updated_at else None,
                },
                "error": None,
                "message": "Anuncio desbloqueado correctamente.",
            }
        except SQLAlchemyError:
            AnuncioRepository.rollback()
            return _error_response("DATABASE_ERROR", "No se pudo desbloquear el anuncio.")

    @staticmethod
    def listar_historial_moderacion(page, limit):
        offset = (page - 1) * limit
        registros, total = AnuncioRepository.listar_historial_moderacion(offset, limit)

        data = []
        for log_entry, admin_nombre, anuncio_titulo in registros:
            data.append({
                "id": log_entry.id,
                "admin_id": log_entry.admin_id,
                "admin_nombre": admin_nombre,
                "anuncio_id": log_entry.anuncio_id,
                "anuncio_titulo": anuncio_titulo,
                "accion": log_entry.accion,
                "motivo_admin": log_entry.motivo_admin,
                "created_at": log_entry.created_at.isoformat() if log_entry.created_at else None,
            })

        total_paginas = ceil(total / limit) if total else 0
        return {
            "success": True,
            "data": data,
            "error": None,
            "message": "Historial de moderacion obtenido correctamente.",
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
    def subir_media(anuncio_id, usuario_id, files, upload_folder):
        anuncio = AnuncioRepository.buscar_anuncio_por_id(anuncio_id)
        if not anuncio:
            return _error_response("NOT_FOUND", "Anuncio no encontrado.")

        ownership_error = _validar_propietario(anuncio, usuario_id)
        if ownership_error:
            return ownership_error

        status_error = _validar_estado_operacion_media(anuncio)
        if status_error:
            return status_error

        archivos = [file for file in files if file and file.filename]
        if not archivos:
            return _error_response("MISSING_FILE", "Debe adjuntar al menos un archivo.")

        try:
            tipos = [classify_media(file)[0] for file in archivos]
        except MediaValidationError as error:
            return _media_error_response(error)

        imagenes_request = tipos.count("imagen")
        videos_request = tipos.count("video")
        if imagenes_request > MAX_IMAGENES_POR_ANUNCIO:
            return _error_response(
                "TOO_MANY_FILES",
                f"No se permiten mas de {MAX_IMAGENES_POR_ANUNCIO} imagenes por peticion.",
            )
        if videos_request > MAX_VIDEOS_POR_ANUNCIO:
            return _error_response(
                "TOO_MANY_FILES",
                f"No se permite mas de {MAX_VIDEOS_POR_ANUNCIO} video por peticion.",
            )

        imagenes_existentes = AnuncioRepository.contar_media(anuncio_id, "imagen")
        videos_existentes = AnuncioRepository.contar_media(anuncio_id, "video")
        if imagenes_existentes + imagenes_request > MAX_IMAGENES_POR_ANUNCIO:
            return _error_response(
                "CONFLICT",
                f"El anuncio ya alcanzo el limite de {MAX_IMAGENES_POR_ANUNCIO} imagenes.",
            )
        if videos_existentes + videos_request > MAX_VIDEOS_POR_ANUNCIO:
            return _error_response("CONFLICT", "El anuncio ya tiene un video registrado.")

        media_creada = []
        archivos_guardados = []
        siguiente_orden = AnuncioRepository.obtener_siguiente_orden_imagen(anuncio_id)
        primera_imagen = imagenes_existentes == 0

        try:
            for file in archivos:
                tipo_media, ruta_relativa, ruta_absoluta = validate_and_store_media(
                    file,
                    upload_folder,
                    anuncio_id,
                )
                archivos_guardados.append(ruta_absoluta)

                es_imagen = tipo_media == "imagen"
                media = MediaAnuncio(
                    anuncio_id=anuncio_id,
                    tipo_media=tipo_media,
                    ruta_relativa=ruta_relativa,
                    es_principal=bool(es_imagen and primera_imagen),
                    orden=siguiente_orden if es_imagen else None,
                )
                AnuncioRepository.agregar_media(media)
                media_creada.append(media)

                if es_imagen:
                    primera_imagen = False
                    siguiente_orden += 1

            AnuncioRepository.commit()
            return {
                "success": True,
                "data": {"media": [media.to_public_dict() for media in media_creada]},
                "error": None,
                "message": "Media cargada correctamente.",
            }
        except MediaValidationError as error:
            AnuncioRepository.rollback()
            _eliminar_archivos(archivos_guardados)
            return _media_error_response(error)
        except SQLAlchemyError:
            AnuncioRepository.rollback()
            _eliminar_archivos(archivos_guardados)
            return _error_response("DATABASE_ERROR", "No se pudo registrar la media del anuncio.")

    @staticmethod
    def reordenar_media(anuncio_id, usuario_id, ordered_media_ids):
        anuncio = AnuncioRepository.buscar_anuncio_por_id(anuncio_id)
        if not anuncio:
            return _error_response("NOT_FOUND", "Anuncio no encontrado.")

        ownership_error = _validar_propietario(anuncio, usuario_id)
        if ownership_error:
            return ownership_error

        status_error = _validar_estado_operacion_media(anuncio)
        if status_error:
            return status_error

        media_items = AnuncioRepository.listar_media_por_anuncio(anuncio_id)
        imagenes = [media for media in media_items if media.tipo_media == "imagen"]
        videos = [media for media in media_items if media.tipo_media == "video"]

        image_ids = [media.id for media in imagenes]
        video_ids = {media.id for media in videos}
        received_ids = list(ordered_media_ids)

        if any(media_id in video_ids for media_id in received_ids):
            return _error_response("VALIDATION_ERROR", "El array orden no puede incluir videos.")

        if len(received_ids) != len(set(received_ids)):
            return _error_response("VALIDATION_ERROR", "El array orden contiene IDs repetidos.")

        if set(received_ids) != set(image_ids):
            return _error_response(
                "VALIDATION_ERROR",
                "El array orden debe incluir todos los IDs de imagen del anuncio sin omitir ni agregar ajenos.",
            )

        image_by_id = {media.id: media for media in imagenes}
        try:
            for posicion, media_id in enumerate(received_ids):
                media = image_by_id[media_id]
                media.orden = posicion
                media.es_principal = posicion == 0

            AnuncioRepository.commit()
            return {
                "success": True,
                "data": {
                    "media": [image_by_id[media_id].to_public_dict() for media_id in received_ids],
                },
                "error": None,
                "message": "Orden de imagenes actualizado correctamente.",
            }
        except SQLAlchemyError:
            AnuncioRepository.rollback()
            return _error_response("DATABASE_ERROR", "No se pudo reordenar la media.")

    @staticmethod
    def eliminar_media(anuncio_id, media_id, usuario_id, upload_folder):
        anuncio = AnuncioRepository.buscar_anuncio_por_id(anuncio_id)
        if not anuncio:
            return _error_response("NOT_FOUND", "Anuncio no encontrado.")

        ownership_error = _validar_propietario(anuncio, usuario_id)
        if ownership_error:
            return ownership_error

        status_error = _validar_estado_operacion_media(anuncio)
        if status_error:
            return status_error

        media = AnuncioRepository.buscar_media_de_anuncio(anuncio_id, media_id)
        if not media:
            return _error_response("NOT_FOUND", "Media no encontrada para el anuncio.")

        imagenes_restantes = [
            item for item in AnuncioRepository.listar_imagenes_por_anuncio(anuncio_id)
            if item.id != media.id
        ]
        _reindexar_imagenes(imagenes_restantes)

        absolute_path = _absolute_media_path(upload_folder, media.ruta_relativa)
        eliminado = {"id": media.id, "tipo_media": media.tipo_media}

        try:
            AnuncioRepository.eliminar_media(media)
            AnuncioRepository.flush()
            absolute_path.unlink()
            AnuncioRepository.commit()
            return {
                "success": True,
                "data": {
                    "eliminado": eliminado,
                    "media_restante": [item.to_public_dict() for item in imagenes_restantes],
                },
                "error": None,
                "message": "Media eliminada correctamente.",
            }
        except FileNotFoundError:
            AnuncioRepository.rollback()
            return _error_response("FILE_DELETE_ERROR", "No se pudo eliminar el archivo fisico asociado.")
        except OSError:
            AnuncioRepository.rollback()
            return _error_response("FILE_DELETE_ERROR", "No se pudo eliminar el archivo fisico asociado.")
        except SQLAlchemyError:
            AnuncioRepository.rollback()
            return _error_response("DATABASE_ERROR", "No se pudo eliminar la media.")

    @staticmethod
    def reemplazar_media(anuncio_id, media_id, usuario_id, file_storage, upload_folder):
        anuncio = AnuncioRepository.buscar_anuncio_por_id(anuncio_id)
        if not anuncio:
            return _error_response("NOT_FOUND", "Anuncio no encontrado.")

        ownership_error = _validar_propietario(anuncio, usuario_id)
        if ownership_error:
            return ownership_error

        status_error = _validar_estado_operacion_media(anuncio)
        if status_error:
            return status_error

        media = AnuncioRepository.buscar_media_de_anuncio(anuncio_id, media_id)
        if not media:
            return _error_response("NOT_FOUND", "Media no encontrada para el anuncio.")

        if not file_storage or not file_storage.filename:
            return _error_response("MISSING_FILE", "Debe adjuntar un archivo.")

        try:
            nuevo_tipo, ruta_relativa, ruta_absoluta = validate_and_store_media(
                file_storage,
                upload_folder,
                anuncio_id,
            )
        except MediaValidationError as error:
            return _media_error_response(error)

        if nuevo_tipo != media.tipo_media:
            _eliminar_archivos([ruta_absoluta])
            return _error_response(
                "INVALID_FILE_TYPE",
                "El archivo nuevo debe ser del mismo tipo de media que el original.",
            )

        ruta_anterior = media.ruta_relativa
        absolute_old_path = _absolute_media_path(upload_folder, ruta_anterior)

        try:
            media.ruta_relativa = ruta_relativa
            AnuncioRepository.commit()
        except SQLAlchemyError:
            AnuncioRepository.rollback()
            _eliminar_archivos([ruta_absoluta])
            return _error_response("DATABASE_ERROR", "No se pudo reemplazar la media.")

        try:
            absolute_old_path.unlink(missing_ok=False)
        except OSError:
            current_app.logger.warning(
                "No se pudo eliminar archivo previo de media anuncio_id=%s media_id=%s ruta=%s",
                anuncio_id,
                media_id,
                ruta_anterior,
            )

        return {
            "success": True,
            "data": media.to_public_dict(),
            "error": None,
            "message": "Media reemplazada correctamente.",
        }

    @staticmethod
    def _registrar_contacto_async(comprador_id, vendedor_id, anuncio_id, created_at):
        if current_app.config.get("TESTING"):
            AnuncioService._registrar_contacto(comprador_id, vendedor_id, anuncio_id, created_at)
            return

        app = current_app._get_current_object()
        thread = threading.Thread(
            target=AnuncioService._registrar_contacto_thread,
            args=(app, comprador_id, vendedor_id, anuncio_id, created_at),
            daemon=True,
        )
        thread.start()

    @staticmethod
    def _registrar_contacto_thread(app, comprador_id, vendedor_id, anuncio_id, created_at):
        with app.app_context():
            AnuncioService._registrar_contacto(comprador_id, vendedor_id, anuncio_id, created_at)

    @staticmethod
    def _registrar_contacto(comprador_id, vendedor_id, anuncio_id, created_at):
        try:
            contacto_log = ContactoLog(
                comprador_id=comprador_id,
                vendedor_id=vendedor_id,
                anuncio_id=anuncio_id,
                created_at=created_at,
            )
            AnuncioRepository.agregar_contacto_log(contacto_log)
            AnuncioRepository.commit()
        except SQLAlchemyError:
            AnuncioRepository.rollback()
            current_app.logger.exception(
                "No se pudo registrar contacto comprador_id=%s vendedor_id=%s anuncio_id=%s",
                comprador_id,
                vendedor_id,
                anuncio_id,
            )


def _error_response(error_code, message, data=None):
    return {
        "success": False,
        "data": data or {},
        "error": error_code,
        "message": message,
    }


def _utcnow_naive():
    return datetime.now(UTC).replace(tzinfo=None)


def _day_bounds_peru(reference=None):
    now_utc = reference or datetime.now(UTC)
    now_local = now_utc.astimezone(PERU_TIMEZONE) if PERU_TIMEZONE else now_utc
    start_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    end_local = start_local + timedelta(days=1)
    start_utc = start_local.astimezone(UTC).replace(tzinfo=None) if PERU_TIMEZONE else start_local.replace(tzinfo=None)
    end_utc = end_local.astimezone(UTC).replace(tzinfo=None) if PERU_TIMEZONE else end_local.replace(tzinfo=None)
    return start_utc, end_utc


def _validar_propietario(anuncio, usuario_id):
    if anuncio.usuario_id != usuario_id:
        return _error_response("FORBIDDEN", "El anuncio no pertenece al usuario autenticado.")
    return None


def _validar_estado_edicion(anuncio):
    if anuncio.estado == "BLOQUEADO":
        return _error_response("FORBIDDEN", "El anuncio se encuentra bloqueado.")
    if anuncio.estado == "VENDIDO":
        return _error_response("CONFLICT", "El anuncio vendido no puede modificarse.")
    return None


def _validar_estado_para_vendido(anuncio):
    if anuncio.estado == "BLOQUEADO":
        return _error_response("CONFLICT", "El anuncio bloqueado no puede marcarse como vendido.")
    if anuncio.estado == "VENDIDO":
        return _error_response("CONFLICT", "El anuncio ya se encuentra vendido.")
    if anuncio.estado == "INACTIVO":
        return _error_response("CONFLICT", "El anuncio inactivo no puede marcarse como vendido.")
    return None


def _validar_estado_para_desactivar(anuncio):
    if anuncio.estado == "BLOQUEADO":
        return _error_response("CONFLICT", "El anuncio bloqueado no puede desactivarse.")
    if anuncio.estado == "VENDIDO":
        return _error_response("CONFLICT", "El anuncio vendido no puede desactivarse.")
    if anuncio.estado == "INACTIVO":
        return _error_response("CONFLICT", "El anuncio ya se encuentra inactivo.")
    return None


def _validar_estado_para_reactivar(anuncio):
    if anuncio.estado == "BLOQUEADO":
        return _error_response("CONFLICT", "El anuncio bloqueado no puede reactivarse.")
    if anuncio.estado == "VENDIDO":
        return _error_response("CONFLICT", "El anuncio vendido no puede reactivarse.")
    if anuncio.estado == "ACTIVO":
        return _error_response("CONFLICT", "El anuncio ya se encuentra activo.")
    return None


def _validar_estado_operacion_media(anuncio):
    if anuncio.estado == "BLOQUEADO":
        return _error_response("FORBIDDEN", "El anuncio se encuentra bloqueado.")
    if anuncio.estado == "VENDIDO":
        return _error_response("CONFLICT", "El anuncio vendido no permite cambios de media.")
    return None


def _validar_estado_comprador_contacto(usuario):
    if usuario.estado == "PENDIENTE_VERIFICACION":
        return _error_response("FORBIDDEN", "La cuenta debe estar activa para contactar anuncios.")

    if usuario.estado == "BLOQUEADO":
        return _error_response("FORBIDDEN", "La cuenta se encuentra bloqueada.")

    if usuario.rol == "TIENDA_VERIFICADA":
        tienda = getattr(usuario, "tienda", None)
        if tienda and tienda.estado == "EN_REVISION":
            return _error_response("FORBIDDEN", "La cuenta debe estar activa para contactar anuncios.")
        if tienda and tienda.estado == "RECHAZADO":
            return _error_response("FORBIDDEN", "La cuenta debe estar activa para contactar anuncios.")

    return None


def _media_error_response(error):
    return _error_response(error.error_code, error.message)


def _serialize_public_listing(item):
    precio = item.precio
    if hasattr(precio, "as_tuple"):
        precio = float(precio)

    return {
        "id": item.id,
        "titulo": item.titulo,
        "precio": precio,
        "categoria": item.categoria,
        "subcategoria": item.subcategoria,
        "condicion": item.condicion,
        "imagen_principal": item.imagen_principal,
        "vendedor_nombre": item.vendedor_nombre,
        "es_tienda_verificada": item.vendedor_rol == "TIENDA_VERIFICADA",
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "updated_at": item.updated_at.isoformat() if item.updated_at else None,
    }


def _serialize_detail_listing(anuncio, vendedor, tienda, media, viewer_user_id, es_propietario):
    precio = anuncio.precio
    if hasattr(precio, "as_tuple"):
        precio = float(precio)

    vendedor_data = {
        "id": vendedor.id,
        "nombre": vendedor.nombre,
        "es_tienda_verificada": vendedor.rol == "TIENDA_VERIFICADA",
        "telefono": vendedor.telefono if viewer_user_id is not None else None,
    }
    if vendedor.rol == "TIENDA_VERIFICADA" and tienda is not None:
        vendedor_data["tienda"] = {
            "nombre_comercial": tienda.nombre_comercial,
            "direccion": tienda.direccion,
        }

    response = {
        "id": anuncio.id,
        "titulo": anuncio.titulo,
        "descripcion": anuncio.descripcion,
        "categoria": anuncio.categoria,
        "subcategoria": anuncio.subcategoria,
        "condicion": anuncio.condicion,
        "precio": precio,
        "especificaciones": anuncio.especificaciones or {},
        "media": [item.to_public_dict() for item in media],
        "created_at": anuncio.created_at.isoformat() if anuncio.created_at else None,
        "updated_at": anuncio.updated_at.isoformat() if anuncio.updated_at else None,
        "es_propietario": es_propietario,
        "vendedor": vendedor_data,
    }

    if es_propietario:
        response["estado_propietario"] = {
            "estado": anuncio.estado,
            "reactivaciones_restantes": max(0, MAX_REACTIVACIONES - anuncio.reactivaciones_count),
        }

    return response


def _build_applied_filters(filters):
    applied = {"order_by": filters["order_by"]}
    for key in ("categoria", "subcategoria", "condicion", "q"):
        if filters.get(key):
            applied[key] = filters[key]

    if filters.get("precio_min") is not None:
        applied["precio_min"] = str(filters["precio_min"])

    if filters.get("precio_max") is not None:
        applied["precio_max"] = str(filters["precio_max"])

    if filters.get("specs"):
        applied["specs"] = dict(filters["specs"])

    return applied


def _build_spec_filter(spec_key, spec_value):
    expression = _json_spec_expression(spec_key)
    if spec_value in ("true", "false"):
        alternate = "1" if spec_value == "true" else "0"
        return or_(
            func.lower(cast(expression, String)) == spec_value,
            cast(expression, String) == alternate,
        )

    return cast(expression, String) == spec_value


def _json_spec_expression(spec_key):
    path = f"$.{spec_key}"
    dialect_name = Anuncio.query.session.get_bind().dialect.name
    extracted = func.json_extract(Anuncio.especificaciones, path)
    if dialect_name == "sqlite":
        return extracted
    return func.json_unquote(extracted)


def _escape_like(value):
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _sanitize_contact_title(value):
    sanitized = []
    for char in value:
        if char in {'"', "'"}:
            continue
        if ord(char) < 32 or ord(char) == 127:
            continue
        sanitized.append(char)
    return "".join(sanitized).strip()


def _now_local_naive():
    if PERU_TIMEZONE is None:
        return (datetime.now(UTC) - timedelta(hours=5)).replace(tzinfo=None)
    return datetime.now(PERU_TIMEZONE).replace(tzinfo=None)


def _eliminar_archivos(paths):
    for path in paths:
        try:
            Path(path).unlink(missing_ok=True)
        except OSError:
            pass


def _json_merge_patch(current_value, patch_value):
    # Replica el comportamiento de JSON_MERGE_PATCH para conservar claves no
    # enviadas y borrar las que lleguen explicitamente en null.
    if patch_value is None:
        return None

    if not isinstance(patch_value, dict):
        return deepcopy(patch_value)

    base = deepcopy(current_value) if isinstance(current_value, dict) else {}
    for key, value in patch_value.items():
        if value is None:
            base.pop(key, None)
            continue

        if isinstance(value, dict):
            base[key] = _json_merge_patch(base.get(key), value)
            continue

        base[key] = deepcopy(value)

    return base


def _reindexar_imagenes(imagenes):
    for posicion, image in enumerate(imagenes):
        image.orden = posicion
        image.es_principal = posicion == 0


def _absolute_media_path(upload_folder, relative_path):
    normalized = Path(relative_path)
    if normalized.parts and normalized.parts[0] == "uploads":
        normalized = Path(*normalized.parts[1:])
    return Path(upload_folder) / normalized

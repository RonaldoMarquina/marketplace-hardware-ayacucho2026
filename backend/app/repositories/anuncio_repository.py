from sqlalchemy import case

from app import db
from app.models.admin_log import AdminLog
from app.models.apelacion_evidencia import ApelacionEvidencia
from app.models.apelacion_moderacion import ApelacionModeracion
from app.models.anuncio import Anuncio
from app.models.contacto_log import ContactoLog
from app.models.media_anuncio import MediaAnuncio
from app.models.moderacion_log import ModeracionLog
from app.models.reporte import Reporte
from app.models.reporte_evidencia import ReporteEvidencia
from app.models.tienda import Tienda
from app.models.transaccion import Transaccion
from app.models.usuario import Usuario


class AnuncioRepository:
    @staticmethod
    def buscar_usuario_por_id(usuario_id):
        return db.session.get(Usuario, usuario_id)

    @staticmethod
    def buscar_anuncio_por_id(anuncio_id):
        return db.session.get(Anuncio, anuncio_id)

    @staticmethod
    def contar_anuncios_activos(usuario_id):
        return Anuncio.query.filter_by(usuario_id=usuario_id, estado="ACTIVO").count()

    @staticmethod
    def contar_media(anuncio_id, tipo_media):
        return MediaAnuncio.query.filter_by(
            anuncio_id=anuncio_id,
            tipo_media=tipo_media,
        ).count()

    @staticmethod
    def obtener_siguiente_orden_imagen(anuncio_id):
        max_orden = db.session.query(db.func.max(MediaAnuncio.orden)).filter_by(
            anuncio_id=anuncio_id,
            tipo_media="imagen",
        ).scalar()
        return 0 if max_orden is None else max_orden + 1

    @staticmethod
    def listar_media_por_anuncio(anuncio_id):
        return MediaAnuncio.query.filter_by(anuncio_id=anuncio_id).order_by(
            MediaAnuncio.tipo_media.asc(),
            case((MediaAnuncio.orden.is_(None), 1), else_=0),
            MediaAnuncio.orden.asc(),
            MediaAnuncio.id.asc(),
        ).all()

    @staticmethod
    def listar_imagenes_por_anuncio(anuncio_id):
        return MediaAnuncio.query.filter_by(
            anuncio_id=anuncio_id,
            tipo_media="imagen",
        ).order_by(MediaAnuncio.orden.asc(), MediaAnuncio.id.asc()).all()

    @staticmethod
    def buscar_media_de_anuncio(anuncio_id, media_id):
        return MediaAnuncio.query.filter_by(anuncio_id=anuncio_id, id=media_id).first()

    @staticmethod
    def contar_anuncios_publicos():
        return Anuncio.query.filter_by(estado="ACTIVO").count()

    @staticmethod
    def listar_feed_publico(offset, limit):
        return AnuncioRepository.construir_query_publica_base().order_by(
            Anuncio.created_at.desc(),
            Anuncio.id.desc(),
        ).offset(offset).limit(limit).all()

    @staticmethod
    def construir_query_publica_base():
        return db.session.query(
            Anuncio.id,
            Anuncio.titulo,
            Anuncio.precio,
            Anuncio.categoria,
            Anuncio.subcategoria,
            Anuncio.condicion,
            Anuncio.created_at,
            Anuncio.updated_at,
            Usuario.id.label("vendedor_id"),
            Usuario.nombre.label("vendedor_nombre"),
            Usuario.rol.label("vendedor_rol"),
            MediaAnuncio.ruta_relativa.label("imagen_principal"),
        ).join(
            Usuario,
            Usuario.id == Anuncio.usuario_id,
        ).outerjoin(
            MediaAnuncio,
            db.and_(
                MediaAnuncio.anuncio_id == Anuncio.id,
                MediaAnuncio.tipo_media == "imagen",
                MediaAnuncio.es_principal.is_(True),
            ),
        ).filter(
            Anuncio.estado == "ACTIVO",
        )

    @staticmethod
    def contar_query_publica(query):
        subquery = query.order_by(None).subquery()
        return db.session.query(db.func.count()).select_from(subquery).scalar()

    @staticmethod
    def listar_query_publica(query, offset, limit):
        return query.offset(offset).limit(limit).all()

    @staticmethod
    def buscar_detalle_anuncio(anuncio_id):
        return db.session.query(
            Anuncio,
            Usuario,
            Tienda,
        ).join(
            Usuario,
            Usuario.id == Anuncio.usuario_id,
        ).outerjoin(
            Tienda,
            Tienda.usuario_id == Usuario.id,
        ).filter(
            Anuncio.id == anuncio_id,
        ).first()

    @staticmethod
    def listar_media_detalle(anuncio_id):
        return MediaAnuncio.query.filter_by(anuncio_id=anuncio_id).order_by(
            MediaAnuncio.tipo_media.asc(),
            case((MediaAnuncio.orden.is_(None), 1), else_=0),
            MediaAnuncio.orden.asc(),
            MediaAnuncio.id.asc(),
        ).all()

    @staticmethod
    def listar_contactos_anuncio_propietario(anuncio_id):
        return db.session.query(
            Usuario.id.label("id"),
            Usuario.nombre.label("nombre"),
            Usuario.correo.label("correo"),
            Usuario.telefono.label("telefono"),
            Usuario.estado.label("estado"),
            db.func.count(ContactoLog.id).label("total_contactos"),
            db.func.max(ContactoLog.created_at).label("ultimo_contacto_at"),
        ).join(
            Usuario,
            Usuario.id == ContactoLog.comprador_id,
        ).filter(
            ContactoLog.anuncio_id == anuncio_id,
        ).group_by(
            Usuario.id,
            Usuario.nombre,
            Usuario.correo,
            Usuario.telefono,
            Usuario.estado,
        ).order_by(
            db.func.max(ContactoLog.created_at).desc(),
            Usuario.id.desc(),
        ).all()

    @staticmethod
    def contar_contactos_distintos_hoy(comprador_id, day_start, day_end):
        return db.session.query(db.func.count(db.distinct(ContactoLog.vendedor_id))).filter(
            ContactoLog.comprador_id == comprador_id,
            ContactoLog.created_at >= day_start,
            ContactoLog.created_at < day_end,
        ).scalar()

    @staticmethod
    def buscar_ultimo_contacto_anuncio(comprador_id, anuncio_id):
        return ContactoLog.query.filter(
            ContactoLog.comprador_id == comprador_id,
            ContactoLog.anuncio_id == anuncio_id,
        ).order_by(ContactoLog.created_at.desc(), ContactoLog.id.desc()).first()

    @staticmethod
    def existe_contacto_anuncio(comprador_id, anuncio_id):
        return db.session.query(ContactoLog.id).filter(
            ContactoLog.comprador_id == comprador_id,
            ContactoLog.anuncio_id == anuncio_id,
        ).first() is not None

    @staticmethod
    def buscar_ultimo_desbloqueo_anuncio(anuncio_id):
        return ModeracionLog.query.filter(
            ModeracionLog.anuncio_id == anuncio_id,
            ModeracionLog.accion == "DESBLOQUEADO",
        ).order_by(ModeracionLog.created_at.desc(), ModeracionLog.id.desc()).first()

    @staticmethod
    def buscar_reporte_duplicado_en_ciclo(comprador_id, anuncio_id, created_at_min=None):
        query = Reporte.query.filter(
            Reporte.comprador_id == comprador_id,
            Reporte.anuncio_id == anuncio_id,
            Reporte.estado.in_(("PENDIENTE", "REVISADO")),
        )
        if created_at_min is not None:
            query = query.filter(Reporte.created_at >= created_at_min)
        return query.order_by(Reporte.created_at.desc(), Reporte.id.desc()).first()

    @staticmethod
    def contar_reportes_usuario_hoy(comprador_id, day_start, day_end):
        return Reporte.query.filter(
            Reporte.comprador_id == comprador_id,
            Reporte.created_at >= day_start,
            Reporte.created_at < day_end,
        ).count()

    @staticmethod
    def listar_anuncios_reportados(offset=None, limit=None):
        total_reportes = db.func.count(Reporte.id)
        ultimo_reporte = db.func.max(Reporte.created_at)
        motivos = db.func.group_concat(Reporte.motivo, ",")

        query = db.session.query(
            Anuncio.id.label("anuncio_id"),
            Anuncio.titulo,
            Anuncio.categoria,
            Anuncio.subcategoria,
            Anuncio.estado.label("estado_anuncio"),
            Usuario.id.label("vendedor_id"),
            Usuario.nombre.label("vendedor_nombre"),
            Usuario.rol.label("vendedor_rol"),
            total_reportes.label("total_reportes"),
            motivos.label("motivos"),
            ultimo_reporte.label("ultimo_reporte"),
        ).join(
            Reporte,
            Reporte.anuncio_id == Anuncio.id,
        ).join(
            Usuario,
            Usuario.id == Anuncio.usuario_id,
        ).filter(
            Reporte.estado == "PENDIENTE",
        ).group_by(
            Anuncio.id,
            Anuncio.titulo,
            Anuncio.categoria,
            Anuncio.subcategoria,
            Anuncio.estado,
            Usuario.id,
            Usuario.nombre,
            Usuario.rol,
        ).order_by(
            total_reportes.desc(),
            ultimo_reporte.desc(),
            Anuncio.id.desc(),
        )

        total = db.session.query(db.func.count()).select_from(query.order_by(None).subquery()).scalar()
        if offset is not None and limit is not None:
            items = query.offset(offset).limit(limit).all()
        else:
            items = query.all()
        return items, total

    @staticmethod
    def listar_reportes_pendientes_para_anuncios(anuncio_ids):
        if not anuncio_ids:
            return []

        return db.session.query(
            Reporte,
            Usuario.nombre.label("comprador_nombre"),
            Usuario.correo.label("comprador_correo"),
            Usuario.estado.label("comprador_estado"),
            Usuario.created_at.label("comprador_created_at"),
            Usuario.total_calificaciones_comprador.label("comprador_total_calificaciones"),
            Usuario.calificacion_promedio_comprador.label("comprador_calificacion_promedio"),
            Anuncio.usuario_id.label("vendedor_id"),
        ).join(
            Usuario,
            Usuario.id == Reporte.comprador_id,
        ).join(
            Anuncio,
            Anuncio.id == Reporte.anuncio_id,
        ).filter(
            Reporte.anuncio_id.in_(anuncio_ids),
            Reporte.estado == "PENDIENTE",
        ).order_by(
            Reporte.created_at.desc(),
            Reporte.id.desc(),
        ).all()

    @staticmethod
    def contar_reportes_pendientes(anuncio_id):
        return Reporte.query.filter_by(anuncio_id=anuncio_id, estado="PENDIENTE").count()

    @staticmethod
    def listar_reportes_pendientes_por_anuncio(anuncio_id):
        return db.session.query(
            Reporte,
            Usuario.nombre.label("comprador_nombre"),
            Usuario.correo.label("comprador_correo"),
            Usuario.estado.label("comprador_estado"),
        ).join(
            Usuario,
            Usuario.id == Reporte.comprador_id,
        ).filter(
            Reporte.anuncio_id == anuncio_id,
            Reporte.estado == "PENDIENTE",
        ).order_by(
            Reporte.created_at.desc(),
            Reporte.id.desc(),
        ).all()

    @staticmethod
    def listar_reportes_por_anuncio_con_comprador(anuncio_id):
        return db.session.query(
            Reporte,
            Usuario.nombre.label("comprador_nombre"),
            Usuario.correo.label("comprador_correo"),
            Usuario.estado.label("comprador_estado"),
        ).join(
            Usuario,
            Usuario.id == Reporte.comprador_id,
        ).filter(
            Reporte.anuncio_id == anuncio_id,
        ).order_by(
            Reporte.created_at.desc(),
            Reporte.id.desc(),
        ).all()

    @staticmethod
    def listar_evidencias_reporte(reporte_ids):
        if not reporte_ids:
            return []

        return ReporteEvidencia.query.filter(
            ReporteEvidencia.reporte_id.in_(reporte_ids),
        ).order_by(
            ReporteEvidencia.created_at.asc(),
            ReporteEvidencia.id.asc(),
        ).all()

    @staticmethod
    def buscar_ultimo_bloqueo_anuncio(anuncio_id):
        return ModeracionLog.query.filter(
            ModeracionLog.anuncio_id == anuncio_id,
            ModeracionLog.accion == "BLOQUEADO",
        ).order_by(ModeracionLog.created_at.desc(), ModeracionLog.id.desc()).first()

    @staticmethod
    def listar_reportes_por_anuncio(anuncio_id):
        return Reporte.query.filter(
            Reporte.anuncio_id == anuncio_id,
        ).order_by(
            Reporte.created_at.desc(),
            Reporte.id.desc(),
        ).all()

    @staticmethod
    def buscar_apelacion_por_id(apelacion_id):
        return db.session.get(ApelacionModeracion, apelacion_id)

    @staticmethod
    def listar_apelaciones_por_anuncio(anuncio_id):
        return db.session.query(
            ApelacionModeracion,
            Usuario.nombre.label("usuario_nombre"),
            Usuario.correo.label("usuario_correo"),
            Usuario.rol.label("usuario_rol"),
        ).join(
            Usuario,
            Usuario.id == ApelacionModeracion.usuario_id,
        ).filter(
            ApelacionModeracion.anuncio_id == anuncio_id,
        ).order_by(
            ApelacionModeracion.created_at.desc(),
            ApelacionModeracion.id.desc(),
        ).all()

    @staticmethod
    def listar_evidencias_apelacion(apelacion_ids):
        if not apelacion_ids:
            return []

        return ApelacionEvidencia.query.filter(
            ApelacionEvidencia.apelacion_id.in_(apelacion_ids),
        ).order_by(
            ApelacionEvidencia.created_at.asc(),
            ApelacionEvidencia.id.asc(),
        ).all()

    @staticmethod
    def contar_compras_por_comprador_ids(usuario_ids):
        if not usuario_ids:
            return {}

        rows = db.session.query(
            Transaccion.comprador_id,
            db.func.count(Transaccion.id).label("total"),
        ).filter(
            Transaccion.comprador_id.in_(usuario_ids),
        ).group_by(
            Transaccion.comprador_id,
        ).all()
        return {row.comprador_id: row.total for row in rows}

    @staticmethod
    def contar_reportes_desde_por_comprador_ids(usuario_ids, created_at_min):
        if not usuario_ids:
            return {}

        rows = db.session.query(
            Reporte.comprador_id,
            db.func.count(Reporte.id).label("total"),
        ).filter(
            Reporte.comprador_id.in_(usuario_ids),
            Reporte.created_at >= created_at_min,
        ).group_by(
            Reporte.comprador_id,
        ).all()
        return {row.comprador_id: row.total for row in rows}

    @staticmethod
    def contar_reportes_contra_vendedor_desde(usuario_ids, created_at_min):
        if not usuario_ids:
            return {}

        rows = db.session.query(
            Reporte.comprador_id,
            Anuncio.usuario_id.label("vendedor_id"),
            db.func.count(Reporte.id).label("total"),
        ).join(
            Anuncio,
            Anuncio.id == Reporte.anuncio_id,
        ).filter(
            Reporte.comprador_id.in_(usuario_ids),
            Reporte.created_at >= created_at_min,
        ).group_by(
            Reporte.comprador_id,
            Anuncio.usuario_id,
        ).all()
        return {(row.comprador_id, row.vendedor_id): row.total for row in rows}

    @staticmethod
    def buscar_apelacion_en_ciclo(anuncio_id, usuario_id, created_at_min):
        return ApelacionModeracion.query.filter(
            ApelacionModeracion.anuncio_id == anuncio_id,
            ApelacionModeracion.usuario_id == usuario_id,
            ApelacionModeracion.created_at >= created_at_min,
        ).order_by(
            ApelacionModeracion.created_at.desc(),
            ApelacionModeracion.id.desc(),
        ).first()

    @staticmethod
    def listar_anuncios_bloqueados_o_apelados_por_usuario(usuario_id):
        ultimo_bloqueo_subquery = db.session.query(
            ModeracionLog.anuncio_id.label("anuncio_id"),
            db.func.max(ModeracionLog.id).label("max_log_id"),
        ).filter(
            ModeracionLog.accion == "BLOQUEADO",
        ).group_by(
            ModeracionLog.anuncio_id,
        ).subquery()

        ultima_apelacion_subquery = db.session.query(
            ApelacionModeracion.anuncio_id.label("anuncio_id"),
            db.func.max(ApelacionModeracion.id).label("max_apelacion_id"),
        ).group_by(
            ApelacionModeracion.anuncio_id,
        ).subquery()

        ultimo_reporte_pendiente_subquery = db.session.query(
            Reporte.anuncio_id.label("anuncio_id"),
            db.func.max(Reporte.id).label("max_reporte_id"),
            db.func.count(Reporte.id).label("total_reportes_pendientes"),
        ).filter(
            Reporte.estado == "PENDIENTE",
        ).group_by(
            Reporte.anuncio_id,
        ).subquery()

        return db.session.query(
            Anuncio.id.label("anuncio_id"),
            Anuncio.titulo.label("titulo"),
            Anuncio.estado.label("estado_anuncio"),
            ModeracionLog.motivo_admin.label("motivo_bloqueo"),
            ModeracionLog.created_at.label("bloqueado_at"),
            ApelacionModeracion.id.label("apelacion_id"),
            ApelacionModeracion.estado.label("apelacion_estado"),
            ApelacionModeracion.created_at.label("apelacion_created_at"),
            Reporte.motivo.label("motivo_reporte"),
            Reporte.created_at.label("ultimo_reporte_at"),
            ultimo_reporte_pendiente_subquery.c.total_reportes_pendientes.label("total_reportes_pendientes"),
        ).join(
            ultimo_bloqueo_subquery,
            ultimo_bloqueo_subquery.c.anuncio_id == Anuncio.id,
            isouter=True,
        ).outerjoin(
            ModeracionLog,
            ModeracionLog.id == ultimo_bloqueo_subquery.c.max_log_id,
        ).outerjoin(
            ultima_apelacion_subquery,
            ultima_apelacion_subquery.c.anuncio_id == Anuncio.id,
        ).outerjoin(
            ApelacionModeracion,
            ApelacionModeracion.id == ultima_apelacion_subquery.c.max_apelacion_id,
        ).outerjoin(
            ultimo_reporte_pendiente_subquery,
            ultimo_reporte_pendiente_subquery.c.anuncio_id == Anuncio.id,
        ).outerjoin(
            Reporte,
            Reporte.id == ultimo_reporte_pendiente_subquery.c.max_reporte_id,
        ).filter(
            Anuncio.usuario_id == usuario_id,
            db.or_(
                Anuncio.estado == "BLOQUEADO",
                ApelacionModeracion.id.isnot(None),
                ultimo_reporte_pendiente_subquery.c.max_reporte_id.isnot(None),
            ),
        ).order_by(
            db.func.coalesce(
                ModeracionLog.created_at,
                Reporte.created_at,
                Anuncio.updated_at,
                Anuncio.created_at,
            ).desc(),
            Anuncio.id.desc(),
        ).all()

    @staticmethod
    def listar_apelaciones_pendientes(offset, limit):
        query = db.session.query(
            ApelacionModeracion,
            Anuncio.titulo.label("titulo"),
            Anuncio.estado.label("estado_anuncio"),
            Usuario.nombre.label("usuario_nombre"),
            Usuario.rol.label("usuario_rol"),
        ).join(
            Anuncio,
            Anuncio.id == ApelacionModeracion.anuncio_id,
        ).join(
            Usuario,
            Usuario.id == ApelacionModeracion.usuario_id,
        ).filter(
            ApelacionModeracion.estado == "PENDIENTE",
        ).order_by(
            ApelacionModeracion.created_at.desc(),
            ApelacionModeracion.id.desc(),
        )

        total = db.session.query(db.func.count()).select_from(query.order_by(None).subquery()).scalar()
        items = query.offset(offset).limit(limit).all()
        return items, total

    @staticmethod
    def marcar_reportes_revisados(anuncio_id):
        return Reporte.query.filter_by(anuncio_id=anuncio_id, estado="PENDIENTE").update(
            {"estado": "REVISADO"},
            synchronize_session=False,
        )

    @staticmethod
    def listar_historial_moderacion(offset, limit):
        query = db.session.query(
            ModeracionLog,
            Usuario.nombre.label("admin_nombre"),
            Anuncio.titulo.label("anuncio_titulo"),
        ).join(
            Usuario,
            Usuario.id == ModeracionLog.admin_id,
        ).join(
            Anuncio,
            Anuncio.id == ModeracionLog.anuncio_id,
        ).order_by(
            ModeracionLog.created_at.desc(),
            ModeracionLog.id.desc(),
        )
        total = db.session.query(db.func.count()).select_from(query.order_by(None).subquery()).scalar()
        items = query.offset(offset).limit(limit).all()
        return items, total

    @staticmethod
    def agregar(anuncio):
        db.session.add(anuncio)

    @staticmethod
    def agregar_media(media):
        db.session.add(media)

    @staticmethod
    def agregar_contacto_log(contacto_log):
        db.session.add(contacto_log)

    @staticmethod
    def agregar_reporte(reporte):
        db.session.add(reporte)

    @staticmethod
    def agregar_reporte_evidencia(evidencia):
        db.session.add(evidencia)

    @staticmethod
    def agregar_apelacion(apelacion):
        db.session.add(apelacion)

    @staticmethod
    def agregar_apelacion_evidencia(evidencia):
        db.session.add(evidencia)

    @staticmethod
    def agregar_moderacion_log(log_entry):
        db.session.add(log_entry)

    @staticmethod
    def agregar_admin_log(log_entry):
        db.session.add(log_entry)

    @staticmethod
    def agregar_transaccion(transaccion):
        db.session.add(transaccion)

    @staticmethod
    def eliminar_media(media):
        db.session.delete(media)

    @staticmethod
    def flush():
        db.session.flush()

    @staticmethod
    def commit():
        db.session.commit()

    @staticmethod
    def rollback():
        db.session.rollback()

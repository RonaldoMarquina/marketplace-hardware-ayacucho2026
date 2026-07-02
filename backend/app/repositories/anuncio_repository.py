from app import db
from app.models.admin_log import AdminLog
from app.models.anuncio import Anuncio
from app.models.contacto_log import ContactoLog
from app.models.media_anuncio import MediaAnuncio
from app.models.moderacion_log import ModeracionLog
from app.models.reporte import Reporte
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
            MediaAnuncio.orden.asc().nullslast(),
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
            MediaAnuncio.orden.asc().nullslast(),
            MediaAnuncio.id.asc(),
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
    def listar_anuncios_reportados(offset, limit):
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
        items = query.offset(offset).limit(limit).all()
        return items, total

    @staticmethod
    def contar_reportes_pendientes(anuncio_id):
        return Reporte.query.filter_by(anuncio_id=anuncio_id, estado="PENDIENTE").count()

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

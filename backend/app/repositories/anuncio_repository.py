from app import db
from app.models.anuncio import Anuncio
from app.models.media_anuncio import MediaAnuncio
from app.models.tienda import Tienda
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
    def agregar(anuncio):
        db.session.add(anuncio)

    @staticmethod
    def agregar_media(media):
        db.session.add(media)

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

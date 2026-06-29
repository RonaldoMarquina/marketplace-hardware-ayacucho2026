from app import db
from app.models.anuncio import Anuncio
from app.models.media_anuncio import MediaAnuncio
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

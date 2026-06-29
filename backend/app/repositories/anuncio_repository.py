from app import db
from app.models.anuncio import Anuncio
from app.models.usuario import Usuario


class AnuncioRepository:
    @staticmethod
    def buscar_usuario_por_id(usuario_id):
        return db.session.get(Usuario, usuario_id)

    @staticmethod
    def contar_anuncios_activos(usuario_id):
        return Anuncio.query.filter_by(usuario_id=usuario_id, estado="ACTIVO").count()

    @staticmethod
    def agregar(anuncio):
        db.session.add(anuncio)

    @staticmethod
    def commit():
        db.session.commit()

    @staticmethod
    def rollback():
        db.session.rollback()

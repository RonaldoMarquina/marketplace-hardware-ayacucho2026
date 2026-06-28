from app import db
from app.models.tienda import Tienda
from app.models.usuario import Usuario


class AuthRepository:
    @staticmethod
    def buscar_usuario_por_correo(correo):
        return Usuario.query.filter_by(correo=correo).first()

    @staticmethod
    def buscar_usuario_por_telefono(telefono):
        return Usuario.query.filter_by(telefono=telefono).first()

    @staticmethod
    def buscar_usuario_por_nombre(nombre):
        return Usuario.query.filter_by(nombre=nombre).first()

    @staticmethod
    def buscar_tienda_por_ruc(ruc):
        return Tienda.query.filter_by(ruc=ruc).first()

    @staticmethod
    def agregar_usuario(usuario):
        db.session.add(usuario)

    @staticmethod
    def agregar_tienda(tienda):
        db.session.add(tienda)

    @staticmethod
    def flush():
        db.session.flush()

    @staticmethod
    def commit():
        db.session.commit()

    @staticmethod
    def rollback():
        db.session.rollback()

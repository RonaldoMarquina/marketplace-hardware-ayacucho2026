from app import db
from app.models.tienda import Tienda
from app.models.token_verificacion import TokenVerificacion
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
    def buscar_token_verificacion(token):
        return TokenVerificacion.query.filter_by(token=token).first()

    @staticmethod
    def buscar_tokens_activos_usuario(usuario_id, tipo="EMAIL_VERIFICATION"):
        return TokenVerificacion.query.filter_by(
            usuario_id=usuario_id,
            tipo=tipo,
            usado=False,
        ).all()

    @staticmethod
    def agregar_usuario(usuario):
        db.session.add(usuario)

    @staticmethod
    def agregar_tienda(tienda):
        db.session.add(tienda)

    @staticmethod
    def agregar_token_verificacion(token_verificacion):
        db.session.add(token_verificacion)

    @staticmethod
    def flush():
        db.session.flush()

    @staticmethod
    def commit():
        db.session.commit()

    @staticmethod
    def rollback():
        db.session.rollback()

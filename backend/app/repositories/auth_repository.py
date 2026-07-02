from app import db
from sqlalchemy import or_

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
    def buscar_usuario_por_correo_o_telefono(correo, telefono):
        return Usuario.query.filter(
            or_(
                Usuario.correo == correo,
                Usuario.telefono == telefono,
            )
        ).first()

    @staticmethod
    def buscar_tienda_por_ruc(ruc):
        return Tienda.query.filter_by(ruc=ruc).first()

    @staticmethod
    def buscar_tienda_por_nombre_comercial(nombre_comercial):
        return Tienda.query.filter_by(nombre_comercial=nombre_comercial).first()

    @staticmethod
    def buscar_token_verificacion(token):
        return TokenVerificacion.query.filter_by(token=token).first()

    @staticmethod
    def buscar_token_por_valor_y_tipo(token, tipo):
        return TokenVerificacion.query.filter_by(token=token, tipo=tipo).first()

    @staticmethod
    def buscar_tokens_activos_usuario(usuario_id, tipo="EMAIL_VERIFICATION"):
        return TokenVerificacion.query.filter_by(
            usuario_id=usuario_id,
            tipo=tipo,
            usado=False,
        ).all()

    @staticmethod
    def buscar_primer_token_usuario(usuario_id, tipo="EMAIL_VERIFICATION"):
        return TokenVerificacion.query.filter_by(
            usuario_id=usuario_id,
            tipo=tipo,
        ).order_by(TokenVerificacion.created_at.asc(), TokenVerificacion.id.asc()).first()

    @staticmethod
    def contar_tokens_recientes_usuario(usuario_id, desde, tipo="EMAIL_VERIFICATION"):
        return TokenVerificacion.query.filter(
            TokenVerificacion.usuario_id == usuario_id,
            TokenVerificacion.tipo == tipo,
            TokenVerificacion.created_at >= desde,
        ).count()

    @staticmethod
    def listar_tokens_recientes_usuario(usuario_id, desde, tipo):
        return TokenVerificacion.query.filter(
            TokenVerificacion.usuario_id == usuario_id,
            TokenVerificacion.tipo == tipo,
            TokenVerificacion.created_at >= desde,
        ).order_by(TokenVerificacion.created_at.asc(), TokenVerificacion.id.asc()).all()

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

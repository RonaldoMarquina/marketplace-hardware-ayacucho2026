import bcrypt
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app import db
from app.models.usuario import Usuario


class AuthService:
    @staticmethod
    def registrar_usuario(data):
        usuario_existente = Usuario.query.filter(
            or_(
                Usuario.correo == data["correo"],
                Usuario.telefono == data["telefono"],
                Usuario.nombre == data["nombre"],
            )
        ).first()

        if usuario_existente:
            if usuario_existente.correo == data["correo"]:
                mensaje = "El correo ya se encuentra registrado."
            elif usuario_existente.telefono == data["telefono"]:
                mensaje = "El telefono ya se encuentra registrado."
            else:
                mensaje = "El nombre ya se encuentra registrado."

            return {
                "success": False,
                "data": {},
                "error": "CONFLICT",
                "message": mensaje,
            }

        password_hash = bcrypt.hashpw(
            data["password"].encode("utf-8"),
            bcrypt.gensalt(rounds=10),
        ).decode("utf-8")

        usuario = Usuario(
            nombre=data["nombre"],
            correo=data["correo"],
            password_hash=password_hash,
            telefono=data["telefono"],
            rol="USER_ESTANDAR",
            estado="PENDIENTE_VERIFICACION",
        )

        try:
            db.session.add(usuario)
            db.session.commit()
            return {
                "success": True,
                "data": usuario.to_public_dict(),
                "error": None,
                "message": "Usuario registrado correctamente.",
            }
        except IntegrityError:
            db.session.rollback()
            return {
                "success": False,
                "data": {},
                "error": "CONFLICT",
                "message": "El correo, telefono o nombre ya se encuentra registrado.",
            }
        except SQLAlchemyError:
            db.session.rollback()
            return {
                "success": False,
                "data": {},
                "error": "DATABASE_ERROR",
                "message": "No se pudo registrar el usuario.",
            }

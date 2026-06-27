from app import db


class Usuario(db.Model):
    """Modelo SQLAlchemy para la tabla usuarios definida en DATABASE.md."""

    __tablename__ = "usuarios"

    # SQLAlchemy representa la tabla real de MySQL. Mantener los mismos nombres
    # de columnas evita traducciones innecesarias entre modelo, BD y servicios.
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    correo = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(9), nullable=True, unique=True)
    rol = db.Column(
        db.Enum("USER_ESTANDAR", "TIENDA_VERIFICADA", "ADMIN"),
        nullable=False,
        default="USER_ESTANDAR",
    )
    estado = db.Column(
        db.Enum("PENDIENTE_VERIFICACION", "ACTIVO", "BLOQUEADO"),
        nullable=False,
        default="PENDIENTE_VERIFICACION",
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )

    def to_public_dict(self):
        # Este helper centraliza la salida segura del usuario. Nunca incluye
        # password_hash porque SECURITY.md prohibe exponer datos sensibles.
        return {
            "id": self.id,
            "nombre": self.nombre,
            "correo": self.correo,
            "rol": self.rol,
        }

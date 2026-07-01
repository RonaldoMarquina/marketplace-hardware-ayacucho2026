from app import db


class Tienda(db.Model):
    """Modelo SQLAlchemy para la tabla tiendas definida en database.sql."""

    __tablename__ = "tiendas"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        unique=True,
    )
    nombre_comercial = db.Column(db.String(100), nullable=False, unique=True)
    ruc = db.Column(db.String(11), nullable=False, unique=True)
    direccion = db.Column(db.String(200), nullable=False)
    documento_identidad = db.Column(db.String(255), nullable=False)
    estado = db.Column(
        db.Enum("EN_REVISION", "ACTIVO", "RECHAZADO"),
        nullable=False,
        default="EN_REVISION",
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

    usuario = db.relationship("Usuario", backref=db.backref("tienda", uselist=False))

    def to_public_dict(self):
        return {
            "id": self.usuario_id,
            "nombre_comercial": self.nombre_comercial,
            "ruc": self.ruc,
            "correo": self.usuario.correo,
            "rol": self.usuario.rol,
            "estado": self.estado,
        }

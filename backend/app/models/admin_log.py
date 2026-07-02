from app import db


ACCIONES_ADMIN_LOG = (
    "USUARIO_ACTIVADO",
    "TIENDA_RECHAZADA",
    "USUARIO_BLOQUEADO",
    "USUARIO_DESBLOQUEADO",
    "BLOQUEADO",
    "DESBLOQUEADO",
)


class AdminLog(db.Model):
    __tablename__ = "admin_log"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
        index=True,
    )
    anuncio_id = db.Column(
        db.Integer,
        db.ForeignKey("anuncios.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
        index=True,
    )
    accion = db.Column(db.Enum(*ACCIONES_ADMIN_LOG), nullable=False, index=True)
    motivo = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
        index=True,
    )

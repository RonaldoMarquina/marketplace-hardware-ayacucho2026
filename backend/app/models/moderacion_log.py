from app import db


ACCIONES_MODERACION = (
    "BLOQUEADO",
    "DESBLOQUEADO",
)


class ModeracionLog(db.Model):
    __tablename__ = "moderacion_log"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    anuncio_id = db.Column(
        db.Integer,
        db.ForeignKey("anuncios.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    accion = db.Column(db.Enum(*ACCIONES_MODERACION), nullable=False, index=True)
    motivo_admin = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
        index=True,
    )

from app import db


ESTADOS_APELACION_MODERACION = (
    "PENDIENTE",
    "ACEPTADA",
    "RECHAZADA",
)


class ApelacionModeracion(db.Model):
    __tablename__ = "apelaciones_moderacion"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    anuncio_id = db.Column(
        db.Integer,
        db.ForeignKey("anuncios.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    mensaje = db.Column(db.Text, nullable=False)
    estado = db.Column(
        db.Enum(*ESTADOS_APELACION_MODERACION),
        nullable=False,
        default="PENDIENTE",
        server_default="PENDIENTE",
        index=True,
    )
    respuesta_admin = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
        index=True,
    )
    resolved_at = db.Column(db.DateTime, nullable=True, index=True)

    def to_public_dict(self):
        return {
            "id": self.id,
            "anuncio_id": self.anuncio_id,
            "usuario_id": self.usuario_id,
            "mensaje": self.mensaje,
            "estado": self.estado,
            "respuesta_admin": self.respuesta_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "evidencias": [evidencia.to_public_dict() for evidencia in self.evidencias],
        }

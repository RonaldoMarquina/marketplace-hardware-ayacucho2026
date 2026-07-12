from app import db


TIPOS_EVIDENCIA_APELACION = (
    "IMAGEN",
)


class ApelacionEvidencia(db.Model):
    __tablename__ = "apelacion_evidencias"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    apelacion_id = db.Column(
        db.Integer,
        db.ForeignKey("apelaciones_moderacion.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    tipo_archivo = db.Column(
        db.Enum(*TIPOS_EVIDENCIA_APELACION),
        nullable=False,
        default="IMAGEN",
        server_default="IMAGEN",
        index=True,
    )
    ruta_relativa = db.Column(db.String(500), nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
        index=True,
    )

    apelacion = db.relationship(
        "ApelacionModeracion",
        backref=db.backref(
            "evidencias",
            lazy=True,
            cascade="all, delete-orphan",
        ),
    )

    def to_public_dict(self):
        return {
            "id": self.id,
            "tipo_archivo": self.tipo_archivo,
            "ruta_relativa": self.ruta_relativa,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


from app import db


TIPOS_MEDIA = ("imagen", "video")


class MediaAnuncio(db.Model):
    """Archivo multimedia asociado a un anuncio: imagen o video."""

    __tablename__ = "media_anuncio"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    anuncio_id = db.Column(
        db.Integer,
        db.ForeignKey("anuncios.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    tipo_media = db.Column(db.Enum(*TIPOS_MEDIA), nullable=False, index=True)
    ruta_relativa = db.Column(db.String(500), nullable=False)
    es_principal = db.Column(db.Boolean, nullable=False, default=False)
    orden = db.Column(db.Integer, nullable=True)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
    )

    anuncio = db.relationship("Anuncio", backref=db.backref("media", lazy=True))

    def to_public_dict(self):
        return {
            "id": self.id,
            "tipo_media": self.tipo_media,
            "ruta_relativa": self.ruta_relativa,
            "es_principal": bool(self.es_principal),
            "orden": self.orden,
        }

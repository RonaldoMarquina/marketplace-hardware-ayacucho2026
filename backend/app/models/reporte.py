from app import db


MOTIVOS_REPORTE = (
    "FRAUDE",
    "PRECIO_ENGANOSO",
    "PRODUCTO_FALSO",
    "CONTENIDO_INAPROPIADO",
    "DUPLICADO",
    "OTRO",
)

ESTADOS_REPORTE = (
    "PENDIENTE",
    "REVISADO",
)


class Reporte(db.Model):
    __tablename__ = "reportes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comprador_id = db.Column(
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
    motivo = db.Column(db.Enum(*MOTIVOS_REPORTE), nullable=False)
    estado = db.Column(
        db.Enum(*ESTADOS_REPORTE),
        nullable=False,
        default="PENDIENTE",
        server_default="PENDIENTE",
        index=True,
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
        index=True,
    )

from app import db


TIPOS_CALIFICACION = (
    "COMPRADOR_A_VENDEDOR",
    "VENDEDOR_A_COMPRADOR",
)


class Calificacion(db.Model):
    __tablename__ = "calificaciones"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transaccion_id = db.Column(
        db.Integer,
        db.ForeignKey("transacciones.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    calificador_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    calificado_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    tipo = db.Column(db.Enum(*TIPOS_CALIFICACION), nullable=False, index=True)
    puntaje = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
        index=True,
    )

from app import db


class TokenVerificacion(db.Model):
    """Token de un solo uso para verificar correos electronicos."""

    __tablename__ = "tokens_verificacion"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    token = db.Column(db.String(64), nullable=False, unique=True, index=True)
    tipo = db.Column(
        db.Enum("EMAIL_VERIFICATION"),
        nullable=False,
        default="EMAIL_VERIFICATION",
    )
    expira_en = db.Column(db.DateTime, nullable=False)
    usado = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
    )

    usuario = db.relationship(
        "Usuario",
        backref=db.backref("tokens_verificacion", lazy=True),
    )

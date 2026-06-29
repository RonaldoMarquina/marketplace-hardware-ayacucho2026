from decimal import Decimal

from app import db


CATEGORIAS_ANUNCIO = (
    "COMPONENTES",
    "REFRIGERACION",
    "GABINETES",
    "PERIFERICOS",
    "MONITORES",
    "REDES",
    "MOBILIARIO",
    "ALMACENAMIENTO_EXTERNO",
    "ACCESORIOS",
    "PORTATILES",
)

SUBCATEGORIAS_POR_CATEGORIA = {
    "COMPONENTES": (
        "PROCESADOR",
        "PLACA_MADRE",
        "RAM",
        "GPU",
        "ALMACENAMIENTO",
        "FUENTE_PODER",
    ),
    "REFRIGERACION": (
        "AIRE",
        "LIQUIDA_AIO",
        "CUSTOM_LOOP",
        "PASTA_TERMICA",
    ),
    "GABINETES": (
        "CASE",
        "VENTILADORES",
        "SOPORTES_GPU",
        "FILTROS",
    ),
    "PERIFERICOS": (
        "TECLADO",
        "MOUSE",
        "AURICULARES",
        "MOUSEPAD",
        "MICROFONO",
        "WEBCAM",
    ),
    "MONITORES": (
        "MONITOR",
        "SOPORTES_VESA",
        "CABLES",
    ),
    "REDES": (
        "TARJETA_RED",
        "ROUTER",
        "ADAPTADORES",
        "UPS",
    ),
    "MOBILIARIO": (
        "SILLA_GAMER",
        "ESCRITORIO",
        "ACCESORIOS",
    ),
    "ALMACENAMIENTO_EXTERNO": (
        "SSD_EXTERNO",
        "HDD_EXTERNO",
        "EXTERNOS",
        "NAS",
    ),
    "ACCESORIOS": (
        "CABLES",
        "LIMPIEZA",
        "ORGANIZADORES",
        "RGB",
    ),
    "PORTATILES": (
        "LAPTOP",
        "TABLET",
    ),
}

SUBCATEGORIAS_ANUNCIO = tuple(
    subcategoria
    for subcategorias in SUBCATEGORIAS_POR_CATEGORIA.values()
    for subcategoria in subcategorias
)

CONDICIONES_ANUNCIO = (
    "NUEVO",
    "COMO_NUEVO",
    "USADO",
    "PARA_REPUESTOS",
)

ESTADOS_ANUNCIO = (
    "ACTIVO",
    "INACTIVO",
    "VENDIDO",
    "BLOQUEADO",
)


class Anuncio(db.Model):
    """Modelo de la tabla anuncios, centro del marketplace."""

    __tablename__ = "anuncios"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.Enum(*CATEGORIAS_ANUNCIO), nullable=False, index=True)
    # subcategoria es taxonomia buscable/filtrable. No debe mezclarse con specs.
    subcategoria = db.Column(db.String(80), nullable=False, index=True)
    condicion = db.Column(db.Enum(*CONDICIONES_ANUNCIO), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    # especificaciones guarda solo atributos tecnicos del producto concreto.
    especificaciones = db.Column(db.JSON, nullable=True)
    estado = db.Column(
        db.Enum(*ESTADOS_ANUNCIO),
        nullable=False,
        default="ACTIVO",
        index=True,
    )
    reactivaciones_count = db.Column(
        db.Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
        index=True,
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )

    usuario = db.relationship("Usuario", backref=db.backref("anuncios", lazy=True))

    def to_public_dict(self):
        precio = self.precio
        if isinstance(precio, Decimal):
            precio = float(precio)

        return {
            "id": self.id,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "categoria": self.categoria,
            "subcategoria": self.subcategoria,
            "condicion": self.condicion,
            "precio": precio,
            "especificaciones": self.especificaciones,
            "estado": self.estado,
            "reactivaciones_count": self.reactivaciones_count,
            "usuario_id": self.usuario_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

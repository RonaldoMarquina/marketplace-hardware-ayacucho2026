from decimal import Decimal, InvalidOperation

from marshmallow import Schema, ValidationError, fields, pre_load, validate, validates, validates_schema

from app.models.anuncio import (
    CATEGORIAS_ANUNCIO,
    CONDICIONES_ANUNCIO,
    SUBCATEGORIAS_ANUNCIO,
    SUBCATEGORIAS_POR_CATEGORIA,
)


class CrearAnuncioSchema(Schema):
    """Valida el body de HU-05 antes de tocar la base de datos."""

    titulo = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={"required": "El titulo es obligatorio."},
    )
    categoria = fields.String(
        required=True,
        validate=validate.OneOf(CATEGORIAS_ANUNCIO),
        error_messages={"required": "La categoria es obligatoria."},
    )
    subcategoria = fields.String(
        required=True,
        validate=validate.OneOf(SUBCATEGORIAS_ANUNCIO),
        error_messages={"required": "La subcategoria es obligatoria."},
    )
    condicion = fields.String(
        required=True,
        validate=validate.OneOf(CONDICIONES_ANUNCIO),
        error_messages={"required": "La condicion es obligatoria."},
    )
    precio = fields.Decimal(
        required=True,
        as_string=False,
        error_messages={"required": "El precio es obligatorio."},
    )
    descripcion = fields.String(
        required=True,
        validate=validate.Length(min=1),
        error_messages={"required": "La descripcion es obligatoria."},
    )
    especificaciones = fields.Dict(keys=fields.String(), values=fields.Raw(), allow_none=True, load_default=None)

    @pre_load
    def normalizar_entrada(self, data, **kwargs):
        if not isinstance(data, dict):
            raise ValidationError("El cuerpo de la solicitud debe ser JSON.")

        datos = data.copy()
        for campo in ("titulo", "categoria", "subcategoria", "condicion", "descripcion"):
            if isinstance(datos.get(campo), str):
                datos[campo] = datos[campo].strip()

        if isinstance(datos.get("categoria"), str):
            datos["categoria"] = datos["categoria"].upper()

        if isinstance(datos.get("subcategoria"), str):
            datos["subcategoria"] = _normalizar_taxonomia(datos["subcategoria"])

        if isinstance(datos.get("condicion"), str):
            datos["condicion"] = datos["condicion"].upper()

        return datos

    @validates("precio")
    def validar_precio(self, value, **kwargs):
        try:
            precio = Decimal(value)
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValidationError("El precio debe ser numerico.") from exc

        if precio <= 0:
            raise ValidationError("El precio debe ser mayor que 0.")

        if precio.as_tuple().exponent < -2:
            raise ValidationError("El precio no puede tener mas de 2 decimales.")

    @validates_schema
    def validar_subcategoria_corresponde_a_categoria(self, data, **kwargs):
        categoria = data.get("categoria")
        subcategoria = data.get("subcategoria")
        if not categoria or not subcategoria:
            return

        if subcategoria not in SUBCATEGORIAS_POR_CATEGORIA.get(categoria, ()): 
            raise ValidationError(
                "La subcategoria no corresponde a la categoria seleccionada.",
                field_name="subcategoria",
            )


class EditarAnuncioSchema(Schema):
    """Valida el PATCH parcial de HU-07 solo sobre campos editables."""

    titulo = fields.String(validate=validate.Length(min=1, max=100))
    categoria = fields.String(validate=validate.OneOf(CATEGORIAS_ANUNCIO))
    subcategoria = fields.String(validate=validate.OneOf(SUBCATEGORIAS_ANUNCIO))
    condicion = fields.String(validate=validate.OneOf(CONDICIONES_ANUNCIO))
    precio = fields.Decimal(as_string=False)
    descripcion = fields.String(validate=validate.Length(min=1))
    especificaciones = fields.Dict(
        keys=fields.String(),
        values=fields.Raw(allow_none=True),
        allow_none=True,
    )

    @pre_load
    def normalizar_entrada(self, data, **kwargs):
        if not isinstance(data, dict):
            raise ValidationError("El cuerpo de la solicitud debe ser JSON.")

        datos = data.copy()
        for campo in ("titulo", "categoria", "subcategoria", "condicion", "descripcion"):
            if isinstance(datos.get(campo), str):
                datos[campo] = datos[campo].strip()

        if isinstance(datos.get("categoria"), str):
            datos["categoria"] = datos["categoria"].upper()

        if isinstance(datos.get("subcategoria"), str):
            datos["subcategoria"] = _normalizar_taxonomia(datos["subcategoria"])

        if isinstance(datos.get("condicion"), str):
            datos["condicion"] = datos["condicion"].upper()

        return datos

    @validates("precio")
    def validar_precio(self, value, **kwargs):
        try:
            precio = Decimal(value)
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValidationError("El precio debe ser numerico.") from exc

        if precio <= 0:
            raise ValidationError("El precio debe ser mayor que 0.")

        if precio.as_tuple().exponent < -2:
            raise ValidationError("El precio no puede tener mas de 2 decimales.")


class ReordenarMediaSchema(Schema):
    """Valida la lista ordenada de IDs de imagenes."""

    orden = fields.List(
        fields.Integer(strict=True),
        required=True,
        validate=validate.Length(min=1),
        error_messages={"required": "El campo orden es obligatorio."},
    )


class BuscarAnunciosSchema(Schema):
    """Valida los query params publicos de HU-10."""

    categoria = fields.String(validate=validate.OneOf(CATEGORIAS_ANUNCIO))
    subcategoria = fields.String(
        validate=[
            validate.Length(min=1, max=50),
            validate.Regexp(
                r"^[A-Za-z0-9 ]+$",
                error="La subcategoria solo permite caracteres alfanumericos y espacios.",
            ),
        ]
    )
    condicion = fields.String(validate=validate.OneOf(CONDICIONES_ANUNCIO))
    precio_min = fields.Decimal(as_string=False)
    precio_max = fields.Decimal(as_string=False)
    q = fields.String(validate=validate.Length(min=2, max=100))
    order_by = fields.String(
        load_default="reciente",
        validate=validate.OneOf(("precio_asc", "precio_desc", "reciente")),
    )
    page = fields.Integer(load_default=1, validate=validate.Range(min=1))
    limit = fields.Integer(load_default=20, validate=validate.Range(min=1, max=50))

    @pre_load
    def normalizar_entrada(self, data, **kwargs):
        if not isinstance(data, dict):
            raise ValidationError("Los parametros de busqueda son invalidos.")

        datos = data.copy()
        for campo in (
            "categoria",
            "subcategoria",
            "condicion",
            "precio_min",
            "precio_max",
            "q",
            "order_by",
            "page",
            "limit",
        ):
            if isinstance(datos.get(campo), str):
                datos[campo] = datos[campo].strip()

        if isinstance(datos.get("categoria"), str):
            datos["categoria"] = datos["categoria"].upper()

        if isinstance(datos.get("condicion"), str):
            datos["condicion"] = datos["condicion"].upper()

        if isinstance(datos.get("order_by"), str):
            datos["order_by"] = datos["order_by"].lower()

        return datos

    @validates("precio_min")
    def validar_precio_min(self, value, **kwargs):
        _validar_decimal_positivo(value, "precio_min")

    @validates("precio_max")
    def validar_precio_max(self, value, **kwargs):
        _validar_decimal_positivo(value, "precio_max")

    @validates_schema
    def validar_rango_precios(self, data, **kwargs):
        precio_min = data.get("precio_min")
        precio_max = data.get("precio_max")
        if precio_min is not None and precio_max is not None and precio_min > precio_max:
            raise ValidationError(
                {"precio_min": ["precio_min no puede ser mayor que precio_max."]}
            )


def _normalizar_taxonomia(value):
    return value.upper().replace(" ", "_").replace("-", "_")


def _validar_decimal_positivo(value, field_name):
    try:
        precio = Decimal(value)
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValidationError(f"{field_name} debe ser numerico.") from exc

    if precio <= 0:
        raise ValidationError(f"{field_name} debe ser mayor que 0.")

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


def _normalizar_taxonomia(value):
    return value.upper().replace(" ", "_").replace("-", "_")

from marshmallow import Schema, ValidationError, fields, pre_load, validate, validates


class RegistroTiendaSchema(Schema):
    """Valida la entrada multipart/form-data de HU-02."""

    nombre_comercial = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={"required": "El nombre comercial es obligatorio."},
    )
    ruc = fields.String(
        required=True,
        validate=validate.Regexp(
            r"^\d{11}$",
            error="El RUC debe tener exactamente 11 digitos numericos.",
        ),
        error_messages={"required": "El RUC es obligatorio."},
    )
    direccion = fields.String(
        required=True,
        validate=validate.Length(min=1, max=200),
        error_messages={"required": "La direccion es obligatoria."},
    )
    telefono = fields.String(
        required=True,
        validate=validate.Regexp(
            r"^\d{9}$",
            error="El telefono debe tener exactamente 9 digitos numericos.",
        ),
        error_messages={"required": "El telefono es obligatorio."},
    )
    correo = fields.Email(
        required=True,
        validate=validate.Length(max=150),
        error_messages={
            "required": "El correo es obligatorio.",
            "invalid": "El correo no tiene un formato valido.",
        },
    )
    password = fields.String(
        required=True,
        validate=validate.Regexp(
            r"^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>]).{8,}$",
            error="La contrasena debe tener al menos 8 caracteres, una mayuscula, un numero y un caracter especial.",
        ),
        load_only=True,
        error_messages={"required": "El password es obligatorio."},
    )

    @pre_load
    def normalizar_entrada(self, data, **kwargs):
        if not hasattr(data, "items"):
            raise ValidationError("La solicitud debe enviarse como multipart/form-data.")

        datos_normalizados = dict(data.items())
        for campo in (
            "nombre_comercial",
            "ruc",
            "direccion",
            "telefono",
            "correo",
            "password",
        ):
            if isinstance(datos_normalizados.get(campo), str):
                datos_normalizados[campo] = datos_normalizados[campo].strip()

        if isinstance(datos_normalizados.get("correo"), str):
            datos_normalizados["correo"] = datos_normalizados["correo"].lower()

        return datos_normalizados

    @validates("ruc")
    def validar_ruc(self, value, **kwargs):
        if not value.isdigit() or len(value) != 11:
            raise ValidationError("El RUC debe tener exactamente 11 digitos numericos.")

    @validates("telefono")
    def validar_telefono(self, value, **kwargs):
        if not value.isdigit() or len(value) != 9:
            raise ValidationError(
                "El telefono debe tener exactamente 9 digitos numericos."
            )

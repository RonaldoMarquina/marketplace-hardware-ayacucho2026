from marshmallow import Schema, ValidationError, fields, pre_load, validate, validates


class RegistroUsuarioSchema(Schema):
    """Valida la entrada de HU-01 antes de llegar a la capa de servicio."""

    # El schema es la primera barrera de la arquitectura:
    # aqui validamos tipos, formatos y campos obligatorios antes de tocar la BD.
    nombre = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={"required": "El nombre es obligatorio."},
    )

    correo = fields.Email(
        required=True,
        validate=validate.Length(max=150),
        error_messages={
            "required": "El correo es obligatorio.",
            "invalid": "El correo no tiene un formato valido.",
        },
    )
    # La contraseña debe tener caracteres especiales, mayúsculas y mínimo 8 caracteres
    password = fields.String(
        required=True,
        validate=validate.Regexp(
            r"^(?=.*[A-Z])(?=.*[!@#$%^&*(),.?\":{}|<>]).{8,}$",
            error="La contraseña debe tener al menos 8 caracteres, una mayúscula y un carácter especial.",
        ),
        load_only=True,
        error_messages={"required": "El password es obligatorio."},
    )

    telefono = fields.String(
        required=True,
        validate=validate.Regexp(
            r"^\d{9}$",
            error="El telefono debe tener exactamente 9 digitos numericos.",
        ),
        error_messages={"required": "El telefono es obligatorio."},
    )

    @pre_load
    def normalizar_entrada(self, data, **kwargs):
        # Normalizar en el schema evita duplicar limpieza en controllers/services.
        # El correo se guarda en minusculas para hacer consistente la busqueda.
        if not isinstance(data, dict):
            raise ValidationError("El cuerpo de la solicitud debe ser JSON.")

        datos_normalizados = data.copy()
        for campo in ("nombre", "correo", "password", "telefono"):
            if isinstance(datos_normalizados.get(campo), str):
                datos_normalizados[campo] = datos_normalizados[campo].strip()

        if isinstance(datos_normalizados.get("correo"), str):
            datos_normalizados["correo"] = datos_normalizados["correo"].lower()

        return datos_normalizados

    @validates("telefono")
    def validar_telefono(self, value, **kwargs):
        # La HU-01 exige exactamente 9 digitos; no aceptamos espacios,
        # prefijos ni separadores porque el dato debe persistirse limpio.
        # No deveria duplicarse en la BD
        if not value.isdigit() or len(value) != 9:
            raise ValidationError(
                "El telefono debe tener exactamente 9 digitos numericos."
            )
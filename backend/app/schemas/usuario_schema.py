from marshmallow import Schema, ValidationError, fields, pre_load, validate, validates


PASSWORD_COMPLEXITY_REGEX = (
    r"^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>]).{8,}$"
)
PASSWORD_COMPLEXITY_MESSAGE = (
    "La contrasena debe tener al menos 8 caracteres, una mayuscula, un numero y un caracter especial."
)
JSON_BODY_REQUIRED_MESSAGE = "El cuerpo de la solicitud debe ser JSON."
PHONE_FORMAT_MESSAGE = "El telefono debe tener exactamente 9 digitos numericos."
EMAIL_REQUIRED_MESSAGE = "El correo es obligatorio."
EMAIL_INVALID_MESSAGE = "El correo no tiene un formato valido."
PASSWORD_REQUIRED_MESSAGE = "El password es obligatorio."


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
            "required": EMAIL_REQUIRED_MESSAGE,
            "invalid": EMAIL_INVALID_MESSAGE,
        },
    )
    # La contrasena debe tener caracteres especiales, mayusculas y minimo 8 caracteres.
    password = fields.String(
        required=True,
        validate=validate.Regexp(
            PASSWORD_COMPLEXITY_REGEX,
            error=PASSWORD_COMPLEXITY_MESSAGE,
        ),
        load_only=True,
        error_messages={"required": PASSWORD_REQUIRED_MESSAGE},
    )

    telefono = fields.String(
        required=True,
        validate=validate.Regexp(
            r"^\d{9}$",
            error=PHONE_FORMAT_MESSAGE,
        ),
        error_messages={"required": "El telefono es obligatorio."},
    )

    @pre_load
    def normalizar_entrada(self, data, **kwargs):
        # Normalizar aqui evita duplicar limpieza en controllers/services.
        # El correo se guarda en minusculas para hacer consistente la busqueda.
        if not isinstance(data, dict):
            raise ValidationError(JSON_BODY_REQUIRED_MESSAGE)

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
        if not value.isdigit() or len(value) != 9:
            raise ValidationError(PHONE_FORMAT_MESSAGE)


class LoginUsuarioSchema(Schema):
    """Valida la entrada de HU-04: correo + password para login."""

    correo = fields.Email(
        required=True,
        error_messages={
            "required": EMAIL_REQUIRED_MESSAGE,
            "invalid": EMAIL_INVALID_MESSAGE,
        },
    )
    password = fields.String(
        required=True,
        validate=validate.Length(min=1),
        load_only=True,
        error_messages={"required": PASSWORD_REQUIRED_MESSAGE},
    )

    @pre_load
    def normalizar_entrada(self, data, **kwargs):
        # En login solo normalizamos correo y espacios externos. La verificacion
        # real de credenciales queda en el service, no en el controller.
        if not isinstance(data, dict):
            raise ValidationError(JSON_BODY_REQUIRED_MESSAGE)

        datos_normalizados = data.copy()
        for campo in ("correo", "password"):
            if isinstance(datos_normalizados.get(campo), str):
                datos_normalizados[campo] = datos_normalizados[campo].strip()

        if isinstance(datos_normalizados.get("correo"), str):
            datos_normalizados["correo"] = datos_normalizados["correo"].lower()

        return datos_normalizados


class ForgotPasswordSchema(Schema):
    correo = fields.Email(
        required=True,
        error_messages={
            "required": EMAIL_REQUIRED_MESSAGE,
            "invalid": EMAIL_INVALID_MESSAGE,
        },
    )

    @pre_load
    def normalizar_entrada(self, data, **kwargs):
        if not isinstance(data, dict):
            raise ValidationError(JSON_BODY_REQUIRED_MESSAGE)

        datos = data.copy()
        if isinstance(datos.get("correo"), str):
            datos["correo"] = datos["correo"].strip().lower()
        return datos


class ResetPasswordSchema(Schema):
    token = fields.String(
        required=True,
        validate=validate.Length(min=1, max=128),
        error_messages={"required": "El token es obligatorio."},
    )
    password = fields.String(
        required=True,
        validate=validate.Regexp(
            PASSWORD_COMPLEXITY_REGEX,
            error=PASSWORD_COMPLEXITY_MESSAGE,
        ),
        load_only=True,
        error_messages={"required": PASSWORD_REQUIRED_MESSAGE},
    )

    @pre_load
    def normalizar_entrada(self, data, **kwargs):
        if not isinstance(data, dict):
            raise ValidationError(JSON_BODY_REQUIRED_MESSAGE)

        datos = data.copy()
        for campo in ("token", "password"):
            if isinstance(datos.get(campo), str):
                datos[campo] = datos[campo].strip()
        return datos


class HistorialTransaccionesSchema(Schema):
    tipo = fields.String(
        load_default="ambas",
        validate=validate.OneOf(("ventas", "compras", "ambas")),
    )

    @pre_load
    def normalizar_entrada(self, data, **kwargs):
        if not isinstance(data, dict):
            raise ValidationError("Los parametros son invalidos.")

        datos = data.copy()
        if isinstance(datos.get("tipo"), str):
            datos["tipo"] = datos["tipo"].strip().lower()
        return datos


class ActualizarPerfilSchema(Schema):
    nombre = fields.String(
        required=False,
        allow_none=False,
        validate=validate.Length(min=1, max=100),
    )
    telefono = fields.String(
        required=False,
        allow_none=False,
        validate=validate.Regexp(
            r"^\d{9}$",
            error=PHONE_FORMAT_MESSAGE,
        ),
    )
    nombre_comercial = fields.String(
        required=False,
        allow_none=False,
        validate=validate.Length(min=1, max=100),
    )
    direccion = fields.String(
        required=False,
        allow_none=False,
        validate=validate.Length(min=1, max=200),
    )

    @pre_load
    def normalizar_entrada(self, data, **kwargs):
        if not isinstance(data, dict):
            raise ValidationError(JSON_BODY_REQUIRED_MESSAGE)

        datos = data.copy()
        for campo in ("nombre", "telefono", "nombre_comercial", "direccion"):
            if isinstance(datos.get(campo), str):
                datos[campo] = datos[campo].strip()
        return datos


class ApelarModeracionSchema(Schema):
    mensaje = fields.String(
        required=True,
        allow_none=False,
        validate=validate.Length(min=10, max=1500),
        error_messages={"required": "El mensaje de apelacion es obligatorio."},
    )

    @pre_load
    def normalizar_entrada(self, data, **kwargs):
        if not isinstance(data, dict):
            raise ValidationError(JSON_BODY_REQUIRED_MESSAGE)

        datos = data.copy()
        if isinstance(datos.get("mensaje"), str):
            datos["mensaje"] = datos["mensaje"].strip()
        return datos


class ResolverApelacionAdminSchema(Schema):
    decision = fields.String(
        required=True,
        validate=validate.OneOf(("ACEPTAR", "RECHAZAR")),
        error_messages={"required": "La decision es obligatoria."},
    )
    motivo_admin = fields.String(
        required=True,
        validate=validate.Length(min=1, max=500),
        error_messages={"required": "El motivo administrativo es obligatorio."},
    )

    @pre_load
    def normalizar_entrada(self, data, **kwargs):
        if not isinstance(data, dict):
            raise ValidationError(JSON_BODY_REQUIRED_MESSAGE)

        datos = data.copy()
        if isinstance(datos.get("decision"), str):
            datos["decision"] = datos["decision"].strip().upper()
        if isinstance(datos.get("motivo_admin"), str):
            datos["motivo_admin"] = datos["motivo_admin"].strip()
        return datos


class AdminUsuariosFiltroSchema(Schema):
    estado = fields.String(
        required=False,
        allow_none=True,
        validate=validate.OneOf((
            "ACTIVO",
            "PENDIENTE_VERIFICACION",
            "EN_REVISION",
            "BLOQUEADO",
            "RECHAZADO",
        )),
    )
    rol = fields.String(
        required=False,
        allow_none=True,
        validate=validate.OneOf(("USER_ESTANDAR", "TIENDA_VERIFICADA")),
    )
    q = fields.String(required=False, allow_none=True, validate=validate.Length(min=2, max=100))

    @pre_load
    def normalizar_entrada(self, data, **kwargs):
        if not isinstance(data, dict):
            raise ValidationError("Los parametros son invalidos.")

        datos = data.copy()
        for campo in ("estado", "rol", "q"):
            if isinstance(datos.get(campo), str):
                datos[campo] = datos[campo].strip()
        if isinstance(datos.get("estado"), str):
            datos["estado"] = datos["estado"].upper()
        if isinstance(datos.get("rol"), str):
            datos["rol"] = datos["rol"].upper()
        return datos


class MotivoAdminUsuarioSchema(Schema):
    motivo = fields.String(
        required=True,
        validate=validate.Length(min=1, max=500),
        error_messages={"required": "El motivo es obligatorio."},
    )

    @pre_load
    def normalizar_entrada(self, data, **kwargs):
        if not isinstance(data, dict):
            raise ValidationError(JSON_BODY_REQUIRED_MESSAGE)

        datos = data.copy()
        if isinstance(datos.get("motivo"), str):
            datos["motivo"] = datos["motivo"].strip()
        return datos

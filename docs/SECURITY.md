# SECURITY.md — HardwareAyacucho

## Autenticación

- JWT HS256, vigencia 8h, secret en `.env` como `JWT_SECRET`.
- Sin refresh token en MVP.
- `jwt_required()` en todos los endpoints protegidos.
- Rutas `/admin/*`: `jwt_required()` → `check_admin_role()` encadenados.

## Contraseñas

- bcrypt con salt=10.
- Nunca retornar ni loggear `password_hash`.
- Mensaje idéntico para correo inexistente y password incorrecto → previene enumeración de usuarios.

## Rate Limiting

| Endpoint | Límite | Bloqueo |
|----------|--------|---------|
| `POST /auth/login` | 5 intentos fallidos por IP | 15 min |
| `POST /auth/verify-email/resend` | 3 requests por IP/usuario | 15 min |

## Tokens de Verificación

- Generados con `secrets.token_hex(32)` (64 chars hex).
- Vigencia 24h, un solo uso, un token activo por usuario.
- Índice en columna `token` para búsqueda eficiente.

## Archivos Subidos

- Validar mimetype real, no solo extensión.
- Nombre siempre reemplazado por `{uuid}-{timestamp}.{ext}`.
- Ruta guardada en BD como relativa, nunca absoluta.
- `/uploads/` en `.gitignore`.
- Límites: 2MB imágenes de anuncio / 5MB documento de tienda.

## Queries SQL

- Siempre prepared statements o SQLAlchemy ORM.
- Nunca interpolación de strings en queries.
- Escapar `%`, `_`, `\` antes de queries LIKE (campo `q`).
- `spec_key` solo alfanumérico + guion bajo (validar con regex).

## Datos Sensibles

- `password_hash` nunca en ninguna respuesta.
- `telefono` del vendedor solo visible con JWT válido (HU-11).
- `usuario_id` siempre extraído del JWT, nunca del body.
- No exponer stack traces en producción — solo loggear internamente.

## Variables de Entorno (`.env`)

```
JWT_SECRET=
DB_HOST=
DB_PORT=
DB_NAME=
DB_USER=
DB_PASSWORD=
MAIL_SERVER=
MAIL_USER=
MAIL_PASSWORD=
FRONTEND_URL=
```

- `.env` en `.gitignore`.
- `.env.example` en el repo sin valores reales.

## Borrado Lógico

- Nunca ejecutar `DELETE` en BD.
- Estados: `INACTIVO`, `VENDIDO`, `BLOQUEADO` ocultan el recurso.
- `moderacion_log` es auditoría permanente — `ON DELETE RESTRICT`.
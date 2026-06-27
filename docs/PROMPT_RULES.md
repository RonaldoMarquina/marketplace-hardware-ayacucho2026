# PROMPT_RULES.md — HardwareAyacucho

Reglas para agentes IA (Cursor, Copilot, Codex). Leer antes de generar cualquier código.

## Contexto del Proyecto

- Plataforma de anuncios de hardware para Ayacucho, Perú.
- Backend: Flask + SQLAlchemy + MySQL.
- Frontend: React.js + Tailwind CSS.
- Docs de referencia: `PROJECT.md`, `STACK.md`, `API_GUIDE.md`, `DATABASE.md`.

## Reglas Generales

- Leer los archivos de `/docs` antes de generar código.
- No inventar endpoints, tablas ni campos que no estén en las HUs.
- No agregar librerías fuera del `STACK.md` sin preguntar.
- No usar `DELETE` físico — siempre borrado lógico vía `PATCH`.
- Campos en `snake_case` en todo el proyecto.
- Fechas en ISO 8601.

## Backend Flask

- `usuario_id` siempre del JWT (`get_jwt_identity()`), nunca del body.
- Validar con Marshmallow antes de tocar la BD.
- ENUMs validados en Marshmallow, no en lógica manual.
- Queries siempre con SQLAlchemy ORM o prepared statements — nunca f-strings SQL.
- Transacciones con `db.session` — `commit()` al final, `rollback()` en excepción.
- Contraseñas con `bcrypt`, salt=10. Nunca loggear ni retornar password.
- JWT secret desde `os.environ['JWT_SECRET']`.
- Errores con estructura `{ "success": false, "error": "CODE", "message": "..." }`.
- Rutas `/admin/*` con middlewares encadenados: `jwt_required()` → `check_admin_role()`.

## Base de Datos

- Respetar exactamente el esquema de `DATABASE.md` y `database.sql`.
- No alterar nombres de tablas ni columnas.
- Índices definidos en el esquema — no agregar nuevos sin justificación.
- `especificaciones` es columna `JSON` — acceder con `JSON_EXTRACT` + prepared statement.

## Frontend React

- Llamadas HTTP con Axios.
- JWT almacenado en memoria o `httpOnly cookie` — nunca en `localStorage`.
- Manejar `telefono: null` del vendedor sin romper el render.
- `imagen_principal` puede ser `null` — mostrar placeholder.
- Paginación con params `?page=&limit=`.

## Seguridad

- No hardcodear secrets, URLs ni credenciales.
- No exponer stack traces en respuestas de error.
- Escapar `%`, `_`, `\` antes de queries LIKE.
- Validar mimetype real de archivos, no solo extensión.
- Ver `SECURITY.md` para reglas completas.

## Lo que NO debe hacer el agente

- ❌ Crear endpoints no definidos en `API_GUIDE.md`
- ❌ Usar `DELETE` en BD
- ❌ Poner `usuario_id` en el body del request
- ❌ Retornar `password_hash` en ninguna respuesta
- ❌ Instalar dependencias fuera del `STACK.md`
- ❌ Usar interpolación de strings en queries SQL
- ❌ Guardar el nombre original de archivos subidos
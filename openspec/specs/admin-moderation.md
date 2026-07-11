# OS-03 - Administracion y Moderacion

## Objetivo

Definir las reglas de gestion administrativa sobre anuncios reportados, usuarios
y solicitudes de tienda.

## Historias relacionadas

- HU-13
- HU-20

## Reglas funcionales clave

- solo usuarios con rol `ADMIN` acceden a rutas administrativas
- los compradores pueden reportar anuncios
- el administrador puede bloquear o desbloquear anuncios
- el administrador puede bloquear o desbloquear usuarios segun flujo permitido
- las acciones administrativas deben quedar registradas

## Reglas tecnicas clave

- el control de rol se valida en backend
- las operaciones de moderacion generan trazabilidad en logs
- el modulo debe responder con errores claros cuando el actor no tiene permiso

## Artefactos vinculados

- `backend/app/controllers/admin_controller.py`
- `backend/app/services/admin_user_service.py`
- `backend/app/models/reporte.py`
- `backend/app/models/admin_log.py`
- `backend/app/models/moderacion_log.py`
- `backend/tests/integration/test_moderacion_anuncios.py`
- `backend/tests/integration/test_admin_usuarios.py`

## Validacion esperada

- PyTest para control de rol y moderacion
- Postman para evidencia manual de endpoints admin
- SonarQube para control de calidad sobre cambios nuevos

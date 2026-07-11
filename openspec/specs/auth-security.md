# OS-01 - Autenticacion y Seguridad

## Objetivo

Definir las reglas del ciclo de acceso, verificacion de identidad y proteccion
de credenciales en la plataforma.

## Historias relacionadas

- HU-01
- HU-02
- HU-03
- HU-04
- HU-21

## Reglas funcionales clave

- todo usuario inicia como pendiente de verificacion
- el acceso requiere correo verificado y estado permitido
- el login usa JWT para autenticacion
- las solicitudes protegidas consumen JWT por header Authorization
- la recuperacion de contrasena usa token temporal de un solo uso

## Reglas tecnicas clave

- secretos de app y JWT deben resolverse desde variables de entorno
- en testing se permite secreto efimero para no bloquear la suite
- los tokens JWT no se almacenan en cookies del navegador
- las sesiones endurecen `HttpOnly`, `SameSite` y `Secure` en produccion
- la API JSON queda exenta de CSRF tradicional porque no depende de formularios
  server-rendered autenticados por cookie

## Artefactos vinculados

- `backend/app/__init__.py`
- `backend/app/services/auth_service.py`
- `backend/app/controllers/auth_controller.py`
- `backend/app/models/token_verificacion.py`
- `backend/tests/integration/test_login.py`
- `backend/tests/integration/test_verificacion_email.py`
- `backend/tests/integration/test_password_reset.py`

## Validacion esperada

- PyTest para login, verificacion y reset
- SonarQube para hotspots y seguridad estatica
- Pylint para convenciones del backend

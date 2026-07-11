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
- produccion publica requiere un canal real de correo transaccional para
  verificacion y recuperacion de cuentas
- los tokens reutilizables de reset password no deben persistirse en claro
- un cambio exitoso de contrasena debe invalidar JWT emitidos antes del reset
- el flujo de recuperacion debe dejar trazas auditables sin exponer secretos
- Google login sigue fuera de alcance y puede implementarse en un cambio
  posterior

## Escenarios normativos

### Verificacion y correo real

#### Scenario: Successful email verification delivery is required for public production
- **WHEN** a user registration or store registration creates an email
  verification token in a public production environment
- **THEN** the system MUST attempt delivery through a configured real email
  provider instead of relying only on application logs

#### Scenario: Password reset delivery uses a real email channel
- **WHEN** an active account requests password recovery in a public production
  environment
- **THEN** the system MUST attempt delivery of the reset link through the
  configured real email provider

#### Scenario: Testing avoids external email delivery
- **WHEN** automated tests execute registration, verification resend or password
  reset flows
- **THEN** the system MUST avoid sending real emails and MUST keep the flows
  testable without external provider credentials

#### Scenario: Public production without email configuration is not considered ready
- **WHEN** the deployment checklist or technical documentation is reviewed for a
  public production release
- **THEN** the project MUST treat real transactional email configuration as a
  prerequisite for public launch of the current authentication flows

### Hardening de recuperacion

#### Scenario: Reset tokens reduce impact of database disclosure
- **WHEN** the system issues a password reset token
- **THEN** the reset flow MUST avoid persisting the reusable plain token value
  in a way that would let a database reader directly use it

#### Scenario: Password reset invalidates prior authenticated sessions
- **WHEN** a password reset completes successfully
- **THEN** the system MUST invalidate or reject authentication tokens issued
  before the credential change

#### Scenario: Password reset remains non-enumerating
- **WHEN** a password recovery request is sent for an unknown, inactive or
  blocked account
- **THEN** the API MUST keep a generic external response that does not confirm
  whether the account is recoverable

#### Scenario: Reset flow emits security audit signals
- **WHEN** password reset is requested, rate-limited, completed or rejected
- **THEN** the system MUST record enough operational evidence to investigate
  abuse without exposing secrets in logs

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

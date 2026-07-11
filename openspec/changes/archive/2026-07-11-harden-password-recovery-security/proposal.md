## Why

La recuperacion de contrasena ya funciona, pero en una salida publica sigue
siendo un flujo de alto riesgo: un atacante puede abusar solicitudes de reset,
aprovechar tokens filtrados y mantener sesiones activas incluso despues de que
la contrasena cambie.

## What Changes

- endurecer el flujo de recuperacion de contrasena con controles adicionales de
  abuso y revocacion
- reducir el impacto de filtracion de tokens de reset
- mejorar trazabilidad y señales operativas del proceso de recuperacion
- dejar `Google login` fuera de alcance: este cambio protege el flujo actual por
  correo, no agrega autenticacion federada

## Capabilities

### New Capabilities

### Modified Capabilities

- `auth-security`: la recuperacion de contrasena adopta controles mas fuertes de
  almacenamiento, uso y revocacion de tokens y sesiones

## Impact

- backend: `auth_service`, repositorios de auth, modelo de tokens y JWT
- testing: nuevas pruebas de seguridad para password reset
- documentacion tecnica: seguridad, testing y criterios operativos
- operacion: monitoreo de solicitudes de reset y manejo de eventos sensibles

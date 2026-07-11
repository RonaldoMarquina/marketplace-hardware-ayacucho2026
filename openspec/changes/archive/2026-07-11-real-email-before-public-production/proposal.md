## Why

El backend ya implementa registro, verificacion de correo y recuperacion de
contrasena, pero hoy el envio real de correos no existe: los enlaces solo se
registran en logs. Antes de una produccion publica, eso deja incompletos los
flujos de activacion y recuperacion de cuenta.

## What Changes

- integrar envio real de correos para verificacion de cuenta y reset de
  contrasena
- formalizar variables de entorno y configuracion operativa para un proveedor de
  correo transaccional
- ajustar backend y testing para que el sistema pueda distinguir entre entorno
  local, testing y produccion publica
- documentar que `Google login` queda fuera de alcance en este cambio y se
  tratara como mejora posterior

## Capabilities

### New Capabilities

### Modified Capabilities

- `auth-security`: la autenticacion y recuperacion de cuenta pasan de enlaces
  solo en logs a entrega real de correo previa a produccion publica

## Impact

- backend: `auth_service`, configuracion de aplicacion y manejo de correo
- testing: cobertura para integracion del adaptador de correo y fallback de
  entornos
- documentacion tecnica: despliegue, seguridad y flujo de autenticacion
- operacion: credenciales SMTP o proveedor transaccional, remitente verificado y
  politica de errores para envio

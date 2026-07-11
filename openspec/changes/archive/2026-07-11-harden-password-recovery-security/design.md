## Context

El proyecto ya implementa reset password por correo real, pero todavia hay
controles de seguridad que conviene reforzar antes de una salida publica. Hoy
los tokens de reset se persisten en claro, el cambio de contrasena no invalida
JWT ya emitidos y el sistema no deja una auditoria suficientemente fuerte para
investigar abuso del flujo.

La meta de este cambio no es hacer el flujo “mas dificil” para el usuario
legitimo, sino volverlo mas resistente contra:

- reuso o filtracion de tokens
- abuso automatizado del endpoint de reset
- secuestro de cuenta con sesiones viejas aun validas
- baja trazabilidad despues de un incidente

## Goals / Non-Goals

**Goals:**

- evitar que un token expuesto tenga valor duradero o reutilizable
- invalidar sesiones previas despues de un cambio de contrasena
- fortalecer reglas de rate limit y auditoria del flujo de reset
- mantener una UX razonable para usuarios legitimos

**Non-Goals:**

- no reemplazar el flujo de correo por `Google login`
- no redisenar el modelo completo de autenticacion del proyecto
- no introducir MFA completo en esta etapa

## Decisions

### 1. Persistir solo huella de tokens de reset

Se propone almacenar hash del token de reset, no el valor plano. El enlace por
correo seguira conteniendo el token real, pero la base solo conservara una
representacion irreversible para comparacion.

Alternativas consideradas:

- seguir guardando tokens en claro
- cifrar el token reversible en base de datos

Razones para no elegirlas:

- la primera amplifica el impacto de una lectura indebida de base
- la segunda agrega complejidad innecesaria frente a un hash suficiente

### 2. Revocar sesiones activas tras cambio de contrasena

El reset password exitoso debe invalidar JWT o al menos dejar una marca de
version/fecha de credencial para rechazar tokens viejos.

Alternativas consideradas:

- conservar sesiones activas por comodidad
- forzar solo nuevo login sin invalidacion efectiva

Razones para no elegirlas:

- ambas dejan una ventana donde un atacante con token previo sigue autenticado

### 3. Endurecer abuso sin romper UX

Se reforzaran limites por IP/correo, señales de auditoria y mensajes
consistentes. La respuesta seguira siendo generica para no enumerar cuentas.

Alternativas consideradas:

- endurecer con CAPTCHA inmediato
- mantener solo el rate limit actual

Razones para no elegirlas:

- la primera agrega friccion temprana innecesaria
- la segunda puede quedarse corta ante abuso distribuido o sostenido

## Risks / Trade-offs

- [Mayor complejidad en validacion de tokens] -> Mitigar con pruebas unitarias e
  integracion del nuevo almacenamiento
- [Invalidacion de sesiones puede sorprender al usuario] -> Mitigar con mensaje
  claro post-reset y redireccion a login
- [Auditoria excesiva puede exponer datos sensibles] -> Mitigar registrando solo
  metadatos utiles sin secretos ni contrasenas
- [Cambios en JWT pueden tocar varias rutas] -> Mitigar con estrategia de
  versionado o marca temporal acotada al servicio auth

## Open Questions

- conviene usar `password_changed_at` o un contador de version de credenciales
- si la auditoria de reset necesita modelo propio o alcanza con logging
- si una segunda fase deberia agregar CAPTCHA o challenge adaptativo

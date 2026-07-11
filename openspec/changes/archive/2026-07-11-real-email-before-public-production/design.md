## Context

El proyecto ya emite tokens de verificacion y reset password, pero actualmente
`AuthService` solo construye el enlace y lo escribe en logs. Eso es suficiente
para desarrollo local, pero no para una produccion publica donde el usuario
debe recibir realmente el mensaje para activar su cuenta o recuperar acceso.

El cambio cruza varias capas: configuracion de aplicacion, servicio de
autenticacion, dependencias externas y documentacion operativa. Tambien hay una
decision de alcance importante: `Google login` no es prerequisito para salir a
produccion publica, mientras que correo real si lo es.

## Goals / Non-Goals

**Goals:**

- habilitar envio real de correos para verificacion de cuenta y reset password
- mantener el comportamiento actual de testing sin depender de un proveedor
  externo
- dejar clara la configuracion minima necesaria antes de produccion publica
- separar este prerrequisito de autenticacion del trabajo futuro de `Google
  login`

**Non-Goals:**

- no implementar `Google login` en este cambio
- no redisenar los flujos de registro, login o reset ya existentes
- no introducir una plataforma completa de marketing o notificaciones

## Decisions

### 1. Introducir un adaptador de correo transaccional

Se incorporara una abstraccion de envio de correo para que `AuthService` no
dependa directamente de `logging` ni de un proveedor especifico.

Alternativas consideradas:

- seguir enviando enlaces solo a logs
- invocar un proveedor externo directamente desde `AuthService`

Razones para no elegirlas:

- la primera bloquea una salida publica usable
- la segunda acopla demasiado la logica de autenticacion con detalles de
  infraestructura

### 2. Mantener un modo seguro para desarrollo y testing

En `TESTING` no se debe enviar correo real. En desarrollo local puede existir un
modo fallback que registre enlaces o use un backend simulado, pero produccion
publica debe exigir configuracion valida.

Alternativas consideradas:

- obligar siempre a usar un proveedor real
- permitir que produccion siga degradando silenciosamente a logs

Razones para no elegirlas:

- la primera vuelve mas fragil el desarrollo local
- la segunda oculta una falla critica de salida a produccion

### 3. Tratar correo real como gate de produccion publica

La documentacion y el despliegue deben expresar que la app no esta lista para
produccion publica si no puede enviar correos transaccionales reales.

Alternativas consideradas:

- desplegar primero y dejar correo como mejora opcional
- priorizar `Google login` antes de correo real

Razones para no elegirlas:

- la primera deja incompletos flujos base de recuperacion y verificacion
- la segunda mejora la comodidad de acceso, pero no resuelve la necesidad minima
  del sistema actual

## Risks / Trade-offs

- [Configuracion sensible de credenciales de correo] -> Mitigar con variables de
  entorno, remitente validado y documentacion de secretos
- [Fallas transitorias del proveedor] -> Mitigar con manejo de errores claro,
  logging operativo y pruebas del adaptador
- [Diferencias entre entornos local y produccion] -> Mitigar con modos
  explicitos y validacion de configuracion al arrancar
- [Acoplamiento a un proveedor especifico] -> Mitigar usando un adaptador con
  interfaz estable

## Migration Plan

1. definir configuracion y adaptador de correo
2. conectar verificacion de cuenta y reset password al adaptador
3. cubrir pruebas unitarias o de integracion del envio
4. documentar precondiciones de despliegue para produccion publica
5. validar el flujo completo con credenciales reales en entorno controlado

## Open Questions

- que proveedor se usara primero: SMTP tradicional, Resend, SendGrid u otro
- si produccion debe fallar al arrancar cuando falte configuracion de correo o
  solo bloquear rutas sensibles
- si el remitente y las plantillas se gestionaran desde backend o desde el
  proveedor elegido

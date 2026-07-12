## Context

Hoy la plataforma ya tiene backend para registrar reportes de anuncios con
motivos cerrados, limite diario, proteccion contra autoreporte y duplicidad por
ciclo activo. Tambien existe un panel administrativo para revisar anuncios
reportados y decidir si se bloquean o desbloquean.

La brecha esta en la experiencia publica: el usuario autenticado puede
contactar por WhatsApp, pero no tiene una accion visible para denunciar un
anuncio sospechoso. En la practica, eso vuelve invisible una capacidad de
moderacion ya desarrollada.

## Goals / Non-Goals

**Goals:**

- hacer visible y entendible el reporte de anuncios desde el detalle publico
- permitir solo reportes autenticados y no propietarios del anuncio
- reutilizar los motivos ya soportados por backend
- mantener la decision de bloqueo bajo revision administrativa, no automatica
- reforzar el flujo con mensajes y restricciones claras contra abuso

**Non-Goals:**

- no crear un sistema automatico de bloqueo por cantidad de reportes
- no introducir reputacion avanzada o machine learning de fraude en este cambio
- no redisenar por completo el panel administrativo existente
- no reemplazar el modelo actual de motivos cerrados por texto libre total

## Decisions

### 1. Mostrar el reporte solo a usuarios autenticados que no sean propietarios

El detalle del anuncio mostrara `Reportar anuncio` solo cuando el usuario haya
iniciado sesion y no sea el duenio del anuncio.

Razones:

- evita exponer un CTA inutil al propietario
- reduce friccion y ruido para visitantes anonimos
- se alinea con la regla backend que exige JWT y evita autoreporte

### 2. Usar un modal con motivos cerrados y mensaje educativo

La UI pedira al usuario elegir uno de los motivos ya soportados:
`FRAUDE`, `PRECIO_ENGANOSO`, `PRODUCTO_FALSO`, `CONTENIDO_INAPROPIADO`,
`DUPLICADO`, `OTRO`.

El modal debe explicar que:

- el reporte sera revisado por administracion
- reportar no bloquea el anuncio automaticamente
- reportes duplicados o abusivos pueden ser rechazados por el sistema

Razones:

- reduce ambiguedad
- hace visible el criterio humano de moderacion
- evita que el usuario espere una baja inmediata del anuncio

### 3. Mantener controles antiabuso simples y efectivos

Se conservaran y explicitaran estas reglas:

- cuenta activa obligatoria
- no autoreporte
- no duplicidad del mismo usuario sobre el mismo anuncio en el mismo ciclo
- limite diario de 10 reportes por usuario

Adicionalmente, para `OTRO` se recomienda pedir un detalle breve opcional o
validar un comentario minimo en una segunda iteracion si el equipo detecta abuso
real.

Razones:

- ya existe una base de hardening util en backend
- evita complejidad innecesaria para esta fase
- deja espacio para endurecer solo si el uso real lo exige

### 4. Mantener la moderacion como decision administrativa

Ni el frontend ni el backend publico deben cambiar el estado del anuncio por el
solo hecho de recibir reportes. El panel admin sigue siendo el punto de cierre.

Razones:

- reduce falsos positivos
- protege a vendedores legitimos
- conserva trazabilidad y criterio humano

## Risks / Trade-offs

- [Mas friccion visual en detalle de anuncio] -> Mitigar con un CTA secundario
  discreto y modal breve
- [Usuarios que esperan bloqueo automatico] -> Mitigar con mensajes claros de
  revision manual
- [Abuso del motivo `OTRO`] -> Mitigar con reglas actuales y opcion futura de
  comentario obligatorio o reputacion
- [Diferencias entre mensajes frontend y errores backend] -> Mitigar alineando
  copy con codigos `409`, `422` y `429`

## Migration Plan

1. agregar CTA de reporte en detalle de anuncio para usuarios elegibles
2. conectar modal de motivos con el endpoint ya existente
3. mostrar mensajes claros segun respuesta del backend
4. cubrir pruebas de interfaz y flujo de negocio
5. actualizar specs y documentacion funcional de moderacion

## Open Questions

- si `OTRO` debe salir ya con comentario obligatorio o quedar solo como motivo
  cerrado en esta fase
- si el historial del usuario reportante debe mostrarse luego al admin
- si conviene ocultar temporalmente el CTA a cuentas `PENDIENTE_VERIFICACION` en
  frontend ademas de bloquearlas en backend

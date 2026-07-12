# Base de Datos

## Fuente de verdad

El archivo fuente del esquema es `docs/database.sql`. Este documento solo
resume la estructura funcional y las reglas principales para facilitar lectura
humana.

## Motor y acceso

- Motor: MySQL
- ORM principal del backend: SQLAlchemy
- Charset: `utf8mb4`
- Collation: `utf8mb4_unicode_ci`

## Tablas principales

- `usuarios`
- `tiendas`
- `tokens_verificacion`
- `anuncios`
- `media_anuncio`
- `reportes`
- `reporte_evidencias`
- `apelaciones_moderacion`
- `apelacion_evidencias`
- `moderacion_log`
- `admin_log`
- `transacciones`
- `calificaciones`
- `contactos_log`

## Relaciones clave

- un `usuario` puede tener muchos `anuncios`
- un `usuario` puede tener una `tienda`
- un `anuncio` puede tener multiples registros en `media_anuncio`
- un `anuncio` puede generar `reportes`, `contactos_log` y `transacciones`
- un `reporte` puede generar multiples `reporte_evidencias`
- una `apelacion_moderacion` puede generar multiples `apelacion_evidencias`
- una `transaccion` puede generar `calificaciones`

## Reglas generales

- claves primarias enteras autoincrementales
- claves foraneas con sufijo `_id`
- fechas de auditoria con `created_at` y, cuando aplica, `updated_at`
- uso de estados para moderacion, activacion y ciclo de vida
- `especificaciones` de anuncios almacenadas en JSON

## Reglas de negocio relevantes

- correos, telefonos, RUC y tokens sensibles usan restricciones de unicidad
- un anuncio puede pasar por estados como `ACTIVO`, `INACTIVO`, `VENDIDO` o
  `BLOQUEADO`
- los flujos de verificacion y recuperacion usan `tokens_verificacion`
- la moderacion administrativa queda auditada en `moderacion_log` y `admin_log`
- un `reporte` puede incluir `detalle` descriptivo y evidencias adjuntas del
  reportante
- un anuncio bloqueado puede recibir una sola `apelacion_moderacion` por ciclo
  de bloqueo y esa apelacion puede adjuntar evidencias propias
- las transacciones y calificaciones soportan reputacion de comprador y vendedor

## Recomendacion

Cuando exista una diferencia entre este resumen y `database.sql`, se debe tomar
como valido `database.sql`.

Para cambios incrementales sobre una base ya existente, el proyecto puede dejar
scripts de migracion auxiliares en `scripts/`. En la fase 1 del reporte
enriquecido se agrego `scripts/migrate-moderation-phase1.py` para aplicar los
cambios de `reportes` y `reporte_evidencias` sobre una BD local existente. En
la fase 2 se agrega `scripts/migrate-moderation-phase2.py` para crear
`apelaciones_moderacion` y `apelacion_evidencias`.

La fase 3 de priorizacion y abuso no agrega tablas nuevas en esta iteracion:
trabaja con metricas derivadas calculadas a partir de `usuarios`, `reportes`,
`anuncios`, `moderacion_log` y `transacciones`.

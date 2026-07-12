## Why

El proyecto ya soporta reportes de anuncios y revision administrativa basica,
pero todavia falta convertir esa capacidad en un sistema de moderacion mas
robusto, justo y defendible. Hoy el reporte se limita practicamente a un motivo
cerrado, sin evidencia, sin descargo del vendedor y sin flujo formal de
apelacion.

Si la plataforma quiere madurar antes o despues del despliegue, conviene
planificar esa evolucion por fases para no mezclar una mejora razonable de corto
plazo con una solucion demasiado grande en un solo cambio.

## What Changes

- definir una hoja de ruta en tres fases para robustecer la moderacion de
  anuncios reportados
- formalizar fase 1 como mejora inmediata del reporte con detalle y evidencias
- formalizar fase 2 como flujo de apelacion y descargo para vendedor o tienda
- formalizar fase 3 como capa avanzada de reputacion, priorizacion y deteccion
  de abuso

## Capabilities

### Modified Capabilities

- `admin-moderation`: la moderacion pasa de reportes basicos a casos con mejor
  evidencia, respuesta del denunciado y evolucion futura de priorizacion
- `marketplace-core`: el detalle del anuncio y los paneles relacionados pasan a
  soportar reportes mas completos y futuras apelaciones

## Impact

- frontend: detalle del anuncio, panel admin y potencial panel de vendedor o
  tienda
- backend: endpoints de reporte, detalle de caso, resolucion y apelacion
- base de datos: tablas o campos nuevos para evidencia, descargos y estados de
  caso
- testing y documentacion: reglas nuevas de moderacion, abuso y flujo de vida
  del caso

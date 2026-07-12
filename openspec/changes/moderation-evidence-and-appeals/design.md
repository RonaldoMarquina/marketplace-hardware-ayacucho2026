## Context

Actualmente el sistema ya soporta:

- reporte de anuncio por motivo cerrado
- restricciones basicas antiabuso como no autoreporte, no duplicidad por ciclo
  y limite diario
- revision administrativa de anuncios reportados
- bloqueo y desbloqueo manual por administracion

Lo que todavia no existe es una nocion mas rica de `caso de moderacion` con
evidencia, defensa del vendedor y apelacion. Sin eso, las decisiones pueden ser
mas dificiles de justificar y los actores afectados no tienen una via clara de
respuesta.

## Goals / Non-Goals

**Goals:**

- dividir la evolucion de moderacion en tres fases entendibles
- priorizar una primera fase util y alcanzable antes de intentar automatismos
- mejorar la calidad de la evidencia para administracion
- introducir un camino futuro de apelacion y una capa posterior de inteligencia
  operativa

**Non-Goals:**

- no implementar las tres fases de golpe
- no automatizar bloqueo por simple volumen bruto de reportes
- no introducir machine learning real en la primera iteracion

## Decisions

### 1. Fase 1: reporte enriquecido con evidencia

La primera fase debe enfocarse en mejorar la calidad del reporte original sin
romper el flujo actual.

Incluye:

- motivo de reporte
- detalle textual del reportante
- evidencia adjunta limitada
- mejor vista admin del caso
- resolucion administrativa con motivo obligatorio

Razones:

- aumenta la calidad de la decision admin
- tiene valor inmediato
- afecta varias capas, pero sigue siendo acotable

### 2. Fase 2: apelacion y descargo del vendedor o tienda

La segunda fase agrega equilibrio procesal: el denunciado puede responder o
apelar.

Incluye:

- descargo del vendedor o tienda
- evidencia de defensa
- estado de apelacion
- plazos y una sola apelacion por caso resuelto

Razones:

- evita decisiones unilaterales sin contexto
- mejora justicia y trazabilidad del sistema
- encaja mejor despues de tener casos mas ricos en fase 1

### 3. Fase 3: reputacion, priorizacion y abuso avanzado

La tercera fase agrega inteligencia operativa, no solo CRUD.

Incluye:

- peso o reputacion del reportante
- score de severidad del caso
- priorizacion de cola admin
- deteccion de abuso repetido de reportes
- señales de riesgo para cuentas nuevas o patron sospechoso

Razones:

- es util cuando ya existe historial suficiente
- seria prematuro sin evidencia, descargos y estados mas maduros
- debe tratarse como evolucion avanzada, no como prerequisito del despliegue

## Phase Breakdown

### Fase 1

**Objetivo:**

Dar al administrador evidencia suficiente para tomar mejores decisiones.

**Backend:**

- ampliar el endpoint de reporte para aceptar `detalle`
- soportar evidencias adjuntas o referencias controladas
- exponer detalle completo del caso al admin
- registrar motivo admin de resolucion y estado del caso

**Frontend:**

- formulario de reporte con motivo y descripcion
- carga limitada de evidencias
- vista admin con detalle del caso, evidencia y accion de resolver

**Base de datos:**

- ampliar `reportes` con descripcion y metadatos de resolucion
- agregar tabla de evidencias de reporte

### Fase 2

**Objetivo:**

Permitir que vendedor o tienda presenten descargo o apelacion de forma trazable.

**Backend:**

- endpoints de apelacion
- validacion de plazo y unicidad de apelacion
- evidencia de defensa

**Frontend:**

- panel de estado del caso para vendedor o tienda
- formulario de apelacion
- vista admin de apelaciones

**Base de datos:**

- tabla de apelaciones
- opcional tabla de evidencias de apelacion

### Fase 3

**Objetivo:**

Optimizar la moderacion con priorizacion y control avanzado de abuso.

**Backend:**

- calculo de score de confianza o severidad
- priorizacion de cola
- reglas de reputacion o abuso

**Frontend:**

- panel admin con orden inteligente
- indicadores de riesgo y confianza

**Base de datos:**

- campos historicos o estructuras para score, señales y estadisticas

## Risks / Trade-offs

- [Mayor complejidad de UI y flujo] -> Mitigar con rollout por fases
- [Mas almacenamiento por evidencias] -> Mitigar con limites de tamano,
  cantidad y tipos permitidos
- [Apelaciones dilatando moderacion] -> Mitigar con plazos claros y estados
  cerrados
- [Falsos positivos en reputacion avanzada] -> Mitigar tratando fase 3 como
  apoyo, no como decision final automatica

## Migration Plan

1. implementar fase 1 y estabilizarla
2. medir uso y revisar necesidad real de apelacion
3. implementar fase 2 con reglas de plazo y evidencia
4. acumular historial suficiente
5. evaluar fase 3 como mejora operativa avanzada

## Open Questions

- si la evidencia de fase 1 debe permitir solo imagenes o tambien links y PDF
- si la apelacion debe abrirse solo para anuncios bloqueados o tambien para
  reportes descartados
- si la reputacion de fase 3 sera visible para admins o solo una senal interna

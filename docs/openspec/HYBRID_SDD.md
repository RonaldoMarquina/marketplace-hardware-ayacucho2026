# Enfoque Hibrido SDD + OpenSpec

## Contexto

HardwareAyacucho ya cuenta con implementacion funcional, pruebas automatizadas,
modelo de datos y documentacion por historias de usuario. Debido a ello, no
resulta eficiente reconstruir toda la solucion bajo una herramienta SDD desde
cero.

## Decision de trabajo

Se adopta un enfoque hibrido:

- La base historica del sistema se conserva en documentos manuales del proyecto
- OpenSpec se usa como mecanismo incremental para especificar, refactorizar y
  gobernar cambios futuros

## Distribucion acordada

- `docs/` conserva la base documental humana y academica
- `openspec/` representa la capa operativa real de OpenSpec
- `docs/openspec/` documenta y explica la adopcion hibrida para trazabilidad
- `.codex/` y `.github/` soportan el trabajo asistido por IA, pero no
  reemplazan la documentacion principal

## Que se mantiene en documentacion manual

- HU-01 a HU-21
- requisitos funcionales y no funcionales
- guia API
- esquema de base de datos
- evidencia de pruebas y validacion

## Que pasa a OpenSpec

- cambios funcionales nuevos
- refactors relevantes
- decisiones tecnicas
- endurecimiento de seguridad
- cambios de arquitectura, despliegue o integracion

Las especificaciones activas y canonicamente vigentes deben residir en
`openspec/specs/`.

## Beneficios del enfoque

- evita rehacer documentacion ya valida
- mejora trazabilidad de cambios
- se adapta a un proyecto brownfield
- permite alinear el trabajo con un enfoque SDD realista

## Regla practica

Si el cambio modifica comportamiento, seguridad, arquitectura o flujos
principales, debe registrarse en `openspec/` y reflejarse en la capa humana de
`docs/openspec/` cuando sea relevante para trazabilidad o evaluacion.

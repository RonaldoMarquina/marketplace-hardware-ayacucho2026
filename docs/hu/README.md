# Historias de Usuario

## Proposito

Esta carpeta contiene las historias de usuario del proyecto en formato tecnico.
Su objetivo es describir comportamiento esperado, reglas de negocio, interfaces
y criterios de validacion, no funcionar como tutorial de implementacion.

## Estructura recomendada

Cada HU debe priorizar, cuando aplique, las siguientes secciones:

- `Objetivo`
- `Interfaz` o `Endpoints`
- `Entrada`, `Body` o `Query params`
- `Flujo principal`
- `Respuesta`
- `Errores`
- `Reglas`

## Regla de estilo

- redactar en tono tecnico
- evitar texto narrativo o academico excesivo
- evitar repetir contenido general que ya existe en `PROJECT.md`, `TESTING.md`,
  `DATABASE.md` o `SECURITY.md`
- mantener trazabilidad con endpoints, tablas, estados y validaciones reales del
  proyecto

## Relacion con OpenSpec

Las HUs documentan la base funcional implementada del sistema.

- `docs/hu/` conserva la capa historica y funcional
- `openspec/` gestiona cambios incrementales y futura evolucion
- `docs/openspec/` explica la adopcion hibrida para fines humanos y academicos

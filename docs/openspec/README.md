# OpenSpec - Adopcion Hibrida en HardwareAyacucho

## Proposito

Esta carpeta introduce una capa de trabajo estilo OpenSpec sobre un proyecto ya
existente. No reemplaza la documentacion historica del repositorio; la ordena y
la complementa para gestionar cambios incrementales en un entorno brownfield.

## Enfoque Adoptado

HardwareAyacucho usa un enfoque hibrido:

- Documentacion manual existente para la base funcional del sistema
- Especificaciones estilo OpenSpec para cambios, refactors y decisiones nuevas

Esto permite mantener trazabilidad sin rehacer el proyecto desde cero.

## Relacion con la documentacion actual

- Historias de usuario: `docs/hu/`
- Vision funcional del sistema: `docs/PROJECT.md`
- Requisitos funcionales y no funcionales:
  `docs/Requisitos_funcionales-No_funcionales.md`
- Contratos API: `docs/API_GUIDE.md`
- Base de datos: `docs/database.sql`
- Validacion y testing: `docs/TESTING.md`

## Estructura inicial

- `HYBRID_SDD.md`: define como conviven la documentacion manual y OpenSpec
- `SPEC_INDEX.md`: indice de especificaciones activas
- `specs/`: espacio explicativo o de apoyo humano cuando sea necesario
- `../REPOSITORY_STRUCTURE.md`: regla general de ubicacion documental

## Diferencia con `openspec/`

La carpeta `docs/openspec/` no reemplaza a `openspec/`.

- `openspec/` es la capa operativa real de la herramienta
- `docs/openspec/` es la capa explicativa para humanos

## Fuente canonica de especificaciones

Las especificaciones activas del proyecto viven en:

- `openspec/specs/auth-security.md`
- `openspec/specs/marketplace-core.md`
- `openspec/specs/admin-moderation.md`

Por tanto:

- `openspec/specs/` es la fuente canonica operativa
- `docs/openspec/` solo explica la adopcion, trazabilidad y uso academico

## Como usar OpenSpec desde ahora

Cuando se haga un cambio importante, se recomienda:

1. Identificar la historia o modulo afectado
2. Registrar el cambio en la spec correspondiente
3. Actualizar API, BD o pruebas si aplica
4. Vincular la validacion ejecutada: PyTest, Pylint, SonarQube o Postman

## Alcance de la primera adopcion

La primera adopcion OpenSpec cubre tres frentes del proyecto:

- autenticacion y seguridad
- marketplace y anuncios
- administracion y moderacion

Las demas areas pueden migrarse de forma progresiva segun necesidad.

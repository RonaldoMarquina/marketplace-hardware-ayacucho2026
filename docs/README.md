# Documentacion del Proyecto

## Proposito

Esta carpeta contiene la documentacion humana y academica principal de
HardwareAyacucho. Aqui deben vivir los documentos funcionales, tecnicos y de
validacion que explican el sistema sin depender de una herramienta especifica.

## Documentos principales

- `PROJECT.md`: vision general del producto, alcance y HU implementadas
- `REPOSITORY_STRUCTURE.md`: politica de organizacion del repositorio
- `STACK.md`: stack tecnologico, arquitectura base y convenciones tecnicas
- `API_GUIDE.md`: reglas generales de la API REST
- `DATABASE.md`: resumen funcional del modelo de datos
- `DEPLOYMENT.md`: estrategia de despliegue publico y checklist operativo
- `database.sql`: esquema fuente de la base de datos MySQL
- `SECURITY.md`: controles y reglas de seguridad aplicadas
- `TESTING.md`: estrategia de pruebas, cobertura y calidad
- `CODING_STYLE.md`: convenciones de codigo
- `Requisitos_funcionales-No_funcionales.md`: requisitos del sistema
- `ARQUITECTURA_Y_METODOLOGIA.md`: marco metodologico y arquitectura explicada
- `Guia_SonarQube_Local.docx`: guia local para analisis con SonarQube

## Subcarpetas

- `hu/`: historias de usuario
- `openspec/`: capa explicativa de la adopcion hibrida con OpenSpec

## Documentacion de apoyo para IA

Los prompts de trabajo asistido, contexto de frontend para agentes y reglas de
prompt ya no forman parte de la documentacion principal. Ese material vive en
`.codex/context/legacy-prompts/` para evitar ruido y redundancia en `docs/`.

Los scripts auxiliares de generacion o soporte tecnico deben vivir fuera de
`docs/`, por ejemplo en `scripts/`.

## Regla practica

Si el documento sirve para el informe, defensa, mantenimiento humano o
trazabilidad funcional, debe quedarse en `docs/`.

Si el documento fue creado para guiar a asistentes IA durante el desarrollo, no
debe permanecer en la capa principal de `docs/`.

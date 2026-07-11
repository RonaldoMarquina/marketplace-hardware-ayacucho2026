# Estructura del Repositorio

## Objetivo

Este documento define que tipo de informacion debe vivir en cada carpeta
principal del proyecto para evitar duplicidad, mezcla de responsabilidades o
confusion entre documentacion academica, contexto operativo de IA y
especificacion incremental.

## Regla general

- `docs/` guarda documentacion humana, academica y funcional del proyecto
- `.codex/` guarda contexto operativo exclusivo para Codex
- `.github/` guarda contexto operativo para GitHub y GitHub Copilot
- `openspec/` guarda artefactos reales de OpenSpec administrados por la
  herramienta

## Que va en `docs/`

Usar `docs/` para artefactos que una persona del equipo o un evaluador debe
leer sin depender de una herramienta especifica.

Ejemplos:

- historias de usuario
- requisitos funcionales y no funcionales
- guia API
- esquema de base de datos
- evidencia de pruebas
- stack tecnologico
- seguridad
- decisiones de proyecto explicadas en lenguaje humano

No usar `docs/` para:

- prompts historicos de asistentes IA
- scripts auxiliares
- artefactos operativos exclusivos de herramientas

## Que va en `.codex/`

Usar `.codex/` para instrucciones, skills y contexto que ayudan a Codex a
trabajar mejor dentro del repositorio.

Ejemplos:

- skills locales
- flujos de trabajo de Codex
- reglas operativas para asistencia en desarrollo

No usar esta carpeta para:

- documentacion academica
- historias de usuario
- evidencia formal del proyecto

## Que va en `.github/`

Usar `.github/` para integraciones y contexto asociado a GitHub y GitHub
Copilot.

Ejemplos:

- prompts para Copilot
- skills compatibles con Copilot
- workflows de GitHub Actions
- plantillas de issues o pull requests

No usar esta carpeta para:

- especificacion funcional principal
- documentos del informe

## Que va en `openspec/`

Usar `openspec/` como espacio oficial de trabajo de la herramienta OpenSpec.
Esta carpeta representa la implementacion real del enfoque SDD incremental.

Ejemplos:

- `config.yaml`
- `changes/`
- `specs/`
- artefactos generados o mantenidos por OpenSpec

## Diferencia entre `openspec/` y `docs/openspec/`

- `openspec/` es la capa operativa real de la herramienta
- `docs/openspec/` es la capa explicativa y trazable para humanos

En otras palabras:

- si OpenSpec genera, sincroniza o gestiona el artefacto, va en `openspec/`
- si el documento explica como adoptamos OpenSpec en el proyecto, va en
  `docs/openspec/`

## Politica practica para este proyecto

- la base historica del sistema sigue en `docs/`
- los cambios nuevos o refactors importantes deben reflejarse en `openspec/`
- `docs/openspec/` sirve para justificar la adopcion hibrida ante revision
  academica o tecnica
- `.codex/` y `.github/` no reemplazan la documentacion del proyecto; solo
  soportan el trabajo asistido por IA

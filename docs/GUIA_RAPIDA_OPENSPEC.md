# Guia Rapida de OpenSpec

## Proposito

Este archivo sirve como apoyo temporal para aprender a pedir cambios usando
OpenSpec dentro del proyecto.

## Idea base

OpenSpec se usa para trabajar cambios con este flujo:

```text
idea -> especificacion -> implementacion -> validacion -> cierre
```

En este repositorio:

- `openspec/` contiene la capa operativa real
- `docs/openspec/` explica la adopcion hibrida
- Codex puede ayudarte a proponer, explorar, implementar y cerrar cambios

## Formas utiles de pedir cambios

### 1. Proponer un cambio

Usa esto cuando todavia no existe el cambio y quieres estructurarlo.

```text
Usa OpenSpec para proponer un cambio sobre QA hardening.
Objetivo: integrar Bandit al backend y reforzar SonarQube.
Alcance: backend, testing y documentacion tecnica.
No incluir: despliegue ni login con Google.
```

### 2. Explorar una idea

Usa esto cuando aun quieres pensar antes de implementar.

```text
Usa OpenSpec para explorar si conviene empezar por Bandit + Sonar o por despliegue.
```

### 3. Aplicar un cambio

Usa esto cuando ya existe una propuesta o ya se decidio el cambio.

```text
Usa OpenSpec para aplicar el cambio de QA hardening y comienza por Bandit.
```

### 4. Sincronizar especificaciones

Usa esto cuando ya implementaste cambios y quieres reflejarlos en las specs.

```text
Usa OpenSpec para sincronizar las especificaciones con lo ya implementado en QA hardening.
```

### 5. Archivar un cambio

Usa esto cuando el cambio ya termino.

```text
Usa OpenSpec para archivar el cambio de QA hardening porque ya quedo implementado.
```

## Plantilla corta recomendada

```text
Usa OpenSpec para [explorar / proponer / aplicar / sincronizar / archivar] un cambio sobre [tema].
Objetivo: [...]
Alcance: [...]
No incluir: [...]
```

## Primer ejercicio recomendado

Para empezar a practicar, usa algo como:

```text
Usa OpenSpec para proponer un cambio sobre QA hardening.
Objetivo: integrar Bandit al backend y reforzar SonarQube.
Alcance: backend, testing y documentacion tecnica.
No incluir: despliegue ni login con Google.
```

## Nota

Este documento es temporal y puede eliminarse cuando el flujo de OpenSpec ya
forme parte del trabajo normal del proyecto.

Lo que falta
despliegue
produccion publica
Google login



## Why

El proyecto ya cuenta con PyTest, Pylint y SonarQube, pero la capa de seguridad
estatica del backend aun no esta formalizada como parte del flujo de QA. Esto
limita la deteccion temprana de patrones inseguros y deja criterios dispersos
entre documentacion, ejecucion local y validacion manual.

## What Changes

- integrar `Bandit` como analisis estatico de seguridad para el backend Python
- reforzar el flujo local de `SonarQube` para que use artefactos y pasos
  consistentes con la cobertura actual del proyecto
- documentar un flujo unificado de QA hardening para backend, testing y calidad
  estatica
- definir criterios minimos de ejecucion para analisis local antes de despliegue

## Capabilities

### New Capabilities
- `qa-static-analysis`: define el flujo de analisis estatico y seguridad del
  backend mediante Bandit, SonarQube y artefactos de soporte para QA local

### Modified Capabilities

## Impact

- backend: dependencias y comandos de analisis estatico
- testing: flujo de cobertura y validacion previa a SonarQube
- documentacion tecnica: `docs/TESTING.md`, seguridad y metodologia
- operacion local: scripts o comandos de QA usados antes de despliegue

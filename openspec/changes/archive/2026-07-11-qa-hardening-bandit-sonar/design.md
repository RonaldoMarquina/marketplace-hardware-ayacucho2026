## Context

El proyecto ya dispone de pruebas automatizadas, cobertura, Pylint y un flujo
local de SonarQube. Sin embargo, la seguridad estatica del backend Python aun
no se ejecuta como parte del endurecimiento de QA, y la secuencia de analisis
previa a SonarQube depende de conocimiento manual del equipo.

El cambio afecta varias capas del trabajo tecnico:

- dependencias del backend
- comandos de validacion local
- documentacion de testing y seguridad
- integracion entre cobertura y analisis estatico

## Goals / Non-Goals

**Goals:**

- integrar `Bandit` como herramienta oficial de seguridad estatica del backend
- estandarizar un flujo local de QA que combine pruebas, cobertura, Bandit,
  Pylint y SonarQube
- dejar documentacion tecnica coherente para ejecucion local y futura defensa
  academica

**Non-Goals:**

- no desplegar pipeline CI/CD remoto en esta etapa
- no introducir autenticacion con Google ni correo transaccional real
- no redefinir reglas funcionales de negocio del marketplace

## Decisions

### 1. Incorporar Bandit solo para backend Python

Se limita `Bandit` al backend porque es donde existe el riesgo de patrones
inseguros en Python. El frontend seguira cubierto por SonarQube y validaciones
propias del stack.

Alternativa considerada:

- analizar todo el monorepo con una sola herramienta de seguridad

Razon para no elegirla:

- mezclaria tecnologias distintas y agregaria ruido sin mejorar el valor del
  primer endurecimiento

### 2. Mantener SonarQube como capa agregadora de calidad, no como unica fuente

SonarQube seguira consolidando cobertura, duplicacion y hotspots, pero el flujo
local debera generar antes los artefactos que Sonar consume.

Alternativa considerada:

- depender unicamente de SonarQube para seguridad estatica

Razon para no elegirla:

- Bandit ofrece hallazgos especificos de Python y sirve como control temprano
  antes del escaneo agregado

### 3. Formalizar una secuencia local de QA hardening

La secuencia objetivo sera:

```text
PyTest -> cobertura -> Pylint -> Bandit -> SonarQube
```

Esto permite detectar primero errores funcionales, luego cobertura y calidad
basica, y finalmente seguridad y analisis consolidado.

Alternativa considerada:

- ejecutar herramientas en cualquier orden segun necesidad puntual

Razon para no elegirla:

- deja resultados inconsistentes y dificulta repetir el proceso

## Risks / Trade-offs

- [Bandit genera falsos positivos iniciales] -> Mitigar con una configuracion
  minima, exclusion justificada y documentacion de hallazgos aceptados
- [El flujo de QA se vuelve mas largo] -> Mitigar distinguiendo validaciones
  rapidas locales de validaciones completas previas a despliegue
- [SonarQube y Bandit pueden solapar hallazgos] -> Mitigar definiendo a Bandit
  como control especializado de Python y a SonarQube como vista consolidada
- [La documentacion puede desalinearse del flujo real] -> Mitigar actualizando
  `docs/TESTING.md`, `docs/SECURITY.md` y la metodologia junto con la
  implementacion

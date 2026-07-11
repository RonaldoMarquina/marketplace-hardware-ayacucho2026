## Context

El proyecto ya cuenta con un flujo documentado de analisis local que combina
pruebas, cobertura, `Pylint`, `Bandit` y `SonarQube`. La siguiente necesidad no
es agregar una herramienta nueva, sino consolidar la operacion de ese flujo
para que sea facil de ejecutar, validar y explicar dentro del marco metodologico
del proyecto.

Actualmente el mayor costo esta en tres puntos:

- la secuencia depende de varios comandos manuales
- la validacion integral aun no queda registrada como parte del cambio
- la documentacion metodologica todavia enfatiza `Pylint` y `SonarQube` sin
  reflejar con la misma claridad la presencia de `Bandit` y del QA hardening

## Goals / Non-Goals

**Goals:**

- centralizar la ejecucion del flujo local de QA en un script o comando oficial
- verificar que el flujo completo siga siendo ejecutable con la base actual del
  proyecto
- alinear testing, arquitectura y metodologia con el estado real del QA
- distinguir entre ejecucion rapida para desarrollo y validacion completa previa
  a despliegue

**Non-Goals:**

- no desplegar CI/CD remoto en esta etapa
- no introducir herramientas nuevas de seguridad mas alla de las ya adoptadas
- no abordar despliegue, infraestructura productiva ni autenticacion externa

## Decisions

### 1. Formalizar un entry point local para QA hardening

Se definira un script o comando unico como punto de entrada oficial del flujo
completo.

Alternativas consideradas:

- mantener solo comandos documentados por separado
- mover el flujo completo directamente a un pipeline remoto

Razones para no elegirlas:

- la primera mantiene friccion operativa y errores manuales
- la segunda adelanta una etapa de infraestructura que aun no es el foco

### 2. Conservar una secuencia escalonada

La secuencia completa seguira este orden:

```text
PyTest -> cobertura -> Pylint -> Bandit -> SonarQube
```

Tambien se documentara una variante rapida para cambios pequenos, de modo que
el flujo completo no se vuelva una barrera innecesaria durante iteraciones
cortas.

### 3. Tratar la metodologia como parte del entregable tecnico

La alineacion metodologica no se dejara como nota secundaria. Si el proyecto
declara una estrategia de calidad, esa estrategia debe reflejar el flujo real
que el equipo ejecuta.

## Risks / Trade-offs

- [El script unificado puede duplicar logica ya documentada] -> Mitigar usando
  el script como entry point y la documentacion como guia de uso
- [La suite completa puede tardar demasiado para cambios pequenos] -> Mitigar
  distinguiendo chequeos rapidos de validacion completa
- [SonarQube local puede depender de entorno externo] -> Mitigar documentando
  precondiciones y separando con claridad lo obligatorio de lo opcional
- [La metodologia puede volver a quedar desactualizada] -> Mitigar vinculando
  su contenido al flujo de QA oficial definido por este cambio

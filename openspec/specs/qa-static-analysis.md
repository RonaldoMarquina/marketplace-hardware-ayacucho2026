# OS-04 - QA Hardening y Analisis Estatico

## Objetivo

Definir el flujo oficial de validacion local para pruebas, cobertura, analisis
estatico y endurecimiento de calidad antes de despliegue.

## Historias relacionadas

- HU-01
- HU-02
- HU-03
- HU-04
- HU-05
- HU-06
- HU-07
- HU-08
- HU-09
- HU-10
- HU-11
- HU-12
- HU-13
- HU-14
- HU-15
- HU-16
- HU-17
- HU-18
- HU-19
- HU-20
- HU-21

## Reglas funcionales clave

- el proyecto debe ofrecer un entry point oficial para la validacion completa de
  QA local
- la validacion completa debe ejecutar `PyTest -> cobertura -> Pylint -> Bandit
  -> SonarQube`
- el proyecto debe distinguir entre una validacion rapida para iteraciones
  cortas y una validacion completa previa a despliegue
- el backend debe contar con analisis estatico de seguridad usando `Bandit`
- SonarQube debe usarse como tablero global complementario para cobertura,
  duplicacion, fiabilidad y mantenibilidad

## Reglas tecnicas clave

- `Bandit` debe ejecutarse solo sobre `backend/app`
- la cobertura del backend debe seguir siendo compatible con la configuracion de
  SonarQube del repositorio
- la documentacion tecnica debe reflejar el flujo real de QA hardening
- la ejecucion local debe documentar limitaciones o ajustes dependientes del
  entorno, especialmente en Windows
- si la instancia local de SonarQube no permite administrar quality gates de
  forma confiable, el proyecto no debe bloquear el cierre QA por esa limitacion
- cualquier criterio de `New Code` o quality gates debe tratarse como referencia
  futura o configuracion deseable, no como prerrequisito operativo del flujo
  local actual

## Artefactos vinculados

- `scripts/run-qa-hardening.ps1`
- `scripts/run-sonar-local.ps1`
- `backend/bandit.yaml`
- `backend/pytest.ini`
- `pytest.ini`
- `docs/TESTING.md`
- `docs/ARQUITECTURA_Y_METODOLOGIA.md`
- `docs/SECURITY.md`

## Validacion esperada

- PyTest para validar la suite funcional del backend
- pytest-cov para regenerar `backend/coverage.xml`
- Pylint para calidad estatica general del backend
- Bandit para patrones de seguridad especificos de Python
- SonarQube para consolidacion final del analisis local

## Uso operativo de SonarQube

- SonarQube se usa como tablero global de apoyo para revisar:
  cobertura, duplicacion, fiabilidad, mantenibilidad y hotspots
- el control operativo principal del proyecto sigue siendo:
  `PyTest`, cobertura, `Pylint` y `Bandit`
- si la instancia local permite quality gates sanas, el equipo puede usar
  criterios sobre `New Code` como recomendacion complementaria
- si la instancia local presenta limitaciones de permisos o de interfaz, el
  equipo debe documentar esa restriccion y continuar usando SonarQube como
  evidencia global no bloqueante

## Referencias futuras no obligatorias

- si mas adelante el equipo estabiliza una instancia administrable de SonarQube,
  puede retomar quality gates sobre `New Code`
- ejemplos razonables de referencia futura incluyen:
  `No new Blocker issues`, `No new Critical issues`, `Coverage >= 80%`,
  `Duplicated Lines <= 3%`, `Security Hotspots Reviewed = 100%` y
  `Maintainability A` en codigo nuevo

## Nota metodologica

- para este proyecto de ciclo completo, la imposibilidad de operacionalizar una
  quality gate local no invalida el QA si el equipo conserva evidencia clara de
  pruebas, cobertura, `Pylint`, `Bandit` y analisis global en SonarQube

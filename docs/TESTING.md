# Testing - HardwareAyacucho

## Objetivo

Este documento resume como se valida el backend del proyecto a nivel funcional,
de cobertura y de calidad estatica.

## Herramientas usadas

- `PyTest`
- `pytest-cov`
- `Pylint`
- `Bandit`
- `Postman`
- `SonarQube`

## Estructura de pruebas

```text
backend/tests/
  conftest.py
  integration/
  unit/
```

## Tipos de prueba

### Unitarias

Se concentran en funciones puras, helpers y validaciones puntuales.

Ejemplos:

- normalizacion de taxonomias
- merge de especificaciones
- validacion de decimales
- reglas auxiliares del servicio de anuncios

### Integracion

Validan el comportamiento de endpoints y flujos del sistema usando cliente Flask
de pruebas y base de datos de testing.

Ejemplos:

- autenticacion
- registro y verificacion
- publicacion y edicion de anuncios
- busqueda, detalle y contacto
- moderacion y administracion
- perfil, panel, historial y calificaciones

## Marcadores PyTest

En `backend/pytest.ini` se registran:

- `unit`
- `integration`

Ademas, la configuracion del repositorio fija `basetemp` locales separados para
las corridas desde la raiz y desde `backend`, con el fin de evitar bloqueos de
archivos temporales en Windows y mantener estables las ejecuciones locales. El
script oficial de QA sigue usando una carpeta bajo `%TEMP%` para aislar
ejecuciones largas o paralelas.

## Comandos principales

### Ejecutar toda la suite

```bash
py -m pytest
```

Ejecutado desde la raiz del repositorio, `pytest` toma `./pytest.ini`. Si lo
ejecutas dentro de `backend`, toma `backend/pytest.ini`. En ambos casos no es
necesario pasar `--basetemp` manualmente.

Tampoco es necesario borrar carpetas temporales en cada corrida. La
configuracion usa directorios separados para evitar choques entre ejecuciones
desde la raiz y desde `backend`.

### Ejecutar unitarias

```bash
py -m pytest -m unit
```

### Ejecutar integracion

```bash
py -m pytest -m integration
```

## Cobertura

La configuracion vive en `backend/.coveragerc`.

### Cobertura completa

```bash
py -m pytest --cov=app --cov-config=.coveragerc --cov-report=term-missing --cov-report=xml
```

### Salida esperada

- reporte en consola
- archivo `coverage.xml` para integracion con SonarQube

## Pylint

El backend incluye configuracion en `backend/.pylintrc`.

### Ejecutar analisis estatico

```bash
py -m pylint --rcfile=backend/.pylintrc backend/app backend/run.py
```

### Que revisa

- imports no usados
- variables no usadas
- convenciones de nombres
- complejidad
- malos olores de codigo

## Bandit

El backend define `Bandit` como analisis estatico de seguridad oficial para el
codigo Python de `backend/app`.

### Ejecutar analisis de seguridad

```bash
py -m bandit -c backend/bandit.yaml -r backend/app
```

### Alcance configurado

- analisis recursivo solo sobre `backend/app`
- exclusiones de caches, uploads y artefactos temporales locales
- omision temporal de `B105` por falsos positivos sobre mensajes de validacion
  y mapas de estados HTTP ligados a flujos de password

Bandit complementa a `Pylint`: `Pylint` cubre calidad general y Bandit revisa
patrones de seguridad especificos de Python.

## SonarQube

El proyecto usa `sonar-project.properties` para analizar:

- `backend/app`
- `frontend/src`
- cobertura del backend desde `backend/coverage.xml`

### Entry point oficial de QA hardening

El flujo local de QA queda centralizado en:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-qa-hardening.ps1 -SonarToken "<token>"
```
```GitBash
powershell.exe -ExecutionPolicy Bypass -File ./scripts/run-qa-hardening.ps1 -SonarToken "tu_token_aqui"
```

Precondiciones para el flujo completo:

- dependencias Python del backend instaladas
- `py` disponible en Windows
- SonarQube local accesible
- `sonar-scanner` disponible en la ruta esperada o indicado con `-ScannerBat`

El script fuerza `pytest` a usar una carpeta unica por ejecucion bajo
`%TEMP%\hardware-ayacucho-pytest` para evitar errores de permisos cuando el
repositorio vive dentro de `OneDrive` o cuando se lanzan corridas paralelas.

### Validacion rapida

Para cambios pequenos o iteraciones cortas:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-qa-hardening.ps1 -Quick
```

La ruta rapida ejecuta:

- `pytest -m unit`
- `Pylint`
- `Bandit`

No ejecuta cobertura ni SonarQube.

### Flujo recomendado

1. ejecutar `powershell -ExecutionPolicy Bypass -File .\scripts\run-qa-hardening.ps1 -SonarToken "<token>"`
2. validar que `backend/coverage.xml` se haya regenerado durante la etapa de cobertura
3. revisar resultados de `Pylint`, `Bandit` y `SonarQube`

### Secuencia interna del flujo completo

```text
PyTest -> cobertura -> Pylint -> Bandit -> SonarQube
```

Si el entorno local no tiene token o servidor SonarQube disponible, puede
ejecutarse una validacion intermedia con:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-qa-hardening.ps1 -SkipSonar
```

### Hallazgos de validacion en este entorno

Durante la aplicacion de `qa-hardening-phase-2` se corrigieron dos causas
operativas que impedian validar el flujo local:

- faltaba `Flask-WTF` en el entorno Python activo
- `pytest` fallaba con `PermissionError` sobre `backend/.pytest_tmp` cuando el
  repositorio estaba sincronizado en `OneDrive`

Estado actual observado:

- `py -m pytest` pasa con `189 passed, 1 skipped`
- `py -m pylint --rcfile=backend/.pylintrc backend/app backend/run.py` pasa con
  calificacion `10.00/10`
- `py -m bandit -c backend/bandit.yaml -r backend/app` no reporta issues
- `scripts/run-sonar-local.ps1` completa el analisis local y publica el reporte
  en `http://localhost:9000/dashboard?id=HardwareAyacucho`

El script oficial resuelve el segundo punto usando `%TEMP%` como base temporal
de `pytest`, por lo que la limitacion original queda corregida para este
entorno local.

La suite puede disparar `ResourceWarning` esporadicos ligados al manejo interno
de archivos temporales en dependencias del stack web durante pruebas
`multipart/form-data`. Esos avisos no afectan el resultado funcional del
backend y se filtran en `pytest.ini` para mantener la salida de QA enfocada en
fallos reales.

Si una corrida fue interrumpida o Windows deja archivos temporales bloqueados,
puede ser necesario cerrar la terminal y reintentar. Solo si el problema
persiste conviene eliminar manualmente `./.pytest_tmp_root` o
`backend/.pytest_tmp_backend` antes de lanzar nuevamente `py -m pytest`.

Para SonarQube, el staging local se prepara en `./.sonar_runs/<run-id>` dentro
del workspace en lugar de `%TEMP%`, con el fin de evitar errores de acceso al
resolver el directorio base durante el escaneo en Windows y aislar cada
ejecucion del scanner.

## Cobertura funcional por HU

- HU-01 a HU-04: autenticacion y verificacion
- HU-05 a HU-14: anuncios, media, busqueda, detalle, contacto y ventas
- HU-15 a HU-20: calificaciones, perfil, historial, panel y administracion
- HU-21: recuperacion de contrasena

## Estado general esperado

- unitarias para logica aislada
- integracion para flujos principales
- cobertura exportable para QA
- analisis estatico complementario con Pylint, Bandit y SonarQube

## Recomendaciones

- ejecutar `pytest -m unit` durante cambios pequenos
- ejecutar `pytest -m integration` antes de cerrar cambios funcionales
- regenerar cobertura antes de analisis en SonarQube
- ejecutar Bandit despues de Pylint para detectar patrones inseguros del backend
- usar `scripts/run-qa-hardening.ps1` como entry point oficial del flujo local
- mantener nuevas reglas puras en `tests/unit`
- mantener nuevos endpoints o flujos en `tests/integration`

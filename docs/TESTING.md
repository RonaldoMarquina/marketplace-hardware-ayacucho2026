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
- moderacion, reporte con evidencia y administracion
- perfil, panel, historial y calificaciones

## Marcadores PyTest

En `backend/pytest.ini` se registran:

- `unit`
- `integration`

Ademas, la configuracion del repositorio fija `basetemp` locales separados para
las corridas desde la raiz y desde `backend`, con el fin de evitar bloqueos de
archivos temporales en Windows y mantener estables las ejecuciones locales. El
script oficial de QA usa una carpeta temporal versionada localmente dentro del
workspace para aislar ejecuciones largas o paralelas sin depender de permisos
variables sobre `%TEMP%`.

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

## Correo en testing

Los tests no envian correos reales. El backend usa `EMAIL_DELIVERY_MODE=testing`
y registra cada mensaje en una bandeja interna (`mail_outbox`) para poder
validar verificacion de correo, reset password y notificaciones operativas de
moderacion sin credenciales externas.

## Hardening de reset password

La suite ya cubre tres garantias extra del flujo de recuperacion:

- el token enviado por correo no queda persistido reusable en claro
- un JWT emitido antes del cambio de contrasena queda revocado despues del reset
- la confirmacion del reset tiene rate limit dedicado para frenar abuso por IP

## Moderacion de anuncios

La suite de integracion ya cubre reglas base y fase 1 del reporte enriquecido:

- registro de reporte con `motivo` y `detalle`
- rechazo de autoreporte y duplicidad por ciclo activo
- limite diario de reportes por usuario
- carga de evidencias `JPG` o `PNG`
- detalle administrativo del caso con reportes y evidencias
- notificacion por correo al vendedor cuando su anuncio recibe un reporte
- visibilidad del caso reportado en el panel del propietario antes del bloqueo
- apelacion habilitada solo para anuncios efectivamente bloqueados

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

### Uso recomendado de SonarQube

Para este proyecto de ciclo completo, SonarQube se usa principalmente como
tablero global de apoyo para revisar:

- cobertura
- duplicacion
- fiabilidad
- mantenibilidad
- hotspots de seguridad

El control operativo principal del QA sigue siendo:

- `PyTest`
- cobertura del backend
- `Pylint`
- `Bandit`

Si la instancia local de SonarQube permite quality gates sanas, el equipo puede
usar criterios de `New Code` como referencia futura. Pero si la instancia local
presenta limitaciones de permisos o de interfaz, eso no debe bloquear el cierre
QA mientras exista evidencia clara de pruebas, cobertura y analisis estatico.

Referencias futuras no obligatorias para `New Code`:

- `No new Blocker issues`
- `No new Critical issues`
- `Coverage >= 80%`
- `Duplicated Lines <= 3%`
- `Security Hotspots Reviewed = 100%`
- `Maintainability A`

### Entry point oficial de QA hardening

El flujo local de QA queda centralizado en:

```powershell
# Usar solo desde PowerShell / Windows Terminal
powershell -ExecutionPolicy Bypass -File .\scripts\run-qa-hardening.ps1 -SonarToken "<token>"
```

```GitBash
# Usar desde Git Bash en Windows
powershell.exe -ExecutionPolicy Bypass -File ./scripts/run-qa-hardening.ps1 -SonarToken "tu_token_aqui"
```

```GitBash
# Opcion alternativa solo si tienes PowerShell 7 instalado
pwsh -ExecutionPolicy Bypass -File ./scripts/run-qa-hardening.ps1 -SonarToken "tu_token_aqui"
```

No mezclar sintaxis: en Git Bash no uses `.\scripts\...`, y en PowerShell no
uses `./scripts/...`.

Si `powershell.exe` interpreta mal la ruta desde Git Bash, usa esta variante:

```GitBash
powershell.exe -ExecutionPolicy Bypass -File "$(pwd)/scripts/run-qa-hardening.ps1" -SonarToken "tu_token_aqui"
```

Precondiciones para el flujo completo:

- dependencias Python del backend instaladas
- `py` disponible en Windows
- SonarQube local accesible
- `sonar-scanner` disponible en la ruta esperada o indicado con `-ScannerBat`

El script fuerza `pytest` a usar una carpeta unica por ejecucion bajo
`./.pytest_tmp_runs/` para evitar errores de permisos sobre `%TEMP%` y mantener
aisladas las corridas paralelas del flujo de QA.

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
3. revisar resultados de `Pylint`, `Bandit` y el tablero global de `SonarQube`

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

El script oficial resuelve el segundo punto usando `./.pytest_tmp_runs/` como
base temporal de `pytest`, por lo que la limitacion original queda corregida
para este entorno local incluso si Windows restringe el acceso a `%TEMP%`.

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

## Resumen operativo

- para validar rapido: `py -m pytest`
- para cobertura: `py -m pytest --cov=app --cov-config=.coveragerc --cov-report=term-missing --cov-report=xml`
- para QA local completo: `run-qa-hardening.ps1`
- para Git Bash: usar rutas `./scripts/...`
- para PowerShell: usar rutas `.\scripts\...`

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
- no considerar la app lista para produccion publica sin `EMAIL_DELIVERY_MODE=smtp`
  y credenciales reales de correo transaccional
- mantener nuevas reglas puras en `tests/unit`
- mantener nuevos endpoints o flujos en `tests/integration`
- cuando cambie el modelo de datos local, actualizar tambien `docs/database.sql`
  y dejar un script de migracion reutilizable si aplica

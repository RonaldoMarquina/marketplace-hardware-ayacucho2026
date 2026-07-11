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

Ademas, la configuracion del repositorio fija un `basetemp` local para evitar
fallos por permisos en el directorio temporal global de Windows.

## Comandos principales

### Ejecutar toda la suite

```bash
pytest
```

No es necesario pasar `--basetemp` manualmente, porque ya queda resuelto desde
la configuracion del proyecto.

### Ejecutar unitarias

```bash
pytest -m unit
```

### Ejecutar integracion

```bash
pytest -m integration
```

## Cobertura

La configuracion vive en `backend/.coveragerc`.

### Cobertura completa

```bash
pytest --cov=app --cov-config=.coveragerc --cov-report=term-missing --cov-report=xml
```

### Salida esperada

- reporte en consola
- archivo `coverage.xml` para integracion con SonarQube

## Pylint

El backend incluye configuracion en `backend/.pylintrc`.

### Ejecutar analisis estatico

```bash
python -m pylint --rcfile=backend/.pylintrc backend/app backend/run.py
```

### Que revisa

- imports no usados
- variables no usadas
- convenciones de nombres
- complejidad
- malos olores de codigo

## Bandit

Se considera `Bandit` como analisis estatico de seguridad para el backend
Python. Su incorporacion formal queda prevista para una siguiente etapa de QA y
hardening del proyecto.

### Alcance esperado

- deteccion de patrones inseguros en codigo Python
- revision complementaria a `Pylint` y `SonarQube`
- apoyo para reforzar controles antes de despliegue

## SonarQube

El proyecto usa `sonar-project.properties` para analizar:

- `backend/app`
- `frontend/src`
- cobertura del backend desde `backend/coverage.xml`

### Flujo recomendado

1. generar cobertura del backend
2. volver a la raiz del repositorio
3. ejecutar `sonar-scanner`

## Cobertura funcional por HU

- HU-01 a HU-04: autenticacion y verificacion
- HU-05 a HU-14: anuncios, media, busqueda, detalle, contacto y ventas
- HU-15 a HU-20: calificaciones, perfil, historial, panel y administracion
- HU-21: recuperacion de contrasena

## Estado general esperado

- unitarias para logica aislada
- integracion para flujos principales
- cobertura exportable para QA
- analisis estatico complementario con Pylint y SonarQube

## Recomendaciones

- ejecutar `pytest -m unit` durante cambios pequenos
- ejecutar `pytest -m integration` antes de cerrar cambios funcionales
- regenerar cobertura antes de analisis en SonarQube
- mantener nuevas reglas puras en `tests/unit`
- mantener nuevos endpoints o flujos en `tests/integration`

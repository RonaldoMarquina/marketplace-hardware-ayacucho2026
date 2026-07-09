# TESTING.md - HardwareAyacucho

## Herramientas

- `PyTest`: pruebas automatizadas del backend
- `pytest-cov`: cobertura de codigo
- `Postman`: validacion manual de endpoints REST

## Estructura actual de pruebas

```text
backend/tests/
|-- conftest.py
|-- integration/
|   |-- test_admin_usuarios.py
|   |-- test_busqueda_anuncios.py
|   |-- test_calificacion_comprador.py
|   |-- test_calificacion_vendedor.py
|   |-- test_contacto_anuncio.py
|   |-- test_db.py
|   |-- test_detalle_anuncio.py
|   |-- test_edicion_anuncio.py
|   |-- test_feed_anuncios.py
|   |-- test_historial_transacciones.py
|   |-- test_login.py
|   |-- test_media_anuncio.py
|   |-- test_moderacion_anuncios.py
|   |-- test_panel_usuario.py
|   |-- test_password_reset.py
|   |-- test_perfil_usuario.py
|   |-- test_publicar_anuncio.py
|   |-- test_registro_tienda.py
|   |-- test_registro_usuario.py
|   `-- test_verificacion_email.py
`-- unit/
    |-- test_anuncio_schema_unit.py
    `-- test_anuncio_service_helpers_unit.py
```

## Clasificacion

### Pruebas unitarias

Validan funciones puras o helpers sin depender de base de datos, cliente Flask ni endpoints HTTP.

Ejemplos:
- normalizacion de taxonomias
- validacion de decimales
- merge de especificaciones
- sanitizacion de texto
- reglas auxiliares del servicio de anuncios

### Pruebas de integracion

Validan el flujo entre controladores, servicios, modelos, base de datos en memoria y cliente de prueba Flask.

Ejemplos:
- login y registro
- publicacion y busqueda de anuncios
- contacto por WhatsApp
- moderacion administrativa
- historial, perfil, panel y calificaciones

## Marcadores PyTest

En `backend/pytest.ini` se registran dos marcadores:

- `unit`
- `integration`

Los tests de `backend/tests/unit` usan `pytest.mark.unit`.
Los tests de `backend/tests/integration` usan `pytest.mark.integration`.

## Comandos de ejecucion

### Ejecutar todas las pruebas

```bash
pytest
```

### Ejecutar solo pruebas unitarias

```bash
pytest -m unit
```

o por carpeta:

```bash
pytest tests/unit
```

### Ejecutar solo pruebas de integracion

```bash
pytest -m integration
```

o por carpeta:

```bash
pytest tests/integration
```

## Cobertura de codigo

El backend incluye configuracion de cobertura en `backend/.coveragerc`.

### Cobertura de toda la suite

```bash
pytest --cov=app --cov-config=.coveragerc --cov-report=term-missing --cov-report=xml
```

### Cobertura solo de unitarias

```bash
pytest -m unit --cov=app --cov-config=.coveragerc --cov-report=term-missing
```

### Cobertura solo de integracion

```bash
pytest -m integration --cov=app --cov-config=.coveragerc --cov-report=term-missing
```

El reporte XML generado (`coverage.xml`) puede usarse luego en herramientas como SonarQube o SonarCloud.

## Alcance cubierto por PyTest

- HU-01 al HU-04: registro, verificacion y autenticacion
- HU-05 al HU-14: anuncios, media, feed, busqueda, detalle, contacto, moderacion y ventas
- HU-15 al HU-20: calificaciones, perfil, historial, panel y administracion
- HU-21: recuperacion de contrasena

## Recomendaciones de uso

- Ejecutar `pytest -m unit` en cambios pequenos de logica interna.
- Ejecutar `pytest -m integration` antes de cerrar cambios funcionales.
- Ejecutar cobertura completa antes de entrega o despliegue academico.
- Mantener nuevas funciones puras cubiertas en `tests/unit`.
- Mantener nuevos flujos HTTP o de base de datos cubiertos en `tests/integration`.

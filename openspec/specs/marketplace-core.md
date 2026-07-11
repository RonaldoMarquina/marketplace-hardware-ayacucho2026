# OS-02 - Marketplace y Anuncios

## Objetivo

Definir el comportamiento central del marketplace: publicacion, edicion,
exploracion, busqueda tecnica, contacto y cierre de venta.

## Historias relacionadas

- HU-05
- HU-06
- HU-07
- HU-08
- HU-09
- HU-10
- HU-11
- HU-12
- HU-14

## Reglas funcionales clave

- solo usuarios autorizados pueden publicar anuncios
- un anuncio tiene categoria, subcategoria, condicion, precio y especificaciones
- la media del anuncio admite imagenes `JPG`, `JPEG`, `PNG`, `WEBP`, `AVIF` y video `MP4` con limites definidos
- el feed publico muestra solo anuncios visibles
- la busqueda tecnica puede filtrar por categoria, subcategoria, precio y specs
- el contacto se realiza por WhatsApp y deja traza en el sistema
- el vendedor puede marcar el anuncio como vendido

## Reglas tecnicas clave

- las especificaciones tecnicas se almacenan en JSON
- los uploads se validan antes de persistirse
- la logica de busqueda se concentra en el servicio de anuncios
- el feed y la busqueda tienen pruebas de integracion dedicadas

## Artefactos vinculados

- `backend/app/services/anuncio_service.py`
- `backend/app/controllers/anuncio_controller.py`
- `backend/app/models/anuncio.py`
- `backend/app/models/media_anuncio.py`
- `frontend/src/pages/anuncios/`
- `backend/tests/integration/test_publicar_anuncio.py`
- `backend/tests/integration/test_feed_anuncios.py`
- `backend/tests/integration/test_busqueda_anuncios.py`
- `backend/tests/integration/test_detalle_anuncio.py`
- `backend/tests/integration/test_contacto_anuncio.py`

## Validacion esperada

- PyTest para flujos HTTP y reglas de negocio
- Postman para validaciones manuales de endpoints
- SonarQube para duplicacion y complejidad

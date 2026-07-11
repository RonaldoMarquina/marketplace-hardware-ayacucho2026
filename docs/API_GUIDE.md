# API Guide

## Base URL

```text
/api/v1
```

## Autenticacion

Las rutas protegidas usan JWT en el encabezado:

```text
Authorization: Bearer <token>
```

## Respuesta exitosa

```json
{
  "success": true,
  "message": "Operacion realizada correctamente.",
  "data": {}
}
```

## Respuesta de error

```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "Descripcion del error."
}
```

## Codigos HTTP frecuentes

| Codigo | Uso |
|--------|-----|
| 200 | Consulta o actualizacion correcta |
| 201 | Recurso creado |
| 204 | Eliminacion logica o respuesta sin cuerpo |
| 400 | Solicitud invalida |
| 401 | No autenticado |
| 403 | Sin permisos |
| 404 | Recurso no encontrado |
| 409 | Conflicto de estado o duplicidad |
| 415 | Tipo de archivo no permitido |
| 422 | Error de validacion |
| 500 | Error interno |

## Reglas REST

- usar el metodo HTTP correcto
- validar datos antes de procesarlos
- mantener respuestas JSON uniformes
- no exponer informacion sensible
- centralizar el manejo de errores

## Patrones comunes

```text
GET    /recurso
GET    /recurso/{id}
POST   /recurso
PATCH  /recurso/{id}
DELETE /recurso/{id}
```

## Paginacion y filtros

```text
?page=1&limit=20
?sort=campo&order=asc
?campo=valor
```

Se pueden combinar multiples filtros en endpoints de busqueda.

## Archivos

- `multipart/form-data` para media y documentos
- validacion de tipo real de archivo
- limites segun modulo
- imagenes de anuncios: `JPG`, `JPEG`, `PNG`, `WEBP`, `AVIF`
- video de anuncio: `MP4`

## Nota

Este documento resume reglas generales de la API. El detalle funcional por
modulo debe mantenerse alineado con las historias de usuario, las pruebas y el
codigo fuente.

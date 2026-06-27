# API_GUIDE.md

# API REST

## Base URL

```
/api/v1
```

# Respuesta Exitosa

```json
{
  "success": true,
  "message": "Operación realizada correctamente.",
  "data": {}
}
```

# Respuesta de Error

```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "Descripción del error."
}
```

# Códigos HTTP

| Código | Uso |
|---------|-----|
|200|Consulta|
|201|Creación|
|204|Eliminación|
|400|Solicitud inválida|
|401|No autenticado|
|403|Sin permisos|
|404|No encontrado|
|409|Conflicto|
|415|Archivo inválido|
|422|Validación|
|500|Error interno|

# Autenticación

```
Authorization: Bearer <token>
```

JWT obligatorio en rutas protegidas.

# Endpoints REST

```
GET    /recurso
GET    /recurso/{id}
POST   /recurso
PUT    /recurso/{id}
PATCH  /recurso/{id}
DELETE /recurso/{id}
```

# Paginación

```
?page=1&limit=20
```

# Ordenamiento

```
?sort=campo&order=asc
```

# Filtros

```
?campo=valor
```

Se pueden combinar múltiples filtros.

# Archivos

- multipart/form-data
- JPG / PNG
- Máximo 5 MB

# Respuestas

- JSON
- UTF-8
- camelCase

# Reglas

- Usar métodos HTTP correctos.
- Validar datos antes de procesarlos.
- Consultas parametrizadas.
- Manejo centralizado de errores.
- No exponer información sensible.
- Mantener compatibilidad REST.
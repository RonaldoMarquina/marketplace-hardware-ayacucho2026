# DATABASE.md

# Base de Datos

Motor: MySQL  
ORM: SQLAlchemy  

# Esquema General

- usuarios
- tiendas
- tokens_verificacion
- anuncios
- imagenes_anuncio
- reportes
- moderacion_log
- contactos_log

# Relaciones

```
usuarios 1 ─── N anuncios
usuarios 1 ─── 1 tiendas
usuarios 1 ─── N reportes
usuarios 1 ─── N contactos_log

anuncios 1 ─── N imagenes_anuncio
anuncios 1 ─── N reportes
anuncios 1 ─── N moderacion_log
anuncios 1 ─── N contactos_log

usuarios 1 ─── N tokens_verificacion
```

# Reglas Generales

- PK: id (INT UNSIGNED AUTO_INCREMENT)
- FK: *_id
- Fechas: created_at, updated_at
- JSON permitido en especificaciones de anuncios
- Soft delete solo cuando aplique (estado o deleted_at)

# Tabla: usuarios

- id
- nombre
- correo UNIQUE
- password_hash (bcrypt)
- telefono (9 dígitos)
- rol:
  - USER_ESTANDAR
  - TIENDA_VERIFICADA
  - ADMIN
- estado:
  - PENDIENTE_VERIFICACION
  - ACTIVO
  - BLOQUEADO

# Tabla: tiendas

- usuario_id UNIQUE
- ruc UNIQUE (11 dígitos)
- estado:
  - EN_REVISION
  - ACTIVO
  - RECHAZADO
- documento_identidad (UUID file path)

# Tabla: anuncios

- usuario_id FK
- titulo
- descripcion
- categoria (ENUM hardware)
- condicion (NUEVO | USADO | etc.)
- precio > 0
- especificaciones JSON
- estado (ACTIVO | INACTIVO | VENDIDO | BLOQUEADO)

# Tabla: imagenes_anuncio

- anuncio_id FK
- ruta_relativa
- es_principal
- orden

# Tabla: reportes

- anuncio_id FK
- usuario_id FK
- motivo (FRAUDE | OTRO | etc.)
- estado (PENDIENTE | REVISADO)

Regla:
- Un usuario no puede duplicar reporte PENDIENTE sobre el mismo anuncio.

# Tabla: moderacion_log

- anuncio_id FK
- admin_id FK
- accion (BLOQUEADO | DESBLOQUEADO)
- motivo_admin

Regla:
- Solo auditoría, no eliminación.

# Tabla: contactos_log

- comprador_id FK
- anuncio_id FK
- created_at

Regla:
- Registro de interacción, no eliminar.

# Tabla: tokens_verificacion

- usuario_id FK
- token (64 chars)
- tipo: EMAIL_VERIFICATION
- expira_en
- usado

# Índices Clave

- usuarios.correo UNIQUE
- tiendas.ruc UNIQUE
- anuncios.estado
- anuncios.categoria
- anuncios.created_at
- reportes.estado
- tokens_verificacion.token

# Integridad

- Todas las FK deben respetarse.
- No registros huérfanos.
- Transacciones obligatorias en operaciones múltiples.

# Reglas de Negocio Globales

- No eliminar datos críticos físicamente.
- Usar estados en lugar de DELETE.
- Password nunca se expone.
- Archivos siempre por UUID.
- Consultas siempre parametrizadas.
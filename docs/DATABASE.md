# Base de Datos

## Fuente de verdad

El archivo fuente del esquema es `docs/database.sql`. Este documento solo
resume la estructura funcional y las reglas principales para facilitar lectura
humana.

## Motor y acceso

- Motor: MySQL
- ORM principal del backend: SQLAlchemy
- Charset: `utf8mb4`
- Collation: `utf8mb4_unicode_ci`

## Entornos de base de datos

### Desarrollo local

- Motor local historico: MySQL
- Uso principal: desarrollo diario, respaldo y pruebas locales rapidas
- Cadena de conexion: configurada mediante `DATABASE_URL` en `backend/.env`

### Base de datos en nube

- Proveedor validado para despliegue: `TiDB Cloud Starter`
- Compatibilidad: MySQL-compatible
- Uso previsto: despliegue del backend y validacion pre-produccion publica
- Estado actual: conectividad funcional validada desde la aplicacion

## Despliegue actual de la BD

La base de datos en nube del proyecto se desplego en `TiDB Cloud Starter` y se
valido con flujos reales de la aplicacion. No se trato solo de una prueba de
conexion aislada: la aplicacion pudo leer y persistir datos correctamente sobre
la instancia remota.

Validaciones realizadas sobre la BD en nube:

- registro de cuentas desde el frontend
- inicio de sesion
- elevacion controlada de un usuario a `ADMIN`
- acceso al panel administrativo
- creacion de anuncios como usuario estandar
- creacion de anuncios como tienda
- persistencia de metadatos de imagenes con soporte Cloudinary

Estas evidencias confirman que la integracion `backend + SQLAlchemy + TiDB`
responde correctamente para los flujos funcionales principales ya probados.

Nota de cierre de iteracion:

- el registro crea correctamente usuarios y tokens en TiDB
- el flujo de verificacion por correo ya funciona con proveedor externo real
- la verificacion cambia el estado del usuario en la BD remota como se espera
- si una prueba falla a mitad del flujo, pueden quedar cuentas en
  `PENDIENTE_VERIFICACION`; en ese caso se pueden limpiar junto con sus tokens
  relacionados antes de repetir pruebas

## Importacion del esquema en nube

La instancia remota se inicializa usando el archivo fuente
`docs/database.sql`.

Proceso aplicado en esta iteracion:

1. crear la base `hardware_ayacucho` en TiDB Cloud
2. ejecutar el contenido de `docs/database.sql` en `SQL Editor`
3. validar que las tablas queden creadas en el schema remoto
4. apuntar `DATABASE_URL` del backend a la instancia cloud
5. probar flujos reales desde la aplicacion

## Conexion del backend a TiDB

La aplicacion backend puede conectarse a TiDB mediante `PyMySQL` usando
`DATABASE_URL`.

Estructura general esperada:

```env
DATABASE_URL=mysql+pymysql://USUARIO:PASSWORD@HOST:4000/hardware_ayacucho?ssl_verify_cert=false&ssl_verify_identity=false
```

Notas:

- `HOST`, `PORT`, `USERNAME` y `PASSWORD` se obtienen desde `Connect` en TiDB
  Cloud
- para pruebas iniciales del proyecto se uso conexion publica
- si la contrasena contiene caracteres especiales, debe codificarse para URL
- en despliegue, las credenciales reales deben quedar solo en variables de
  entorno del proveedor y nunca en el repositorio
- para pruebas repetidas de correo, puede ser necesario eliminar usuarios en
  estado `PENDIENTE_VERIFICACION` y sus filas relacionadas en
  `tokens_verificacion` cuando se quiera volver a registrar el mismo correo

## Tablas principales

- `usuarios`
- `tiendas`
- `tokens_verificacion`
- `anuncios`
- `media_anuncio`
- `reportes`
- `reporte_evidencias`
- `apelaciones_moderacion`
- `apelacion_evidencias`
- `moderacion_log`
- `admin_log`
- `transacciones`
- `calificaciones`
- `contactos_log`

## Tabla `media_anuncio`

La tabla `media_anuncio` sigue siendo la encargada de relacionar archivos
multimedia con cada anuncio, pero desde la integracion con Cloudinary ahora
soporta dos modos de persistencia:

- almacenamiento local historico mediante ruta relativa en `uploads/`
- almacenamiento remoto mediante URL segura y metadatos de Cloudinary

Campos funcionales relevantes:

- `tipo_media`: distingue `imagen` o `video`
- `ruta_relativa`: guarda la ruta local historica o la URL `https` entregada por
  Cloudinary
- `public_id`: identificador remoto del asset en Cloudinary
- `resource_type`: tipo remoto usado por el proveedor, normalmente `image` o
  `video`
- `formato`: extension o formato final reportado por Cloudinary
- `bytes_size`: peso del archivo
- `width` y `height`: dimensiones cuando aplican
- `version`: version remota util para cache busting
- `es_principal` y `orden`: conservan la logica de portada y orden visual de
  imagenes

Decision tecnica actual:

- TiDB almacena metadatos y referencias
- Cloudinary almacena el archivo binario real cuando la integracion esta activa
- el backend conserva compatibilidad con almacenamiento local como fallback para
  entornos sin Cloudinary

## Relaciones clave

- un `usuario` puede tener muchos `anuncios`
- un `usuario` puede tener una `tienda`
- un `anuncio` puede tener multiples registros en `media_anuncio`
- un `anuncio` puede generar `reportes`, `contactos_log` y `transacciones`
- un `reporte` puede generar multiples `reporte_evidencias`
- una `apelacion_moderacion` puede generar multiples `apelacion_evidencias`
- una `transaccion` puede generar `calificaciones`

## Reglas generales

- claves primarias enteras autoincrementales
- claves foraneas con sufijo `_id`
- fechas de auditoria con `created_at` y, cuando aplica, `updated_at`
- uso de estados para moderacion, activacion y ciclo de vida
- `especificaciones` de anuncios almacenadas en JSON

## Reglas de negocio relevantes

- correos, telefonos, RUC y tokens sensibles usan restricciones de unicidad
- un anuncio puede pasar por estados como `ACTIVO`, `INACTIVO`, `VENDIDO` o
  `BLOQUEADO`
- la tabla `media_anuncio` no guarda binarios dentro de TiDB; solo guarda
  referencias y metadatos del archivo
- los flujos de verificacion y recuperacion usan `tokens_verificacion`
- la moderacion administrativa queda auditada en `moderacion_log` y `admin_log`
- un `reporte` puede incluir `detalle` descriptivo y evidencias adjuntas del
  reportante
- un anuncio bloqueado puede recibir una sola `apelacion_moderacion` por ciclo
  de bloqueo y esa apelacion puede adjuntar evidencias propias
- las transacciones y calificaciones soportan reputacion de comprador y vendedor

## Recomendacion

Cuando exista una diferencia entre este resumen y `database.sql`, se debe tomar
como valido `database.sql`.

## Recomendacion operativa para despliegue

- mantener MySQL local como respaldo durante la fase de despliegue
- usar TiDB Cloud como base remota principal para backend en Render
- usar Cloudinary como almacenamiento de imagenes y videos para despliegue
  publico
- no insertar usuarios manuales con contrasena en texto plano
- mantener el flujo real de verificacion por correo para la demo publica,
  sabiendo que algunos mensajes pueden llegar inicialmente a `Spam`
- para cuentas administrativas, preferir:
  1. registro real desde frontend
  2. verificacion real por correo
  3. cambio de `rol` a `ADMIN` por SQL solo cuando sea necesario para la demo

Para cambios incrementales sobre una base ya existente, el proyecto puede dejar
scripts de migracion auxiliares en `scripts/`. En la fase 1 del reporte
enriquecido se agrego `scripts/migrate-moderation-phase1.py` para aplicar los
cambios de `reportes` y `reporte_evidencias` sobre una BD local existente. En
la fase 2 se agrega `scripts/migrate-moderation-phase2.py` para crear
`apelaciones_moderacion` y `apelacion_evidencias`.

La fase 3 de priorizacion y abuso no agrega tablas nuevas en esta iteracion:
trabaja con metricas derivadas calculadas a partir de `usuarios`, `reportes`,
`anuncios`, `moderacion_log` y `transacciones`.

En la integracion de media para despliegue publico, la evolucion relevante de
esta iteracion es la ampliacion de `media_anuncio` con metadatos remotos para
Cloudinary sin cambiar el resto del modelo relacional principal.

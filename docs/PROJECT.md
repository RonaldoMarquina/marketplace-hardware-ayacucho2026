# PROJECT.md — HardwareAyacucho

Plataforma web de anuncios clasificados para la compra y venta segura de hardware nuevo y de segunda mano entre tiendas y usuarios de la región de Ayacucho.

## Objetivo

Conectar compradores y vendedores de componentes de hardware en Ayacucho, Perú, con un sistema de anuncios verificados, contacto directo por WhatsApp y moderación administrativa.

## Roles

| Rol | Descripción |
|-----|-------------|
| USER_ESTANDAR | Ciudadano registrado. Publica hasta 10 anuncios activos. |
| TIENDA_VERIFICADA | Negocio con RUC verificado por admin. Sin límite de anuncios. |
| ADMIN | Modera anuncios, bloquea/desbloquea, revisa reportes. |

## Flujo Principal

- Usuario se registra → recibe correo de verificación (HU-01 / HU-02)
- Activa cuenta → estado ACTIVO (HU-03)
- Publica anuncio con fotos (HU-05 / HU-06)
- Comprador busca y filtra (HU-09 / HU-10)
- Comprador ve detalle → obtiene URL WhatsApp con JWT (HU-11 / HU-12)
- Admin modera reportes si es necesario (HU-13)

## Alcance MVP

- Registro y autenticación con JWT
- Verificación de correo
- Publicación, edición y borrado lógico de anuncios
- Carga de imágenes (máx 5 por anuncio)
- Feed paginado y filtrado técnico por specs JSON
- Contacto directo vía WhatsApp (sin chat interno)
- Panel de moderación para ADMIN

## Fuera de Alcance (MVP)

- Chat interno
- Pagos en línea
- Notificaciones al vendedor al ser bloqueado
- Refresh token
- Contador de vistas

---

## Región

Ayacucho, Perú — prefijo telefónico WhatsApp: 51
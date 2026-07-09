# PROJECT.md - HardwareAyacucho

Plataforma web de anuncios clasificados para compra y venta de hardware nuevo y de segunda mano entre usuarios y tiendas verificadas de Ayacucho, Peru.

## Objetivo

Conectar compradores y vendedores de hardware en Ayacucho con un sistema de anuncios moderados, contacto directo por WhatsApp, reputacion entre usuarios y administracion centralizada.

## Roles

| Rol | Descripcion |
|-----|-------------|
| USER_ESTANDAR | Usuario registrado. Puede publicar hasta 25 anuncios activos. |
| TIENDA_VERIFICADA | Negocio verificado por administracion. No tiene limite de anuncios activos. |
| ADMIN | Modera anuncios, gestiona usuarios y revisa solicitudes de tienda. |

## Historias de Usuario Implementadas

| HU | Funcionalidad |
|----|---------------|
| HU-01 | Registro de usuario estandar |
| HU-02 | Registro de tienda verificada |
| HU-03 | Verificacion de correo electronico |
| HU-04 | Autenticacion con login y JWT |
| HU-05 | Publicar anuncio |
| HU-06 | Carga de imagenes y video del anuncio |
| HU-07 | Edicion de anuncio propio |
| HU-08 | Estados del anuncio |
| HU-09 | Feed principal de anuncios |
| HU-10 | Busqueda y filtrado tecnico |
| HU-11 | Vista detallada del anuncio |
| HU-12 | Contacto directo por WhatsApp |
| HU-13 | Moderacion de anuncios y reportes |
| HU-14 | Marcar anuncio como vendido |
| HU-15 | Calificar al vendedor |
| HU-16 | Calificar al comprador |
| HU-17 | Perfil publico de usuario |
| HU-18 | Historial de transacciones |
| HU-19 | Panel del usuario |
| HU-20 | Gestion de usuarios desde admin |
| HU-21 | Recuperacion de contrasena |

## Flujo Principal

- El usuario o tienda se registra y recibe un enlace de verificacion.
- Tras verificar su correo, puede iniciar sesion segun su estado.
- El vendedor publica un anuncio con imagenes y, opcionalmente, video.
- Los compradores exploran el feed, usan filtros tecnicos y revisan el detalle.
- El contacto se realiza por WhatsApp y queda registrado en el sistema.
- El vendedor puede marcar el anuncio como vendido y luego ambas partes pueden calificarse.
- El usuario dispone de panel privado, historial y perfil publico.
- El administrador revisa reportes, bloquea o desbloquea anuncios y gestiona usuarios.

## Alcance Actual

- Registro de usuarios y tiendas con validaciones
- Verificacion de correo y reenvio de verificacion
- Login con JWT y control de estados de cuenta
- Recuperacion y cambio de contrasena
- Publicacion, edicion y gestion de anuncios
- Carga, reemplazo, eliminacion y reordenamiento de media
- Feed publico, busqueda avanzada y filtros tecnicos por especificaciones
- Detalle de anuncio con visibilidad controlada segun rol y estado
- Contacto por WhatsApp con protecciones y registro de contacto
- Marcado de venta y generacion de transacciones
- Calificaciones entre comprador y vendedor
- Perfil publico, panel privado e historial de transacciones
- Moderacion de anuncios reportados
- Gestion administrativa de usuarios y tiendas

## Fuera de Alcance

- Chat interno en la plataforma
- Pagos en linea
- Pasarela de envio o logistica integrada
- Recomendaciones inteligentes o ranking avanzado
- Notificaciones push en tiempo real

## Region

Ayacucho, Peru

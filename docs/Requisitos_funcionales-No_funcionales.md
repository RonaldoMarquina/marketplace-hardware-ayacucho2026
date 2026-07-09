# Requisitos Funcionales y No Funcionales

## 1. Requisitos funcionales

### RF-01. Registro y acceso

- El sistema debe permitir el registro de usuarios estandar.
- El sistema debe permitir el registro de tiendas verificadas con documento y RUC.
- El sistema debe enviar y validar enlaces de verificacion de correo.
- El sistema debe permitir el inicio de sesion mediante correo y contrasena.
- El sistema debe restringir el acceso segun estado de cuenta y rol.
- El sistema debe permitir la recuperacion de contrasena mediante token temporal.

Historias relacionadas: HU-01, HU-02, HU-03, HU-04, HU-21.

### RF-02. Publicacion y gestion de anuncios

- El sistema debe permitir publicar anuncios de hardware con titulo, descripcion, categoria, subcategoria, condicion, precio y especificaciones.
- El sistema debe permitir cargar imagenes y un video por anuncio.
- El sistema debe permitir editar anuncios propios.
- El sistema debe permitir desactivar, reactivar y marcar anuncios como vendidos segun reglas de negocio.
- El sistema debe controlar los estados del anuncio: ACTIVO, INACTIVO, VENDIDO y BLOQUEADO.
- El sistema debe limitar a los usuarios estandar a 25 anuncios activos simultaneos.

Historias relacionadas: HU-05, HU-06, HU-07, HU-08, HU-14.

### RF-03. Exploracion y busqueda

- El sistema debe mostrar un feed publico de anuncios activos.
- El sistema debe permitir la busqueda por texto.
- El sistema debe permitir filtrar anuncios por categoria, subcategoria, condicion, rango de precio y especificaciones tecnicas.
- El sistema debe mostrar el detalle de cada anuncio con su media, informacion del vendedor y especificaciones.

Historias relacionadas: HU-09, HU-10, HU-11.

### RF-04. Contacto y reputacion

- El sistema debe permitir generar un enlace de contacto por WhatsApp entre comprador y vendedor.
- El sistema debe registrar el contacto realizado sobre un anuncio.
- El sistema debe permitir marcar una venta indicando un comprador valido que haya contactado previamente el anuncio.
- El sistema debe permitir que el comprador califique al vendedor.
- El sistema debe permitir que el vendedor califique al comprador.

Historias relacionadas: HU-12, HU-14, HU-15, HU-16.

### RF-05. Perfil, panel e historial

- El sistema debe mostrar un perfil publico del usuario con reputacion y anuncios activos.
- El sistema debe mostrar un panel privado con resumen de anuncios, reputacion y accesos rapidos.
- El sistema debe mostrar el historial de transacciones del usuario autenticado.

Historias relacionadas: HU-17, HU-18, HU-19.

### RF-06. Moderacion y administracion

- El sistema debe permitir reportar anuncios por motivos definidos.
- El sistema debe permitir al administrador listar anuncios reportados.
- El sistema debe permitir al administrador bloquear y desbloquear anuncios.
- El sistema debe permitir al administrador listar usuarios, ver detalle y consultar su estado.
- El sistema debe permitir al administrador activar tiendas en revision.
- El sistema debe permitir al administrador rechazar tiendas en revision.
- El sistema debe permitir al administrador bloquear y desbloquear usuarios.
- El sistema debe registrar auditoria de acciones administrativas y de moderacion.

Historias relacionadas: HU-13, HU-20.

## 2. Requisitos no funcionales

### RNF-01. Seguridad

- El sistema debe proteger endpoints privados mediante JWT.
- El sistema debe aplicar control de acceso por rol para rutas administrativas.
- El sistema debe almacenar contrasenas usando hash seguro.
- El sistema no debe exponer datos sensibles innecesarios en respuestas publicas.

### RNF-02. Validacion de datos

- El sistema debe validar formato, obligatoriedad y consistencia de los datos de entrada.
- El sistema debe rechazar archivos no permitidos o que excedan los limites definidos.
- El sistema debe validar el estado de usuarios y anuncios antes de ejecutar acciones sensibles.

### RNF-03. Rendimiento

- El sistema debe responder de forma paginada en feed, busquedas, historial y listados administrativos.
- El sistema debe soportar filtros tecnicos sobre especificaciones sin degradar la experiencia de uso en el alcance del proyecto.

### RNF-04. Usabilidad

- El sistema debe ofrecer una interfaz clara para explorar anuncios, publicar productos y gestionar la cuenta.
- El sistema debe presentar mensajes comprensibles ante errores de validacion, autenticacion o permisos.

### RNF-05. Integridad y trazabilidad

- El sistema debe mantener consistencia entre anuncios, media, reportes, transacciones y calificaciones.
- El sistema debe conservar registros de moderacion y auditoria administrativa.

### RNF-06. Disponibilidad funcional

- El sistema debe permitir el acceso desde navegador web en entorno local de desarrollo y despliegue academico.
- El sistema debe mantener separacion entre frontend, backend y base de datos.

### RNF-07. Escalabilidad basica

- El sistema debe permitir ampliar funcionalidades futuras como pagos, chat interno, notificaciones o integraciones externas sin rehacer la arquitectura principal.

## 3. Trazabilidad resumida

| Modulo | Historias de usuario |
|--------|----------------------|
| Registro y autenticacion | HU-01, HU-02, HU-03, HU-04, HU-21 |
| Anuncios y media | HU-05, HU-06, HU-07, HU-08, HU-14 |
| Exploracion y busqueda | HU-09, HU-10, HU-11 |
| Contacto y reputacion | HU-12, HU-15, HU-16 |
| Perfil, panel e historial | HU-17, HU-18, HU-19 |
| Moderacion y administracion | HU-13, HU-20 |

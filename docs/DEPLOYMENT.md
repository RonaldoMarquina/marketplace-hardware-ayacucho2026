# DEPLOYMENT.md - HardwareAyacucho

## Proposito

Este documento describe la estrategia de despliegue de `HardwareAyacucho` para
su salida a produccion publica en un contexto academico de bajo costo.

La documentacion se alinea con la metodologia **SDD (Spec-Driven Development)**
y toma como referencia el cambio OpenSpec:

- `openspec/changes/public-deployment-render-vercel-google-login/`

En esta etapa el objetivo no es construir una infraestructura empresarial, sino
dejar una arquitectura publica, defendible y funcional para presentacion y
evaluacion academica.

## Estado actual del despliegue

### Completado

- base de datos remota desplegada en `TiDB Cloud Starter`
- conectividad del backend validada contra TiDB
- tabla `media_anuncio` ampliada en TiDB con metadatos para Cloudinary
- integracion de media desplegada con `Cloudinary`
- backend desplegado en `Render`
- frontend desplegado en `Vercel`
- comunicacion publica `Vercel -> Render -> TiDB` validada
- dominio academico comprado para correo transaccional:
  - `hardwareayacucho.shop`
- dominio autenticado en `Brevo` para correo transaccional:
  - `hardwareayacucho.shop`
- remitente operativo en produccion:
  - `Soporte HardwareAyacucho <no-reply@hardwareayacucho.shop>`
- pruebas funcionales reales sobre la BD remota:
  - registro
  - verificacion por correo real
  - login
  - acceso admin
  - creacion de anuncios
  - publicacion y visualizacion de imagenes con Cloudinary

### Pendiente

- decision final sobre `Google login`
- mejorar reputacion de entrega para reducir llegada a carpeta `Spam`
- validar en una iteracion posterior la recuperacion de contrasena con el mismo
  proveedor y remitente ya autenticado

## Arquitectura objetivo de produccion publica

```text
Usuario
  -> Frontend (Vercel)
  -> Backend API (Render)
  -> TiDB Cloud Starter
  -> Cloudinary
```

## Decision de despliegue

### Base de datos

- proveedor: `TiDB Cloud Starter`
- razon principal:
  - compatibilidad con MySQL
  - integracion directa con SQLAlchemy
  - costo adecuado para cierre del proyecto academico

### Backend

- proveedor elegido: `Render`
- responsabilidad:
  - exponer la API REST Flask
  - gestionar autenticacion JWT
  - conectarse a TiDB
  - enviar correos reales cuando el proveedor externo quede habilitado
  - subir y registrar imagenes en Cloudinary

### Frontend

- proveedor elegido: `Vercel`
- responsabilidad:
  - servir la SPA React/Vite
  - consumir la API publica del backend
  - exponer la experiencia web publica

### Imagenes y media

- proveedor recomendado: `Cloudinary`
- razon principal:
  - almacenamiento externo mas apropiado que el disco local de Render
  - URLs publicas y CDN
  - menor complejidad de integracion para este proyecto

## Por que no guardar imagenes en TiDB o Render

### No en TiDB

TiDB debe conservar datos estructurados del sistema, no binarios pesados de
imagenes. Lo correcto es guardar en base de datos solo metadatos y referencias.

### No en Render

El disco local de un servicio desplegado no es la mejor fuente de persistencia
para imagenes en una salida publica. En reinicios o redeploys puede perderse la
continuidad de archivos.

## Modelo de persistencia recomendado para media

En `TiDB` se debe guardar por cada imagen:

- `public_id`
- `secure_url`
- `resource_type`
- `format`
- `bytes`
- `width`
- `height`
- `orden`
- `anuncio_id`

En `Cloudinary` se guarda el archivo fisico de la imagen.

## Secuencia recomendada de despliegue

### 1. TiDB

Ya completado.

Objetivo:

- mantener TiDB como fuente remota principal de datos

### 2. Cloudinary

Ya completado.

Objetivo:

- sacar la persistencia de imagenes del filesystem local
- dejar la solucion de media desacoplada del backend

### 3. Render

Ya completado.

Objetivo:

- publicar la API Flask
- apuntar a TiDB
- habilitar integracion real con Cloudinary
- dejar variables de entorno productivas y correo real

### 4. Vercel

Ya completado.

Objetivo:

- apuntar `VITE_API_ORIGIN` a la URL publica de Render
- validar rutas, login y consumo real de imagenes
- reescribir rutas SPA como `/verificar` hacia `index.html` para evitar `404`

### 5. Validacion final

En progreso.

Objetivo:

- demostrar que la plataforma funciona como sistema integrado

## Variables de entorno esperadas

### Backend en Render

```env
FLASK_ENV=production
DATABASE_URL=mysql+pymysql://USUARIO:PASSWORD@HOST:4000/hardware_ayacucho?ssl_verify_cert=false&ssl_verify_identity=false
FRONTEND_URL=https://tu-frontend.vercel.app
FLASK_APP_SECRET=...
JWT_SECRET_KEY=...
EMAIL_DELIVERY_MODE=log|smtp|resend_api
EMAIL_PUBLIC_PRODUCTION=false|true
EMAIL_FROM=...
EMAIL_SUBJECT_PREFIX=[HardwareAyacucho]
BREVO_API_KEY=...
BREVO_API_BASE_URL=https://api.brevo.com/v3/smtp/email
SMTP_HOST=...
SMTP_PORT=587
SMTP_USERNAME=...
SMTP_PASSWORD=...
SMTP_USE_TLS=true
SMTP_USE_SSL=false
SMTP_TIMEOUT_SECONDS=15
RESEND_API_KEY=...
RESEND_API_BASE_URL=https://api.resend.com/emails
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
CLOUDINARY_FOLDER=hardware-ayacucho/anuncios
```

### Frontend en Vercel

```env
VITE_API_ORIGIN=https://tu-backend.onrender.com
```

## Alcance actual de Google login

`Google login` no es un bloqueo para la salida publica inicial y queda fuera de
esta iteracion de go-live.

Decision actual:

- el flujo base de produccion publica sigue siendo:
  - registro
  - verificacion por correo
  - login con correo y password

Preparacion documentada si se retoma despues:

- variables esperadas: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- callback backend de produccion: `https://marketplace-hardware-ayacucho2026.onrender.com/...`
- origen frontend de produccion: `https://marketplace-hardware-ayacucho2026.vercel.app`
- convivencia requerida:
  - no reemplazar login por correo/password
  - no duplicar cuentas si un correo ya existe
  - mantener compatibilidad con roles actuales y verificacion previa

`Google login` puede implementarse despues como mejora opcional, siempre que:

- no rompa el flujo actual
- use secretos OAuth por variables de entorno
- utilice callback URLs de produccion reales

## Checklist de despliegue

### Infraestructura

- [x] TiDB accesible desde entorno cloud
- [x] cuenta Cloudinary creada
- [x] backend configurado en Render
- [x] frontend configurado en Vercel
- [x] dominio `hardwareayacucho.shop` comprado
- [x] dominio `hardwareayacucho.shop` autenticado en Brevo

### Configuracion

- [x] `DATABASE_URL` valida
- [x] `FRONTEND_URL` valida
- [x] `VITE_API_ORIGIN` valida
- [x] secretos JWT y app cargados
- [x] credenciales de Cloudinary configuradas
- [x] remitente con dominio verificado configurado
- [x] proveedor de correo externo enviando exitosamente en produccion mediante `brevo_api`

### Validacion funcional

- [x] registro de usuario
- [x] correo de verificacion recibido
- [x] verificacion exitosa con correo real
- [x] login exitoso
- [x] publicacion de anuncio
- [x] carga de imagen
- [x] visualizacion de imagen desde frontend
- [x] acceso al panel del usuario
- [x] acceso al panel admin
- [x] apertura correcta del enlace `/verificar` desde Vercel sin `404`

## URLs publicas actuales

- frontend publico estable:
  - `https://marketplace-hardware-ayacucho2026.vercel.app`
- backend publico estable:
  - `https://marketplace-hardware-ayacucho2026.onrender.com`

Nota:

- la ruta raiz del backend puede devolver `404`, lo cual es aceptable si los
  endpoints REST bajo `/api/v1/...` responden correctamente

## Estado actual del correo transaccional

Situacion operativa actual:

- el backend soporta `smtp`, `resend_api` y `brevo_api`
- `SMTP` no fue viable en `Render` por `TimeoutError` al abrir conexion saliente
- `Resend API` fue implementado como fallback HTTPS, pero rechazo la cuenta con:
  - `HTTP 403`
  - `error code: 1010`
- la solucion definitiva de esta iteracion fue `Brevo API` por HTTPS
- el dominio `hardwareayacucho.shop` fue autenticado en Brevo
- el remitente activo en produccion es:
  - `Soporte HardwareAyacucho <no-reply@hardwareayacucho.shop>`
- el flujo de verificacion por correo ya entrega mensajes reales y enlaces
  funcionales hacia el frontend publico

Variables efectivas de correo en Render:

```env
EMAIL_DELIVERY_MODE=brevo_api
EMAIL_PUBLIC_PRODUCTION=true
EMAIL_FROM=Soporte HardwareAyacucho <no-reply@hardwareayacucho.shop>
BREVO_API_KEY=...
BREVO_API_BASE_URL=https://api.brevo.com/v3/smtp/email
```

Observaciones operativas:

- el correo puede llegar inicialmente a carpeta `Spam` mientras el dominio y el
  remitente ganan reputacion
- esto es esperable en una salida reciente y no invalida el flujo funcional
- para la demo academica, el criterio cumplido es:
  - el usuario recibe correo real
  - abre el enlace
  - verifica la cuenta

## Evidencia esperada para entrega

Como parte del entregable academico, se recomienda presentar:

- URL publica del frontend
- URL publica del backend
- captura o evidencia de TiDB operativo
- captura o evidencia de Cloudinary almacenando imagenes
- captura o evidencia de Brevo enviando correo transaccional real
- prueba funcional de:
  - registro
  - verificacion por correo real
  - login
  - publicacion de anuncio
  - visualizacion de imagenes
  - acceso administrativo

## Riesgos conocidos

- planes gratuitos pueden dormir servicios o limitar recursos
- una mala configuracion de CORS puede romper la comunicacion frontend/backend
- un proveedor de correo puede enviar inicialmente a `Spam` mientras construye
  reputacion del dominio/remitente
- integrar `Google login` en esta fase puede ampliar innecesariamente el
  alcance

## Recomendacion final

Para cerrar correctamente esta etapa del proyecto:

1. mantener `TiDB` como base remota principal
2. integrar `Cloudinary` para imagenes
3. desplegar backend en `Render` con correo por `Brevo API`
4. desplegar frontend en `Vercel` con reescritura SPA para rutas publicas
5. dejar `Google login` como mejora opcional posterior, salvo que el equipo
   tenga tiempo suficiente para implementarlo sin poner en riesgo la entrega

## Relacion con SDD

Este documento responde a la etapa de despliegue definida mediante SDD y debe
leerse junto con:

- [PROJECT.md](/D:/Repos/marketplace-hardware-ayacucho/docs/PROJECT.md)
- [STACK.md](/D:/Repos/marketplace-hardware-ayacucho/docs/STACK.md)
- [DATABASE.md](/D:/Repos/marketplace-hardware-ayacucho/docs/DATABASE.md)
- [proposal.md](/D:/Repos/marketplace-hardware-ayacucho/openspec/changes/public-deployment-render-vercel-google-login/proposal.md)
- [design.md](/D:/Repos/marketplace-hardware-ayacucho/openspec/changes/public-deployment-render-vercel-google-login/design.md)
- [tasks.md](/D:/Repos/marketplace-hardware-ayacucho/openspec/changes/public-deployment-render-vercel-google-login/tasks.md)

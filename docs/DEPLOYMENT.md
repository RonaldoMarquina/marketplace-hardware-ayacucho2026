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
- pruebas funcionales reales sobre la BD remota:
  - registro
  - verificacion de correo
  - login
  - acceso admin
  - creacion de anuncios

### Pendiente

- almacenamiento persistente de imagenes en nube
- despliegue del backend en `Render`
- despliegue del frontend en `Vercel`
- validacion publica end-to-end
- decision final sobre `Google login`

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

- proveedor propuesto: `Render`
- responsabilidad:
  - exponer la API REST Flask
  - gestionar autenticacion JWT
  - conectarse a TiDB
  - enviar correos reales
  - subir y registrar imagenes en Cloudinary

### Frontend

- proveedor propuesto: `Vercel`
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

Siguiente paso recomendado.

Objetivo:

- sacar la persistencia de imagenes del filesystem local
- dejar la solucion de media desacoplada del backend

### 3. Render

Una vez resuelto Cloudinary, desplegar el backend.

Objetivo:

- publicar la API Flask
- apuntar a TiDB
- habilitar integracion real con Cloudinary
- dejar variables de entorno productivas y correo real

### 4. Vercel

Con el backend publico disponible, desplegar el frontend.

Objetivo:

- apuntar `VITE_API_ORIGIN` a la URL publica de Render
- validar rutas, login y consumo real de imagenes

### 5. Validacion final

Con todo desplegado, ejecutar una verificacion completa.

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
EMAIL_DELIVERY_MODE=smtp
EMAIL_PUBLIC_PRODUCTION=true
EMAIL_FROM=...
EMAIL_SUBJECT_PREFIX=[HardwareAyacucho]
SMTP_HOST=...
SMTP_PORT=587
SMTP_USERNAME=...
SMTP_PASSWORD=...
SMTP_USE_TLS=true
SMTP_USE_SSL=false
SMTP_TIMEOUT_SECONDS=15
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
```

### Frontend en Vercel

```env
VITE_API_ORIGIN=https://tu-backend.onrender.com
```

## Alcance actual de Google login

`Google login` no es un bloqueo para la salida publica inicial.

Decision actual:

- el flujo base de produccion publica sigue siendo:
  - registro
  - verificacion por correo
  - login con correo y password

`Google login` puede implementarse despues como mejora opcional, siempre que:

- no rompa el flujo actual
- use secretos OAuth por variables de entorno
- utilice callback URLs de produccion reales

## Checklist de despliegue

### Infraestructura

- [ ] TiDB accesible desde entorno cloud
- [ ] cuenta Cloudinary creada
- [ ] backend configurado en Render
- [ ] frontend configurado en Vercel

### Configuracion

- [ ] `DATABASE_URL` valida
- [ ] `FRONTEND_URL` valida
- [ ] `VITE_API_ORIGIN` valida
- [ ] secretos JWT y app cargados
- [ ] SMTP real configurado
- [ ] credenciales de Cloudinary configuradas

### Validacion funcional

- [ ] registro de usuario
- [ ] correo de verificacion recibido
- [ ] verificacion exitosa
- [ ] login exitoso
- [ ] publicacion de anuncio
- [ ] carga de imagen
- [ ] visualizacion de imagen desde frontend
- [ ] acceso al panel del usuario
- [ ] acceso al panel admin

## Evidencia esperada para entrega

Como parte del entregable academico, se recomienda presentar:

- URL publica del frontend
- URL publica del backend
- captura o evidencia de TiDB operativo
- captura o evidencia de Cloudinary almacenando imagenes
- prueba funcional de:
  - registro
  - login
  - publicacion de anuncio
  - visualizacion de imagenes
  - acceso administrativo

## Riesgos conocidos

- planes gratuitos pueden dormir servicios o limitar recursos
- una mala configuracion de CORS puede romper la comunicacion frontend/backend
- correo real mal configurado bloquea produccion publica
- integrar `Google login` en esta fase puede ampliar innecesariamente el
  alcance

## Recomendacion final

Para cerrar correctamente esta etapa del proyecto:

1. mantener `TiDB` como base remota principal
2. integrar `Cloudinary` para imagenes
3. desplegar backend en `Render`
4. desplegar frontend en `Vercel`
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

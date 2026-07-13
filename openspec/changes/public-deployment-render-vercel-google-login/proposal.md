## Why

La base de datos remota en TiDB Cloud Starter ya fue validada, pero el proyecto
todavia no cuenta con una ruta formal de salida a produccion publica para
backend y frontend. En esta etapa final del proyecto academico hace falta dejar
una arquitectura de despliegue casi gratuita, operable y documentada, sin
convertir `Google login` en un bloqueo para publicar la aplicacion.

## What Changes

- formalizar el despliegue publico del backend en Render conectado a TiDB Cloud
- formalizar el despliegue publico del frontend en Vercel apuntando al backend
  remoto
- definir configuracion minima de produccion: variables de entorno, CORS,
  URLs publicas, uploads y chequeos operativos basicos
- documentar el flujo de despliegue y validacion posterior al release para un
  entorno academico de bajo costo
- introducir el alcance de `Google login` como integracion opcional y
  desacoplada del login actual por correo y password
- mantener el sistema listo para salir a publico aun si `Google login` no se
  implementa en la primera iteracion de despliegue

## Capabilities

### New Capabilities

- `public-deployment`: capacidad operativa para exponer la plataforma en
  produccion publica con frontend en Vercel, backend en Render y TiDB Cloud
  como base remota principal

### Modified Capabilities

- `auth-security`: la seguridad de autenticacion debe contemplar URLs publicas,
  configuracion productiva real y una futura extension opcional de `Google
  login` sin romper el flujo actual

## Impact

- backend: configuracion de entorno, CORS, secretos, origen frontend y
  conectividad con TiDB Cloud desde Render
- frontend: URL base de API, variables de entorno y validacion de flujos contra
  backend publico desde Vercel
- documentacion tecnica: guia de despliegue, checklist de produccion publica y
  costos/limitaciones del stack gratuito
- autenticacion: definicion de alcance para `Google login`, callback URLs,
  secretos OAuth y convivencia con el login actual
- operacion: dependencias externas de Render, Vercel, TiDB Cloud y proveedor de
  correo real ya exigido para produccion publica

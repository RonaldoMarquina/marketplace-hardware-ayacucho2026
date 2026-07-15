## 1. Backend public deployment

- [x] 1.1 Revisar y ajustar configuracion del backend para Render: `DATABASE_URL`, `FRONTEND_URL`, secretos, correo real y CORS de produccion
- [x] 1.2 Integrar almacenamiento de imagenes con Cloudinary y reemplazar la dependencia de `UPLOAD_FOLDER` para medios publicos
- [x] 1.3 Ajustar modelos o payloads para guardar en TiDB solo metadatos y URLs de Cloudinary, no binarios de imagen
- [x] 1.4 Desplegar el backend en Render conectado a TiDB Cloud y validar arranque sin dependencias locales

## 2. Frontend public deployment

- [x] 2.1 Configurar el frontend para usar la URL publica real del backend mediante variables de entorno de Vercel
- [x] 2.2 Verificar que la UI consuma correctamente las URLs de imagen entregadas por Cloudinary
- [x] 2.3 Desplegar el frontend en Vercel y validar navegacion publica, autenticacion y consumo real de API
- [x] 2.4 Verificar que las rutas protegidas, redirecciones y llamadas autenticadas funcionen con dominios publicos

## 3. Public production validation

- [x] 3.1 Ejecutar checklist funcional post-release: registro, verificacion por correo, login, panel usuario, publicacion de anuncios y panel admin
- [x] 3.2 Validar carga, lectura y persistencia de imagenes usando Cloudinary desde el entorno publico
- [x] 3.3 Documentar la topologia final Vercel + Render + TiDB + Cloudinary y las restricciones operativas del stack gratuito
- [x] 3.4 Registrar evidencia de que los medios ya no dependen del disco efimero de Render

## 4. Google login scope and integration readiness

- [x] 4.1 Definir si `Google login` entra en esta iteracion o queda explicitamente como fase posterior sin bloquear el go-live
- [x] 4.2 Si se implementa, definir variables OAuth, callback URLs y reglas de convivencia con el login actual
- [x] 4.3 Actualizar documentacion y checklist de produccion para reflejar el alcance real de `Google login`

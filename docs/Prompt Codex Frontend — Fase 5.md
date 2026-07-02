# Prompt Codex — Fase 5: Admin

Lee los archivos `docs/FRONTEND_CONTEXT.md` y este prompt completo antes de escribir cualquier línea de código. Respeta la estructura de carpetas y convenciones definidas en el contexto.

## Tarea

Implementa el panel de administración: moderación de anuncios reportados y gestión de usuarios y tiendas. Todas las rutas de esta fase requieren rol ADMIN — ProtectedRoute ya lo maneja.

---

## Layout compartido: `src/components/layout/AdminLayout.jsx`

Crea primero este layout — lo usan todas las páginas admin.

### UI
- Sidebar fija izquierda (colapsable en mobile):
  - Logo / nombre "HardwareAyacucho Admin"
  - Links de navegación:
    - "Anuncios reportados" → `/admin/reportados`
    - "Gestión de usuarios" → `/admin/usuarios`
  - Botón "Volver al sitio" → `/`
  - Botón "Cerrar sesión" → `logout()` + redirigir a `/login`
- Contenido principal a la derecha
- Header con nombre del admin logueado y badge "ADMIN"

### Lógica
- Envolver con `ProtectedRoute requiereAdmin={true}`
- Usar en `AppRoutes.jsx` como layout para todas las rutas `/admin/*`

---

## Página 1: `src/pages/admin/Reportados.jsx`

### UI

**Header**
- Título "Anuncios Reportados"
- Badge con total de pendientes: "X pendientes"

**Tabla de anuncios reportados**

Columnas:
- Miniatura + título del anuncio (clickeable → abre detalle en nueva pestaña)
- Categoría / Subcategoría
- Vendedor (nombre + badge tienda si aplica)
- Total reportes (número destacado)
- Motivos (chips de colores por motivo: FRAUDE rojo, PRODUCTO_FALSO naranja, PRECIO_ENGAÑOSO amarillo, CONTENIDO_INAPROPIADO morado, DUPLICADO gris, OTRO gris)
- Último reporte con `formatDateTime`
- Estado del anuncio (ACTIVO verde, BLOQUEADO rojo)
- Acciones:
  - Botón "Bloquear" (rojo) — visible si estado=ACTIVO
  - Botón "Desbloquear" (verde) — visible si estado=BLOQUEADO

**Modal — Bloquear anuncio**
- Título "Bloquear anuncio"
- Info del anuncio: título, vendedor
- Textarea `motivo_admin` (obligatorio, max 500 chars, contador)
- Botón "Confirmar bloqueo" (rojo)
- Botón "Cancelar"

**Modal — Desbloquear anuncio**
- Título "Desbloquear anuncio"
- Info del anuncio: título, vendedor
- Textarea `motivo_admin` (obligatorio, max 500 chars, contador)
- Botón "Confirmar desbloqueo" (verde)
- Botón "Cancelar"

**Paginación** al final

### Lógica
1. Al montar → llamar `GET /admin/anuncios/reportados?page=1&limit=20`.
2. Paginar con `Paginacion.jsx`.
3. Botón Bloquear → abrir modal, al confirmar:
   - Llamar `PATCH /admin/anuncios/:id/bloquear` con `{ motivo_admin }`.
   - Si responde 200 → actualizar estado del anuncio en la tabla localmente.
   - Mostrar toast de éxito "Anuncio bloqueado correctamente."
4. Botón Desbloquear → abrir modal, al confirmar:
   - Llamar `PATCH /admin/anuncios/:id/desbloquear` con `{ motivo_admin }`.
   - Si responde 200 → actualizar estado localmente.
   - Mostrar toast de éxito "Anuncio desbloqueado correctamente."
5. Si `motivo_admin` vacío → deshabilitar botón de confirmar.
6. Skeleton mientras carga.

---

## Página 2: `src/pages/admin/Usuarios.jsx`

### UI

**Header**
- Título "Gestión de Usuarios"
- Contador total de usuarios

**Filtros**
- Input búsqueda `q` (nombre o correo)
- Select estado: Todos | ACTIVO | PENDIENTE_VERIFICACION | EN_REVISION | BLOQUEADO | RECHAZADO
- Select rol: Todos | USER_ESTANDAR | TIENDA_VERIFICADA
- Botón "Buscar" y "Limpiar"

**Tabla de usuarios**

Columnas:
- ID
- Nombre + correo
- Teléfono
- Rol (USER_ESTANDAR gris, TIENDA_VERIFICADA azul)
- Estado (chip de color):
  - ACTIVO → verde
  - PENDIENTE_VERIFICACION → amarillo
  - EN_REVISION → naranja
  - BLOQUEADO → rojo
  - RECHAZADO → gris oscuro
- Nombre comercial + RUC (si es tienda, sino "—")
- Fecha de registro con `formatDate`
- Acciones (según estado actual):
  - EN_REVISION → botón "Activar" (verde) + botón "Rechazar" (rojo)
  - ACTIVO → botón "Bloquear" (rojo)
  - BLOQUEADO → botón "Desbloquear" (verde)
  - PENDIENTE_VERIFICACION → sin acciones
  - RECHAZADO → sin acciones
- Botón "Ver detalle" siempre visible → abre panel lateral

**Panel lateral — Detalle de usuario**
Slide-in desde la derecha al hacer click en "Ver detalle":
- Todos los datos del usuario
- Si es tienda → datos de tienda + link al documento de identidad
- Reputación como vendedor y comprador con estrellas
- Historial de acciones admin (últimas 5):
  - Acción | Motivo | Admin | Fecha
- Botones de acción según estado (igual que en tabla)

**Modal — Activar tienda**
- Título "Activar cuenta de tienda"
- Info: nombre comercial, RUC, nombre del propietario
- Link al documento de identidad (abrir en nueva pestaña)
- Botón "Confirmar activación" (verde)
- Botón "Cancelar"
- Sin campo de motivo — activar no requiere justificación

**Modal — Rechazar tienda**
- Título "Rechazar solicitud de tienda"
- Info: nombre comercial, RUC
- Textarea `motivo` (obligatorio, max 500 chars, contador)
- Texto de ayuda: "El motivo será registrado en el log de administración."
- Botón "Confirmar rechazo" (rojo)
- Botón "Cancelar"

**Modal — Bloquear usuario**
- Título "Bloquear cuenta"
- Info: nombre, correo, rol
- Advertencia: "Los anuncios activos de este usuario serán desactivados automáticamente."
- Textarea `motivo` (obligatorio, max 500 chars, contador)
- Botón "Confirmar bloqueo" (rojo)
- Botón "Cancelar"

**Modal — Desbloquear usuario**
- Título "Desbloquear cuenta"
- Info: nombre, correo
- Advertencia: "Los anuncios desactivados por el bloqueo NO se reactivarán automáticamente."
- Textarea `motivo` (obligatorio, max 500 chars, contador)
- Botón "Confirmar desbloqueo" (verde)
- Botón "Cancelar"

**Paginación** al final

### Lógica
1. Al montar → llamar `GET /admin/usuarios?page=1&limit=20`.
2. Al buscar → agregar params `q`, `estado`, `rol` a la query.
3. Sincronizar filtros con query params en la URL.
4. Botón Activar → abrir modal, al confirmar:
   - Llamar `PATCH /admin/usuarios/:id/activar`.
   - Si responde 200 → actualizar estado en tabla + panel lateral.
   - Toast "Tienda activada correctamente."
5. Botón Rechazar → abrir modal, al confirmar:
   - Llamar `PATCH /admin/usuarios/:id/rechazar` con `{ motivo }`.
   - Toast "Solicitud rechazada."
6. Botón Bloquear → abrir modal, al confirmar:
   - Llamar `PATCH /admin/usuarios/:id/bloquear` con `{ motivo }`.
   - Mostrar `anuncios_desactivados` en el toast: "Usuario bloqueado. X anuncios desactivados."
7. Botón Desbloquear → abrir modal, al confirmar:
   - Llamar `PATCH /admin/usuarios/:id/desbloquear` con `{ motivo }`.
   - Toast "Usuario desbloqueado correctamente."
8. Botón "Ver detalle" → llamar `GET /admin/usuarios/:id` y abrir panel lateral.
9. Si `motivo` vacío en modales que lo requieren → deshabilitar botón confirmar.
10. Skeleton mientras carga.

---

## Componente compartido: `src/components/ui/Toast.jsx`

Sistema de notificaciones toast reutilizable en toda la app.

### Props
- `mensaje` → string
- `tipo` → "exito" | "error" | "advertencia" | "info"
- `duracion` → ms (default 3000)

### UI
- Aparece en esquina inferior derecha
- Color según tipo: verde | rojo | amarillo | azul
- Ícono según tipo
- Texto del mensaje
- Botón X para cerrar manualmente
- Desaparece automáticamente tras `duracion` ms
- Permite múltiples toasts apilados

### Implementación
- Crear `src/context/ToastContext.jsx` con:
  - `showToast(mensaje, tipo, duracion)` — función global
- Agregar `ToastProvider` en `main.jsx` junto a `AuthProvider`
- Crear hook `src/hooks/useToast.js` para consumirlo

---

## Componente compartido: `src/components/ui/Modal.jsx`

Modal reutilizable para confirmaciones.

### Props
- `abierto` → boolean
- `onCerrar` → callback
- `titulo` → string
- `children` → contenido del modal
- `tamano` → "sm" | "md" | "lg" (default "md")

### UI
- Overlay oscuro con blur
- Card centrada con título, contenido y botones
- Cerrar con click en overlay o botón X
- Animación de entrada suave

---

## Convenciones para esta fase

- Todas las acciones destructivas (bloquear, rechazar) requieren confirmación en modal — nunca acción directa.
- `motivo` obligatorio en rechazar, bloquear y desbloquear — botón confirmar deshabilitado si está vacío.
- Activar no requiere motivo — confirmación simple.
- Tras cada acción exitosa → actualizar estado localmente sin recargar la página.
- Usar `Toast.jsx` para feedback de todas las acciones.
- `formatDate`, `formatDateTime` siempre desde `src/utils/format.js`.
- `Paginacion.jsx` y `SkeletonCard.jsx` de Fase 3.
- `Estrellas.jsx` de Fase 4 para reputación en detalle de usuario.
- El link al documento de identidad construye la URL con `formatImageUrl`.
- Importar siempre axios desde `src/api/axios.js`.

---

## Actualizar `AppRoutes.jsx`

Envolver las rutas admin con `AdminLayout`:

```jsx
<Route path="/admin" element={<AdminLayout />}>
  <Route path="reportados" element={<Reportados />} />
  <Route path="usuarios" element={<Usuarios />} />
</Route>
```

Usar `<Outlet />` dentro de `AdminLayout` para renderizar las páginas hijas.

---

## Verificación final

Cuando termines verifica que:
- [ ] Rutas `/admin/*` redirigen a `/` si no hay token de admin
- [ ] AdminLayout muestra sidebar con navegación correcta
- [ ] Reportados carga lista de anuncios reportados con paginación
- [ ] Modal de bloquear requiere motivo y lo envía al backend
- [ ] Modal de desbloquear requiere motivo y lo envía al backend
- [ ] Estado del anuncio se actualiza en tabla tras bloquear/desbloquear
- [ ] Usuarios carga con filtros funcionales
- [ ] Panel lateral de detalle carga datos del usuario correctamente
- [ ] Activar tienda funciona sin motivo
- [ ] Rechazar tienda requiere motivo
- [ ] Bloquear usuario muestra advertencia de anuncios y requiere motivo
- [ ] Toast aparece tras cada acción exitosa o fallida
- [ ] No hay errores en consola del navegador


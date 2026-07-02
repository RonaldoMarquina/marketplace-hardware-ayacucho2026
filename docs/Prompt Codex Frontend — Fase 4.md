# Prompt Codex — Fase 4: Usuario

Lee los archivos `docs/FRONTEND_CONTEXT.md` y este prompt completo antes de escribir cualquier línea de código. Respeta la estructura de carpetas y convenciones definidas en el contexto.

## Tarea

Implementa las páginas del usuario autenticado: panel de control, historial de transacciones con calificaciones, y perfil público.

---

## Página 1: `src/pages/usuario/Panel.jsx`

### UI

Layout de dos columnas en desktop (sidebar izquierda, contenido derecha).

**Sidebar — Perfil resumido**
- Avatar con inicial del nombre (círculo con color)
- Nombre completo
- Badge "Tienda Verificada" si `es_tienda_verificada === true`
- Correo y teléfono
- Si es tienda → nombre comercial, RUC y dirección
- Badge de estado: ACTIVO (verde)
- Fecha miembro desde con `formatDate`
- Botón "Cerrar sesión" → llama `logout()` y redirige a `/`

**Contenido principal — 4 secciones**

**Sección 1 — Resumen de anuncios**
- 3 cards de métricas lado a lado:
  - Anuncios activos / límite (ej: "3 / 25") — si `TIENDA_VERIFICADA` → "3 / Sin límite"
  - Anuncios inactivos
  - Anuncios vendidos
- Botón "Publicar nuevo anuncio" → `/anuncios/crear`
- Botón "Ver mis anuncios" → filtra feed por usuario (futura mejora, por ahora deshabilitado)

**Sección 2 — Reputación**
- Dos cards lado a lado:
  - **Como vendedor**: estrellas + promedio + total calificaciones + total ventas
  - **Como comprador**: estrellas + promedio + total calificaciones + total compras
- Si `calificacion_promedio === null` → mostrar "Sin calificaciones aún"
- Si `calificaciones_pendientes > 0` → banner amarillo:
  "Tienes {N} calificación(es) pendiente(s). Ve a tu historial para calificar."
  Con link a `/usuario/historial`

**Sección 3 — Mis anuncios activos**
- Grid de AnuncioCard (máx 6, los más recientes)
- Cada card tiene botones extra visibles: "Editar" | "Desactivar"
- Botón "Ver todos" si hay más de 6

**Sección 4 — Accesos rápidos**
- Link "Mi historial de transacciones" → `/usuario/historial`
- Link "Mi perfil público" → `/usuarios/:id/perfil`
- Si `es_admin` → Link "Panel de administración" → `/admin/reportados`

### Lógica
1. Verificar JWT + `esActivo()` (ProtectedRoute ya lo hace).
2. Al montar → llamar `GET /usuarios/me/panel`.
3. Extraer `usuario_id` del AuthContext para construir el link al perfil público.
4. Mostrar skeleton mientras carga.

---

## Página 2: `src/pages/usuario/Historial.jsx`

### UI

**Tabs en la parte superior:**
- "Todas" | "Mis ventas" | "Mis compras"
- Contador de pendientes en badge sobre la tab correspondiente

**Por cada transacción — card expandible:**

Vista colapsada:
- Imagen del anuncio (pequeña)
- Título del anuncio
- Badge "Venta" (azul) o "Compra" (verde)
- Monto con `formatPrice`
- Nombre de la contraparte
- Fecha con `formatDate`
- Si `calificacion_pendiente === true` → badge amarillo "Pendiente calificar"
- Si `calificacion_emitida` → estrellas del puntaje emitido

Vista expandida (al hacer click en la card):
- Toda la info de la vista colapsada
- **Si `calificacion_pendiente === true`:**
  - Formulario de calificación inline:
    - Selector de estrellas (1 a 5, interactivo)
    - Textarea comentario (opcional, max 500 chars, contador)
    - Botón "Enviar calificación"
- **Si `calificacion_emitida` no es null:**
  - Mostrar puntaje emitido con estrellas
  - Mostrar comentario si existe
  - Mostrar fecha con `formatDateTime`

**Resumen fijo arriba:**
- Total ventas | Total compras | Calificaciones pendientes

**Paginación** al final (limit 10)

### Lógica
1. Al montar → llamar `GET /usuarios/me/transacciones?tipo=ambas&page=1&limit=10`.
2. Al cambiar tab → cambiar param `tipo`: `ventas` | `compras` | `ambas`.
3. Sincronizar tab activa con query param `?tipo=` en la URL.
4. Al enviar calificación en una venta:
   - Llamar `POST /transacciones/:id/calificar/comprador` con `{ puntaje, comentario }`.
   - Si responde 200 → actualizar la card localmente sin recargar toda la lista.
5. Al enviar calificación en una compra:
   - Llamar `POST /transacciones/:id/calificar/vendedor` con `{ puntaje, comentario }`.
   - Si responde 200 → actualizar la card localmente.
6. Si responde 409 en calificación → "Ya calificaste esta transacción."
7. Mostrar skeleton mientras carga.

---

## Página 3: `src/pages/usuario/Perfil.jsx`

### UI

**Header del perfil**
- Avatar grande con inicial del nombre
- Nombre completo
- Badge "Tienda Verificada" si aplica
- Si es tienda → nombre comercial y dirección
- Miembro desde con `formatDate`

**Sección reputación — dos cards lado a lado**
- **Como vendedor:**
  - Estrellas interactivas (solo visualización)
  - Promedio con 1 decimal
  - Total calificaciones
  - Total ventas
- **Como comprador:**
  - Estrellas interactivas (solo visualización)
  - Promedio con 1 decimal
  - Total calificaciones
  - Total compras
- Si `calificacion_promedio === null` → "Sin calificaciones aún"

**Sección anuncios activos**
- Título "Anuncios de {nombre}"
- Grid de AnuncioCard (los que devuelve el backend, máx 10)
- Si `total_anuncios_activos > 10` → texto "Y {N} anuncios más"
- Si `anuncios_activos: []` → "Este usuario no tiene anuncios activos"

### Lógica
1. Al montar → llamar `GET /usuarios/:usuario_id/perfil`.
   - `usuario_id` viene de `useParams()`.
2. Si responde 404 → mostrar "Usuario no encontrado" con link al feed.
3. No requiere JWT — es página pública.
4. Mostrar skeleton mientras carga.

---

## Componente compartido: `src/components/ui/Estrellas.jsx`

Reutilizable en Perfil, Historial y Detalle de anuncio.

### Props
- `puntaje` → número 1-5 o null
- `interactivo` → boolean (default false)
- `onCambiar(nuevoPuntaje)` → callback (solo si interactivo=true)
- `tamano` → "sm" | "md" | "lg" (default "md")

### UI
- 5 estrellas SVG
- Si `puntaje === null` → todas grises con texto "Sin calificaciones"
- Si `interactivo === false` → estrellas de solo lectura coloreadas según puntaje
- Si `interactivo === true` → estrellas clickeables con hover effect
- Mostrar el número del puntaje al lado si `tamano !== "sm"`

---

## Componente compartido: `src/components/ui/MetricaCard.jsx`

Card de métrica reutilizable para el panel.

### Props
- `titulo` → string
- `valor` → string o number
- `subtitulo` → string (opcional)
- `color` → "verde" | "azul" | "amarillo" | "gris" (default "gris")

### UI
- Card con borde izquierdo del color indicado
- Título pequeño gris arriba
- Valor grande en el centro
- Subtítulo pequeño abajo si existe

---

## Convenciones para esta fase

- `formatPrice`, `formatDate`, `formatDateTime`, `formatRating`, `formatImageUrl` — siempre desde `src/utils/format.js`.
- El `usuario_id` del usuario autenticado se obtiene de `AuthContext` — nunca hardcodeado.
- Las calificaciones se actualizan localmente en el estado después de enviar — sin recargar la página.
- Si `calificacion_promedio === null` nunca mostrar "0" — mostrar "Sin calificaciones aún".
- Paginación con `Paginacion.jsx` creado en Fase 3.
- Skeleton con `SkeletonCard.jsx` creado en Fase 3.
- `AnuncioCard.jsx` creado en Fase 3 — reutilizar sin modificar.

---

## Verificación final

Cuando termines verifica que:
- [ ] Panel carga correctamente con datos reales del backend
- [ ] Panel muestra límite de anuncios correcto según rol
- [ ] Banner de calificaciones pendientes aparece si hay pendientes
- [ ] Historial cambia de tab y actualiza los resultados
- [ ] Calificación inline funciona y actualiza la card sin recargar
- [ ] No se puede calificar dos veces la misma transacción
- [ ] Perfil público carga sin JWT
- [ ] Perfil muestra dos reputaciones separadas (vendedor y comprador)
- [ ] `calificacion_promedio === null` muestra "Sin calificaciones aún" en todos lados
- [ ] Estrellas interactivas funcionan en el formulario de calificación
- [ ] No hay errores en consola del navegador
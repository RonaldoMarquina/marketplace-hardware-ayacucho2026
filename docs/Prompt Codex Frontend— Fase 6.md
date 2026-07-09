# Prompt Codex — Fase 6: Landing Page

Lee los archivos `docs/FRONTEND_CONTEXT.md` y este prompt completo antes de escribir cualquier línea de código. Respeta la estructura de carpetas y convenciones definidas en el contexto.

## Tarea

Implementa la landing page del marketplace. A diferencia de las fases anteriores, esta página es puramente de presentación y marketing — usa datos reales del backend para mostrar anuncios recientes y estadísticas.

---

## Página: `src/pages/Landing.jsx`

Reemplaza el placeholder del Feed en la ruta `/` solo si el usuario NO está autenticado. Si está autenticado → redirigir directamente al Feed (`/feed`).

### Lógica de redirección en `AppRoutes.jsx`

```jsx
// Ruta /
<Route path="/" element={
  usuario ? <Navigate to="/feed" replace /> : <Landing />
} />

// Ruta /feed (Feed real paginado)
<Route path="/feed" element={<Feed />} />
```

---

## Secciones de la Landing

### Sección 1 — Hero

**UI**
- Fondo oscuro con gradiente sutil (no imagen de stock)
- Headline principal grande:
  "El marketplace de hardware para Ayacucho"
- Subtítulo:
  "Compra y vende componentes, periféricos y equipos de tecnología con vendedores de tu región."
- Dos botones lado a lado:
  - "Explorar anuncios" → `/feed` (primario, color de acento)
  - "Publicar anuncio" → `/login` (secundario, outline)
- Barra de búsqueda rápida debajo de los botones:
  - Input de texto con placeholder "¿Qué estás buscando? Ej: RTX 4070, Teclado mecánico..."
  - Botón "Buscar" → navega a `/buscar?q={texto}`
  - Al presionar Enter → mismo comportamiento

---

### Sección 2 — Categorías destacadas

**UI**
- Título "Explora por categoría"
- Grid de 5 categorías en desktop, 2 en mobile:
  - COMPONENTES → ícono de chip
  - PERIFERICOS → ícono de teclado
  - MONITORES → ícono de monitor
  - PORTATILES → ícono de laptop
  - GABINETES → ícono de case
  - Ver todas → link a `/buscar`
- Cada categoría es un card clickeable → navega a `/buscar?categoria={CATEGORIA}`
- Diseño limpio con ícono SVG grande + nombre de categoría

---

### Sección 3 — Anuncios recientes

**UI**
- Título "Publicaciones recientes"
- Grid de 8 AnuncioCard (componente de Fase 3)
- Botón "Ver todos los anuncios" centrado abajo → `/feed`
- Skeleton de 8 cards mientras carga

**Lógica**
- Al montar → llamar `GET /anuncios?page=1&limit=8`
- Si `data: []` → ocultar sección completa
- Sin paginación en la landing — solo los 8 más recientes

---

### Sección 4 — ¿Por qué HardwareAyacucho?

**UI**
- Título "¿Por qué elegirnos?"
- Grid de 3 cards con ícono + título + descripción:
  - **Vendedores locales** → "Compra a personas y tiendas de Ayacucho. Sin envíos largos ni intermediarios."
  - **Contacto directo** → "Habla directamente con el vendedor por WhatsApp. Sin comisiones ni tarifas ocultas."
  - **Tiendas verificadas** → "Identifica fácilmente a los vendedores verificados por nuestra plataforma."

---

### Sección 5 — Estadísticas

**UI**
- Fondo de acento suave
- 3 métricas grandes centradas:
  - Anuncios activos
  - Categorías disponibles → "10 categorías"
  - Región → "Ayacucho, Perú"
- Solo "Anuncios activos" es un dato real del backend (viene del `total` de `GET /anuncios`)
- Los otros dos son estáticos

---

### Sección 6 — CTA Final

**UI**
- Fondo oscuro
- Título "¿Tienes algo para vender?"
- Subtítulo "Publica tu anuncio gratis en minutos y llega a compradores de Ayacucho."
- Dos botones:
  - "Crear cuenta gratis" → `/register` (primario)
  - "Ya tengo cuenta" → `/login` (secundario, outline)

---

### Sección 7 — Footer

**UI**
- Logo + nombre "HardwareAyacucho"
- Tagline: "El marketplace de hardware de Ayacucho, Perú."
- Links:
  - "Explorar anuncios" → `/feed`
  - "Publicar anuncio" → `/login`
  - "Crear cuenta" → `/register`
  - "Registrar tienda" → `/register/tienda`
- Texto de copyright: "© 2026 HardwareAyacucho. Proyecto universitario — UNSCH."

---

## Actualizar `src/components/layout/Navbar.jsx`

La navbar debe comportarse diferente en la landing vs el resto del sitio:

### Sin sesión (visitante)
- Logo "HardwareAyacucho" → `/`
- Link "Explorar" → `/feed`
- Link "Buscar" → `/buscar`
- Botón "Ingresar" → `/login` (outline)
- Botón "Crear cuenta" → `/register` (primario)

### Con sesión (autenticado)
- Logo → `/feed`
- Link "Explorar" → `/feed`
- Link "Buscar" → `/buscar`
- Botón "Publicar" → `/anuncios/crear` (primario)
- Menú dropdown con nombre del usuario:
  - "Mi panel" → `/usuario/panel`
  - "Mi historial" → `/usuario/historial`
  - "Mi perfil público" → `/usuarios/:id/perfil`
  - Si `es_admin` → "Panel admin" → `/admin/reportados`
  - Separador
  - "Cerrar sesión" → `logout()` + redirigir a `/`

### En mobile
- Hamburger menu con todos los links
- Cerrar al navegar

---

## Convenciones para esta fase

- La landing NO tiene sidebar ni layout de admin — usa solo Navbar y Footer.
- `AnuncioCard.jsx` de Fase 3 — reutilizar sin modificar.
- `SkeletonCard.jsx` de Fase 3 para la sección de anuncios recientes.
- La barra de búsqueda del hero navega a `/buscar?q=` — no hace llamada al backend directamente.
- Las categorías clickeables navegan a `/buscar?categoria=` — el componente Buscar ya maneja ese param.
- Íconos SVG inline o de una librería ligera — sin dependencias pesadas.
- Diseño responsive obligatorio: mobile first.
- Sin animaciones complejas — solo transiciones suaves de hover con Tailwind.
- `formatImageUrl` de `utils/format.js` para imágenes en AnuncioCard.

---

## Verificación final

Cuando termines verifica que:
- [ ] Visitante ve la landing en `/`
- [ ] Usuario autenticado es redirigido a `/feed` desde `/`
- [ ] Barra de búsqueda del hero navega a `/buscar?q=texto`
- [ ] Cards de categorías navegan a `/buscar?categoria=CATEGORIA`
- [ ] Sección de anuncios recientes carga datos reales del backend
- [ ] Skeleton aparece mientras cargan los anuncios
- [ ] Si no hay anuncios la sección se oculta
- [ ] Estadística de anuncios activos refleja el total real
- [ ] Navbar muestra opciones correctas según estado de sesión
- [ ] Dropdown del usuario funciona y cierra al hacer click fuera
- [ ] Footer tiene todos los links correctos
- [ ] Diseño es responsive en mobile, tablet y desktop
- [ ] No hay errores en consola del navegador


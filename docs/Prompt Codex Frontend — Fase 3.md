# Prompt Codex — Fase 3: Core del Marketplace

Lee los archivos `docs/FRONTEND_CONTEXT.md` y este prompt completo antes de escribir cualquier línea de código. Respeta la estructura de carpetas y convenciones definidas en el contexto.

## Tarea

Implementa el núcleo del marketplace: feed, búsqueda, detalle, crear y editar anuncios. Son las páginas más importantes del proyecto.

---

## Componente compartido: `src/components/ui/AnuncioCard.jsx`

Crea primero este componente — lo usan Feed, Buscar y Perfil.

### Props
- `anuncio` → objeto con `id, titulo, precio, categoria, subcategoria, condicion, imagen_principal, vendedor_nombre, es_tienda_verificada, created_at, updated_at`

### UI
- Card con sombra suave y hover con elevación
- Imagen principal arriba (aspect-ratio 4/3)
  - Si `imagen_principal` es null → mostrar placeholder gris con ícono de imagen
  - Usar `formatImageUrl` de `utils/format.js`
- Badge de condición sobre la imagen: NUEVO (verde) | COMO_NUEVO (azul) | USADO (amarillo) | PARA_REPUESTOS (rojo)
- Si `es_tienda_verificada === true` → badge "Tienda Verificada" con ícono de check
- Título (max 2 líneas con truncate)
- Precio formateado con `formatPrice`
- Subcategoría en texto pequeño gris
- Nombre del vendedor
- Fecha con `formatDate`
- Al hacer click → navegar a `/anuncios/:id`

---

## Página 1: `src/pages/anuncios/Feed.jsx`

### UI
- Grid de AnuncioCard responsive: 1 col mobile, 2 col tablet, 3 col desktop, 4 col wide
- Paginación al final: botones Anterior / Siguiente + indicador "Página X de Y"
- Estado vacío: ilustración + "No hay anuncios disponibles por el momento"
- Skeleton loader mientras carga (8 cards grises animadas)

### Lógica
1. Al montar → llamar `GET /anuncios?page=1&limit=20`.
2. Manejar paginación con query param `?page=N` en la URL — sincronizar con `useSearchParams`.
3. Al cambiar página → hacer scroll al top automáticamente.
4. Mostrar skeleton mientras `cargando === true`.
5. Si `data: []` → mostrar estado vacío.

---

## Página 2: `src/pages/anuncios/Buscar.jsx`

### UI

#### Panel de filtros (sidebar en desktop, drawer en mobile)
- Input de búsqueda `q` (texto libre)
- Select de categoría → al cambiar, actualizar opciones de subcategoría
- Select de subcategoría → dependiente de categoría seleccionada
- Select de condición: NUEVO | COMO_NUEVO | USADO | PARA_REPUESTOS
- Inputs precio mínimo y precio máximo lado a lado
- Select de orden: Más reciente | Precio menor | Precio mayor
- Sección "Filtros técnicos" (specs):
  - Botón "Agregar filtro técnico"
  - Permite agregar hasta 10 pares clave-valor dinámicos
  - Cada par tiene: input clave (ej: socket) + input valor (ej: AM4) + botón eliminar
- Botón "Buscar" y botón "Limpiar filtros"

#### Panel de resultados
- Contador "X resultados encontrados"
- Grid de AnuncioCard igual que Feed
- Paginación

### Lógica
1. Leer filtros desde query params de la URL al montar — permite compartir búsquedas.
2. Al buscar → construir query params:
   - Params simples: `q`, `categoria`, `subcategoria`, `condicion`, `precio_min`, `precio_max`, `order_by`
   - Specs: `specs[socket]=AM4&specs[nucleos]=6`
3. Llamar `GET /anuncios/buscar` con todos los params presentes.
4. Actualizar URL con los filtros aplicados sin recargar la página (`useSearchParams`).
5. Mostrar `filtros_aplicados` como chips eliminables sobre los resultados.
6. Al eliminar un chip → quitar ese filtro y rebuscar automáticamente.
7. Subcategorías disponibles según categoría seleccionada — usar el mapa de categorías del FRONTEND_CONTEXT.md.
8. Si `precio_min > precio_max` → mostrar error antes de enviar.
9. Skeleton loader mientras carga.

---

## Página 3: `src/pages/anuncios/Detalle.jsx`

### UI
- Layout de dos columnas en desktop (media izquierda, info derecha)
- **Galería de media:**
  - Imagen principal grande arriba
  - Miniaturas de imágenes abajo, clickeables para cambiar la principal
  - Si hay video → miniatura con ícono play, al clickear reproducir en modal o inline
  - Si no hay media → placeholder gris con ícono
- **Columna de información:**
  - Badge de condición
  - Título (text-2xl)
  - Precio grande con `formatPrice`
  - Categoría → Subcategoría (breadcrumb)
  - Descripción completa
  - Especificaciones técnicas en tabla: clave | valor
    - Formatear claves: `velocidad_base_ghz` → "Velocidad base (GHz)"
    - Omitir valores null o vacíos
  - **Card del vendedor:**
    - Nombre + badge "Tienda Verificada" si aplica
    - Si `es_tienda_verificada` → mostrar nombre comercial y dirección
    - Calificación como vendedor con estrellas (si disponible en HU-17)
    - Botón "Contactar por WhatsApp" (verde)
    - Si no hay JWT → botón redirige a `/login` con mensaje "Inicia sesión para contactar"
  - Fecha de publicación con `formatDate`
  - Si fue editado → "Actualizado el {formatDate(updated_at)}"
- **Si es propietario (`es_propietario === true`):**
  - Banner "Este es tu anuncio"
  - Botones: "Editar" → `/anuncios/:id/editar` | "Desactivar" | "Marcar como vendido"
  - Si `estado_propietario.estado === "INACTIVO"` → botón "Reactivar" + badge "Inactivo"
  - Mostrar `reactivaciones_restantes`

### Lógica
1. Al montar → llamar `GET /anuncios/:id` (con JWT en header si existe — axios lo agrega automáticamente).
2. Si responde 404 → mostrar "Anuncio no encontrado" con link al feed.
3. Si responde 400 → redirigir al feed.
4. Botón WhatsApp → llamar `GET /anuncios/:id/contacto`:
   - Si responde 200 → abrir `whatsapp_url` en nueva pestaña.
   - Si responde 429 → mostrar mensaje con `disponible_en`.
   - Si responde 401 → redirigir a `/login`.
5. Botón Desactivar → confirmar con modal, llamar `PATCH /anuncios/:id/desactivar`, recargar.
6. Botón Reactivar → llamar `PATCH /anuncios/:id/reactivar`, recargar.
7. Botón Marcar vendido → abrir modal para ingresar `comprador_id`, llamar `PATCH /anuncios/:id/vendido`.

---

## Página 4: `src/pages/anuncios/Crear.jsx`

### UI
- Formulario en una columna centrada con secciones:

**Sección 1 — Información básica**
- Input título (max 100 chars, contador de caracteres)
- Select categoría → actualiza subcategorías disponibles
- Select subcategoría (dependiente de categoría)
- Select condición
- Input precio (numérico, prefijo "S/")
- Textarea descripción

**Sección 2 — Especificaciones técnicas**
- Aparece después de seleccionar subcategoría
- Renderizar dinámicamente los campos correspondientes a la subcategoría según el mapa del FRONTEND_CONTEXT.md
- Ejemplos:
  - Procesador → inputs para socket, nucleos, velocidad_base_ghz, velocidad_boost_ghz, generacion, tdp_w + checkbox incluye_cooler
  - GPU → inputs para vram_gb, tipo_memoria, conectores_display, longitud_mm, tdp_w, requiere_pcie_pin, incluye_rgb
  - Todos los campos de specs son opcionales

**Sección 3 — Imágenes y video**
- Zona de drag & drop para imágenes (hasta 8, JPG/PNG/WEBP, max 10MB cada una)
- Zona separada para video (1 MP4, max 30MB)
- Preview de imágenes con botón eliminar
- Orden de imágenes arrastrable (la primera es la principal)
- Validar tamaños y formatos en frontend antes de enviar

**Botón "Publicar anuncio"** (full width, al final)

### Lógica
1. Validar campos obligatorios: titulo, categoria, subcategoria, condicion, precio.
2. Llamar `POST /anuncios` con los campos del anuncio.
3. Si responde 201 → subir media si hay archivos:
   - Llamar `POST /anuncios/:id/media` con las imágenes y video en `FormData`.
4. Tras subir media → redirigir a `/anuncios/:id`.
5. Si falla el POST del anuncio → mostrar error, no subir media.
6. Si falla la subida de media → redirigir igual al anuncio (el anuncio ya existe).
7. Mostrar barra de progreso durante subida de archivos.
8. Si `USER_ESTANDAR` tiene 25 anuncios activos → mostrar advertencia antes del form.

---

## Página 5: `src/pages/anuncios/Editar.jsx`

### UI
- Igual que Crear pero con datos precargados del anuncio
- **Sección adicional — Gestión de media:**
  - Grid de imágenes actuales con botón eliminar en cada una
  - Drag & drop para reordenar imágenes (la primera es la principal)
  - Botón "Guardar orden" si se reordenaron
  - Botón para reemplazar imagen individual (input file oculto)
  - Si hay video → mostrarlo con botón eliminar y botón reemplazar
  - Zona para agregar nuevas imágenes/video si no se alcanzó el límite

### Lógica
1. Al montar → llamar `GET /anuncios/:id` para precargar datos.
2. Si `es_propietario === false` → redirigir a `/`.
3. Si `estado_propietario.estado !== "ACTIVO"` → redirigir a `/`.
4. Al guardar → llamar `PATCH /anuncios/:id` solo con campos modificados.
5. Si `categoria` cambia → `subcategoria` es obligatoria en el mismo PATCH.
6. Operaciones de media:
   - Reordenar → `PATCH /anuncios/:id/media/orden`
   - Eliminar → `DELETE /anuncios/:id/media/:media_id`
   - Reemplazar → `PUT /anuncios/:id/media/:media_id`
   - Agregar → `POST /anuncios/:id/media`
7. Cada operación de media es independiente — un fallo no cancela las otras.
8. Tras guardar → redirigir a `/anuncios/:id`.

---

## Componente compartido: `src/components/ui/Paginacion.jsx`

Reutilizable en Feed, Buscar y otras páginas:
### Props
- `paginacion` → objeto con `total, pagina_actual, total_paginas, limit, tiene_siguiente, tiene_anterior`
- `onCambiarPagina(nuevaPagina)` → callback

### UI
- Botón "← Anterior" deshabilitado si `tiene_anterior === false`
- Indicador "Página X de Y (Z resultados)"
- Botón "Siguiente →" deshabilitado si `tiene_siguiente === false`

---

## Componente compartido: `src/components/ui/SkeletonCard.jsx`

Card de carga animada con `animate-pulse` de Tailwind.
Mismas dimensiones que AnuncioCard.

---

## Mapa de especificaciones por subcategoría

Crea `src/utils/especificaciones.js` con el mapa completo de campos por subcategoría:

```js
export const ESPECIFICACIONES = {
  "Procesador": ["socket", "nucleos", "velocidad_base_ghz", "velocidad_boost_ghz", "generacion", "tdp_w", "incluye_cooler"],
  "Placa Madre": ["socket", "chipset", "factor_forma", "tipo_ram_soportada", "slots_ram", "puertos_m2", "puertos_pcie", "puertos_usb", "incluye_wifi", "incluye_bluetooth"],
  "RAM": ["tipo_ddr", "capacidad_gb", "velocidad_mhz", "cantidad_modulos", "latencia_cl", "incluye_rgb"],
  "GPU": ["vram_gb", "tipo_memoria", "conectores_display", "longitud_mm", "tdp_w", "requiere_pcie_pin", "incluye_rgb"],
  // ... completar con todas las subcategorías del FRONTEND_CONTEXT.md
}

export const CATEGORIAS_SUBCATEGORIAS = {
  "COMPONENTES": ["Procesador", "Placa Madre", "RAM", "GPU", "Almacenamiento", "Fuente Poder"],
  "REFRIGERACION": ["Aire", "Líquida AIO", "Custom Loop", "Pasta Térmica"],
  // ... completar con todas las categorías
}

// Campos booleanos — renderizar como checkbox
export const CAMPOS_BOOLEAN = ["incluye_cooler", "incluye_rgb", "incluye_wifi", "incluye_bluetooth", "inalambrico", "ajustable", "lavable", "autoadhesivo", "reutilizable", "mu_mimo", "curvado", "altura_ajustable", "gestion_cables", "reposapiés", "lumbar_ajustable", "reposabrazos_ajustables", "enfoque_automatico", "incluye_microfono", "incluye_filtro_pop", "incluye_antena", "incluye_protector_sobretension", "os_incluido", "compatible_stylus", "gpu_dedicada", "modular", "resistencia_agua_polvo"]

// Campos numéricos — renderizar como input type number
export const CAMPOS_NUMERICOS = ["nucleos", "capacidad_gb", "velocidad_mhz", "velocidad_base_ghz", "velocidad_boost_ghz", "tdp_w", "vram_gb", "longitud_mm", "slots_ram", "puertos_m2", "puertos_pcie", "puertos_usb", "tamano_radiador_mm", "cantidad_ventiladores", "altura_mm", "tamano_mm", "velocidad_max_rpm", "nivel_ruido_dba", "tasa_refresco_hz", "tamano_pulgadas", "tiempo_respuesta_ms", "velocidad_maxima_mbps", "capacidad_va", "potencia_w", "cantidad_tomas", "tiempo_respaldo_min", "peso_maximo_soportado_kg", "reclinable_grados", "largo_cm", "ancho_cm", "altura_cm", "capacidad_carga_kg", "dpi_maximo", "cantidad_botones", "peso_gramos", "fps_maximo", "campo_vision_grados", "patron_vesa_mm", "peso_maximo_kg", "brazos_cantidad", "ram_gb", "bahias_disco", "puertos_red", "cantidad_leds", "bateria_wh", "bateria_mah", "tamano_pantalla_pulgadas", "velocidad_rpm", "conductividad_termica_wm", "capacidad_gramos", "caudal_lpm", "diametro_tuberia_mm", "grosor_mm", "cantidad_modulos", "latencia_cl", "frecuencia_hz", "tipo_driver_mm", "longitud_m", "velocidad_max_gbps", "velocidad_transferencia_gbps", "carga_maxima_w", "volumen_ml", "cantidad_piezas", "cantidad_tomas", "bandas_wifi", "puertos_lan"]
```

---

## Convenciones para esta fase

- Todos los selects de categoría y subcategoría usan `CATEGORIAS_SUBCATEGORIAS` de `especificaciones.js`.
- Al cambiar categoría → resetear subcategoría y especificaciones a vacío.
- Los campos de especificaciones se renderizan dinámicamente según `ESPECIFICACIONES[subcategoria]`.
- Campos en `CAMPOS_BOOLEAN` → `<input type="checkbox">`.
- Campos en `CAMPOS_NUMERICOS` → `<input type="number" min="0">`.
- Resto → `<input type="text">`.
- Formatear labels de specs: `velocidad_base_ghz` → "Velocidad base (GHz)", `incluye_cooler` → "Incluye cooler".
- Nunca enviar specs con valor vacío o null al backend.
- Importar siempre axios desde `src/api/axios.js`.

---

## Verificación final

Cuando termines verifica que:
- [ ] Feed carga y pagina correctamente
- [ ] Buscar filtra por categoría, subcategoría, condición y precio
- [ ] Buscar soporta múltiples specs simultáneas
- [ ] Los chips de filtros aplicados se eliminan individualmente
- [ ] Detalle muestra galería, specs y card de vendedor
- [ ] Botón WhatsApp abre la URL correcta en nueva pestaña
- [ ] Crear anuncio sube el anuncio y luego la media en pasos separados
- [ ] Editar precarga los datos y permite modificar campos y media
- [ ] Los campos de specs cambian al cambiar la subcategoría
- [ ] Ningún campo de spec vacío se envía al backend
- [ ] No hay errores en consola del navegador
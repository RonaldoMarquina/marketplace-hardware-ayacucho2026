export const CATEGORIAS_SUBCATEGORIAS = {
  COMPONENTES: [
    'PROCESADOR',
    'PLACA_MADRE',
    'RAM',
    'GPU',
    'ALMACENAMIENTO',
    'FUENTE_PODER',
  ],
  REFRIGERACION: ['AIRE', 'LIQUIDA_AIO', 'CUSTOM_LOOP', 'PASTA_TERMICA'],
  GABINETES: ['CASE', 'VENTILADORES', 'SOPORTES_GPU', 'FILTROS'],
  PERIFERICOS: ['TECLADO', 'MOUSE', 'AURICULARES', 'MOUSEPAD', 'MICROFONO', 'WEBCAM'],
  MONITORES: ['MONITOR', 'SOPORTES_VESA', 'CABLES'],
  REDES: ['TARJETA_RED', 'ROUTER', 'ADAPTADORES', 'UPS'],
  MOBILIARIO: ['SILLA_GAMER', 'ESCRITORIO', 'ACCESORIOS'],
  ALMACENAMIENTO_EXTERNO: ['SSD_EXTERNO', 'HDD_EXTERNO', 'EXTERNOS', 'NAS'],
  ACCESORIOS: ['CABLES', 'LIMPIEZA', 'ORGANIZADORES', 'RGB'],
  PORTATILES: ['LAPTOP', 'TABLET'],
}

export const ESPECIFICACIONES = {
  PROCESADOR: [
    'socket',
    'nucleos',
    'velocidad_base_ghz',
    'velocidad_boost_ghz',
    'generacion',
    'tdp_w',
    'incluye_cooler',
  ],
  PLACA_MADRE: [
    'socket',
    'chipset',
    'factor_forma',
    'tipo_ram_soportada',
    'slots_ram',
    'puertos_m2',
    'puertos_pcie',
    'puertos_usb',
    'incluye_wifi',
    'incluye_bluetooth',
  ],
  RAM: [
    'tipo_ddr',
    'capacidad_gb',
    'velocidad_mhz',
    'cantidad_modulos',
    'latencia_cl',
    'incluye_rgb',
  ],
  GPU: [
    'vram_gb',
    'tipo_memoria',
    'conectores_display',
    'longitud_mm',
    'tdp_w',
    'requiere_pcie_pin',
    'incluye_rgb',
  ],
  ALMACENAMIENTO: [
    'capacidad_gb',
    'tipo_memoria',
    'velocidad_transferencia_gbps',
    'velocidad_rpm',
    'factor_forma',
    'resistencia_agua_polvo',
  ],
  FUENTE_PODER: ['potencia_w', 'modular', 'certificacion', 'factor_forma', 'incluye_rgb'],
  AIRE: ['tamano_mm', 'altura_mm', 'cantidad_ventiladores', 'nivel_ruido_dba', 'incluye_rgb'],
  LIQUIDA_AIO: [
    'tamano_radiador_mm',
    'cantidad_ventiladores',
    'nivel_ruido_dba',
    'incluye_rgb',
  ],
  CUSTOM_LOOP: ['caudal_lpm', 'diametro_tuberia_mm', 'capacidad_ml', 'incluye_rgb'],
  PASTA_TERMICA: ['conductividad_termica_wm', 'capacidad_gramos'],
  CASE: [
    'factor_forma',
    'cantidad_ventiladores',
    'altura_mm',
    'longitud_mm',
    'incluye_rgb',
    'gestion_cables',
  ],
  VENTILADORES: ['tamano_mm', 'velocidad_max_rpm', 'nivel_ruido_dba', 'incluye_rgb'],
  SOPORTES_GPU: ['longitud_mm', 'ajustable', 'incluye_rgb'],
  FILTROS: ['tamano_mm', 'lavable', 'reutilizable', 'autoadhesivo'],
  TECLADO: ['inalambrico', 'tipo_switch', 'incluye_rgb', 'cantidad_teclas'],
  MOUSE: ['dpi_maximo', 'cantidad_botones', 'peso_gramos', 'inalambrico', 'incluye_rgb'],
  AURICULARES: ['inalambrico', 'tipo_driver_mm', 'incluye_microfono', 'incluye_rgb'],
  MOUSEPAD: ['largo_cm', 'ancho_cm', 'incluye_rgb', 'resistencia_agua_polvo'],
  MICROFONO: ['tipo_microfono', 'incluye_filtro_pop', 'incluye_rgb'],
  WEBCAM: ['fps_maximo', 'campo_vision_grados', 'enfoque_automatico', 'incluye_microfono'],
  MONITOR: [
    'tamano_pulgadas',
    'tasa_refresco_hz',
    'tiempo_respuesta_ms',
    'resolucion',
    'curvado',
    'incluye_rgb',
  ],
  SOPORTES_VESA: ['patron_vesa_mm', 'peso_maximo_kg', 'brazos_cantidad', 'altura_ajustable'],
  CABLES: ['longitud_m', 'velocidad_max_gbps', 'carga_maxima_w', 'resistencia_agua_polvo'],
  TARJETA_RED: ['velocidad_maxima_mbps', 'incluye_antena', 'mu_mimo'],
  ROUTER: ['velocidad_maxima_mbps', 'bandas_wifi', 'puertos_lan', 'mu_mimo', 'incluye_antena'],
  ADAPTADORES: ['velocidad_max_gbps', 'inalambrico', 'incluye_antena'],
  UPS: ['capacidad_va', 'potencia_w', 'cantidad_tomas', 'tiempo_respaldo_min', 'incluye_protector_sobretension'],
  SILLA_GAMER: [
    'peso_maximo_soportado_kg',
    'reclinable_grados',
    'altura_ajustable',
    'lumbar_ajustable',
    'reposabrazos_ajustables',
    'reposapies',
  ],
  ESCRITORIO: ['largo_cm', 'ancho_cm', 'altura_cm', 'capacidad_carga_kg', 'gestion_cables'],
  ACCESORIOS: ['cantidad_piezas', 'reutilizable', 'autoadhesivo', 'incluye_rgb'],
  SSD_EXTERNO: ['capacidad_gb', 'velocidad_transferencia_gbps', 'resistencia_agua_polvo'],
  HDD_EXTERNO: ['capacidad_gb', 'velocidad_rpm', 'resistencia_agua_polvo'],
  EXTERNOS: ['capacidad_gb', 'velocidad_transferencia_gbps', 'resistencia_agua_polvo'],
  NAS: ['bahias_disco', 'puertos_red', 'capacidad_gb'],
  LIMPIEZA: ['volumen_ml', 'cantidad_piezas', 'reutilizable'],
  ORGANIZADORES: ['cantidad_piezas', 'autoadhesivo', 'reutilizable'],
  RGB: ['cantidad_leds', 'incluye_rgb', 'longitud_m'],
  LAPTOP: [
    'ram_gb',
    'capacidad_gb',
    'tamano_pantalla_pulgadas',
    'bateria_wh',
    'gpu_dedicada',
    'os_incluido',
  ],
  TABLET: [
    'ram_gb',
    'capacidad_gb',
    'tamano_pantalla_pulgadas',
    'bateria_mah',
    'os_incluido',
    'compatible_stylus',
  ],
}

export const CAMPOS_BOOLEAN = [
  'incluye_cooler',
  'incluye_rgb',
  'incluye_wifi',
  'incluye_bluetooth',
  'inalambrico',
  'ajustable',
  'lavable',
  'autoadhesivo',
  'reutilizable',
  'mu_mimo',
  'curvado',
  'altura_ajustable',
  'gestion_cables',
  'reposapies',
  'lumbar_ajustable',
  'reposabrazos_ajustables',
  'enfoque_automatico',
  'incluye_microfono',
  'incluye_filtro_pop',
  'incluye_antena',
  'incluye_protector_sobretension',
  'os_incluido',
  'compatible_stylus',
  'gpu_dedicada',
  'modular',
  'resistencia_agua_polvo',
]

export const CAMPOS_NUMERICOS = [
  'nucleos',
  'capacidad_gb',
  'velocidad_mhz',
  'velocidad_base_ghz',
  'velocidad_boost_ghz',
  'tdp_w',
  'vram_gb',
  'longitud_mm',
  'slots_ram',
  'puertos_m2',
  'puertos_pcie',
  'puertos_usb',
  'tamano_radiador_mm',
  'cantidad_ventiladores',
  'altura_mm',
  'tamano_mm',
  'velocidad_max_rpm',
  'nivel_ruido_dba',
  'tasa_refresco_hz',
  'tamano_pulgadas',
  'tiempo_respuesta_ms',
  'velocidad_maxima_mbps',
  'capacidad_va',
  'potencia_w',
  'cantidad_tomas',
  'tiempo_respaldo_min',
  'peso_maximo_soportado_kg',
  'reclinable_grados',
  'largo_cm',
  'ancho_cm',
  'altura_cm',
  'capacidad_carga_kg',
  'dpi_maximo',
  'cantidad_botones',
  'peso_gramos',
  'fps_maximo',
  'campo_vision_grados',
  'patron_vesa_mm',
  'peso_maximo_kg',
  'brazos_cantidad',
  'ram_gb',
  'bahias_disco',
  'puertos_red',
  'cantidad_leds',
  'bateria_wh',
  'bateria_mah',
  'tamano_pantalla_pulgadas',
  'velocidad_rpm',
  'conductividad_termica_wm',
  'capacidad_gramos',
  'caudal_lpm',
  'diametro_tuberia_mm',
  'grosor_mm',
  'cantidad_modulos',
  'latencia_cl',
  'frecuencia_hz',
  'tipo_driver_mm',
  'longitud_m',
  'velocidad_max_gbps',
  'velocidad_transferencia_gbps',
  'carga_maxima_w',
  'volumen_ml',
  'cantidad_piezas',
  'bandas_wifi',
  'cantidad_teclas',
]

const TAXONOMY_LABELS = {
  COMPONENTES: 'Componentes',
  REFRIGERACION: 'Refrigeracion',
  GABINETES: 'Gabinetes',
  PERIFERICOS: 'Perifericos',
  MONITORES: 'Monitores',
  REDES: 'Redes',
  MOBILIARIO: 'Mobiliario',
  ALMACENAMIENTO_EXTERNO: 'Almacenamiento externo',
  ACCESORIOS: 'Accesorios',
  PORTATILES: 'Portatiles',
  PROCESADOR: 'Procesador',
  PLACA_MADRE: 'Placa Madre',
  RAM: 'RAM',
  GPU: 'GPU',
  ALMACENAMIENTO: 'Almacenamiento',
  FUENTE_PODER: 'Fuente Poder',
  AIRE: 'Aire',
  LIQUIDA_AIO: 'Liquida AIO',
  CUSTOM_LOOP: 'Custom Loop',
  PASTA_TERMICA: 'Pasta Termica',
  CASE: 'Case',
  VENTILADORES: 'Ventiladores',
  SOPORTES_GPU: 'Soportes GPU',
  FILTROS: 'Filtros',
  TECLADO: 'Teclado',
  MOUSE: 'Mouse',
  AURICULARES: 'Auriculares',
  MOUSEPAD: 'Mousepad',
  MICROFONO: 'Microfono',
  WEBCAM: 'Webcam',
  MONITOR: 'Monitor',
  SOPORTES_VESA: 'Soportes VESA',
  CABLES: 'Cables',
  TARJETA_RED: 'Tarjeta Red',
  ROUTER: 'Router',
  ADAPTADORES: 'Adaptadores',
  UPS: 'UPS',
  SILLA_GAMER: 'Silla Gamer',
  ESCRITORIO: 'Escritorio',
  SSD_EXTERNO: 'SSD Externo',
  HDD_EXTERNO: 'HDD Externo',
  EXTERNOS: 'Externos',
  NAS: 'NAS',
  LIMPIEZA: 'Limpieza',
  ORGANIZADORES: 'Organizadores',
  RGB: 'RGB',
  LAPTOP: 'Laptop',
  TABLET: 'Tablet',
}

const SPEC_LABELS = {
  velocidad_base_ghz: 'Velocidad base (GHz)',
  velocidad_boost_ghz: 'Velocidad boost (GHz)',
  tdp_w: 'TDP (W)',
  vram_gb: 'VRAM (GB)',
  capacidad_gb: 'Capacidad (GB)',
  velocidad_mhz: 'Velocidad (MHz)',
  latencia_cl: 'Latencia CL',
  tamano_pulgadas: 'Tamano (pulgadas)',
  tamano_pantalla_pulgadas: 'Tamano pantalla (pulgadas)',
  tasa_refresco_hz: 'Tasa de refresco (Hz)',
  tiempo_respuesta_ms: 'Tiempo de respuesta (ms)',
  longitud_mm: 'Longitud (mm)',
  altura_mm: 'Altura (mm)',
  tamano_mm: 'Tamano (mm)',
  velocidad_max_rpm: 'Velocidad maxima (RPM)',
  nivel_ruido_dba: 'Nivel de ruido (dBA)',
  tamano_radiador_mm: 'Tamano radiador (mm)',
  velocidad_maxima_mbps: 'Velocidad maxima (Mbps)',
  cantidad_ventiladores: 'Cantidad de ventiladores',
  peso_maximo_soportado_kg: 'Peso maximo soportado (kg)',
  peso_maximo_kg: 'Peso maximo (kg)',
  largo_cm: 'Largo (cm)',
  ancho_cm: 'Ancho (cm)',
  altura_cm: 'Altura (cm)',
  capacidad_carga_kg: 'Capacidad de carga (kg)',
  dpi_maximo: 'DPI maximo',
  peso_gramos: 'Peso (g)',
  fps_maximo: 'FPS maximo',
  campo_vision_grados: 'Campo de vision (grados)',
  patron_vesa_mm: 'Patron VESA (mm)',
  bateria_wh: 'Bateria (Wh)',
  bateria_mah: 'Bateria (mAh)',
  conductividad_termica_wm: 'Conductividad termica (W/m)',
  capacidad_gramos: 'Capacidad (g)',
  caudal_lpm: 'Caudal (LPM)',
  diametro_tuberia_mm: 'Diametro tuberia (mm)',
  longitud_m: 'Longitud (m)',
  velocidad_max_gbps: 'Velocidad maxima (Gbps)',
  velocidad_transferencia_gbps: 'Velocidad de transferencia (Gbps)',
  carga_maxima_w: 'Carga maxima (W)',
  volumen_ml: 'Volumen (ml)',
}

export const normalizeTaxonomyValue = (value) =>
  String(value ?? '')
    .trim()
    .replaceAll('-', '_')
    .replace(/\s+/g, '_')
    .toUpperCase()

export const getTaxonomyLabel = (value) =>
  TAXONOMY_LABELS[normalizeTaxonomyValue(value)] ?? String(value ?? '')

export const getSpecLabel = (field) => {
  if (SPEC_LABELS[field]) {
    return SPEC_LABELS[field]
  }

  return String(field ?? '')
    .split('_')
    .filter(Boolean)
    .map((part, index) => {
      const normalized = part.toLowerCase()
      if (normalized === 'ghz') return 'GHz'
      if (normalized === 'gb') return 'GB'
      if (normalized === 'w') return 'W'
      if (normalized === 'mm') return 'mm'
      if (normalized === 'cm') return 'cm'
      if (normalized === 'cl') return 'CL'
      if (normalized === 'rgb') return 'RGB'
      if (normalized === 'usb') return 'USB'
      if (normalized === 'pcie') return 'PCIe'
      if (normalized === 'm2') return 'M.2'
      if (normalized === 'vesa') return 'VESA'
      if (normalized === 'ups') return 'UPS'
      if (normalized === 'wifi') return 'WiFi'
      if (normalized === 'os') return 'OS'
      if (normalized === 'tdp') return 'TDP'
      if (normalized === 'dpi') return 'DPI'
      if (normalized === 'fps') return 'FPS'
      if (normalized === 'lan') return 'LAN'
      return index === 0
        ? normalized.charAt(0).toUpperCase() + normalized.slice(1)
        : normalized
    })
    .join(' ')
}

export const getSpecFieldType = (field) => {
  if (CAMPOS_BOOLEAN.includes(field)) return 'boolean'
  if (CAMPOS_NUMERICOS.includes(field)) return 'number'
  return 'text'
}

export const getSubcategoriesForCategory = (category) =>
  CATEGORIAS_SUBCATEGORIAS[normalizeTaxonomyValue(category)] ?? []

export const sanitizeSpecsPayload = (specs = {}) =>
  Object.fromEntries(
    Object.entries(specs).filter(([, value]) => {
      if (value === null || value === undefined) {
        return false
      }

      if (typeof value === 'string') {
        return value.trim() !== ''
      }

      return true
    }),
  )

## Why

El backend ya permite reportar anuncios y la administracion ya puede revisar
reportes pendientes, pero la experiencia publica del detalle de anuncio no
expone ninguna accion visible para que un usuario normal reporte contenido
problematico. Eso deja una brecha entre capacidad tecnica y experiencia real:
la plataforma parece no tener mecanismo de denuncia desde la UI.

Ademas, al abrir ese flujo en frontend conviene formalizar medidas basicas
contra reportes falsos o abusivos para que la moderacion siga siendo util y no
se convierta en un vector de spam.

## What Changes

- exponer en la pagina publica de detalle un boton o accion visible para
  `Reportar anuncio`
- agregar un modal o formulario guiado con motivos de reporte permitidos por el
  backend
- reforzar la UX del flujo con mensajes claros sobre elegibilidad, limite
  diario, duplicidad y revision manual por administracion
- endurecer el contrato funcional del reporte para reducir abuso sin bloquear
  reportes legitimos

## Capabilities

### Modified Capabilities

- `marketplace-core`: el detalle publico del anuncio pasa de solo contacto a
  incluir una via visible para reportar anuncios
- `admin-moderation`: la moderacion de anuncios reportados queda conectada con
  una entrada publica usable y con reglas explicitas de control de abuso

## Impact

- frontend: `frontend/src/pages/anuncios/Detalle.jsx` y componentes UI
- backend: reutilizacion del endpoint actual de reporte y, si hace falta,
  pequenos ajustes de respuesta o validacion
- testing: cobertura del flujo de reporte desde UI y validaciones de negocio ya
  existentes
- documentacion funcional: alineacion de HU-13 y specs principales con el flujo
  visible al usuario final

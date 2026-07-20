## Context

El footer de `frontend/src/pages/Landing.jsx` contiene actualmente una unica linea que combina el copyright de HardwareAyacucho con la etiqueta `Proyecto universitario - UNSCH.`. El cambio solicitado debe retirar solo la etiqueta academica y preservar el cierre institucional de la marca.

## Goals / Non-Goals

**Goals:**

- Mostrar un footer centrado exclusivamente en la marca HardwareAyacucho.
- Conservar el copyright y el resto de los enlaces y contenidos existentes.
- Limitar la implementacion al componente de la landing.

**Non-Goals:**

- Redisenar el footer o la landing.
- Modificar rutas, navegacion, estilos, API o persistencia.
- Eliminar referencias academicas de documentos internos o de otras vistas.

## Decisions

- Editar solamente la linea de copyright del footer en `Landing.jsx`, porque es el unico punto visible incluido en el alcance solicitado.
- Conservar el texto de copyright como `© 2026 HardwareAyacucho.` y retirar el sufijo academico completo.
- No crear un componente adicional ni una configuracion externa, ya que una abstraccion para un unico texto aumentaria complejidad sin aportar reutilizacion.

## Risks / Trade-offs

- [El texto academico podria seguir presente en otra superficie no incluida] → Limitar la verificacion a la landing y documentar que otras superficies quedan fuera de alcance.
- [La linea actual presenta un caracter de copyright mal codificado en algunas lecturas] → Verificar visualmente que el navegador muestre `©` correctamente despues de editarla.

import { API_ORIGIN } from '../config/api'

const PLACEHOLDER_IMAGE =
  'https://placehold.co/800x600/e2e8f0/475569?text=Sin+imagen'

export const formatPrice = (precio) => {
  const amount = Number(precio ?? 0)
  return `S/ ${amount.toFixed(2)}`
}

export const formatDate = (fecha) => {
  if (!fecha) {
    return ''
  }

  return new Intl.DateTimeFormat('es-PE').format(new Date(fecha))
}

export const formatDateTime = (fecha) => {
  if (!fecha) {
    return ''
  }

  const date = new Date(fecha)
  const datePart = new Intl.DateTimeFormat('es-PE').format(date)
  const timePart = new Intl.DateTimeFormat('es-PE', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).format(date)

  return `${datePart} ${timePart}`
}

export const formatRating = (rating) => {
  if (rating === null || rating === undefined) {
    return 'Sin calificaciones'
  }

  return Number(rating).toFixed(1)
}

export const formatImageUrl = (rutaRelativa) => {
  if (!rutaRelativa) {
    return PLACEHOLDER_IMAGE
  }

  if (/^https?:\/\//i.test(rutaRelativa)) {
    return rutaRelativa
  }

  const normalizedPath = rutaRelativa.startsWith('/') ? rutaRelativa : `/${rutaRelativa}`

  return `${API_ORIGIN}${normalizedPath}`
}

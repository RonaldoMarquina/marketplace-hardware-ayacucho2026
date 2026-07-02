export const getFieldError = (value, fallback = '') => {
  if (Array.isArray(value)) {
    return value[0] ?? fallback
  }

  if (typeof value === 'string') {
    return value
  }

  return fallback
}

export const normalizeFieldErrors = (errors = {}) =>
  Object.fromEntries(
    Object.entries(errors).map(([key, value]) => [key, getFieldError(value)]),
  )

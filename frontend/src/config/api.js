const DEFAULT_API_ORIGIN = 'http://localhost:5000'

const trimTrailingSlash = (value) => value.replace(/\/+$/, '')

export const API_ORIGIN = trimTrailingSlash(
  import.meta.env.VITE_API_ORIGIN || DEFAULT_API_ORIGIN,
)

export const API_BASE_URL = `${API_ORIGIN}/api/v1`

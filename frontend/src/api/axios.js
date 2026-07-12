import axios from 'axios'
import { API_BASE_URL } from '../config/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

const shouldHandleUnauthorizedGlobally = (error) => {
  if (error.response?.status !== 401) {
    return false
  }

  const requestUrl = error.config?.url ?? ''

  if (requestUrl.includes('/auth/login')) {
    return false
  }

  return true
}

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (shouldHandleUnauthorizedGlobally(error)) {
      localStorage.removeItem('token')
      localStorage.removeItem('auth_user')
      window.location.href = '/login'
    }

    return Promise.reject(error)
  },
)

export default api

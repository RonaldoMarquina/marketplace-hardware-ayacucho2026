import { createContext, useEffect, useState } from 'react'

export const AuthContext = createContext()

const getUserFromPayload = (payload) => ({
  id: payload.id ?? payload.sub ?? null,
  nombre: payload.nombre ?? payload.name ?? null,
  correo: payload.correo ?? payload.email ?? null,
  rol: payload.rol ?? null,
  es_tienda_verificada: payload.es_tienda_verificada ?? false,
  estado: payload.estado ?? null,
})

const mergeUserData = (baseUser, overrideUser = {}) => ({
  ...baseUser,
  ...Object.fromEntries(
    Object.entries(overrideUser).filter(([, value]) => value !== undefined && value !== null),
  ),
})

const parseTokenPayload = (token) => {
  try {
    const [, payload] = token.split('.')

    if (!payload) {
      return null
    }

    const normalizedPayload = payload
      .replace(/-/g, '+')
      .replace(/_/g, '/')
      .padEnd(Math.ceil(payload.length / 4) * 4, '=')

    return JSON.parse(atob(normalizedPayload))
  } catch {
    return null
  }
}

const parseStoredUser = () => {
  try {
    const rawUser = localStorage.getItem('auth_user')
    return rawUser ? JSON.parse(rawUser) : null
  } catch {
    return null
  }
}

export const AuthProvider = ({ children }) => {
  const [authState, setAuthState] = useState({
    usuario: null,
    token: null,
    cargando: true,
  })

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('auth_user')
    setAuthState({
      usuario: null,
      token: null,
      cargando: false,
    })
  }

  const login = (token, datosUsuario) => {
    const payload = parseTokenPayload(token)
    const usuario = mergeUserData(getUserFromPayload(payload ?? {}), datosUsuario)

    localStorage.setItem('token', token)
    localStorage.setItem('auth_user', JSON.stringify(usuario))
    setAuthState({
      usuario,
      token,
      cargando: false,
    })
  }

  const updateUser = (partialUser) => {
    setAuthState((current) => {
      const usuario = mergeUserData(current.usuario ?? {}, partialUser)
      localStorage.setItem('auth_user', JSON.stringify(usuario))
      return {
        ...current,
        usuario,
      }
    })
  }

  const esAdmin = () => authState.usuario?.rol === 'ADMIN'
  const esTienda = () => authState.usuario?.es_tienda_verificada === true
  const esActivo = () => authState.usuario?.estado === 'ACTIVO'

  useEffect(() => {
    const token = localStorage.getItem('token')

    if (!token) {
      setAuthState((prevState) => ({ ...prevState, cargando: false }))
      return
    }

    const payload = parseTokenPayload(token)

    if (!payload || payload.exp <= Date.now() / 1000) {
      logout()
      return
    }

    const storedUser = parseStoredUser()

    setAuthState({
      usuario: mergeUserData(getUserFromPayload(payload), storedUser),
      token,
      cargando: false,
    })
  }, [])

  const value = {
    ...authState,
    login,
    updateUser,
    logout,
    esAdmin,
    esTienda,
    esActivo,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export default AuthContext

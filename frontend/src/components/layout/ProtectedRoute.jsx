import { Navigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

const ProtectedRoute = ({
  children,
  requiereAdmin = false,
  requiereActivo = true,
}) => {
  const { usuario, cargando } = useAuth()

  if (cargando) {
    return <div>Cargando...</div>
  }

  if (!usuario) {
    return <Navigate to="/login" replace />
  }

  if (requiereActivo && usuario.estado !== 'ACTIVO') {
    return <Navigate to="/cuenta-pendiente" replace />
  }

  if (requiereAdmin && usuario.rol !== 'ADMIN') {
    return <Navigate to="/" replace />
  }

  return children
}

export default ProtectedRoute

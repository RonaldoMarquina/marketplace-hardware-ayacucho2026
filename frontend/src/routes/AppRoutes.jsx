import { BrowserRouter, Route, Routes } from 'react-router-dom'
import AdminLayout from '../components/layout/AdminLayout'
import Navbar from '../components/layout/Navbar'
import ProtectedRoute from '../components/layout/ProtectedRoute'
import CuentaPendiente from '../pages/auth/CuentaPendiente'
import Login from '../pages/auth/Login'
import Landing from '../pages/Landing'
import RecuperarPassword from '../pages/auth/RecuperarPassword'
import Register from '../pages/auth/Register'
import RegisterTienda from '../pages/auth/RegisterTienda'
import ResetPassword from '../pages/auth/ResetPassword'
import VerificarEmail from '../pages/auth/VerificarEmail'
import Buscar from '../pages/anuncios/Buscar'
import Crear from '../pages/anuncios/Crear'
import Detalle from '../pages/anuncios/Detalle'
import Editar from '../pages/anuncios/Editar'
import Feed from '../pages/anuncios/Feed'
import Reportados from '../pages/admin/Reportados'
import Usuarios from '../pages/admin/Usuarios'
import Historial from '../pages/usuario/Historial'
import Panel from '../pages/usuario/Panel'
import Perfil from '../pages/usuario/Perfil'

const AppRoutesContent = () => (
  <div className="min-h-screen bg-slate-50 text-slate-900">
    <Navbar />
    <Routes>
      <Route path="/" element={<Landing />} />
        <Route path="/feed" element={<Feed />} />
        <Route path="/buscar" element={<Buscar />} />
        <Route path="/anuncios/:id" element={<Detalle />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/register/tienda" element={<RegisterTienda />} />
        <Route path="/verificar-email" element={<VerificarEmail />} />
        <Route path="/verificar" element={<VerificarEmail />} />
        <Route path="/recuperar-password" element={<RecuperarPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/usuarios/:id/perfil" element={<Perfil />} />
        <Route path="/cuenta-pendiente" element={<CuentaPendiente />} />

        <Route
          path="/anuncios/crear"
          element={
            <ProtectedRoute>
              <Crear />
            </ProtectedRoute>
          }
        />
        <Route
          path="/anuncios/:id/editar"
          element={
            <ProtectedRoute>
              <Editar />
            </ProtectedRoute>
          }
        />
        <Route
          path="/usuario/panel"
          element={
            <ProtectedRoute>
              <Panel />
            </ProtectedRoute>
          }
        />
        <Route
          path="/usuario/historial"
          element={
            <ProtectedRoute>
              <Historial />
            </ProtectedRoute>
          }
        />

        <Route path="/admin" element={<AdminLayout />}>
          <Route path="reportados" element={<Reportados />} />
          <Route path="usuarios" element={<Usuarios />} />
        </Route>

        <Route path="*" element={<h1>404 - Pagina no encontrada</h1>} />
    </Routes>
  </div>
)

const AppRoutes = () => (
  <BrowserRouter>
    <AppRoutesContent />
  </BrowserRouter>
)

export default AppRoutes

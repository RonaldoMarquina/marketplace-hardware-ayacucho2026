import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import ProtectedRoute from './ProtectedRoute'

const navItems = [
  { to: '/admin/reportados', label: 'Anuncios reportados' },
  { to: '/admin/usuarios', label: 'Gestion de usuarios' },
]

const AdminLayout = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const { usuario, logout } = useAuth()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <ProtectedRoute requiereAdmin>
      <div className="min-h-screen bg-[linear-gradient(180deg,#f8fafc_0%,#e2e8f0_100%)]">
        <div className="mx-auto flex min-h-screen max-w-[1600px] flex-col lg:flex-row">
          <aside className="border-b border-slate-200 bg-slate-950 px-5 py-5 text-white lg:min-h-screen lg:w-80 lg:border-b-0 lg:border-r">
            <div className="flex items-center justify-between gap-4 lg:block">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-sky-300">
                  Panel interno
                </p>
                <h1 className="mt-2 text-2xl font-black tracking-tight">HardwareAyacucho Admin</h1>
              </div>
              <span className="rounded-full bg-rose-500 px-3 py-1 text-xs font-bold uppercase tracking-[0.14em] text-white lg:hidden">
                ADMIN
              </span>
            </div>

            <nav className="mt-6 grid gap-2">
              {navItems.map((item) => {
                const active = location.pathname === item.to
                return (
                  <Link
                    className={`rounded-2xl px-4 py-3 text-sm font-semibold transition ${
                      active
                        ? 'bg-white text-slate-950 shadow-sm'
                        : 'text-slate-300 hover:bg-white/10 hover:text-white'
                    }`}
                    key={item.to}
                    to={item.to}
                  >
                    {item.label}
                  </Link>
                )
              })}
            </nav>

            <div className="mt-6 grid gap-3 lg:mt-10">
              <Link
                className="rounded-2xl border border-white/15 px-4 py-3 text-sm font-semibold text-slate-200 transition hover:bg-white/10 hover:text-white"
                to="/"
              >
                Volver al sitio
              </Link>
              <button
                className="rounded-2xl bg-rose-500 px-4 py-3 text-sm font-semibold text-white transition hover:bg-rose-600"
                onClick={handleLogout}
                type="button"
              >
                Cerrar sesion
              </button>
            </div>
          </aside>

          <div className="min-w-0 flex-1">
            <header className="border-b border-slate-200 bg-white/90 px-5 py-4 backdrop-blur lg:px-8">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="text-sm text-slate-500">Sesion activa</p>
                  <h2 className="text-lg font-bold text-slate-900">{usuario?.nombre ?? 'Administrador'}</h2>
                </div>
                <span className="rounded-full bg-slate-900 px-4 py-2 text-xs font-bold uppercase tracking-[0.14em] text-white">
                  ADMIN
                </span>
              </div>
            </header>

            <main className="px-4 py-6 lg:px-8">
              <Outlet />
            </main>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  )
}

export default AdminLayout

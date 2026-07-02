import { useEffect, useRef, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

const hiddenPaths = [
  '/login',
  '/register',
  '/register/tienda',
  '/verificar-email',
  '/recuperar-password',
  '/reset-password',
]

const Navbar = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const { usuario, logout, esAdmin } = useAuth()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropdownRef = useRef(null)
  const shouldHideNavbar =
    hiddenPaths.includes(location.pathname) || location.pathname.startsWith('/admin')

  useEffect(() => {
    setMobileOpen(false)
    setDropdownOpen(false)
  }, [location.pathname])

  useEffect(() => {
    if (!dropdownOpen) {
      return undefined
    }

    const handleClickOutside = (event) => {
      if (!dropdownRef.current?.contains(event.target)) {
        setDropdownOpen(false)
      }
    }

    window.addEventListener('mousedown', handleClickOutside)
    return () => window.removeEventListener('mousedown', handleClickOutside)
  }, [dropdownOpen])

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const logoTarget = '/'

  if (shouldHideNavbar) {
    return null
  }

  return (
    <nav className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/90 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
        <Link className="text-lg font-semibold text-slate-900" to={logoTarget}>
          HardwareAyacucho
        </Link>

        <div className="hidden items-center gap-4 text-sm text-slate-700 md:flex">
          <Link className="transition hover:text-sky-700" to="/feed">
            Explorar
          </Link>
          <Link className="transition hover:text-sky-700" to="/buscar">
            Buscar
          </Link>

          {usuario ? (
            <>
              <Link
                className="rounded-full bg-slate-900 px-4 py-2 font-semibold text-white transition hover:bg-slate-800"
                to="/anuncios/crear"
              >
                Publicar
              </Link>

              <div className="relative" ref={dropdownRef}>
                <button
                  className="rounded-full border border-slate-200 px-4 py-2 font-semibold text-slate-700 transition hover:bg-slate-50"
                  onClick={() => setDropdownOpen((current) => !current)}
                  type="button"
                >
                  {usuario.nombre}
                </button>

                {dropdownOpen ? (
                  <div className="absolute right-0 mt-3 w-64 overflow-hidden rounded-[24px] border border-slate-200 bg-white shadow-[0_20px_55px_-35px_rgba(15,23,42,0.45)]">
                    <div className="border-b border-slate-100 px-4 py-3 text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">
                      Mi cuenta
                    </div>
                    <div className="grid p-2 text-sm text-slate-700">
                      <Link className="rounded-2xl px-3 py-2 transition hover:bg-slate-50" to="/usuario/panel">
                        Mi panel
                      </Link>
                      <Link className="rounded-2xl px-3 py-2 transition hover:bg-slate-50" to="/usuario/historial">
                        Mi historial
                      </Link>
                      {usuario.id ? (
                        <Link
                          className="rounded-2xl px-3 py-2 transition hover:bg-slate-50"
                          to={`/usuarios/${usuario.id}/perfil`}
                        >
                          Mi perfil publico
                        </Link>
                      ) : null}
                      {esAdmin() ? (
                        <Link className="rounded-2xl px-3 py-2 transition hover:bg-slate-50" to="/admin/reportados">
                          Panel admin
                        </Link>
                      ) : null}
                      <div className="my-2 h-px bg-slate-100" />
                      <button
                        className="rounded-2xl px-3 py-2 text-left font-semibold text-rose-600 transition hover:bg-rose-50"
                        onClick={handleLogout}
                        type="button"
                      >
                        Cerrar sesion
                      </button>
                    </div>
                  </div>
                ) : null}
              </div>
            </>
          ) : (
            <>
              <Link
                className="rounded-full border border-slate-300 px-4 py-2 font-semibold text-slate-700 transition hover:border-slate-400 hover:bg-slate-50"
                to="/login"
              >
                Ingresar
              </Link>
              <Link
                className="rounded-full bg-slate-900 px-4 py-2 font-semibold text-white transition hover:bg-slate-800"
                to="/register"
              >
                Crear cuenta
              </Link>
            </>
          )}
        </div>

        <button
          className="inline-flex rounded-full border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-700 md:hidden"
          onClick={() => setMobileOpen((current) => !current)}
          type="button"
        >
          Menu
        </button>
      </div>

      {mobileOpen ? (
        <div className="border-t border-slate-200 bg-white px-4 py-4 md:hidden">
          <div className="grid gap-3 text-sm text-slate-700">
            <Link className="rounded-2xl px-3 py-2 transition hover:bg-slate-50" to="/feed">
              Explorar
            </Link>
            <Link className="rounded-2xl px-3 py-2 transition hover:bg-slate-50" to="/buscar">
              Buscar
            </Link>

            {usuario ? (
              <>
                <Link className="rounded-2xl bg-slate-900 px-3 py-3 text-center font-semibold text-white" to="/anuncios/crear">
                  Publicar
                </Link>
                <Link className="rounded-2xl px-3 py-2 transition hover:bg-slate-50" to="/usuario/panel">
                  Mi panel
                </Link>
                <Link className="rounded-2xl px-3 py-2 transition hover:bg-slate-50" to="/usuario/historial">
                  Mi historial
                </Link>
                {usuario.id ? (
                  <Link className="rounded-2xl px-3 py-2 transition hover:bg-slate-50" to={`/usuarios/${usuario.id}/perfil`}>
                    Mi perfil publico
                  </Link>
                ) : null}
                {esAdmin() ? (
                  <Link className="rounded-2xl px-3 py-2 transition hover:bg-slate-50" to="/admin/reportados">
                    Panel admin
                  </Link>
                ) : null}
                <button
                  className="rounded-2xl border border-rose-200 px-3 py-3 text-left font-semibold text-rose-600"
                  onClick={handleLogout}
                  type="button"
                >
                  Cerrar sesion
                </button>
              </>
            ) : (
              <>
                <Link className="rounded-2xl border border-slate-200 px-3 py-3 text-center font-semibold text-slate-700" to="/login">
                  Ingresar
                </Link>
                <Link className="rounded-2xl bg-slate-900 px-3 py-3 text-center font-semibold text-white" to="/register">
                  Crear cuenta
                </Link>
              </>
            )}
          </div>
        </div>
      ) : null}
    </nav>
  )
}

export default Navbar

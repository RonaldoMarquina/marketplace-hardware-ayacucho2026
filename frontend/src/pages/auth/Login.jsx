import { useEffect, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import api from '../../api/axios'
import PasswordInput from '../../components/ui/PasswordInput'
import { useAuth } from '../../hooks/useAuth'
import { formatDateTime } from '../../utils/format'
import { isValidEmail } from '../../utils/validators'

const Login = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const { login } = useAuth()
  const [form, setForm] = useState({
    correo: '',
    password: '',
  })
  const [errors, setErrors] = useState({})
  const [generalError, setGeneralError] = useState('')
  const [reenvioCorreo, setReenvioCorreo] = useState('')
  const [cargando, setCargando] = useState(false)

  useEffect(() => {
    if (location.state?.message) {
      setGeneralError(location.state.message)
    }
  }, [location.state])

  const handleChange = (event) => {
    const { name, value } = event.target
    setForm((current) => ({ ...current, [name]: value }))
    setErrors((current) => ({ ...current, [name]: '' }))
    setGeneralError('')
    setReenvioCorreo('')
  }

  const handleSubmit = async (event) => {
    event.preventDefault()

    const nextErrors = {}

    if (!isValidEmail(form.correo.trim())) {
      nextErrors.correo = 'Ingresa un correo valido.'
    }

    if (!form.password) {
      nextErrors.password = 'Ingresa tu contraseña.'
    }

    if (Object.keys(nextErrors).length > 0) {
      setErrors(nextErrors)
      return
    }

    setCargando(true)
    setGeneralError('')
    setReenvioCorreo('')

    try {
      const response = await api.post('/auth/login', {
        correo: form.correo.trim(),
        password: form.password,
      })

      const { token, rol, nombre, correo, es_tienda_verificada, estado, id } =
        response.data.data

      login(token, {
        id: id ?? null,
        nombre,
        correo,
        rol,
        es_tienda_verificada,
        estado,
      })

      navigate(rol === 'ADMIN' ? '/admin/reportados' : '/')
    } catch (error) {
      const status = error.response?.status
      const errorCode = error.response?.data?.error
      const errorData = error.response?.data?.data ?? {}

      if (status === 401 || errorCode === 'INVALID_CREDENTIALS') {
        setGeneralError('Correo o contraseña incorrectos.')
      } else if (status === 403 && errorCode === 'ACCOUNT_PENDING') {
        setGeneralError(
          'Debes verificar tu correo antes de iniciar sesion. Puedes reenviar el correo de verificacion.'
        )
        setReenvioCorreo(form.correo.trim())
      } else if (status === 403 && errorCode === 'ACCOUNT_IN_REVIEW') {
        setGeneralError(
          'Tu solicitud de tienda esta en revision. Te avisaremos cuando termine la validacion.'
        )
      } else if (status === 403 && errorCode === 'ACCOUNT_BLOCKED') {
        setGeneralError(
          'Tu cuenta ha sido suspendida. Contacta al administrador para mas informacion.'
        )
      } else if (status === 429) {
        setGeneralError(
          `Demasiados intentos. Intenta nuevamente el ${formatDateTime(errorData.disponible_en)}.`
        )
      } else {
        setGeneralError(
          error.response?.data?.mensaje ||
            error.response?.data?.message ||
            error.response?.data?.error ||
            'No se pudo iniciar sesion.'
        )
      }
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top,#e0f2fe,transparent_35%),linear-gradient(180deg,#f8fafc_0%,#e2e8f0_100%)] px-4 py-10">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <Link className="text-3xl font-black tracking-tight text-slate-900" to="/">
            HardwareAyacucho
          </Link>
          <p className="mt-2 text-sm text-slate-600">
            Ingresa para publicar, vender y gestionar tu cuenta.
          </p>
        </div>

        <div className="rounded-[28px] border border-white/70 bg-white/90 p-8 shadow-[0_25px_80px_-35px_rgba(15,23,42,0.45)] backdrop-blur">
          <form className="space-y-5" onSubmit={handleSubmit}>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700" htmlFor="correo">
                Correo electronico
              </label>
              <input
                className={`w-full rounded-2xl border bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 ${
                  errors.correo ? 'border-rose-400' : 'border-slate-200 focus:border-sky-400'
                }`}
                id="correo"
                name="correo"
                onChange={handleChange}
                placeholder="correo@ejemplo.com"
                type="email"
                value={form.correo}
              />
              {errors.correo ? (
                <p className="text-sm text-rose-600">{errors.correo}</p>
              ) : null}
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700" htmlFor="password">
                Contraseña
              </label>
              <PasswordInput
                autoComplete="current-password"
                error={errors.password}
                name="password"
                onChange={handleChange}
                placeholder="Ingresa tu contraseña"
                value={form.password}
              />
            </div>

            <button
              className="w-full rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
              disabled={cargando}
              type="submit"
            >
              {cargando ? 'Ingresando...' : 'Ingresar'}
            </button>

            {generalError ? (
              <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
                <p>{generalError}</p>
                {reenvioCorreo ? (
                  <Link
                    className="mt-2 inline-block font-semibold text-rose-700 underline"
                    to="/verificar-email"
                    state={{ correo: reenvioCorreo }}
                  >
                    Reenviar verificacion
                  </Link>
                ) : null}
              </div>
            ) : null}

            <div className="space-y-3 text-center text-sm">
              <Link className="text-sky-700 hover:text-sky-800" to="/recuperar-password">
                ¿Olvidaste tu contraseña?
              </Link>
              <p className="text-slate-600">
                ¿No tienes cuenta?{' '}
                <Link className="font-semibold text-slate-900 hover:text-sky-700" to="/register">
                  Crear cuenta
                </Link>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

export default Login

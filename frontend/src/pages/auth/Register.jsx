import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import api from '../../api/axios'
import PasswordInput from '../../components/ui/PasswordInput'
import { normalizeFieldErrors } from '../../utils/forms'
import {
  isValidEmail,
  isValidPassword,
  isValidPhone,
} from '../../utils/validators'

const passwordRules = [
  {
    label: 'Minimo 8 caracteres',
    test: (password) => password.length >= 8,
  },
  {
    label: 'Al menos 1 mayuscula',
    test: (password) => /[A-Z]/.test(password),
  },
  {
    label: 'Al menos 1 numero',
    test: (password) => /\d/.test(password),
  },
  {
    label: 'Al menos 1 caracter especial',
    test: (password) => /[^A-Za-z0-9]/.test(password),
  },
]

const Register = () => {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    nombre: '',
    correo: '',
    password: '',
    confirmarPassword: '',
    telefono: '',
  })
  const [errors, setErrors] = useState({})
  const [generalError, setGeneralError] = useState('')
  const [cargando, setCargando] = useState(false)

  const handleChange = (event) => {
    const { name, value } = event.target
    setForm((current) => ({ ...current, [name]: value }))
    setErrors((current) => ({ ...current, [name]: '' }))
    setGeneralError('')
  }

  const validateForm = () => {
    const nextErrors = {}

    if (!form.nombre.trim()) {
      nextErrors.nombre = 'Ingresa tu nombre.'
    }

    if (!isValidEmail(form.correo.trim())) {
      nextErrors.correo = 'Ingresa un correo valido.'
    }

    if (!isValidPassword(form.password)) {
      nextErrors.password = 'La contraseña no cumple los requisitos.'
    }

    if (form.password !== form.confirmarPassword) {
      nextErrors.confirmarPassword = 'Las contraseñas no coinciden.'
    }

    if (!isValidPhone(form.telefono.trim())) {
      nextErrors.telefono = 'Ingresa un telefono peruano de 9 digitos.'
    }

    return nextErrors
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    const nextErrors = validateForm()

    if (Object.keys(nextErrors).length > 0) {
      setErrors(nextErrors)
      return
    }

    setCargando(true)
    setGeneralError('')

    try {
      await api.post('/auth/register', {
        nombre: form.nombre.trim(),
        correo: form.correo.trim(),
        password: form.password,
        telefono: form.telefono.trim(),
      })

      navigate('/verificar-email', {
        state: { correo: form.correo.trim() },
      })
    } catch (error) {
      const status = error.response?.status
      const message =
        error.response?.data?.mensaje ||
        error.response?.data?.message ||
        error.response?.data?.error ||
        ''
      const fieldErrors = error.response?.data?.data ?? {}

      if (status === 409) {
        if (message.toLowerCase().includes('correo')) {
          setErrors((current) => ({
            ...current,
            correo: 'Este correo ya se encuentra registrado.',
          }))
        } else if (message.toLowerCase().includes('telefono')) {
          setErrors((current) => ({
            ...current,
            telefono: 'Este telefono ya se encuentra registrado.',
          }))
        } else {
          setGeneralError(message || 'No se pudo crear la cuenta.')
        }
      } else if (status === 422 || status === 400) {
        setErrors((current) => ({
          ...current,
          ...normalizeFieldErrors(fieldErrors),
        }))
      } else {
        setGeneralError(message || 'No se pudo crear la cuenta.')
      }
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[linear-gradient(180deg,#fff7ed_0%,#ffedd5_32%,#f8fafc_100%)] px-4 py-10">
      <div className="w-full max-w-lg rounded-[30px] border border-orange-100 bg-white p-8 shadow-[0_30px_80px_-35px_rgba(194,65,12,0.35)]">
        <div className="mb-8 text-center">
          <Link className="text-3xl font-black tracking-tight text-slate-900" to="/">
            HardwareAyacucho
          </Link>
          <p className="mt-2 text-sm text-slate-600">
            Crea tu cuenta para empezar a comprar y vender hardware.
          </p>
        </div>

        <form className="space-y-5" onSubmit={handleSubmit}>
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700" htmlFor="nombre">
              Nombre completo
            </label>
            <input
              className={`w-full rounded-2xl border px-4 py-3 text-sm outline-none ${
                errors.nombre ? 'border-rose-400' : 'border-slate-200 focus:border-orange-400'
              }`}
              id="nombre"
              name="nombre"
              onChange={handleChange}
              placeholder="Tu nombre completo"
              type="text"
              value={form.nombre}
            />
            {errors.nombre ? <p className="text-sm text-rose-600">{errors.nombre}</p> : null}
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700" htmlFor="correo">
              Correo electronico
            </label>
            <input
              className={`w-full rounded-2xl border px-4 py-3 text-sm outline-none ${
                errors.correo ? 'border-rose-400' : 'border-slate-200 focus:border-orange-400'
              }`}
              id="correo"
              name="correo"
              onChange={handleChange}
              placeholder="correo@ejemplo.com"
              type="email"
              value={form.correo}
            />
            {errors.correo ? <p className="text-sm text-rose-600">{errors.correo}</p> : null}
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700" htmlFor="password">
              Contraseña
            </label>
            <PasswordInput
              autoComplete="new-password"
              error={errors.password}
              name="password"
              onChange={handleChange}
              placeholder="Crea una contraseña segura"
              value={form.password}
            />
            <div className="grid gap-2 rounded-2xl bg-orange-50 p-4 text-sm text-slate-600">
              {passwordRules.map((rule) => {
                const fulfilled = rule.test(form.password)

                return (
                  <p key={rule.label} className={fulfilled ? 'text-emerald-700' : 'text-slate-500'}>
                    {fulfilled ? 'OK' : '--'} {rule.label}
                  </p>
                )
              })}
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700" htmlFor="confirmarPassword">
              Confirmar contraseña
            </label>
            <PasswordInput
              autoComplete="new-password"
              error={errors.confirmarPassword}
              name="confirmarPassword"
              onChange={handleChange}
              placeholder="Repite tu contraseña"
              value={form.confirmarPassword}
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700" htmlFor="telefono">
              Telefono
            </label>
            <input
              className={`w-full rounded-2xl border px-4 py-3 text-sm outline-none ${
                errors.telefono ? 'border-rose-400' : 'border-slate-200 focus:border-orange-400'
              }`}
              id="telefono"
              name="telefono"
              onChange={handleChange}
              placeholder="987654321"
              type="text"
              value={form.telefono}
            />
            {errors.telefono ? (
              <p className="text-sm text-rose-600">{errors.telefono}</p>
            ) : null}
          </div>

          {generalError ? (
            <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
              {generalError}
            </div>
          ) : null}

          <button
            className="w-full rounded-2xl bg-orange-500 px-4 py-3 text-sm font-semibold text-white transition hover:bg-orange-600 disabled:cursor-not-allowed disabled:bg-orange-300"
            disabled={cargando}
            type="submit"
          >
            {cargando ? 'Cargando...' : 'Crear cuenta'}
          </button>

          <div className="space-y-3 text-center text-sm">
            <p className="text-slate-600">
              ¿Ya tienes cuenta?{' '}
              <Link className="font-semibold text-slate-900 hover:text-orange-600" to="/login">
                Ingresar
              </Link>
            </p>
            <Link className="text-orange-700 hover:text-orange-800" to="/register/tienda">
              ¿Tienes una tienda? Registrala aqui
            </Link>
          </div>
        </form>
      </div>
    </div>
  )
}

export default Register

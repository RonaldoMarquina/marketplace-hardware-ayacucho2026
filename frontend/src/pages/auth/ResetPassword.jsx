import { Link, Navigate, useLocation } from 'react-router-dom'
import { useMemo, useState } from 'react'
import api from '../../api/axios'
import PasswordInput from '../../components/ui/PasswordInput'
import { isValidPassword } from '../../utils/validators'

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

const resolveTokenFromLocation = (location) => {
  const searchToken = new URLSearchParams(location.search).get('token')
  if (searchToken) {
    return searchToken
  }

  const normalizedHash = location.hash.startsWith('#')
    ? location.hash.slice(1)
    : location.hash

  if (!normalizedHash) {
    return ''
  }

  if (normalizedHash.startsWith('token=')) {
    return new URLSearchParams(normalizedHash).get('token') ?? ''
  }

  const hashQueryIndex = normalizedHash.indexOf('?')
  if (hashQueryIndex >= 0) {
    return new URLSearchParams(normalizedHash.slice(hashQueryIndex + 1)).get('token') ?? ''
  }

  return ''
}

const ResetPassword = () => {
  const location = useLocation()
  const token = useMemo(() => resolveTokenFromLocation(location), [location])
  const [form, setForm] = useState({
    password: '',
    confirmarPassword: '',
  })
  const [errors, setErrors] = useState({})
  const [generalError, setGeneralError] = useState('')
  const [success, setSuccess] = useState(false)
  const [cargando, setCargando] = useState(false)

  if (!token) {
    return <Navigate replace to="/recuperar-password" />
  }

  const handleChange = (event) => {
    const { name, value } = event.target
    setForm((current) => ({ ...current, [name]: value }))
    setErrors((current) => ({ ...current, [name]: '' }))
    setGeneralError('')
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    const nextErrors = {}

    if (!isValidPassword(form.password)) {
      nextErrors.password = 'La contraseña no cumple los requisitos.'
    }

    if (form.password !== form.confirmarPassword) {
      nextErrors.confirmarPassword = 'Las contraseñas no coinciden.'
    }

    if (Object.keys(nextErrors).length > 0) {
      setErrors(nextErrors)
      return
    }

    setCargando(true)
    setGeneralError('')

    try {
      await api.post('/auth/password/reset', {
        token,
        password: form.password,
      })
      setSuccess(true)
    } catch (error) {
      const status = error.response?.status
      const errorCode = error.response?.data?.error

      if (status === 404) {
        setGeneralError('Enlace invalido.')
      } else if (status === 409 && errorCode === 'TOKEN_USED') {
        setGeneralError('Este enlace ya fue usado.')
      } else if (status === 410) {
        setGeneralError('Enlace expirado.')
      } else if (status === 409 && errorCode === 'CONFLICT') {
        setGeneralError('La nueva contraseña debe ser diferente a la actual.')
      } else if (status === 403) {
        setGeneralError(
          error.response?.data?.message ||
            'La cuenta no permite restablecer la contraseña en este momento.'
        )
      } else {
        setGeneralError(
          error.response?.data?.mensaje ||
            error.response?.data?.message ||
            'No se pudo cambiar la contraseña.'
        )
      }
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[linear-gradient(180deg,#ede9fe_0%,#f8fafc_100%)] px-4 py-10">
      <div className="w-full max-w-lg rounded-[30px] border border-violet-100 bg-white p-8 shadow-[0_30px_90px_-40px_rgba(91,33,182,0.35)]">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-black text-slate-900">Nueva contraseña</h1>
          <p className="mt-2 text-sm text-slate-600">
            Elige una contraseña nueva y segura para tu cuenta.
          </p>
        </div>

        {success ? (
          <div className="space-y-5 text-center">
            <div className="rounded-2xl bg-emerald-50 px-4 py-4 text-sm text-emerald-800">
              Contraseña actualizada. Ya puedes ingresar.
            </div>
            <Link className="text-sm font-semibold text-slate-900 hover:text-violet-700" to="/login">
              Ir al login
            </Link>
          </div>
        ) : (
          <form className="space-y-5" onSubmit={handleSubmit}>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700" htmlFor="password">
                Contraseña nueva
              </label>
              <PasswordInput
                autoComplete="new-password"
                error={errors.password}
                name="password"
                onChange={handleChange}
                placeholder="Nueva contraseña"
                value={form.password}
              />
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
                placeholder="Repite tu nueva contraseña"
                value={form.confirmarPassword}
              />
            </div>

            <div className="grid gap-2 rounded-2xl bg-violet-50 p-4 text-sm text-slate-600">
              {passwordRules.map((rule) => {
                const fulfilled = rule.test(form.password)

                return (
                  <p key={rule.label} className={fulfilled ? 'text-emerald-700' : 'text-slate-500'}>
                    {fulfilled ? 'OK' : '--'} {rule.label}
                  </p>
                )
              })}
            </div>

            {generalError ? (
              <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
                {generalError}
                {generalError === 'Enlace expirado.' ? (
                  <div className="mt-2">
                    <Link className="font-semibold underline" to="/recuperar-password">
                      Solicitar un nuevo enlace
                    </Link>
                  </div>
                ) : null}
              </div>
            ) : null}

            <button
              className="w-full rounded-2xl bg-violet-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-violet-700 disabled:cursor-not-allowed disabled:bg-violet-300"
              disabled={cargando}
              type="submit"
            >
              {cargando ? 'Cargando...' : 'Cambiar contraseña'}
            </button>
          </form>
        )}
      </div>
    </div>
  )
}

export default ResetPassword

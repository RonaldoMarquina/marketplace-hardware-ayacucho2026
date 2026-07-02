import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import api from '../../api/axios'
import PasswordInput from '../../components/ui/PasswordInput'
import { normalizeFieldErrors } from '../../utils/forms'
import {
  isValidEmail,
  isValidPassword,
  isValidPhone,
  isValidRUC,
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

const allowedTypes = ['image/jpeg', 'image/png']
const maxFileSize = 5 * 1024 * 1024

const RegisterTienda = () => {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    nombre: '',
    nombre_comercial: '',
    ruc: '',
    direccion: '',
    telefono: '',
    correo: '',
    password: '',
    confirmarPassword: '',
  })
  const [documento, setDocumento] = useState(null)
  const [errors, setErrors] = useState({})
  const [generalError, setGeneralError] = useState('')
  const [cargando, setCargando] = useState(false)

  const handleChange = (event) => {
    const { name, value } = event.target
    setForm((current) => ({ ...current, [name]: value }))
    setErrors((current) => ({ ...current, [name]: '' }))
    setGeneralError('')
  }

  const handleFileChange = (event) => {
    const file = event.target.files?.[0] ?? null
    setErrors((current) => ({ ...current, documento_identidad: '' }))
    setGeneralError('')

    if (!file) {
      setDocumento(null)
      return
    }

    if (!allowedTypes.includes(file.type)) {
      setErrors((current) => ({
        ...current,
        documento_identidad: 'Solo se permiten archivos JPG o PNG.',
      }))
      setDocumento(null)
      return
    }

    if (file.size > maxFileSize) {
      setErrors((current) => ({
        ...current,
        documento_identidad: 'El documento supera el tamaño maximo de 5MB.',
      }))
      setDocumento(null)
      return
    }

    setDocumento(file)
  }

  const validateForm = () => {
    const nextErrors = {}

    if (!form.nombre.trim()) {
      nextErrors.nombre = 'Ingresa el nombre del propietario.'
    }

    if (!form.nombre_comercial.trim()) {
      nextErrors.nombre_comercial = 'Ingresa el nombre comercial.'
    }

    if (!isValidRUC(form.ruc.trim())) {
      nextErrors.ruc = 'Ingresa un RUC valido de 11 digitos.'
    }

    if (!form.direccion.trim()) {
      nextErrors.direccion = 'Ingresa la direccion.'
    }

    if (!isValidPhone(form.telefono.trim())) {
      nextErrors.telefono = 'Ingresa un telefono peruano de 9 digitos.'
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

    if (!documento) {
      nextErrors.documento_identidad = 'Adjunta tu documento de identidad.'
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
      const payload = new FormData()
      payload.append('nombre_comercial', form.nombre_comercial.trim())
      payload.append('ruc', form.ruc.trim())
      payload.append('direccion', form.direccion.trim())
      payload.append('telefono', form.telefono.trim())
      payload.append('correo', form.correo.trim())
      payload.append('password', form.password)
      payload.append('documento_identidad', documento)

      await api.post('/auth/register/tienda', payload, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      navigate('/verificar-email', {
        state: { correo: form.correo.trim(), esTienda: true },
      })
    } catch (error) {
      const status = error.response?.status
      const message =
        error.response?.data?.mensaje ||
        error.response?.data?.message ||
        error.response?.data?.error ||
        ''
      const fieldErrors = error.response?.data?.data ?? {}
      const lowerMessage = message.toLowerCase()

      if (status === 409) {
        if (lowerMessage.includes('correo')) {
          setErrors((current) => ({ ...current, correo: 'Este correo ya se encuentra registrado.' }))
        } else if (lowerMessage.includes('telefono')) {
          setErrors((current) => ({
            ...current,
            telefono: 'Este telefono ya se encuentra registrado.',
          }))
        } else if (lowerMessage.includes('ruc')) {
          setErrors((current) => ({ ...current, ruc: 'Este RUC ya se encuentra registrado.' }))
        } else if (lowerMessage.includes('nombre comercial')) {
          setErrors((current) => ({
            ...current,
            nombre_comercial: 'Este nombre comercial ya se encuentra registrado.',
          }))
        } else {
          setGeneralError(message || 'No se pudo registrar la tienda.')
        }
      } else if (status === 413) {
        setErrors((current) => ({
          ...current,
          documento_identidad: 'El documento supera el tamaño maximo de 5MB.',
        }))
      } else if (status === 415) {
        setErrors((current) => ({
          ...current,
          documento_identidad: 'Solo se permiten archivos JPG o PNG.',
        }))
      } else if (status === 422 || status === 400) {
        setErrors((current) => ({
          ...current,
          ...normalizeFieldErrors(fieldErrors),
        }))
      } else {
        setGeneralError(message || 'No se pudo registrar la tienda.')
      }
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top_left,#d1fae5,transparent_28%),linear-gradient(180deg,#ecfeff_0%,#f8fafc_100%)] px-4 py-10">
      <div className="w-full max-w-3xl rounded-[32px] border border-emerald-100 bg-white p-8 shadow-[0_30px_90px_-40px_rgba(6,95,70,0.35)]">
        <div className="mb-8 text-center">
          <Link className="text-3xl font-black tracking-tight text-slate-900" to="/">
            HardwareAyacucho
          </Link>
          <h1 className="mt-3 text-2xl font-bold text-slate-900">Registrar Tienda</h1>
          <p className="mt-2 text-sm text-slate-600">
            Completa tus datos comerciales para iniciar el proceso de verificacion.
          </p>
        </div>

        <form className="grid gap-5 md:grid-cols-2" onSubmit={handleSubmit}>
          <div className="space-y-2 md:col-span-1">
            <label className="text-sm font-medium text-slate-700" htmlFor="nombre">
              Nombre del propietario
            </label>
            <input
              className={`w-full rounded-2xl border px-4 py-3 text-sm outline-none ${
                errors.nombre ? 'border-rose-400' : 'border-slate-200 focus:border-emerald-400'
              }`}
              id="nombre"
              name="nombre"
              onChange={handleChange}
              placeholder="Nombre completo del propietario"
              type="text"
              value={form.nombre}
            />
            {errors.nombre ? <p className="text-sm text-rose-600">{errors.nombre}</p> : null}
          </div>

          <div className="space-y-2 md:col-span-1">
            <label className="text-sm font-medium text-slate-700" htmlFor="nombre_comercial">
              Nombre comercial
            </label>
            <input
              className={`w-full rounded-2xl border px-4 py-3 text-sm outline-none ${
                errors.nombre_comercial
                  ? 'border-rose-400'
                  : 'border-slate-200 focus:border-emerald-400'
              }`}
              id="nombre_comercial"
              name="nombre_comercial"
              onChange={handleChange}
              placeholder="Nombre de tu tienda"
              type="text"
              value={form.nombre_comercial}
            />
            {errors.nombre_comercial ? (
              <p className="text-sm text-rose-600">{errors.nombre_comercial}</p>
            ) : null}
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700" htmlFor="ruc">
              RUC
            </label>
            <input
              className={`w-full rounded-2xl border px-4 py-3 text-sm outline-none ${
                errors.ruc ? 'border-rose-400' : 'border-slate-200 focus:border-emerald-400'
              }`}
              id="ruc"
              maxLength={11}
              name="ruc"
              onChange={handleChange}
              placeholder="20601234567"
              type="text"
              value={form.ruc}
            />
            {errors.ruc ? <p className="text-sm text-rose-600">{errors.ruc}</p> : null}
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700" htmlFor="direccion">
              Direccion
            </label>
            <input
              className={`w-full rounded-2xl border px-4 py-3 text-sm outline-none ${
                errors.direccion ? 'border-rose-400' : 'border-slate-200 focus:border-emerald-400'
              }`}
              id="direccion"
              name="direccion"
              onChange={handleChange}
              placeholder="Jr. Lima 123, Ayacucho"
              type="text"
              value={form.direccion}
            />
            {errors.direccion ? (
              <p className="text-sm text-rose-600">{errors.direccion}</p>
            ) : null}
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700" htmlFor="telefono">
              Telefono
            </label>
            <input
              className={`w-full rounded-2xl border px-4 py-3 text-sm outline-none ${
                errors.telefono ? 'border-rose-400' : 'border-slate-200 focus:border-emerald-400'
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

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700" htmlFor="correo">
              Correo electronico
            </label>
            <input
              className={`w-full rounded-2xl border px-4 py-3 text-sm outline-none ${
                errors.correo ? 'border-rose-400' : 'border-slate-200 focus:border-emerald-400'
              }`}
              id="correo"
              name="correo"
              onChange={handleChange}
              placeholder="tienda@ejemplo.com"
              type="email"
              value={form.correo}
            />
            {errors.correo ? <p className="text-sm text-rose-600">{errors.correo}</p> : null}
          </div>

          <div className="space-y-2 md:col-span-1">
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
          </div>

          <div className="space-y-2 md:col-span-1">
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

          <div className="rounded-2xl bg-emerald-50 p-4 text-sm text-slate-600 md:col-span-2">
            <div className="grid gap-2 md:grid-cols-2">
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

          <div className="space-y-2 md:col-span-2">
            <label className="text-sm font-medium text-slate-700" htmlFor="documento_identidad">
              Documento de identidad
            </label>
            <label
              className={`flex cursor-pointer items-center justify-between rounded-2xl border border-dashed px-4 py-4 text-sm ${
                errors.documento_identidad
                  ? 'border-rose-400 bg-rose-50 text-rose-700'
                  : 'border-slate-300 bg-slate-50 text-slate-600'
              }`}
              htmlFor="documento_identidad"
            >
              <span>{documento ? documento.name : 'Selecciona un archivo JPG o PNG (max 5MB)'}</span>
              <span className="font-semibold text-slate-900">Elegir archivo</span>
            </label>
            <input
              accept=".jpg,.jpeg,.png"
              className="hidden"
              id="documento_identidad"
              name="documento_identidad"
              onChange={handleFileChange}
              type="file"
            />
            {errors.documento_identidad ? (
              <p className="text-sm text-rose-600">{errors.documento_identidad}</p>
            ) : null}
          </div>

          {generalError ? (
            <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700 md:col-span-2">
              {generalError}
            </div>
          ) : null}

          <button
            className="w-full rounded-2xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-emerald-300 md:col-span-2"
            disabled={cargando}
            type="submit"
          >
            {cargando ? 'Cargando...' : 'Registrar tienda'}
          </button>

          <p className="text-center text-sm text-slate-600 md:col-span-2">
            ¿Ya tienes cuenta?{' '}
            <Link className="font-semibold text-slate-900 hover:text-emerald-700" to="/login">
              Ingresar
            </Link>
          </p>
        </form>
      </div>
    </div>
  )
}

export default RegisterTienda

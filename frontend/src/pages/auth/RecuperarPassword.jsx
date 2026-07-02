import { Link } from 'react-router-dom'
import { useState } from 'react'
import api from '../../api/axios'
import { formatDateTime } from '../../utils/format'
import { isValidEmail } from '../../utils/validators'

const RecuperarPassword = () => {
  const [correo, setCorreo] = useState('')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [sent, setSent] = useState(false)
  const [cargando, setCargando] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()

    if (!isValidEmail(correo.trim())) {
      setError('Ingresa un correo valido.')
      return
    }

    setCargando(true)
    setError('')
    setMessage('')

    try {
      const response = await api.post('/auth/password/forgot', {
        correo: correo.trim(),
      })

      setSent(true)
      setMessage(
        response.data.message ||
          'Si el correo esta registrado y la cuenta esta activa, recibiras un enlace en los proximos minutos.'
      )
    } catch (errorResponse) {
      if (errorResponse.response?.status === 429) {
        setError(
          `Espera hasta el ${formatDateTime(
            errorResponse.response?.data?.data?.disponible_en,
          )} para volver a intentarlo.`
        )
      } else {
        setError(
          errorResponse.response?.data?.mensaje ||
            errorResponse.response?.data?.message ||
            'No se pudo procesar la solicitud.'
        )
      }
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[linear-gradient(180deg,#ecfccb_0%,#f8fafc_100%)] px-4 py-10">
      <div className="w-full max-w-md rounded-[28px] border border-lime-100 bg-white p-8 shadow-[0_28px_80px_-40px_rgba(77,124,15,0.35)]">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-black text-slate-900">Recuperar contraseña</h1>
          <p className="mt-2 text-sm text-slate-600">
            Te enviaremos un enlace para crear una nueva contraseña.
          </p>
        </div>

        {sent ? (
          <div className="space-y-5 text-center">
            <div className="rounded-2xl bg-lime-50 px-4 py-4 text-sm text-lime-800">{message}</div>
            <Link className="text-sm font-semibold text-slate-900 hover:text-lime-700" to="/login">
              Volver al login
            </Link>
          </div>
        ) : (
          <form className="space-y-5" onSubmit={handleSubmit}>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700" htmlFor="correo">
                Correo electronico
              </label>
              <input
                className={`w-full rounded-2xl border px-4 py-3 text-sm outline-none ${
                  error ? 'border-rose-400' : 'border-slate-200 focus:border-lime-400'
                }`}
                id="correo"
                name="correo"
                onChange={(event) => {
                  setCorreo(event.target.value)
                  setError('')
                }}
                placeholder="correo@ejemplo.com"
                type="email"
                value={correo}
              />
            </div>

            {error ? (
              <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
                {error}
              </div>
            ) : null}

            <button
              className="w-full rounded-2xl bg-lime-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-lime-700 disabled:cursor-not-allowed disabled:bg-lime-300"
              disabled={cargando}
              type="submit"
            >
              {cargando ? 'Cargando...' : 'Enviar enlace'}
            </button>

            <div className="text-center">
              <Link className="text-sm text-slate-600 hover:text-slate-900" to="/login">
                Volver al login
              </Link>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}

export default RecuperarPassword

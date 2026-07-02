import { Link, useLocation } from 'react-router-dom'
import { useEffect, useMemo, useState } from 'react'
import api from '../../api/axios'
import { formatDateTime } from '../../utils/format'

const getCooldown = (deadline) => {
  if (!deadline) {
    return 0
  }

  const diff = Math.ceil((new Date(deadline).getTime() - Date.now()) / 1000)
  return diff > 0 ? diff : 0
}

const VerificarEmail = () => {
  const location = useLocation()
  const queryParams = useMemo(
    () => new URLSearchParams(location.search),
    [location.search],
  )
  const correo = location.state?.correo ?? ''
  const esTienda = location.state?.esTienda === true
  const verificationToken = queryParams.get('token')
  const [status, setStatus] = useState(verificationToken ? 'verifying' : 'idle')
  const [message, setMessage] = useState('')
  const [reenvioMensaje, setReenvioMensaje] = useState('')
  const [reenvioError, setReenvioError] = useState('')
  const [reenviando, setReenviando] = useState(false)
  const [cooldownEnd, setCooldownEnd] = useState(null)
  const [cooldown, setCooldown] = useState(0)

  useEffect(() => {
    if (!cooldownEnd) {
      setCooldown(0)
      return undefined
    }

    setCooldown(getCooldown(cooldownEnd))

    const timer = window.setInterval(() => {
      const nextCooldown = getCooldown(cooldownEnd)
      setCooldown(nextCooldown)

      if (nextCooldown <= 0) {
        window.clearInterval(timer)
      }
    }, 1000)

    return () => window.clearInterval(timer)
  }, [cooldown, cooldownEnd])

  useEffect(() => {
    if (!verificationToken) {
      return
    }

    const verifyEmail = async () => {
      setStatus('verifying')
      setMessage('Verificando tu enlace...')

      try {
        const response = await api.get(`/auth/verify-email?token=${verificationToken}`)
        const estado = response.data.data?.estado

        if (estado === 'ACTIVO') {
          setStatus('success')
          setMessage('Cuenta activada. Ya puedes ingresar.')
        } else if (estado === 'EN_REVISION') {
          setStatus('review')
          setMessage('Correo verificado. Espera la aprobacion del administrador.')
        }
      } catch (error) {
        const statusCode = error.response?.status

        if (statusCode === 404) {
          setStatus('error')
          setMessage('Enlace invalido o inexistente.')
        } else if (statusCode === 409) {
          setStatus('error')
          setMessage('Este enlace ya fue usado.')
        } else if (statusCode === 410) {
          setStatus('expired')
          setMessage('Enlace expirado.')
        } else {
          setStatus('error')
          setMessage(
            error.response?.data?.mensaje ||
              error.response?.data?.message ||
              'No se pudo verificar el correo.'
          )
        }
      }
    }

    verifyEmail()
  }, [verificationToken])

  const handleResend = async () => {
    if (!correo) {
      setReenvioError('No encontramos el correo para reenviar la verificacion.')
      return
    }

    setReenviando(true)
    setReenvioError('')
    setReenvioMensaje('')

    try {
      const response = await api.post('/auth/verify-email/resend', { correo })
      setReenvioMensaje(response.data.message || 'Correo reenviado correctamente.')
      setCooldownEnd(new Date(Date.now() + 60_000).toISOString())
    } catch (error) {
      if (error.response?.status === 429) {
        const disponibleEn = error.response?.data?.data?.disponible_en
        setReenvioError(
          `Espera hasta el ${formatDateTime(disponibleEn)} para solicitar otro correo.`
        )
        setCooldownEnd(disponibleEn)
      } else {
        setReenvioError(
          error.response?.data?.mensaje ||
            error.response?.data?.message ||
            'No se pudo reenviar el correo.'
        )
      }
    } finally {
      setReenviando(false)
    }
  }

  const canResend = Boolean(correo) && cooldown <= 0 && !reenviando
  const showResend = !verificationToken || status === 'expired'

  return (
    <div className="flex min-h-screen items-center justify-center bg-[linear-gradient(180deg,#eff6ff_0%,#f8fafc_50%,#eef2ff_100%)] px-4 py-10">
      <div className="w-full max-w-xl rounded-[30px] border border-sky-100 bg-white p-8 shadow-[0_30px_90px_-40px_rgba(14,116,144,0.3)]">
        <div className="mb-6 flex justify-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-sky-100 text-3xl text-sky-700">
            @
          </div>
        </div>

        <div className="space-y-4 text-center">
          <h1 className="text-3xl font-black text-slate-900">Revisa tu correo</h1>

          {esTienda ? (
            <p className="rounded-2xl bg-amber-50 px-4 py-3 text-sm text-amber-800">
              Tu solicitud de tienda sera revisada por un administrador una vez que verifiques tu
              correo.
            </p>
          ) : null}

          {correo ? (
            <p className="text-sm text-slate-600">
              Enviamos un mensaje de verificacion a <span className="font-semibold">{correo}</span>.
            </p>
          ) : null}

          {message ? (
            <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4 text-sm text-slate-700">
              {message}
            </div>
          ) : null}

          {status === 'success' ? (
            <Link
              className="inline-flex rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800"
              to="/login"
            >
              Ir al login
            </Link>
          ) : null}

          {showResend ? (
            <div className="space-y-3">
              <button
                className="w-full rounded-2xl bg-sky-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-sky-300"
                disabled={!canResend}
                onClick={handleResend}
                type="button"
              >
                {reenviando ? 'Cargando...' : 'Reenviar correo de verificacion'}
              </button>

              {cooldown > 0 ? (
                <p className="text-sm text-slate-500">Disponible en {cooldown}s.</p>
              ) : null}

              {reenvioMensaje ? <p className="text-sm text-emerald-700">{reenvioMensaje}</p> : null}
              {reenvioError ? <p className="text-sm text-rose-600">{reenvioError}</p> : null}
            </div>
          ) : null}

          <Link className="inline-block text-sm text-slate-600 hover:text-slate-900" to="/">
            Volver al inicio
          </Link>
        </div>
      </div>
    </div>
  )
}

export default VerificarEmail

import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

const contentByState = {
  PENDIENTE_VERIFICACION: {
    title: 'Verifica tu correo electronico',
    message:
      'Necesitas confirmar tu correo para activar la cuenta y empezar a usar todas las funciones.',
    icon: '@',
  },
  EN_REVISION: {
    title: 'Tu cuenta esta en revision',
    message:
      'Tu solicitud esta siendo evaluada por un administrador. Te avisaremos cuando finalice la revision.',
    icon: '!',
  },
  default: {
    title: 'Acceso restringido',
    message:
      'Tu cuenta no puede acceder a esta seccion en este momento. Si crees que es un error, contacta soporte.',
    icon: '!',
  },
}

const CuentaPendiente = () => {
  const navigate = useNavigate()
  const { usuario, logout } = useAuth()
  const stateKey = usuario?.estado
  const content = contentByState[stateKey] ?? contentByState.default

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex min-h-[calc(100vh-65px)] items-center justify-center px-4 py-10">
      <div className="w-full max-w-lg rounded-[30px] border border-amber-100 bg-white p-8 text-center shadow-[0_28px_90px_-40px_rgba(180,83,9,0.35)]">
        <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-amber-100 text-3xl font-bold text-amber-700">
          {content.icon}
        </div>
        <h1 className="text-3xl font-black text-slate-900">{content.title}</h1>
        <p className="mt-4 text-sm leading-6 text-slate-600">{content.message}</p>
        <button
          className="mt-8 rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800"
          onClick={handleLogout}
          type="button"
        >
          Cerrar sesion
        </button>
      </div>
    </div>
  )
}

export default CuentaPendiente

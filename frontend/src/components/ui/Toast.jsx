import { useEffect } from 'react'

const toastStyles = {
  exito: {
    container: 'border-emerald-200 bg-emerald-50 text-emerald-800',
    icon: 'bg-emerald-600 text-white',
    symbol: '✓',
  },
  error: {
    container: 'border-rose-200 bg-rose-50 text-rose-800',
    icon: 'bg-rose-600 text-white',
    symbol: '!',
  },
  advertencia: {
    container: 'border-amber-200 bg-amber-50 text-amber-800',
    icon: 'bg-amber-500 text-white',
    symbol: '!',
  },
  info: {
    container: 'border-sky-200 bg-sky-50 text-sky-800',
    icon: 'bg-sky-600 text-white',
    symbol: 'i',
  },
}

const Toast = ({ mensaje, tipo = 'info', duracion = 3000, onClose }) => {
  const config = toastStyles[tipo] ?? toastStyles.info

  useEffect(() => {
    const timer = window.setTimeout(() => {
      onClose?.()
    }, duracion)

    return () => window.clearTimeout(timer)
  }, [duracion, onClose])

  return (
    <div
      className={`pointer-events-auto flex items-start gap-3 rounded-[24px] border px-4 py-4 shadow-[0_18px_55px_-30px_rgba(15,23,42,0.45)] ${config.container}`}
      role="status"
    >
      <div
        className={`mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-sm font-black ${config.icon}`}
      >
        {config.symbol}
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium leading-6">{mensaje}</p>
      </div>
      <button
        className="rounded-full px-2 py-1 text-sm font-semibold opacity-70 transition hover:opacity-100"
        onClick={onClose}
        type="button"
      >
        X
      </button>
    </div>
  )
}

export default Toast

import { useEffect } from 'react'

const sizeMap = {
  sm: 'max-w-md',
  md: 'max-w-xl',
  lg: 'max-w-3xl',
}

const Modal = ({ abierto, onCerrar, titulo, children, tamano = 'md' }) => {
  useEffect(() => {
    if (!abierto) {
      return undefined
    }

    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        onCerrar()
      }
    }

    globalThis.addEventListener('keydown', handleEscape)
    return () => globalThis.removeEventListener('keydown', handleEscape)
  }, [abierto, onCerrar])

  if (!abierto) {
    return null
  }

  return (
    <div className="fixed inset-0 z-[80] flex items-center justify-center px-4">
      <button
        aria-label="Cerrar modal"
        className="absolute inset-0 bg-slate-950/55 backdrop-blur-sm"
        onClick={onCerrar}
        type="button"
      />
      <div
        aria-modal="true"
        className={`relative z-10 w-full rounded-[30px] border border-white/60 bg-white p-6 shadow-[0_30px_90px_-40px_rgba(15,23,42,0.55)] transition ${sizeMap[tamano] ?? sizeMap.md}`}
        role="dialog"
      >
        <div className="mb-5 flex items-center justify-between gap-4">
          <h2 className="text-xl font-black text-slate-900">{titulo}</h2>
          <button
            className="rounded-full bg-slate-100 px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-200"
            onClick={onCerrar}
            type="button"
          >
            X
          </button>
        </div>
        {children}
      </div>
    </div>
  )
}

export default Modal

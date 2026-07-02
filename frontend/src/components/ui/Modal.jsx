const sizeMap = {
  sm: 'max-w-md',
  md: 'max-w-xl',
  lg: 'max-w-3xl',
}

const Modal = ({ abierto, onCerrar, titulo, children, tamano = 'md' }) => {
  if (!abierto) {
    return null
  }

  return (
    <div
      className="fixed inset-0 z-[80] flex items-center justify-center bg-slate-950/55 px-4 backdrop-blur-sm"
      onClick={onCerrar}
      role="presentation"
    >
      <div
        className={`w-full rounded-[30px] border border-white/60 bg-white p-6 shadow-[0_30px_90px_-40px_rgba(15,23,42,0.55)] transition ${sizeMap[tamano] ?? sizeMap.md}`}
        onClick={(event) => event.stopPropagation()}
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

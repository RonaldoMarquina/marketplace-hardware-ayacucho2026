const Paginacion = ({ paginacion, onCambiarPagina }) => {
  if (!paginacion || paginacion.total_paginas <= 1) {
    return null
  }

  return (
    <div className="mt-10 flex flex-col items-center justify-between gap-4 rounded-[24px] border border-slate-200 bg-white px-5 py-4 shadow-sm md:flex-row">
      <button
        className="rounded-full border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-slate-300 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
        disabled={!paginacion.tiene_anterior}
        onClick={() => onCambiarPagina(paginacion.pagina_actual - 1)}
        type="button"
      >
        ← Anterior
      </button>

      <p className="text-center text-sm text-slate-600">
        Página {paginacion.pagina_actual} de {paginacion.total_paginas} ({paginacion.total}{' '}
        resultados)
      </p>

      <button
        className="rounded-full border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-slate-300 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
        disabled={!paginacion.tiene_siguiente}
        onClick={() => onCambiarPagina(paginacion.pagina_actual + 1)}
        type="button"
      >
        Siguiente →
      </button>
    </div>
  )
}

export default Paginacion

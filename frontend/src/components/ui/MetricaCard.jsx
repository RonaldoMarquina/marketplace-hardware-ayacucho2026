const colorMap = {
  verde: 'border-emerald-500',
  azul: 'border-sky-500',
  amarillo: 'border-amber-400',
  gris: 'border-slate-300',
}

const MetricaCard = ({ titulo, valor, subtitulo, color = 'gris' }) => (
  <div
    className={`rounded-[24px] border border-slate-200 border-l-4 bg-white p-5 shadow-sm ${
      colorMap[color] ?? colorMap.gris
    }`}
  >
    <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">{titulo}</p>
    <p className="mt-3 text-3xl font-black tracking-tight text-slate-900">{valor}</p>
    {subtitulo ? <p className="mt-2 text-sm text-slate-500">{subtitulo}</p> : null}
  </div>
)

export default MetricaCard

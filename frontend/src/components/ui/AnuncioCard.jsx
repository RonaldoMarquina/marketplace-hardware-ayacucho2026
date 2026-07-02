import { Link } from 'react-router-dom'
import { formatDate, formatImageUrl, formatPrice } from '../../utils/format'
import { getTaxonomyLabel } from '../../utils/especificaciones'

const conditionStyles = {
  NUEVO: 'bg-emerald-500 text-white',
  COMO_NUEVO: 'bg-sky-500 text-white',
  USADO: 'bg-amber-400 text-slate-900',
  PARA_REPUESTOS: 'bg-rose-500 text-white',
}

const ImagePlaceholder = () => (
  <div className="flex h-full w-full items-center justify-center bg-slate-200 text-slate-400">
    <svg
      aria-hidden="true"
      className="h-14 w-14"
      fill="none"
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="1.6"
      viewBox="0 0 24 24"
    >
      <path d="M3.75 5.25h16.5a1.5 1.5 0 0 1 1.5 1.5v10.5a1.5 1.5 0 0 1-1.5 1.5H3.75a1.5 1.5 0 0 1-1.5-1.5V6.75a1.5 1.5 0 0 1 1.5-1.5Z" />
      <path d="m3 16 5.25-5.25a1.5 1.5 0 0 1 2.121 0L14.25 14.625l1.629-1.629a1.5 1.5 0 0 1 2.121 0L21 16" />
      <circle cx="8.25" cy="8.25" r="1.25" />
    </svg>
  </div>
)

const AnuncioCard = ({ anuncio }) => (
  <Link
    className="group overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-sm transition duration-200 hover:-translate-y-1 hover:shadow-xl"
    to={`/anuncios/${anuncio.id}`}
  >
    <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
      {anuncio.imagen_principal ? (
        <img
          alt={anuncio.titulo}
          className="h-full w-full object-cover transition duration-300 group-hover:scale-[1.03]"
          src={formatImageUrl(anuncio.imagen_principal)}
        />
      ) : (
        <ImagePlaceholder />
      )}

      <div className="absolute left-3 top-3 flex flex-wrap gap-2">
        <span
          className={`rounded-full px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.12em] ${
            conditionStyles[anuncio.condicion] ?? 'bg-slate-900 text-white'
          }`}
        >
          {getTaxonomyLabel(anuncio.condicion)}
        </span>

        {anuncio.es_tienda_verificada ? (
          <span className="rounded-full bg-white/90 px-3 py-1 text-[11px] font-semibold text-emerald-700 shadow-sm backdrop-blur">
            ✓ Tienda Verificada
          </span>
        ) : null}
      </div>
    </div>

    <div className="space-y-3 p-4">
      <h3 className="line-clamp-2 min-h-[3.5rem] text-base font-semibold text-slate-900">
        {anuncio.titulo}
      </h3>

      <p className="text-2xl font-black tracking-tight text-slate-900">
        {formatPrice(anuncio.precio)}
      </p>

      <p className="text-sm text-slate-500">{getTaxonomyLabel(anuncio.subcategoria)}</p>

      <div className="flex items-center justify-between gap-4 text-sm text-slate-600">
        <span className="truncate">{anuncio.vendedor_nombre}</span>
        <span className="shrink-0">{formatDate(anuncio.updated_at ?? anuncio.created_at)}</span>
      </div>
    </div>
  </Link>
)

export default AnuncioCard

import { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import api from '../../api/axios'
import Estrellas from '../../components/ui/Estrellas'
import Paginacion from '../../components/ui/Paginacion'
import { formatDate, formatDateTime, formatImageUrl, formatPrice } from '../../utils/format'

const tabs = [
  { label: 'Todas', value: 'ambas' },
  { label: 'Mis ventas', value: 'ventas' },
  { label: 'Mis compras', value: 'compras' },
]

const Historial = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const [transacciones, setTransacciones] = useState([])
  const [resumen, setResumen] = useState(null)
  const [paginacion, setPaginacion] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const [expandedId, setExpandedId] = useState(null)
  const [drafts, setDrafts] = useState({})
  const [submittingId, setSubmittingId] = useState(null)

  const tipo = searchParams.get('tipo') || 'ambas'
  const page = Math.max(1, Number(searchParams.get('page') || '1'))

  useEffect(() => {
    const fetchHistorial = async () => {
      setCargando(true)
      setError('')

      try {
        const response = await api.get('/usuarios/me/transacciones', {
          params: {
            tipo,
            page,
            limit: 10,
          },
        })

        setTransacciones(response.data.data ?? [])
        setResumen(response.data.resumen ?? null)
        setPaginacion(response.data.paginacion ?? null)
      } catch (requestError) {
        setError(
          requestError.response?.data?.mensaje ||
            requestError.response?.data?.message ||
            'No se pudo cargar el historial.'
        )
      } finally {
        setCargando(false)
      }
    }

    fetchHistorial()
  }, [page, tipo])

  const pendingCounts = useMemo(
    () => ({
      ambas: resumen?.calificaciones_pendientes ?? 0,
      ventas:
        resumen?.calificaciones_pendientes_ventas ??
        transacciones.filter((item) => item.tipo === 'venta' && item.calificacion_pendiente).length,
      compras:
        resumen?.calificaciones_pendientes_compras ??
        transacciones.filter((item) => item.tipo === 'compra' && item.calificacion_pendiente).length,
    }),
    [resumen, transacciones],
  )

  const updateParams = (nextTipo, nextPage = 1) => {
    const params = new URLSearchParams()
    if (nextTipo !== 'ambas') {
      params.set('tipo', nextTipo)
    }
    if (nextPage > 1) {
      params.set('page', String(nextPage))
    }
    setSearchParams(params)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleDraftChange = (transaccionId, field, value) => {
    setDrafts((current) => ({
      ...current,
      [transaccionId]: {
        puntaje: current[transaccionId]?.puntaje ?? null,
        comentario: current[transaccionId]?.comentario ?? '',
        ...current[transaccionId],
        [field]: value,
      },
    }))
  }

  const handleCalificar = async (transaccion) => {
    const draft = drafts[transaccion.transaccion_id]

    if (!draft?.puntaje) {
      setError('Debes seleccionar un puntaje antes de enviar la calificación.')
      return
    }

    setSubmittingId(transaccion.transaccion_id)
    setError('')

    try {
      const endpoint =
        transaccion.tipo === 'venta'
          ? `/transacciones/${transaccion.transaccion_id}/calificar/comprador`
          : `/transacciones/${transaccion.transaccion_id}/calificar/vendedor`

      const response = await api.post(endpoint, {
        puntaje: draft.puntaje,
        comentario: draft.comentario || undefined,
      })

      setTransacciones((current) =>
        current.map((item) =>
          item.transaccion_id === transaccion.transaccion_id
            ? {
                ...item,
                calificacion_pendiente: false,
                calificacion_emitida: {
                  puntaje: response.data.data.puntaje,
                  comentario: response.data.data.comentario,
                  created_at: response.data.data.created_at,
                },
              }
            : item,
        ),
      )
      setResumen((current) =>
        current
          ? {
              ...current,
              calificaciones_pendientes: Math.max(0, current.calificaciones_pendientes - 1),
            }
          : current,
      )
    } catch (requestError) {
      if (requestError.response?.status === 409) {
        setError('Ya calificaste esta transacción.')
      } else {
        setError(
          requestError.response?.data?.mensaje ||
            requestError.response?.data?.message ||
            'No se pudo registrar la calificación.'
        )
      }
    } finally {
      setSubmittingId(null)
    }
  }

  if (cargando) {
    return (
      <div className="min-h-screen bg-[linear-gradient(180deg,#f8fafc_0%,#eef2ff_32%,#f8fafc_100%)] px-4 py-8">
        <div className="mx-auto max-w-5xl space-y-6">
          <div className="grid gap-4 md:grid-cols-3">
            {Array.from({ length: 3 }, (_, index) => (
              <div className="h-28 animate-pulse rounded-[24px] bg-slate-200" key={index} />
            ))}
          </div>
          {Array.from({ length: 3 }, (_, index) => (
            <div className="h-36 animate-pulse rounded-[24px] bg-slate-200" key={index} />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[linear-gradient(180deg,#f8fafc_0%,#eef2ff_32%,#f8fafc_100%)] px-4 py-8">
      <div className="mx-auto max-w-5xl space-y-6">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-700">
            Historial
          </p>
          <h1 className="mt-2 text-4xl font-black tracking-tight text-slate-900">
            Transacciones y calificaciones
          </h1>
        </div>

        {resumen ? (
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-[24px] border border-slate-200 bg-white p-5 shadow-sm">
              <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                Total ventas
              </p>
              <p className="mt-3 text-3xl font-black tracking-tight text-slate-900">
                {resumen.total_ventas}
              </p>
            </div>
            <div className="rounded-[24px] border border-slate-200 bg-white p-5 shadow-sm">
              <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                Total compras
              </p>
              <p className="mt-3 text-3xl font-black tracking-tight text-slate-900">
                {resumen.total_compras}
              </p>
            </div>
            <div className="rounded-[24px] border border-slate-200 bg-white p-5 shadow-sm">
              <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                Pendientes
              </p>
              <p className="mt-3 text-3xl font-black tracking-tight text-slate-900">
                {resumen.calificaciones_pendientes}
              </p>
            </div>
          </div>
        ) : null}

        <div className="flex flex-wrap gap-3">
          {tabs.map((tab) => (
            <button
              className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
                tipo === tab.value
                  ? 'bg-slate-900 text-white'
                  : 'border border-slate-200 bg-white text-slate-700'
              }`}
              key={tab.value}
              onClick={() => updateParams(tab.value)}
              type="button"
            >
              {tab.label}
              {pendingCounts[tab.value] > 0 ? (
                <span
                  className={`ml-2 rounded-full px-2 py-0.5 text-xs ${
                    tipo === tab.value ? 'bg-white/20 text-white' : 'bg-amber-100 text-amber-800'
                  }`}
                >
                  {pendingCounts[tab.value]}
                </span>
              ) : null}
            </button>
          ))}
        </div>

        {error ? (
          <div className="rounded-[24px] border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-700">
            {error}
          </div>
        ) : null}

        <div className="space-y-4">
          {transacciones.map((transaccion) => {
            const expanded = expandedId === transaccion.transaccion_id
            const draft = drafts[transaccion.transaccion_id] ?? { puntaje: null, comentario: '' }

            return (
              <article
                className="rounded-[28px] border border-slate-200 bg-white p-5 shadow-sm"
                key={transaccion.transaccion_id}
              >
                <button
                  className="w-full text-left"
                  onClick={() =>
                    setExpandedId((current) =>
                      current === transaccion.transaccion_id ? null : transaccion.transaccion_id,
                    )
                  }
                  type="button"
                >
                  <div className="flex flex-col gap-4 md:flex-row md:items-center">
                    <div className="h-20 w-20 overflow-hidden rounded-2xl bg-slate-100">
                      {transaccion.anuncio.imagen_principal ? (
                        <img
                          alt={transaccion.anuncio.titulo}
                          className="h-full w-full object-cover"
                          src={formatImageUrl(transaccion.anuncio.imagen_principal)}
                        />
                      ) : null}
                    </div>

                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <h2 className="truncate text-lg font-bold text-slate-900">
                          {transaccion.anuncio.titulo}
                        </h2>
                        <span
                          className={`rounded-full px-3 py-1 text-xs font-semibold ${
                            transaccion.tipo === 'venta'
                              ? 'bg-sky-100 text-sky-700'
                              : 'bg-emerald-100 text-emerald-700'
                          }`}
                        >
                          {transaccion.tipo === 'venta' ? 'Venta' : 'Compra'}
                        </span>
                        {transaccion.calificacion_pendiente ? (
                          <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-800">
                            Pendiente calificar
                          </span>
                        ) : null}
                      </div>

                      <div className="mt-3 flex flex-wrap gap-x-6 gap-y-2 text-sm text-slate-600">
                        <p>{formatPrice(transaccion.monto)}</p>
                        <p>Contraparte: {transaccion.contraparte.nombre}</p>
                        <p>{formatDate(transaccion.created_at)}</p>
                      </div>

                      {transaccion.calificacion_emitida ? (
                        <div className="mt-3">
                          <Estrellas puntaje={transaccion.calificacion_emitida.puntaje} tamano="sm" />
                        </div>
                      ) : null}
                    </div>
                  </div>
                </button>

                {expanded ? (
                  <div className="mt-5 border-t border-slate-200 pt-5">
                    {transaccion.calificacion_pendiente ? (
                      <div className="space-y-4 rounded-[24px] bg-slate-50 p-5">
                        <div>
                          <p className="text-sm font-semibold text-slate-900">Califica esta transacción</p>
                          <p className="mt-1 text-sm text-slate-500">
                            Tu opinión ayuda a construir confianza en la comunidad.
                          </p>
                        </div>

                        <Estrellas
                          interactivo
                          onCambiar={(puntaje) =>
                            handleDraftChange(transaccion.transaccion_id, 'puntaje', puntaje)
                          }
                          puntaje={draft.puntaje}
                          tamano="lg"
                        />

                        <div className="space-y-2">
                          <textarea
                            className="min-h-28 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-sky-400"
                            maxLength={500}
                            onChange={(event) =>
                              handleDraftChange(
                                transaccion.transaccion_id,
                                'comentario',
                                event.target.value,
                              )
                            }
                            placeholder="Comentario opcional"
                            value={draft.comentario}
                          />
                          <div className="text-right text-xs text-slate-500">
                            {draft.comentario.length}/500
                          </div>
                        </div>

                        <button
                          className="rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white"
                          disabled={submittingId === transaccion.transaccion_id}
                          onClick={() => handleCalificar(transaccion)}
                          type="button"
                        >
                          {submittingId === transaccion.transaccion_id
                            ? 'Enviando...'
                            : 'Enviar calificación'}
                        </button>
                      </div>
                    ) : transaccion.calificacion_emitida ? (
                      <div className="space-y-3 rounded-[24px] bg-slate-50 p-5">
                        <Estrellas puntaje={transaccion.calificacion_emitida.puntaje} tamano="lg" />
                        {transaccion.calificacion_emitida.comentario ? (
                          <p className="text-sm leading-6 text-slate-700">
                            {transaccion.calificacion_emitida.comentario}
                          </p>
                        ) : null}
                        <p className="text-sm text-slate-500">
                          Emitida el {formatDateTime(transaccion.calificacion_emitida.created_at)}
                        </p>
                      </div>
                    ) : null}
                  </div>
                ) : null}
              </article>
            )
          })}
        </div>

        <Paginacion onCambiarPagina={(nextPage) => updateParams(tipo, nextPage)} paginacion={paginacion} />
      </div>
    </div>
  )
}

export default Historial

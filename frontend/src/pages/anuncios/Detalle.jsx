import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import api from '../../api/axios'
import { useAuth } from '../../hooks/useAuth'
import { formatDate, formatDateTime, formatImageUrl, formatPrice, formatRating } from '../../utils/format'
import { getSpecLabel, getTaxonomyLabel } from '../../utils/especificaciones'

const conditionStyles = {
  NUEVO: 'bg-emerald-500 text-white',
  COMO_NUEVO: 'bg-sky-500 text-white',
  USADO: 'bg-amber-400 text-slate-900',
  PARA_REPUESTOS: 'bg-rose-500 text-white',
}

const EmptyMedia = () => (
  <div className="flex aspect-[4/3] items-center justify-center rounded-[28px] bg-slate-100 text-slate-400">
    <svg
      aria-hidden="true"
      className="h-16 w-16"
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

const VideoPlaceholder = ({ src }) => (
  <div className="relative aspect-[4/3] overflow-hidden rounded-[28px] bg-slate-950">
    <video className="h-full w-full object-cover" controls src={src} />
  </div>
)

const Modal = ({ children, onClose, title }) => (
  <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/55 px-4">
    <div className="w-full max-w-md rounded-[28px] bg-white p-6 shadow-2xl">
      <div className="mb-5 flex items-center justify-between">
        <h2 className="text-lg font-bold text-slate-900">{title}</h2>
        <button
          className="rounded-full bg-slate-100 px-3 py-2 text-sm font-semibold text-slate-700"
          onClick={onClose}
          type="button"
        >
          Cerrar
        </button>
      </div>
      {children}
    </div>
  </div>
)

const StarRating = ({ value }) => {
  const numericValue = Number(value ?? 0)

  return (
    <div className="flex items-center gap-2">
      <div className="flex text-amber-400">
        {Array.from({ length: 5 }, (_, index) => (
          <span key={index}>{index < Math.round(numericValue) ? '★' : '☆'}</span>
        ))}
      </div>
      <span className="text-sm text-slate-600">{formatRating(value)}</span>
    </div>
  )
}

const Detalle = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const { usuario } = useAuth()
  const [anuncio, setAnuncio] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const [contactMessage, setContactMessage] = useState('')
  const [ownerMessage, setOwnerMessage] = useState('')
  const [videoOpen, setVideoOpen] = useState(false)
  const [desactivarOpen, setDesactivarOpen] = useState(false)
  const [vendidoOpen, setVendidoOpen] = useState(false)
  const [compradorId, setCompradorId] = useState('')
  const [actionLoading, setActionLoading] = useState('')

  useEffect(() => {
    const fetchDetalle = async () => {
      setCargando(true)
      setError('')

      try {
        const response = await api.get(`/anuncios/${id}`)
        setAnuncio(response.data.data)
      } catch (requestError) {
        if (requestError.response?.status === 404) {
          setAnuncio(null)
          setError('NOT_FOUND')
        } else if (requestError.response?.status === 400) {
          navigate('/', { replace: true })
        } else {
          setError(
            requestError.response?.data?.mensaje ||
              requestError.response?.data?.message ||
              'No se pudo cargar el anuncio.'
          )
        }
      } finally {
        setCargando(false)
      }
    }

    fetchDetalle()
  }, [id, navigate])

  const media = anuncio?.media ?? []
  const [selectedMediaId, setSelectedMediaId] = useState(null)

  useEffect(() => {
    if (media.length > 0) {
      const preferred = media.find((item) => item.es_principal) ?? media[0]
      setSelectedMediaId(preferred.id)
    }
  }, [anuncio?.id, media])

  const selectedMedia = useMemo(
    () => media.find((item) => item.id === selectedMediaId) ?? media[0] ?? null,
    [media, selectedMediaId],
  )

  const specEntries = useMemo(
    () =>
      Object.entries(anuncio?.especificaciones ?? {}).filter(([, value]) => {
        if (value === null || value === undefined) return false
        if (typeof value === 'string') return value.trim() !== ''
        return true
      }),
    [anuncio?.especificaciones],
  )

  const refreshDetalle = async () => {
    const response = await api.get(`/anuncios/${id}`)
    setAnuncio(response.data.data)
  }

  const handleWhatsapp = async () => {
    setContactMessage('')

    if (!usuario) {
      navigate('/login', {
        state: { message: 'Inicia sesion para contactar este anuncio.' },
      })
      return
    }

    try {
      const response = await api.get(`/anuncios/${id}/contacto`)
      window.open(response.data.data.whatsapp_url, '_blank', 'noopener,noreferrer')
    } catch (requestError) {
      if (requestError.response?.status === 429) {
        setContactMessage(
          `Podrás volver a contactar el ${formatDateTime(
            requestError.response?.data?.data?.disponible_en,
          )}.`
        )
      } else if (requestError.response?.status === 401) {
        navigate('/login', {
          state: { message: 'Inicia sesion para contactar este anuncio.' },
        })
      } else {
        setContactMessage(
          requestError.response?.data?.mensaje ||
            requestError.response?.data?.message ||
            'No se pudo generar el enlace de WhatsApp.'
        )
      }
    }
  }

  const handleDesactivar = async () => {
    setActionLoading('desactivar')
    setOwnerMessage('')

    try {
      await api.patch(`/anuncios/${id}/desactivar`)
      setDesactivarOpen(false)
      await refreshDetalle()
      setOwnerMessage('El anuncio fue desactivado correctamente.')
    } catch (requestError) {
      setOwnerMessage(
        requestError.response?.data?.mensaje ||
          requestError.response?.data?.message ||
          'No se pudo desactivar el anuncio.'
      )
    } finally {
      setActionLoading('')
    }
  }

  const handleReactivar = async () => {
    setActionLoading('reactivar')
    setOwnerMessage('')

    try {
      await api.patch(`/anuncios/${id}/reactivar`)
      await refreshDetalle()
      setOwnerMessage('El anuncio volvió a estar activo.')
    } catch (requestError) {
      setOwnerMessage(
        requestError.response?.data?.mensaje ||
          requestError.response?.data?.message ||
          'No se pudo reactivar el anuncio.'
      )
    } finally {
      setActionLoading('')
    }
  }

  const handleMarcarVendido = async (event) => {
    event.preventDefault()
    setActionLoading('vendido')
    setOwnerMessage('')

    try {
      await api.patch(`/anuncios/${id}/vendido`, {
        comprador_id: Number(compradorId),
      })
      setVendidoOpen(false)
      setCompradorId('')
      navigate('/', { replace: true })
    } catch (requestError) {
      setOwnerMessage(
        requestError.response?.data?.mensaje ||
          requestError.response?.data?.message ||
          'No se pudo marcar el anuncio como vendido.'
      )
    } finally {
      setActionLoading('')
    }
  }

  if (cargando) {
    return (
      <div className="px-4 py-8">
        <div className="mx-auto max-w-7xl animate-pulse space-y-6">
          <div className="grid gap-8 lg:grid-cols-[1.15fr_0.85fr]">
            <div className="aspect-[4/3] rounded-[32px] bg-slate-200" />
            <div className="space-y-4 rounded-[32px] bg-white p-6 shadow-sm">
              <div className="h-6 w-32 rounded-full bg-slate-200" />
              <div className="h-10 w-4/5 rounded-full bg-slate-200" />
              <div className="h-12 w-40 rounded-full bg-slate-200" />
              <div className="h-28 rounded-[24px] bg-slate-200" />
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error === 'NOT_FOUND') {
    return (
      <div className="px-4 py-12">
        <div className="mx-auto max-w-xl rounded-[32px] border border-slate-200 bg-white p-8 text-center shadow-sm">
          <h1 className="text-3xl font-black text-slate-900">Anuncio no encontrado</h1>
          <p className="mt-3 text-sm text-slate-600">
            Es posible que ya no esté disponible o que el enlace sea incorrecto.
          </p>
          <Link
            className="mt-6 inline-flex rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800"
            to="/"
          >
            Volver al feed
          </Link>
        </div>
      </div>
    )
  }

  if (!anuncio) {
    return (
      <div className="px-4 py-12 text-center text-sm text-slate-600">{error || 'Sin datos'}</div>
    )
  }

  return (
    <div className="min-h-screen bg-[linear-gradient(180deg,#f8fafc_0%,#eff6ff_30%,#f8fafc_100%)] px-4 py-8">
      <div className="mx-auto max-w-7xl space-y-8">
        <div className="grid gap-8 lg:grid-cols-[1.15fr_0.85fr]">
          <div className="space-y-4">
            {selectedMedia ? (
              selectedMedia.tipo_media === 'video' ? (
                <VideoPlaceholder src={formatImageUrl(selectedMedia.ruta_relativa)} />
              ) : (
                <img
                  alt={anuncio.titulo}
                  className="aspect-[4/3] w-full rounded-[30px] object-cover shadow-lg"
                  src={formatImageUrl(selectedMedia.ruta_relativa)}
                />
              )
            ) : (
              <EmptyMedia />
            )}

            {media.length > 0 ? (
              <div className="grid grid-cols-4 gap-3 md:grid-cols-5">
                {media.map((item) => (
                  <button
                    className={`relative overflow-hidden rounded-2xl border transition ${
                      selectedMedia?.id === item.id
                        ? 'border-sky-500 ring-2 ring-sky-200'
                        : 'border-slate-200'
                    }`}
                    key={item.id}
                    onClick={() => {
                      setSelectedMediaId(item.id)
                      if (item.tipo_media === 'video') {
                        setVideoOpen(true)
                      }
                    }}
                    type="button"
                  >
                    {item.tipo_media === 'video' ? (
                      <div className="flex aspect-square items-center justify-center bg-slate-900 text-3xl text-white">
                        ▶
                      </div>
                    ) : (
                      <img
                        alt={anuncio.titulo}
                        className="aspect-square w-full object-cover"
                        src={formatImageUrl(item.ruta_relativa)}
                      />
                    )}
                  </button>
                ))}
              </div>
            ) : null}
          </div>

          <div className="space-y-6">
            {anuncio.es_propietario ? (
              <div className="rounded-[28px] border border-amber-200 bg-amber-50 px-5 py-4 text-sm text-amber-800">
                <p className="font-semibold">Este es tu anuncio</p>
                <p className="mt-1">
                  Puedes gestionarlo desde aquí y revisar sus cambios antes de volver a
                  publicarlo.
                </p>
              </div>
            ) : null}

            <div className="rounded-[32px] border border-slate-200 bg-white p-6 shadow-sm">
              <div className="mb-4 flex flex-wrap gap-2">
                <span
                  className={`rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.12em] ${
                    conditionStyles[anuncio.condicion] ?? 'bg-slate-900 text-white'
                  }`}
                >
                  {getTaxonomyLabel(anuncio.condicion)}
                </span>

                {anuncio.estado_propietario?.estado === 'INACTIVO' ? (
                  <span className="rounded-full bg-slate-900 px-3 py-1 text-xs font-semibold uppercase tracking-[0.12em] text-white">
                    Inactivo
                  </span>
                ) : null}
              </div>

              <h1 className="text-3xl font-black tracking-tight text-slate-900">{anuncio.titulo}</h1>
              <p className="mt-3 text-4xl font-black tracking-tight text-slate-900">
                {formatPrice(anuncio.precio)}
              </p>
              <p className="mt-3 text-sm text-slate-500">
                {getTaxonomyLabel(anuncio.categoria)} → {getTaxonomyLabel(anuncio.subcategoria)}
              </p>

              <div className="mt-6 rounded-[24px] bg-slate-50 p-5">
                <h2 className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-500">
                  Descripción
                </h2>
                <p className="mt-3 whitespace-pre-line text-sm leading-7 text-slate-700">
                  {anuncio.descripcion}
                </p>
              </div>

              {specEntries.length > 0 ? (
                <div className="mt-6 overflow-hidden rounded-[24px] border border-slate-200">
                  <div className="border-b border-slate-200 bg-slate-50 px-5 py-4">
                    <h2 className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-500">
                      Especificaciones técnicas
                    </h2>
                  </div>
                  <div className="divide-y divide-slate-200">
                    {specEntries.map(([key, value]) => (
                      <div
                        className="grid gap-3 px-5 py-4 text-sm md:grid-cols-[220px_minmax(0,1fr)]"
                        key={key}
                      >
                        <span className="font-medium text-slate-600">{getSpecLabel(key)}</span>
                        <span className="text-slate-900">
                          {typeof value === 'boolean' ? (value ? 'Sí' : 'No') : String(value)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}

              <div className="mt-6 rounded-[28px] border border-slate-200 p-5">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h2 className="text-lg font-bold text-slate-900">{anuncio.vendedor.nombre}</h2>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {anuncio.vendedor.es_tienda_verificada ? (
                        <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                          ✓ Tienda Verificada
                        </span>
                      ) : null}
                    </div>
                  </div>

                  {anuncio.vendedor.calificacion_promedio !== undefined ? (
                    <StarRating value={anuncio.vendedor.calificacion_promedio} />
                  ) : null}
                </div>

                {anuncio.vendedor.tienda ? (
                  <div className="mt-4 rounded-2xl bg-slate-50 p-4 text-sm text-slate-700">
                    <p className="font-semibold text-slate-900">
                      {anuncio.vendedor.tienda.nombre_comercial}
                    </p>
                    <p className="mt-1">{anuncio.vendedor.tienda.direccion}</p>
                  </div>
                ) : null}

                <button
                  className="mt-5 w-full rounded-2xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-emerald-700"
                  onClick={handleWhatsapp}
                  type="button"
                >
                  {usuario ? 'Contactar por WhatsApp' : 'Inicia sesión para contactar'}
                </button>

                {contactMessage ? (
                  <p className="mt-3 text-sm text-amber-700">{contactMessage}</p>
                ) : null}
              </div>

              <div className="mt-6 space-y-2 text-sm text-slate-500">
                <p>Publicado el {formatDate(anuncio.created_at)}</p>
                {anuncio.updated_at && anuncio.updated_at !== anuncio.created_at ? (
                  <p>Actualizado el {formatDate(anuncio.updated_at)}</p>
                ) : null}
              </div>

              {anuncio.es_propietario ? (
                <div className="mt-6 space-y-4 rounded-[24px] bg-slate-50 p-5">
                  <div className="flex flex-wrap gap-3">
                    <Link
                      className="rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
                      to={`/anuncios/${anuncio.id}/editar`}
                    >
                      Editar
                    </Link>

                    {anuncio.estado_propietario?.estado === 'INACTIVO' ? (
                      <button
                        className="rounded-2xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-white"
                        disabled={actionLoading === 'reactivar'}
                        onClick={handleReactivar}
                        type="button"
                      >
                        {actionLoading === 'reactivar' ? 'Reactivando...' : 'Reactivar'}
                      </button>
                    ) : (
                      <button
                        className="rounded-2xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-white"
                        onClick={() => setDesactivarOpen(true)}
                        type="button"
                      >
                        Desactivar
                      </button>
                    )}

                    <button
                      className="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-semibold text-emerald-700 transition hover:bg-emerald-100"
                      onClick={() => setVendidoOpen(true)}
                      type="button"
                    >
                      Marcar como vendido
                    </button>
                  </div>

                  <p className="text-sm text-slate-600">
                    Reactivaciones restantes:{' '}
                    <span className="font-semibold text-slate-900">
                      {anuncio.estado_propietario?.reactivaciones_restantes ?? 0}
                    </span>
                  </p>

                  {ownerMessage ? <p className="text-sm text-sky-700">{ownerMessage}</p> : null}
                </div>
              ) : null}
            </div>
          </div>
        </div>
      </div>

      {videoOpen && selectedMedia?.tipo_media === 'video' ? (
        <Modal onClose={() => setVideoOpen(false)} title="Video del anuncio">
          <video className="w-full rounded-[20px]" controls src={formatImageUrl(selectedMedia.ruta_relativa)} />
        </Modal>
      ) : null}

      {desactivarOpen ? (
        <Modal onClose={() => setDesactivarOpen(false)} title="Desactivar anuncio">
          <p className="text-sm leading-6 text-slate-600">
            ¿Seguro que deseas desactivar este anuncio? Dejará de aparecer en el feed público.
          </p>
          <div className="mt-6 flex gap-3">
            <button
              className="flex-1 rounded-2xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700"
              onClick={() => setDesactivarOpen(false)}
              type="button"
            >
              Cancelar
            </button>
            <button
              className="flex-1 rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white"
              disabled={actionLoading === 'desactivar'}
              onClick={handleDesactivar}
              type="button"
            >
              {actionLoading === 'desactivar' ? 'Desactivando...' : 'Confirmar'}
            </button>
          </div>
        </Modal>
      ) : null}

      {vendidoOpen ? (
        <Modal onClose={() => setVendidoOpen(false)} title="Marcar como vendido">
          <form className="space-y-4" onSubmit={handleMarcarVendido}>
            <p className="text-sm leading-6 text-slate-600">
              Ingresa el `comprador_id` del usuario que concretó la compra. Debe haber contactado
              este anuncio previamente.
            </p>
            <input
              className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-sky-400"
              min="1"
              onChange={(event) => setCompradorId(event.target.value)}
              placeholder="Ej. 12"
              type="number"
              value={compradorId}
            />
            <button
              className="w-full rounded-2xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white"
              disabled={actionLoading === 'vendido' || !compradorId}
              type="submit"
            >
              {actionLoading === 'vendido' ? 'Guardando...' : 'Confirmar venta'}
            </button>
          </form>
        </Modal>
      ) : null}
    </div>
  )
}

export default Detalle

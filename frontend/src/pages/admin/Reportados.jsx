import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import api from '../../api/axios'
import Modal from '../../components/ui/Modal'
import Paginacion from '../../components/ui/Paginacion'
import { useToast } from '../../hooks/useToast'
import { getTaxonomyLabel } from '../../utils/especificaciones'
import { formatDateTime } from '../../utils/format'

const statusStyles = {
  ACTIVO: 'bg-emerald-50 text-emerald-700',
  BLOQUEADO: 'bg-rose-50 text-rose-700',
}

const motiveStyles = {
  FRAUDE: 'bg-rose-100 text-rose-700',
  PRODUCTO_FALSO: 'bg-orange-100 text-orange-700',
  PRECIO_ENGANOSO: 'bg-amber-100 text-amber-700',
  CONTENIDO_INAPROPIADO: 'bg-fuchsia-100 text-fuchsia-700',
  DUPLICADO: 'bg-slate-200 text-slate-700',
  OTRO: 'bg-slate-100 text-slate-700',
}

const buildPaginationParams = (searchParams, nextPage) => {
  const params = new URLSearchParams(searchParams)

  if (nextPage > 1) {
    params.set('page', String(nextPage))
  } else {
    params.delete('page')
  }

  return params
}

const TableSkeleton = () => (
  <div className="overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-sm">
    <div className="divide-y divide-slate-100">
      {Array.from({ length: 6 }, (_, index) => (
        <div className="grid gap-4 px-5 py-5 lg:grid-cols-[2fr_1.2fr_1.2fr_0.7fr_1.4fr_1fr_0.9fr_1fr]" key={index}>
          {Array.from({ length: 8 }, (_, cell) => (
            <div className="h-5 animate-pulse rounded-full bg-slate-200" key={cell} />
          ))}
        </div>
      ))}
    </div>
  </div>
)

const Reportados = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const [items, setItems] = useState([])
  const [paginacion, setPaginacion] = useState(null)
  const [totalPendientes, setTotalPendientes] = useState(0)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const [modalState, setModalState] = useState({ abierto: false, accion: '', item: null })
  const [motivoAdmin, setMotivoAdmin] = useState('')
  const [actionLoading, setActionLoading] = useState(false)
  const { showToast } = useToast()

  useEffect(() => {
    const fetchReportados = async () => {
      setCargando(true)
      setError('')

      try {
        const response = await api.get('/admin/anuncios/reportados', {
          params: {
            page: Number(searchParams.get('page') ?? '1'),
            limit: 20,
          },
        })

        setItems(response.data.data ?? [])
        setPaginacion(response.data.paginacion ?? null)
        setTotalPendientes(response.data.total_pendientes ?? 0)
      } catch (requestError) {
        setItems([])
        setPaginacion(null)
        setTotalPendientes(0)
        setError(
          requestError.response?.data?.mensaje ||
            requestError.response?.data?.message ||
            'No se pudo cargar la moderacion de anuncios.'
        )
      } finally {
        setCargando(false)
      }
    }

    fetchReportados()
  }, [searchParams])

  const uniqueMotives = useMemo(
    () =>
      items.map((item) => ({
        ...item,
        motivos: [...new Set(item.motivos ?? [])],
      })),
    [items],
  )

  const openModal = (accion, item) => {
    setModalState({ abierto: true, accion, item })
    setMotivoAdmin('')
  }

  const closeModal = () => {
    setModalState({ abierto: false, accion: '', item: null })
    setMotivoAdmin('')
  }

  const handlePageChange = (nextPage) => {
    setSearchParams(buildPaginationParams(searchParams, nextPage))
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleConfirmAction = async () => {
    if (!modalState.item || !motivoAdmin.trim()) {
      return
    }

    const { accion, item } = modalState
    const endpoint =
      accion === 'bloquear'
        ? `/admin/anuncios/${item.anuncio_id}/bloquear`
        : `/admin/anuncios/${item.anuncio_id}/desbloquear`

    setActionLoading(true)

    try {
      const response = await api.patch(endpoint, {
        motivo_admin: motivoAdmin.trim(),
      })

      if (accion === 'bloquear') {
        setItems((current) => current.filter((currentItem) => currentItem.anuncio_id !== item.anuncio_id))
        setTotalPendientes((current) => Math.max(0, current - item.total_reportes))
        setPaginacion((current) =>
          current
            ? {
                ...current,
                total: Math.max(0, current.total - 1),
              }
            : current,
        )
      } else {
        setItems((current) =>
          current.map((currentItem) =>
            currentItem.anuncio_id === item.anuncio_id
              ? { ...currentItem, estado_anuncio: response.data.data?.estado ?? 'ACTIVO' }
              : currentItem,
          ),
        )
      }

      showToast(
        accion === 'bloquear'
          ? 'Anuncio bloqueado correctamente.'
          : 'Anuncio desbloqueado correctamente.',
        'exito',
      )
      closeModal()
    } catch (requestError) {
      showToast(
        requestError.response?.data?.mensaje ||
          requestError.response?.data?.message ||
          'No se pudo completar la accion sobre el anuncio.',
        'error',
        4500,
      )
    } finally {
      setActionLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <section className="rounded-[32px] border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-rose-600">
              Moderacion
            </p>
            <h1 className="mt-2 text-3xl font-black tracking-tight text-slate-900">
              Anuncios Reportados
            </h1>
          </div>
          <span className="inline-flex rounded-full bg-rose-50 px-4 py-2 text-sm font-semibold text-rose-700">
            {totalPendientes} pendientes
          </span>
        </div>
      </section>

      {error ? <div className="rounded-[24px] border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-700">{error}</div> : null}

      {cargando ? (
        <TableSkeleton />
      ) : (
        <section className="overflow-hidden rounded-[32px] border border-slate-200 bg-white shadow-sm">
          {uniqueMotives.length === 0 ? (
            <div className="px-6 py-14 text-center text-sm text-slate-500">
              No hay anuncios reportados pendientes por revisar.
            </div>
          ) : (
            <>
              <div className="hidden border-b border-slate-200 bg-slate-50 px-5 py-4 text-xs font-semibold uppercase tracking-[0.14em] text-slate-500 lg:grid lg:grid-cols-[2fr_1.2fr_1.2fr_0.7fr_1.4fr_1fr_0.9fr_1fr] lg:gap-4">
                <span>Anuncio</span>
                <span>Categoria</span>
                <span>Vendedor</span>
                <span>Total</span>
                <span>Motivos</span>
                <span>Ultimo reporte</span>
                <span>Estado</span>
                <span>Acciones</span>
              </div>

              <div className="divide-y divide-slate-100">
                {uniqueMotives.map((item) => (
                  <div className="grid gap-4 px-5 py-5 lg:grid-cols-[2fr_1.2fr_1.2fr_0.7fr_1.4fr_1fr_0.9fr_1fr] lg:items-start" key={item.anuncio_id}>
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400 lg:hidden">
                        Anuncio
                      </p>
                      <Link
                        className="mt-1 block font-semibold text-slate-900 transition hover:text-sky-700"
                        rel="noreferrer"
                        target="_blank"
                        to={`/anuncios/${item.anuncio_id}`}
                      >
                        {item.titulo}
                      </Link>
                    </div>

                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400 lg:hidden">
                        Categoria
                      </p>
                      <p className="mt-1 text-sm text-slate-700">
                        {getTaxonomyLabel(item.categoria)} / {getTaxonomyLabel(item.subcategoria)}
                      </p>
                    </div>

                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400 lg:hidden">
                        Vendedor
                      </p>
                      <div className="mt-1 flex flex-wrap items-center gap-2">
                        <span className="text-sm font-medium text-slate-800">{item.vendedor_nombre}</span>
                        {item.es_tienda_verificada ? (
                          <span className="rounded-full bg-sky-50 px-2.5 py-1 text-xs font-semibold text-sky-700">
                            Tienda
                          </span>
                        ) : null}
                      </div>
                    </div>

                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400 lg:hidden">
                        Total reportes
                      </p>
                      <p className="mt-1 text-lg font-black text-slate-900">{item.total_reportes}</p>
                    </div>

                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400 lg:hidden">
                        Motivos
                      </p>
                      <div className="mt-1 flex flex-wrap gap-2">
                        {item.motivos.map((motivo) => (
                          <span
                            className={`rounded-full px-2.5 py-1 text-xs font-semibold ${motiveStyles[motivo] ?? motiveStyles.OTRO}`}
                            key={`${item.anuncio_id}-${motivo}`}
                          >
                            {motivo}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400 lg:hidden">
                        Ultimo reporte
                      </p>
                      <p className="mt-1 text-sm text-slate-700">{formatDateTime(item.ultimo_reporte)}</p>
                    </div>

                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400 lg:hidden">
                        Estado
                      </p>
                      <span className={`mt-1 inline-flex rounded-full px-3 py-1 text-xs font-semibold ${statusStyles[item.estado_anuncio] ?? 'bg-slate-100 text-slate-700'}`}>
                        {item.estado_anuncio}
                      </span>
                    </div>

                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400 lg:hidden">
                        Acciones
                      </p>
                      <div className="mt-1 flex flex-wrap gap-2">
                        {item.estado_anuncio === 'ACTIVO' ? (
                          <button
                            className="rounded-2xl bg-rose-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-rose-700"
                            onClick={() => openModal('bloquear', item)}
                            type="button"
                          >
                            Bloquear
                          </button>
                        ) : null}

                        {item.estado_anuncio === 'BLOQUEADO' ? (
                          <button
                            className="rounded-2xl bg-emerald-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700"
                            onClick={() => openModal('desbloquear', item)}
                            type="button"
                          >
                            Desbloquear
                          </button>
                        ) : null}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </section>
      )}

      <Paginacion onCambiarPagina={handlePageChange} paginacion={paginacion} />

      <Modal
        abierto={modalState.abierto}
        onCerrar={closeModal}
        titulo={modalState.accion === 'bloquear' ? 'Bloquear anuncio' : 'Desbloquear anuncio'}
      >
        <div className="space-y-5">
          <div className="rounded-[24px] bg-slate-50 p-4 text-sm text-slate-700">
            <p className="font-semibold text-slate-900">{modalState.item?.titulo}</p>
            <p className="mt-1">Vendedor: {modalState.item?.vendedor_nombre}</p>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700" htmlFor="motivo_admin">
              Motivo administrativo
            </label>
            <textarea
              className="min-h-32 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none transition focus:border-sky-400"
              id="motivo_admin"
              maxLength={500}
              onChange={(event) => setMotivoAdmin(event.target.value)}
              value={motivoAdmin}
            />
            <div className="flex justify-between text-xs text-slate-500">
              <span>Este campo es obligatorio.</span>
              <span>{motivoAdmin.length}/500</span>
            </div>
          </div>

          <div className="flex flex-col gap-3 sm:flex-row">
            <button
              className="flex-1 rounded-2xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
              onClick={closeModal}
              type="button"
            >
              Cancelar
            </button>
            <button
              className={`flex-1 rounded-2xl px-4 py-3 text-sm font-semibold text-white transition disabled:cursor-not-allowed disabled:opacity-50 ${
                modalState.accion === 'bloquear'
                  ? 'bg-rose-600 hover:bg-rose-700'
                  : 'bg-emerald-600 hover:bg-emerald-700'
              }`}
              disabled={actionLoading || !motivoAdmin.trim()}
              onClick={handleConfirmAction}
              type="button"
            >
              {actionLoading
                ? 'Guardando...'
                : modalState.accion === 'bloquear'
                  ? 'Confirmar bloqueo'
                  : 'Confirmar desbloqueo'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  )
}

export default Reportados

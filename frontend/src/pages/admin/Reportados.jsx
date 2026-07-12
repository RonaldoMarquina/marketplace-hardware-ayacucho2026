import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import api from '../../api/axios'
import Modal from '../../components/ui/Modal'
import Paginacion from '../../components/ui/Paginacion'
import { useToast } from '../../hooks/useToast'
import { getTaxonomyLabel } from '../../utils/especificaciones'
import { formatDateTime, formatImageUrl } from '../../utils/format'

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

const priorityStyles = {
  ALTA: 'bg-rose-100 text-rose-700',
  MEDIA: 'bg-amber-100 text-amber-700',
  BAJA: 'bg-slate-100 text-slate-700',
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
  const [appeals, setAppeals] = useState([])
  const [paginacion, setPaginacion] = useState(null)
  const [totalPendientes, setTotalPendientes] = useState(0)
  const [totalApelacionesPendientes, setTotalApelacionesPendientes] = useState(0)
  const [metricasOperativas, setMetricasOperativas] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const [modalState, setModalState] = useState({ abierto: false, accion: '', item: null })
  const [appealModalState, setAppealModalState] = useState({ abierto: false, accion: '', item: null })
  const [detalleCaso, setDetalleCaso] = useState(null)
  const [detalleAbierto, setDetalleAbierto] = useState(false)
  const [motivoAdmin, setMotivoAdmin] = useState('')
  const [motivoApelacionAdmin, setMotivoApelacionAdmin] = useState('')
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
        const appealsResponse = await api.get('/admin/apelaciones', {
          params: {
            page: Number(searchParams.get('page') ?? '1'),
            limit: 20,
          },
        })

        setItems(response.data.data ?? [])
        setPaginacion(response.data.paginacion ?? null)
        setTotalPendientes(response.data.total_pendientes ?? 0)
        setAppeals(appealsResponse.data.data ?? [])
        setTotalApelacionesPendientes(appealsResponse.data.total_pendientes ?? 0)
        setMetricasOperativas(response.data.metricas_operativas ?? null)
      } catch (requestError) {
        setItems([])
        setAppeals([])
        setPaginacion(null)
        setTotalPendientes(0)
        setTotalApelacionesPendientes(0)
        setMetricasOperativas(null)
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

  const openAppealModal = (accion, item) => {
    setAppealModalState({ abierto: true, accion, item })
    setMotivoApelacionAdmin('')
  }

  const closeAppealModal = () => {
    setAppealModalState({ abierto: false, accion: '', item: null })
    setMotivoApelacionAdmin('')
  }

  const closeDetalle = () => {
    setDetalleAbierto(false)
    setDetalleCaso(null)
  }

  const handlePageChange = (nextPage) => {
    setSearchParams(buildPaginationParams(searchParams, nextPage))
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleOpenDetalle = async (anuncioId) => {
    setActionLoading(true)

    try {
      const response = await api.get(`/admin/anuncios/${anuncioId}/reportes`)
      setDetalleCaso(response.data.data)
      setDetalleAbierto(true)
    } catch (requestError) {
      showToast(
        requestError.response?.data?.mensaje ||
          requestError.response?.data?.message ||
          'No se pudo cargar el detalle del caso.',
        'error',
        4500,
      )
    } finally {
      setActionLoading(false)
    }
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

  const handleResolveAppeal = async () => {
    if (!appealModalState.item || !motivoApelacionAdmin.trim()) {
      return
    }

    const decision = appealModalState.accion === 'aceptar' ? 'ACEPTAR' : 'RECHAZAR'
    setActionLoading(true)

    try {
      const response = await api.patch(`/admin/apelaciones/${appealModalState.item.apelacion_id}/resolver`, {
        decision,
        motivo_admin: motivoApelacionAdmin.trim(),
      })

      setAppeals((current) =>
        current.filter((item) => item.apelacion_id !== appealModalState.item.apelacion_id),
      )
      setTotalApelacionesPendientes((current) => Math.max(0, current - 1))
      if (decision === 'ACEPTAR') {
        setItems((current) =>
          current.filter((item) => item.anuncio_id !== response.data.data?.anuncio_id),
        )
        setTotalPendientes((current) => Math.max(0, current - 1))
        setPaginacion((current) =>
          current
            ? {
                ...current,
                total: Math.max(0, current.total - 1),
              }
            : current,
        )
      }
      showToast(
        decision === 'ACEPTAR'
          ? 'Apelacion aceptada y anuncio rehabilitado.'
          : 'Apelacion rechazada correctamente.',
        'exito',
      )
      closeAppealModal()
    } catch (requestError) {
      showToast(
        requestError.response?.data?.mensaje ||
          requestError.response?.data?.message ||
          'No se pudo resolver la apelacion.',
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
          <span className="inline-flex rounded-full bg-sky-50 px-4 py-2 text-sm font-semibold text-sky-700">
            {totalApelacionesPendientes} apelaciones
          </span>
        </div>
        {metricasOperativas ? (
          <div className="mt-4 flex flex-wrap gap-3">
            <span className="rounded-full bg-rose-50 px-4 py-2 text-xs font-semibold text-rose-700">
              {metricasOperativas.alta_prioridad} casos de alta prioridad
            </span>
            <span className="rounded-full bg-amber-50 px-4 py-2 text-xs font-semibold text-amber-700">
              {metricasOperativas.con_senales_abuso} casos con señales de abuso
            </span>
          </div>
        ) : null}
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
                      <div className="mt-2 flex flex-wrap gap-2">
                        <span
                          className={`rounded-full px-2.5 py-1 text-xs font-semibold ${priorityStyles[item.prioridad_nivel] ?? priorityStyles.BAJA}`}
                        >
                          Prioridad {item.prioridad_nivel}
                        </span>
                        <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
                          Score {item.prioridad_score}
                        </span>
                      </div>
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
                      <p className="mt-1 text-xs text-slate-500">
                        {item.reportantes_distintos} reportante(s) · confianza promedio{' '}
                        {item.confiabilidad_promedio_reportantes ?? 'N/D'}
                      </p>
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
                      {item.senales_operativas?.length > 0 ? (
                        <div className="mb-2 flex flex-wrap gap-2">
                          {item.senales_operativas.map((signal) => (
                            <span
                              className="rounded-full bg-amber-50 px-2.5 py-1 text-xs font-semibold text-amber-700"
                              key={`${item.anuncio_id}-${signal.codigo}`}
                              title={signal.descripcion}
                            >
                              {signal.codigo}
                            </span>
                          ))}
                        </div>
                      ) : null}
                      <div className="mt-1 flex flex-wrap gap-2">
                        <button
                          className="rounded-2xl border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
                          disabled={actionLoading}
                          onClick={() => handleOpenDetalle(item.anuncio_id)}
                          type="button"
                        >
                          Ver caso
                        </button>

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

      <section className="overflow-hidden rounded-[32px] border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-200 px-6 py-5">
          <h2 className="text-xl font-black text-slate-900">Apelaciones pendientes</h2>
          <p className="mt-1 text-sm text-slate-500">
            Descargos enviados por vendedores o tiendas tras un bloqueo.
          </p>
        </div>

        {appeals.length === 0 ? (
          <div className="px-6 py-12 text-center text-sm text-slate-500">
            No hay apelaciones pendientes por revisar.
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {appeals.map((item) => (
              <article className="px-6 py-5" key={item.apelacion_id}>
                <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                  <div className="space-y-2">
                    <Link
                      className="block text-lg font-bold text-slate-900 transition hover:text-sky-700"
                      rel="noreferrer"
                      target="_blank"
                      to={`/anuncios/${item.anuncio_id}`}
                    >
                      {item.titulo}
                    </Link>
                    <div className="flex flex-wrap gap-2 text-sm text-slate-600">
                      <span>{item.usuario_nombre}</span>
                      {item.es_tienda_verificada ? (
                        <span className="rounded-full bg-sky-50 px-2.5 py-1 text-xs font-semibold text-sky-700">
                          Tienda
                        </span>
                      ) : null}
                      <span>{formatDateTime(item.created_at)}</span>
                    </div>
                    <p className="max-w-3xl text-sm leading-6 text-slate-700">{item.mensaje}</p>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <button
                      className="rounded-2xl border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
                      disabled={actionLoading}
                      onClick={() => handleOpenDetalle(item.anuncio_id)}
                      type="button"
                    >
                      Ver caso
                    </button>
                    <button
                      className="rounded-2xl bg-emerald-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700"
                      onClick={() => openAppealModal('aceptar', item)}
                      type="button"
                    >
                      Aceptar apelación
                    </button>
                    <button
                      className="rounded-2xl bg-rose-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-rose-700"
                      onClick={() => openAppealModal('rechazar', item)}
                      type="button"
                    >
                      Rechazar apelación
                    </button>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>

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

      <Modal abierto={detalleAbierto} onCerrar={closeDetalle} tamano="lg" titulo="Detalle del caso">
        <div className="space-y-4">
          <div className="rounded-[24px] bg-slate-50 p-4 text-sm text-slate-700">
            <p className="font-semibold text-slate-900">{detalleCaso?.titulo}</p>
            <p className="mt-1">Anuncio #{detalleCaso?.anuncio_id}</p>
            <div className="mt-3 flex flex-wrap gap-2">
              <span
                className={`rounded-full px-3 py-1 text-xs font-semibold ${priorityStyles[detalleCaso?.prioridad_nivel] ?? priorityStyles.BAJA}`}
              >
                Prioridad {detalleCaso?.prioridad_nivel}
              </span>
              <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-slate-700">
                Score {detalleCaso?.prioridad_score ?? 0}
              </span>
            </div>
          </div>

          {detalleCaso?.senales_operativas?.length > 0 ? (
            <div className="rounded-[24px] border border-amber-200 bg-amber-50 p-4">
              <h3 className="text-sm font-semibold uppercase tracking-[0.14em] text-amber-800">
                Señales operativas
              </h3>
              <div className="mt-3 space-y-2 text-sm text-amber-900">
                {detalleCaso.senales_operativas.map((signal) => (
                  <p key={signal.codigo}>
                    <span className="font-semibold">{signal.codigo}:</span> {signal.descripcion}
                  </p>
                ))}
              </div>
            </div>
          ) : null}

          <div className="space-y-4">
            {(detalleCaso?.reportes ?? []).map((reporte) => (
              <article className="rounded-[24px] border border-slate-200 p-4" key={reporte.reporte_id}>
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p className="text-sm font-semibold text-slate-900">{reporte.comprador.nombre}</p>
                    <p className="mt-1 text-xs text-slate-500">
                      {reporte.comprador.correo} · {formatDateTime(reporte.created_at)}
                    </p>
                  </div>
                  {reporte.senal_reportante ? (
                    <div className="mt-2 flex flex-wrap gap-2">
                      <span
                        className={`rounded-full px-2.5 py-1 text-xs font-semibold ${priorityStyles[reporte.senal_reportante.nivel] ?? priorityStyles.BAJA}`}
                      >
                        Confianza {reporte.senal_reportante.nivel}
                      </span>
                      <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
                        Score {reporte.senal_reportante.score}
                      </span>
                      <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
                        {reporte.senal_reportante.account_age_days} dias
                      </span>
                    </div>
                  ) : null}
                  <span className={`rounded-full px-3 py-1 text-xs font-semibold ${motiveStyles[reporte.motivo] ?? motiveStyles.OTRO}`}>
                    {reporte.motivo}
                  </span>
                </div>

                <div className="mt-4 rounded-2xl bg-slate-50 p-4 text-sm leading-6 text-slate-700">
                  {reporte.detalle?.trim() || 'El reportante no agrego detalle adicional.'}
                </div>

                {reporte.evidencias?.length > 0 ? (
                  <div className="mt-4 grid gap-3 sm:grid-cols-2">
                    {reporte.evidencias.map((evidencia) => (
                      <a
                        className="block overflow-hidden rounded-2xl border border-slate-200 bg-white"
                        href={formatImageUrl(evidencia.ruta_relativa)}
                        key={evidencia.id}
                        rel="noreferrer"
                        target="_blank"
                      >
                        <img
                          alt={`Evidencia ${evidencia.id}`}
                          className="aspect-[4/3] w-full object-cover"
                          src={formatImageUrl(evidencia.ruta_relativa)}
                        />
                      </a>
                    ))}
                  </div>
                ) : (
                  <p className="mt-4 text-xs text-slate-500">Sin evidencias adjuntas.</p>
                )}
                {reporte.senal_reportante?.senales?.length > 0 ? (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {reporte.senal_reportante.senales.map((signal) => (
                      <span
                        className="rounded-full bg-amber-50 px-2.5 py-1 text-xs font-semibold text-amber-700"
                        key={`${reporte.reporte_id}-${signal}`}
                      >
                        {signal}
                      </span>
                    ))}
                  </div>
                ) : null}
              </article>
            ))}
          </div>

          {(detalleCaso?.apelaciones ?? []).length > 0 ? (
            <div className="space-y-3 border-t border-slate-200 pt-4">
              <h3 className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-500">
                Apelaciones
              </h3>
              {detalleCaso.apelaciones.map((apelacion) => (
                <article className="rounded-[24px] border border-sky-200 bg-sky-50 p-4" key={apelacion.apelacion_id}>
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-slate-900">{apelacion.usuario.nombre}</p>
                      <p className="mt-1 text-xs text-slate-500">
                        {apelacion.usuario.correo} · {formatDateTime(apelacion.created_at)}
                      </p>
                    </div>
                    <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-sky-700">
                      {apelacion.estado}
                    </span>
                  </div>
                  <div className="mt-4 rounded-2xl bg-white p-4 text-sm leading-6 text-slate-700">
                    {apelacion.mensaje}
                  </div>
                  {apelacion.respuesta_admin ? (
                    <div className="mt-3 rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
                      Respuesta admin: {apelacion.respuesta_admin}
                    </div>
                  ) : null}
                  {apelacion.evidencias?.length > 0 ? (
                    <div className="mt-4 grid gap-3 sm:grid-cols-2">
                      {apelacion.evidencias.map((evidencia) => (
                        <a
                          className="block overflow-hidden rounded-2xl border border-slate-200 bg-white"
                          href={formatImageUrl(evidencia.ruta_relativa)}
                          key={evidencia.id}
                          rel="noreferrer"
                          target="_blank"
                        >
                          <img
                            alt={`Evidencia apelación ${evidencia.id}`}
                            className="aspect-[4/3] w-full object-cover"
                            src={formatImageUrl(evidencia.ruta_relativa)}
                          />
                        </a>
                      ))}
                    </div>
                  ) : null}
                </article>
              ))}
            </div>
          ) : null}
        </div>
      </Modal>

      <Modal
        abierto={appealModalState.abierto}
        onCerrar={closeAppealModal}
        titulo={appealModalState.accion === 'aceptar' ? 'Aceptar apelación' : 'Rechazar apelación'}
      >
        <div className="space-y-5">
          <div className="rounded-[24px] bg-slate-50 p-4 text-sm text-slate-700">
            <p className="font-semibold text-slate-900">{appealModalState.item?.titulo}</p>
            <p className="mt-1">Solicitante: {appealModalState.item?.usuario_nombre}</p>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700" htmlFor="motivo_apelacion_admin">
              Motivo administrativo
            </label>
            <textarea
              className="min-h-32 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none transition focus:border-sky-400"
              id="motivo_apelacion_admin"
              maxLength={500}
              onChange={(event) => setMotivoApelacionAdmin(event.target.value)}
              value={motivoApelacionAdmin}
            />
            <div className="flex justify-between text-xs text-slate-500">
              <span>Este campo es obligatorio.</span>
              <span>{motivoApelacionAdmin.length}/500</span>
            </div>
          </div>

          <div className="flex flex-col gap-3 sm:flex-row">
            <button
              className="flex-1 rounded-2xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
              onClick={closeAppealModal}
              type="button"
            >
              Cancelar
            </button>
            <button
              className={`flex-1 rounded-2xl px-4 py-3 text-sm font-semibold text-white transition disabled:cursor-not-allowed disabled:opacity-50 ${
                appealModalState.accion === 'aceptar'
                  ? 'bg-emerald-600 hover:bg-emerald-700'
                  : 'bg-rose-600 hover:bg-rose-700'
              }`}
              disabled={actionLoading || !motivoApelacionAdmin.trim()}
              onClick={handleResolveAppeal}
              type="button"
            >
              {actionLoading
                ? 'Guardando...'
                : appealModalState.accion === 'aceptar'
                  ? 'Confirmar aceptación'
                  : 'Confirmar rechazo'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  )
}

export default Reportados

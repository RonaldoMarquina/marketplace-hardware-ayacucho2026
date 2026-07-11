import { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import api from '../../api/axios'
import Modal from '../../components/ui/Modal'
import Paginacion from '../../components/ui/Paginacion'
import Estrellas from '../../components/ui/Estrellas'
import { useToast } from '../../hooks/useToast'
import { formatDate, formatImageUrl } from '../../utils/format'

const roleStyles = {
  USER_ESTANDAR: 'bg-slate-100 text-slate-700',
  TIENDA_VERIFICADA: 'bg-sky-100 text-sky-700',
}

const stateStyles = {
  ACTIVO: 'bg-emerald-50 text-emerald-700',
  PENDIENTE_VERIFICACION: 'bg-amber-50 text-amber-700',
  EN_REVISION: 'bg-orange-50 text-orange-700',
  BLOQUEADO: 'bg-rose-50 text-rose-700',
  RECHAZADO: 'bg-slate-200 text-slate-700',
}

const emptyFilters = {
  q: '',
  estado: '',
  rol: '',
}

const getFiltersFromParams = (params) => ({
  q: params.get('q') ?? '',
  estado: params.get('estado') ?? '',
  rol: params.get('rol') ?? '',
})

const buildParamsFromFilters = (filters, page = 1) => {
  const params = new URLSearchParams()

  Object.entries(filters).forEach(([key, value]) => {
    if (value) {
      params.set(key, value)
    }
  })

  if (page > 1) {
    params.set('page', String(page))
  }

  return params
}

const actionLabels = {
  activar: 'Activar cuenta de tienda',
  rechazar: 'Rechazar solicitud de tienda',
  bloquear: 'Bloquear cuenta',
  desbloquear: 'Desbloquear cuenta',
}

const UsersSkeleton = () => (
  <div className="overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-sm">
    <div className="divide-y divide-slate-100">
      {Array.from({ length: 6 }, (_, row) => (
        <div className="grid gap-4 px-5 py-5 lg:grid-cols-[0.5fr_1.7fr_1fr_1fr_1fr_1.3fr_0.9fr_1.2fr]" key={row}>
          {Array.from({ length: 8 }, (_, cell) => (
            <div className="h-5 animate-pulse rounded-full bg-slate-200" key={cell} />
          ))}
        </div>
      ))}
    </div>
  </div>
)

const resolveAvailableActions = (user) => {
  if (!user) {
    return []
  }

  if (user.estado === 'EN_REVISION') {
    return ['activar', 'rechazar']
  }

  if (user.estado === 'ACTIVO') {
    return ['bloquear']
  }

  if (user.estado === 'BLOQUEADO') {
    return ['desbloquear']
  }

  return []
}

const Usuarios = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const [filters, setFilters] = useState(getFiltersFromParams(searchParams))
  const [items, setItems] = useState([])
  const [paginacion, setPaginacion] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const [detailOpen, setDetailOpen] = useState(false)
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailError, setDetailError] = useState('')
  const [selectedUser, setSelectedUser] = useState(null)
  const [modalState, setModalState] = useState({ abierto: false, accion: '', user: null })
  const [motivo, setMotivo] = useState('')
  const [actionLoading, setActionLoading] = useState(false)
  const { showToast } = useToast()

  useEffect(() => {
    setFilters(getFiltersFromParams(searchParams))
  }, [searchParams])

  useEffect(() => {
    const fetchUsuarios = async () => {
      setCargando(true)
      setError('')

      try {
        const response = await api.get('/admin/usuarios', {
          params: {
            page: Number(searchParams.get('page') ?? '1'),
            limit: 20,
            ...Object.fromEntries(buildParamsFromFilters(getFiltersFromParams(searchParams)).entries()),
          },
        })

        setItems(response.data.data ?? [])
        setPaginacion(response.data.paginacion ?? null)
      } catch (requestError) {
        setItems([])
        setPaginacion(null)
        setError(
          requestError.response?.data?.mensaje ||
            requestError.response?.data?.message ||
            'No se pudo cargar la gestion de usuarios.'
        )
      } finally {
        setCargando(false)
      }
    }

    fetchUsuarios()
  }, [searchParams])

  const totalUsuarios = paginacion?.total ?? items.length

  const handleFilterChange = (event) => {
    const { name, value } = event.target
    setFilters((current) => ({ ...current, [name]: value }))
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    setSearchParams(buildParamsFromFilters(filters))
  }

  const handleClear = () => {
    setFilters(emptyFilters)
    setSearchParams({})
  }

  const handlePageChange = (nextPage) => {
    setSearchParams(buildParamsFromFilters(getFiltersFromParams(searchParams), nextPage))
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const updateUserInList = (userId, updates) => {
    setItems((current) =>
      current.map((item) => (item.id === userId ? { ...item, ...updates } : item)),
    )
  }

  const updateSelectedUser = (userId, updates) => {
    setSelectedUser((current) => (current?.id === userId ? { ...current, ...updates } : current))
  }

  const openDetail = async (userId) => {
    setDetailOpen(true)
    setDetailLoading(true)
    setDetailError('')

    try {
      const response = await api.get(`/admin/usuarios/${userId}`)
      setSelectedUser(response.data.data)
    } catch (requestError) {
      setSelectedUser(null)
      setDetailError(
        requestError.response?.data?.mensaje ||
          requestError.response?.data?.message ||
          'No se pudo cargar el detalle del usuario.'
      )
    } finally {
      setDetailLoading(false)
    }
  }

  const openActionModal = (accion, user) => {
    setModalState({ abierto: true, accion, user })
    setMotivo('')
  }

  const closeActionModal = () => {
    setModalState({ abierto: false, accion: '', user: null })
    setMotivo('')
  }

  const getActionEndpoint = (accion, userId) => {
    if (accion === 'activar') return `/admin/usuarios/${userId}/activar`
    if (accion === 'rechazar') return `/admin/usuarios/${userId}/rechazar`
    if (accion === 'bloquear') return `/admin/usuarios/${userId}/bloquear`
    return `/admin/usuarios/${userId}/desbloquear`
  }

  const applyActionResult = (accion, user, responseData) => {
    if (!user) return

    const nextState =
      accion === 'activar' || accion === 'desbloquear'
        ? 'ACTIVO'
        : accion === 'rechazar'
          ? 'RECHAZADO'
          : 'BLOQUEADO'

    updateUserInList(user.id, { estado: nextState })
    updateSelectedUser(user.id, { estado: nextState })

    if (accion === 'bloquear') {
      return `Usuario bloqueado. ${responseData?.anuncios_desactivados ?? 0} anuncios desactivados.`
    }

    if (accion === 'activar') return 'Tienda activada correctamente.'
    if (accion === 'rechazar') return 'Solicitud rechazada.'
    return 'Usuario desbloqueado correctamente.'
  }

  const handleConfirmAction = async () => {
    if (!modalState.user) return
    if (modalState.accion !== 'activar' && !motivo.trim()) return

    setActionLoading(true)

    try {
      const payload = modalState.accion === 'activar' ? undefined : { motivo: motivo.trim() }

      const response =
        modalState.accion === 'activar'
          ? await api.patch(getActionEndpoint(modalState.accion, modalState.user.id))
          : await api.patch(getActionEndpoint(modalState.accion, modalState.user.id), payload)

      showToast(
        applyActionResult(modalState.accion, modalState.user, response.data.data),
        'exito',
        4000,
      )
      closeActionModal()
    } catch (requestError) {
      showToast(
        requestError.response?.data?.mensaje ||
          requestError.response?.data?.message ||
          'No se pudo completar la accion sobre el usuario.',
        'error',
        4500,
      )
    } finally {
      setActionLoading(false)
    }
  }

  const actionButtons = useMemo(
    () => resolveAvailableActions(modalState.user),
    [modalState.user],
  )

  return (
    <div className="space-y-6">
      <section className="rounded-[32px] border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-700">
              Administracion
            </p>
            <h1 className="mt-2 text-3xl font-black tracking-tight text-slate-900">
              Gestion de Usuarios
            </h1>
          </div>
          <span className="inline-flex rounded-full bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-700">
            {totalUsuarios} usuarios
          </span>
        </div>
      </section>

      <form className="rounded-[32px] border border-slate-200 bg-white p-6 shadow-sm" onSubmit={handleSubmit}>
        <div className="grid gap-4 lg:grid-cols-[2fr_1fr_1fr_auto_auto]">
          <input
            className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none transition focus:border-sky-400"
            name="q"
            onChange={handleFilterChange}
            placeholder="Buscar por nombre o correo"
            type="text"
            value={filters.q}
          />

          <select
            className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none transition focus:border-sky-400"
            name="estado"
            onChange={handleFilterChange}
            value={filters.estado}
          >
            <option value="">Todos los estados</option>
            <option value="ACTIVO">ACTIVO</option>
            <option value="PENDIENTE_VERIFICACION">PENDIENTE_VERIFICACION</option>
            <option value="EN_REVISION">EN_REVISION</option>
            <option value="BLOQUEADO">BLOQUEADO</option>
            <option value="RECHAZADO">RECHAZADO</option>
          </select>

          <select
            className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none transition focus:border-sky-400"
            name="rol"
            onChange={handleFilterChange}
            value={filters.rol}
          >
            <option value="">Todos los roles</option>
            <option value="USER_ESTANDAR">USER_ESTANDAR</option>
            <option value="TIENDA_VERIFICADA">TIENDA_VERIFICADA</option>
          </select>

          <button
            className="rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
            type="submit"
          >
            Buscar
          </button>

          <button
            className="rounded-2xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
            onClick={handleClear}
            type="button"
          >
            Limpiar
          </button>
        </div>
      </form>

      {error ? <div className="rounded-[24px] border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-700">{error}</div> : null}

      {cargando ? (
        <UsersSkeleton />
      ) : (
        <section className="overflow-hidden rounded-[32px] border border-slate-200 bg-white shadow-sm">
          {items.length === 0 ? (
            <div className="px-6 py-14 text-center text-sm text-slate-500">
              No se encontraron usuarios con esos filtros.
            </div>
          ) : (
            <>
              <div className="hidden border-b border-slate-200 bg-slate-50 px-5 py-4 text-xs font-semibold uppercase tracking-[0.14em] text-slate-500 lg:grid lg:grid-cols-[0.5fr_1.7fr_1fr_1fr_1fr_1.3fr_0.9fr_1.2fr] lg:gap-4">
                <span>ID</span>
                <span>Usuario</span>
                <span>Telefono</span>
                <span>Rol</span>
                <span>Estado</span>
                <span>Tienda</span>
                <span>Registro</span>
                <span>Acciones</span>
              </div>

              <div className="divide-y divide-slate-100">
                {items.map((item) => (
                  <div className="grid gap-4 px-5 py-5 lg:grid-cols-[0.5fr_1.7fr_1fr_1fr_1fr_1.3fr_0.9fr_1.2fr]" key={item.id}>
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400 lg:hidden">ID</p>
                      <p className="mt-1 text-sm font-semibold text-slate-900">{item.id}</p>
                    </div>

                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400 lg:hidden">Usuario</p>
                      <p className="mt-1 font-semibold text-slate-900">{item.nombre}</p>
                      <p className="text-sm text-slate-600">{item.correo}</p>
                    </div>

                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400 lg:hidden">Telefono</p>
                      <p className="mt-1 text-sm text-slate-700">{item.telefono || '-'}</p>
                    </div>

                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400 lg:hidden">Rol</p>
                      <span className={`mt-1 inline-flex rounded-full px-3 py-1 text-xs font-semibold ${roleStyles[item.rol] ?? 'bg-slate-100 text-slate-700'}`}>
                        {item.rol}
                      </span>
                    </div>

                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400 lg:hidden">Estado</p>
                      <span className={`mt-1 inline-flex rounded-full px-3 py-1 text-xs font-semibold ${stateStyles[item.estado] ?? 'bg-slate-100 text-slate-700'}`}>
                        {item.estado}
                      </span>
                    </div>

                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400 lg:hidden">Tienda</p>
                      <p className="mt-1 text-sm text-slate-700">{item.nombre_comercial || '-'}</p>
                      <p className="text-sm text-slate-500">{item.ruc || '-'}</p>
                    </div>

                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400 lg:hidden">Registro</p>
                      <p className="mt-1 text-sm text-slate-700">{formatDate(item.created_at)}</p>
                    </div>

                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400 lg:hidden">Acciones</p>
                      <div className="mt-1 flex flex-wrap gap-2">
                        {resolveAvailableActions(item).map((action) => (
                          <button
                            className={`rounded-2xl px-3 py-2 text-sm font-semibold text-white transition ${
                              action === 'activar'
                                ? 'bg-emerald-600 hover:bg-emerald-700'
                                : action === 'rechazar' || action === 'bloquear'
                                  ? 'bg-rose-600 hover:bg-rose-700'
                                  : 'bg-sky-600 hover:bg-sky-700'
                            }`}
                            key={`${item.id}-${action}`}
                            onClick={() => openActionModal(action, item)}
                            type="button"
                          >
                            {action === 'activar'
                              ? 'Activar'
                              : action === 'rechazar'
                                ? 'Rechazar'
                                : action === 'bloquear'
                                  ? 'Bloquear'
                                  : 'Desbloquear'}
                          </button>
                        ))}
                        <button
                          className="rounded-2xl border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
                          onClick={() => openDetail(item.id)}
                          type="button"
                        >
                          Ver detalle
                        </button>
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

      {detailOpen ? (
        <div className="fixed inset-0 z-[75] bg-slate-950/30" role="presentation">
          <div
            className="absolute inset-y-0 right-0 w-full max-w-2xl overflow-y-auto border-l border-slate-200 bg-white shadow-[0_0_80px_-35px_rgba(15,23,42,0.55)]"
            role="dialog"
          >
            <div className="sticky top-0 z-10 flex items-center justify-between border-b border-slate-200 bg-white px-5 py-4">
              <div>
                <p className="text-sm text-slate-500">Detalle de usuario</p>
                <h2 className="text-xl font-black text-slate-900">
                  {selectedUser?.nombre ?? 'Cargando...'}
                </h2>
              </div>
              <button
                className="rounded-full bg-slate-100 px-3 py-2 text-sm font-semibold text-slate-700"
                onClick={() => setDetailOpen(false)}
                type="button"
              >
                Cerrar
              </button>
            </div>

            <div className="space-y-6 px-5 py-5">
              {detailLoading ? (
                <div className="space-y-4">
                  {Array.from({ length: 6 }, (_, index) => (
                    <div className="h-6 animate-pulse rounded-full bg-slate-200" key={index} />
                  ))}
                </div>
              ) : detailError ? (
                <div className="rounded-[24px] border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-700">
                  {detailError}
                </div>
              ) : selectedUser ? (
                <>
                  <section className="rounded-[28px] bg-slate-50 p-5">
                    <div className="flex flex-wrap items-center gap-3">
                      <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${roleStyles[selectedUser.rol] ?? 'bg-slate-100 text-slate-700'}`}>
                        {selectedUser.rol}
                      </span>
                      <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${stateStyles[selectedUser.estado] ?? 'bg-slate-100 text-slate-700'}`}>
                        {selectedUser.estado}
                      </span>
                    </div>
                    <div className="mt-4 grid gap-3 text-sm text-slate-700 sm:grid-cols-2">
                      <p><span className="font-semibold text-slate-900">Correo:</span> {selectedUser.correo}</p>
                      <p><span className="font-semibold text-slate-900">Telefono:</span> {selectedUser.telefono || '-'}</p>
                      <p><span className="font-semibold text-slate-900">Miembro desde:</span> {formatDate(selectedUser.miembro_desde)}</p>
                      <p><span className="font-semibold text-slate-900">ID:</span> {selectedUser.id}</p>
                    </div>
                  </section>

                  {selectedUser.tienda ? (
                    <section className="rounded-[28px] border border-slate-200 p-5">
                      <h3 className="text-lg font-bold text-slate-900">Datos de tienda</h3>
                      <div className="mt-4 grid gap-3 text-sm text-slate-700">
                        <p><span className="font-semibold text-slate-900">Nombre comercial:</span> {selectedUser.tienda.nombre_comercial}</p>
                        <p><span className="font-semibold text-slate-900">RUC:</span> {selectedUser.tienda.ruc}</p>
                        <p><span className="font-semibold text-slate-900">Direccion:</span> {selectedUser.tienda.direccion}</p>
                        <a
                          className="font-semibold text-sky-700 underline"
                          href={formatImageUrl(selectedUser.tienda.documento_identidad)}
                          rel="noreferrer"
                          target="_blank"
                        >
                          Ver documento de identidad
                        </a>
                      </div>
                    </section>
                  ) : null}

                  <section className="grid gap-4 md:grid-cols-2">
                    <div className="rounded-[28px] border border-slate-200 p-5">
                      <p className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-500">
                        Reputacion vendedor
                      </p>
                      <div className="mt-4">
                        <Estrellas puntaje={selectedUser.reputacion_vendedor.calificacion_promedio} tamano="lg" />
                      </div>
                      <div className="mt-4 space-y-2 text-sm text-slate-700">
                        <p>Total calificaciones: {selectedUser.reputacion_vendedor.total_calificaciones}</p>
                        <p>Total ventas: {selectedUser.reputacion_vendedor.total_ventas}</p>
                      </div>
                    </div>
                    <div className="rounded-[28px] border border-slate-200 p-5">
                      <p className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-500">
                        Reputacion comprador
                      </p>
                      <div className="mt-4">
                        <Estrellas puntaje={selectedUser.reputacion_comprador.calificacion_promedio} tamano="lg" />
                      </div>
                      <div className="mt-4 space-y-2 text-sm text-slate-700">
                        <p>Total calificaciones: {selectedUser.reputacion_comprador.total_calificaciones}</p>
                        <p>Total compras: {selectedUser.reputacion_comprador.total_compras}</p>
                      </div>
                    </div>
                  </section>

                  <section className="rounded-[28px] border border-slate-200 p-5">
                    <h3 className="text-lg font-bold text-slate-900">Historial de acciones admin</h3>
                    {selectedUser.historial_admin?.length ? (
                      <div className="mt-4 space-y-3">
                        {selectedUser.historial_admin.map((item, index) => (
                          <div className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-700" key={`${item.accion}-${item.created_at}-${index}`}>
                            <p className="font-semibold text-slate-900">{item.accion}</p>
                            <p className="mt-1">Motivo: {item.motivo || 'Sin motivo registrado'}</p>
                            <p className="mt-1">Admin: Admin #{item.admin_id}</p>
                            <p className="mt-1">Fecha: {formatDate(item.created_at)}</p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="mt-4 text-sm text-slate-500">Sin acciones administrativas registradas.</p>
                    )}
                  </section>

                  <section className="rounded-[28px] border border-slate-200 p-5">
                    <h3 className="text-lg font-bold text-slate-900">Acciones disponibles</h3>
                    <div className="mt-4 flex flex-wrap gap-3">
                      {resolveAvailableActions(selectedUser).length === 0 ? (
                        <p className="text-sm text-slate-500">No hay acciones disponibles para este estado.</p>
                      ) : (
                        resolveAvailableActions(selectedUser).map((action) => (
                          <button
                            className={`rounded-2xl px-4 py-3 text-sm font-semibold text-white ${
                              action === 'activar'
                                ? 'bg-emerald-600'
                                : action === 'rechazar' || action === 'bloquear'
                                  ? 'bg-rose-600'
                                  : 'bg-sky-600'
                            }`}
                            key={`detail-${action}`}
                            onClick={() => openActionModal(action, selectedUser)}
                            type="button"
                          >
                            {action === 'activar'
                              ? 'Activar'
                              : action === 'rechazar'
                                ? 'Rechazar'
                                : action === 'bloquear'
                                  ? 'Bloquear'
                                  : 'Desbloquear'}
                          </button>
                        ))
                      )}
                    </div>
                  </section>
                </>
              ) : null}
            </div>
          </div>
        </div>
      ) : null}

      <Modal abierto={modalState.abierto} onCerrar={closeActionModal} titulo={actionLabels[modalState.accion]}>
        <div className="space-y-5">
          {modalState.user ? (
            <div className="rounded-[24px] bg-slate-50 p-4 text-sm text-slate-700">
              <p className="font-semibold text-slate-900">{modalState.user.nombre}</p>
              <p className="mt-1">Correo: {modalState.user.correo}</p>
              <p className="mt-1">Rol: {modalState.user.rol}</p>
              {modalState.user.nombre_comercial ? (
                <p className="mt-1">Tienda: {modalState.user.nombre_comercial}</p>
              ) : null}
              {modalState.user.ruc ? <p className="mt-1">RUC: {modalState.user.ruc}</p> : null}
            </div>
          ) : null}

          {modalState.accion === 'activar' && selectedUser?.tienda ? (
            <a
              className="block rounded-2xl border border-sky-200 bg-sky-50 px-4 py-3 text-sm font-semibold text-sky-700"
              href={formatImageUrl(selectedUser.tienda.documento_identidad)}
              rel="noreferrer"
              target="_blank"
            >
              Abrir documento de identidad
            </a>
          ) : null}

          {modalState.accion === 'bloquear' ? (
            <div className="rounded-[24px] border border-amber-200 bg-amber-50 px-4 py-4 text-sm text-amber-800">
              Los anuncios activos de este usuario seran desactivados automaticamente.
            </div>
          ) : null}

          {modalState.accion === 'desbloquear' ? (
            <div className="rounded-[24px] border border-sky-200 bg-sky-50 px-4 py-4 text-sm text-sky-800">
              Los anuncios desactivados por el bloqueo no se reactivaran automaticamente.
            </div>
          ) : null}

          {modalState.accion !== 'activar' ? (
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700" htmlFor="motivo">
                Motivo
              </label>
              <textarea
                className="min-h-32 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none transition focus:border-sky-400"
                id="motivo"
                maxLength={500}
                onChange={(event) => setMotivo(event.target.value)}
                value={motivo}
              />
              <div className="flex justify-between text-xs text-slate-500">
                <span>
                  {modalState.accion === 'rechazar'
                    ? 'El motivo sera registrado en el log de administracion.'
                    : 'Este campo es obligatorio.'}
                </span>
                <span>{motivo.length}/500</span>
              </div>
            </div>
          ) : null}

          <div className="flex flex-col gap-3 sm:flex-row">
            <button
              className="flex-1 rounded-2xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
              onClick={closeActionModal}
              type="button"
            >
              Cancelar
            </button>
            <button
              className={`flex-1 rounded-2xl px-4 py-3 text-sm font-semibold text-white transition disabled:cursor-not-allowed disabled:opacity-50 ${
                modalState.accion === 'activar' || modalState.accion === 'desbloquear'
                  ? 'bg-emerald-600 hover:bg-emerald-700'
                  : 'bg-rose-600 hover:bg-rose-700'
              }`}
              disabled={actionLoading || (modalState.accion !== 'activar' && !motivo.trim())}
              onClick={handleConfirmAction}
              type="button"
            >
              {actionLoading
                ? 'Guardando...'
                : modalState.accion === 'activar'
                  ? 'Confirmar activacion'
                  : modalState.accion === 'rechazar'
                    ? 'Confirmar rechazo'
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

export default Usuarios

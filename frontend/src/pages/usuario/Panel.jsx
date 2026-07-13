import { useEffect, useMemo, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../../api/axios'
import AnuncioCard from '../../components/ui/AnuncioCard'
import Estrellas from '../../components/ui/Estrellas'
import MetricaCard from '../../components/ui/MetricaCard'
import SkeletonCard from '../../components/ui/SkeletonCard'
import { useAuth } from '../../hooks/useAuth'
import { formatDate, formatDateTime, formatImageUrl } from '../../utils/format'
import { isValidPhone } from '../../utils/validators'

const avatarPalette = [
  'from-sky-500 to-cyan-400',
  'from-emerald-500 to-lime-400',
  'from-amber-500 to-orange-400',
  'from-fuchsia-500 to-pink-400',
]

const getAvatarGradient = (name = '') =>
  avatarPalette[Math.abs(name.length) % avatarPalette.length]

const Modal = ({ children, onClose, title }) => (
  <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/55 px-4">
    <div className="w-full max-w-2xl rounded-[28px] bg-white p-6 shadow-2xl">
      <div className="mb-5 flex items-center justify-between gap-4">
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

const buildProfileForm = (perfil) => ({
  nombre: perfil?.nombre ?? '',
  telefono: perfil?.telefono ?? '',
  nombre_comercial: perfil?.tienda?.nombre_comercial ?? '',
  direccion: perfil?.tienda?.direccion ?? '',
})

const Panel = () => {
  const navigate = useNavigate()
  const { usuario, logout, esAdmin, updateUser } = useAuth()
  const [panel, setPanel] = useState(null)
  const [perfilPublico, setPerfilPublico] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const [accionError, setAccionError] = useState('')
  const [perfilPublicoError, setPerfilPublicoError] = useState('')
  const [loadingActionId, setLoadingActionId] = useState(null)
  const [showAllActive, setShowAllActive] = useState(false)
  const [editOpen, setEditOpen] = useState(false)
  const [editForm, setEditForm] = useState(buildProfileForm(null))
  const [editErrors, setEditErrors] = useState({})
  const [savingProfile, setSavingProfile] = useState(false)
  const [profileMessage, setProfileMessage] = useState('')
  const [moderationModalOpen, setModerationModalOpen] = useState(false)
  const [moderationDetail, setModerationDetail] = useState(null)
  const [moderationLoading, setModerationLoading] = useState(false)
  const [appealMessage, setAppealMessage] = useState('')
  const [appealFiles, setAppealFiles] = useState([])
  const [appealError, setAppealError] = useState('')
  const [appealSuccess, setAppealSuccess] = useState('')
  const [submittingAppeal, setSubmittingAppeal] = useState(false)
  const activeListingsRef = useRef(null)

  const refreshPanelData = async ({ showLoading = false } = {}) => {
    if (showLoading) {
      setCargando(true)
    }

    setError('')
    setPerfilPublicoError('')

    try {
      const panelResponse = await api.get('/usuarios/me/panel')
      const panelData = panelResponse.data.data
      const ownerId = panelData?.perfil?.id

      setPanel(panelData)

      if (!ownerId) {
        setPerfilPublico(null)
        setPerfilPublicoError(
          'No se pudo identificar el usuario para cargar la vista previa del perfil.'
        )
        return
      }

      try {
        const perfilResponse = await api.get(`/usuarios/${ownerId}/perfil`)
        setPerfilPublico(perfilResponse.data.data)
      } catch (perfilError) {
        setPerfilPublico(null)
        setPerfilPublicoError(
          perfilError.response?.data?.mensaje ||
            perfilError.response?.data?.message ||
            'No se pudo cargar la vista previa de tus anuncios activos.'
        )
      }
    } catch (requestError) {
      setError(
        requestError.response?.data?.mensaje ||
          requestError.response?.data?.message ||
          'No se pudo cargar el panel.'
      )
    } finally {
      if (showLoading) {
        setCargando(false)
      }
    }
  }

  useEffect(() => {
    if (!usuario) {
      setCargando(false)
      return
    }

    refreshPanelData({ showLoading: true })
    // refreshPanelData is intentionally omitted from deps because it is recreated on render
    // and we only want to reload when auth user changes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [usuario])

  const anunciosActivos = useMemo(
    () =>
      (perfilPublico?.anuncios_activos ?? []).map((anuncio) => ({
        ...anuncio,
        vendedor_nombre: perfilPublico?.nombre,
        es_tienda_verificada: perfilPublico?.es_tienda_verificada,
      })),
    [perfilPublico],
  )

  const anunciosInactivos = useMemo(
    () =>
      (panel?.anuncios?.inactivos?.items ?? []).map((anuncio) => ({
        ...anuncio,
        vendedor_nombre: perfilPublico?.nombre,
        es_tienda_verificada: perfilPublico?.es_tienda_verificada,
      })),
    [panel, perfilPublico],
  )

  const visibleActiveListings = useMemo(
    () => (showAllActive ? anunciosActivos : anunciosActivos.slice(0, 6)),
    [anunciosActivos, showAllActive],
  )

  const publicProfileId = panel?.perfil?.id ?? usuario?.id ?? null

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const handleViewMyListings = () => {
    setShowAllActive(true)
    window.setTimeout(() => {
      activeListingsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }, 0)
  }

  const handleOpenEditProfile = () => {
    setEditErrors({})
    setProfileMessage('')
    setEditForm(buildProfileForm(panel?.perfil))
    setEditOpen(true)
  }

  const handleEditFieldChange = (field, value) => {
    setEditForm((current) => ({ ...current, [field]: value }))
    setEditErrors((current) => ({ ...current, [field]: '' }))
  }

  const validateProfileForm = () => {
    const nextErrors = {}
    const isStore = panel?.perfil?.es_tienda_verificada

    if (isStore) {
      if (!editForm.nombre_comercial.trim()) {
        nextErrors.nombre_comercial = 'Ingresa el nombre comercial.'
      }
      if (!editForm.direccion.trim()) {
        nextErrors.direccion = 'Ingresa la dirección.'
      }
    } else if (!editForm.nombre.trim()) {
      nextErrors.nombre = 'Ingresa tu nombre.'
    }

    if (!isValidPhone(editForm.telefono.trim())) {
      nextErrors.telefono = 'Ingresa un teléfono peruano de 9 dígitos.'
    }

    setEditErrors(nextErrors)
    return Object.keys(nextErrors).length === 0
  }

  const handleSaveProfile = async (event) => {
    event.preventDefault()

    if (!validateProfileForm()) {
      return
    }

    const isStore = panel?.perfil?.es_tienda_verificada
    const payload = isStore
      ? {
          nombre_comercial: editForm.nombre_comercial.trim(),
          telefono: editForm.telefono.trim(),
          direccion: editForm.direccion.trim(),
        }
      : {
          nombre: editForm.nombre.trim(),
          telefono: editForm.telefono.trim(),
        }

    setSavingProfile(true)
    setProfileMessage('')

    try {
      const response = await api.patch('/usuarios/me/perfil', payload)
      const updatedPerfil = response.data.data?.perfil

      if (updatedPerfil) {
        setPanel((current) =>
          current
            ? {
                ...current,
                perfil: updatedPerfil,
              }
            : current,
        )
        setPerfilPublico((current) =>
          current
            ? {
                ...current,
                nombre: updatedPerfil.nombre,
                es_tienda_verificada: updatedPerfil.es_tienda_verificada,
                tienda: updatedPerfil.tienda
                  ? {
                      ...(current.tienda ?? {}),
                      nombre_comercial: updatedPerfil.tienda.nombre_comercial,
                      direccion: updatedPerfil.tienda.direccion,
                    }
                  : current.tienda,
              }
            : current,
        )
        updateUser({
          nombre: updatedPerfil.nombre,
          telefono: updatedPerfil.telefono,
          correo: updatedPerfil.correo,
        })
      }

      setEditOpen(false)
      setProfileMessage(response.data.message || 'Perfil actualizado correctamente.')
    } catch (requestError) {
      const message =
        requestError.response?.data?.message ||
        requestError.response?.data?.mensaje ||
        'No se pudo actualizar el perfil.'

      if (message.toLowerCase().includes('telefono')) {
        setEditErrors((current) => ({
          ...current,
          telefono: 'Este teléfono ya se encuentra registrado.',
        }))
      } else if (message.toLowerCase().includes('nombre comercial')) {
        setEditErrors((current) => ({
          ...current,
          nombre_comercial: 'Este nombre comercial ya se encuentra registrado.',
        }))
      } else {
        setProfileMessage(message)
      }
    } finally {
      setSavingProfile(false)
    }
  }

  const handleDesactivar = async (anuncioId) => {
    setLoadingActionId(anuncioId)
    setAccionError('')

    try {
      await api.patch(`/anuncios/${anuncioId}/desactivar`)
      await refreshPanelData()
    } catch (requestError) {
      setAccionError(
        requestError.response?.data?.mensaje ||
          requestError.response?.data?.message ||
          'No se pudo desactivar el anuncio.'
      )
    } finally {
      setLoadingActionId(null)
    }
  }

  const handleReactivar = async (anuncioId) => {
    setLoadingActionId(anuncioId)
    setAccionError('')

    try {
      await api.patch(`/anuncios/${anuncioId}/reactivar`)
      await refreshPanelData()
    } catch (requestError) {
      setAccionError(
        requestError.response?.data?.mensaje ||
          requestError.response?.data?.message ||
          'No se pudo reactivar el anuncio.'
      )
    } finally {
      setLoadingActionId(null)
    }
  }

  const handleOpenModerationCase = async (anuncioId) => {
    setModerationLoading(true)
    setAppealError('')
    setAppealSuccess('')
    setAppealMessage('')
    setAppealFiles([])

    try {
      const response = await api.get(`/usuarios/me/anuncios/${anuncioId}/moderacion`)
      setModerationDetail(response.data.data)
      setModerationModalOpen(true)
    } catch (requestError) {
      setAccionError(
        requestError.response?.data?.mensaje ||
          requestError.response?.data?.message ||
          'No se pudo cargar el caso de moderacion.'
      )
    } finally {
      setModerationLoading(false)
    }
  }

  const handleSubmitAppeal = async (event) => {
    event.preventDefault()
    if (!moderationDetail) return

    setSubmittingAppeal(true)
    setAppealError('')
    setAppealSuccess('')

    try {
      const formData = new FormData()
      formData.append('mensaje', appealMessage.trim())
      appealFiles.forEach((file) => formData.append('evidencias', file))

      const response = await api.post(
        `/usuarios/me/anuncios/${moderationDetail.anuncio_id}/apelar`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        },
      )

      setAppealSuccess(response.data.message || 'Apelacion enviada correctamente.')
      setAppealMessage('')
      setAppealFiles([])

      const refreshed = await api.get(`/usuarios/me/anuncios/${moderationDetail.anuncio_id}/moderacion`)
      setModerationDetail(refreshed.data.data)
      setPanel((current) =>
        current
          ? {
              ...current,
              moderacion: {
                casos: (current.moderacion?.casos ?? []).map((caso) =>
                  caso.anuncio_id === moderationDetail.anuncio_id
                    ? {
                        ...caso,
                        apelacion: refreshed.data.data.apelacion_actual
                          ? {
                              apelacion_id: refreshed.data.data.apelacion_actual.apelacion_id,
                              estado: refreshed.data.data.apelacion_actual.estado,
                              created_at: refreshed.data.data.apelacion_actual.created_at,
                            }
                          : caso.apelacion,
                        puede_apelar: refreshed.data.data.puede_apelar,
                      }
                    : caso,
                ),
              },
            }
          : current,
      )
    } catch (requestError) {
      setAppealError(
        requestError.response?.data?.mensaje ||
          requestError.response?.data?.message ||
          'No se pudo registrar la apelacion.',
      )
    } finally {
      setSubmittingAppeal(false)
    }
  }

  if (cargando) {
    return (
      <div className="min-h-screen bg-[linear-gradient(180deg,#f8fafc_0%,#eff6ff_35%,#f8fafc_100%)] px-4 py-8">
        <div className="mx-auto max-w-7xl space-y-6 lg:grid lg:grid-cols-[320px_minmax(0,1fr)] lg:gap-6 lg:space-y-0">
          <div className="rounded-[32px] border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mx-auto h-24 w-24 animate-pulse rounded-full bg-slate-200" />
            <div className="mt-5 h-6 w-2/3 animate-pulse rounded-full bg-slate-200" />
            <div className="mt-3 h-4 w-1/2 animate-pulse rounded-full bg-slate-200" />
            <div className="mt-10 space-y-3">
              {Array.from({ length: 5 }, (_, index) => (
                <div className="h-4 animate-pulse rounded-full bg-slate-200" key={index} />
              ))}
            </div>
          </div>
          <div className="space-y-6">
            <div className="grid gap-4 md:grid-cols-3">
              {Array.from({ length: 3 }, (_, index) => (
                <div className="h-32 animate-pulse rounded-[24px] bg-slate-200" key={index} />
              ))}
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              {Array.from({ length: 2 }, (_, index) => (
                <div className="h-44 animate-pulse rounded-[24px] bg-slate-200" key={index} />
              ))}
            </div>
            <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
              {Array.from({ length: 3 }, (_, index) => (
                <SkeletonCard key={index} />
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error || !panel) {
    return <div className="px-4 py-12 text-center text-sm text-rose-700">{error}</div>
  }

  const { perfil, anuncios, reputacion_vendedor, reputacion_comprador, calificaciones_pendientes } =
    panel
  const casosModeracion = panel?.moderacion?.casos ?? []

  return (
    <div className="min-h-screen bg-[linear-gradient(180deg,#f8fafc_0%,#eff6ff_35%,#f8fafc_100%)] px-4 py-8">
      <div className="mx-auto max-w-7xl space-y-6 lg:grid lg:grid-cols-[320px_minmax(0,1fr)] lg:gap-6 lg:space-y-0">
        <aside className="self-start rounded-[32px] border border-slate-200 bg-white p-6 shadow-sm">
          <div
            className={`mx-auto flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br ${getAvatarGradient(
              perfil.nombre,
            )} text-4xl font-black text-white`}
          >
            {perfil.nombre?.charAt(0)?.toUpperCase() ?? 'U'}
          </div>

          <div className="mt-5 text-center">
            <h1 className="text-2xl font-black tracking-tight text-slate-900">{perfil.nombre}</h1>
            {perfil.es_tienda_verificada ? (
              <span className="mt-3 inline-flex rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                ✓ Tienda Verificada
              </span>
            ) : null}
          </div>

          <div className="mt-8 space-y-4 text-sm text-slate-600">
            <div>
              <p className="font-semibold text-slate-900">Correo</p>
              <p>{perfil.correo}</p>
            </div>
            <div>
              <p className="font-semibold text-slate-900">Teléfono</p>
              <p>{perfil.telefono}</p>
            </div>

            {perfil.tienda ? (
              <>
                <div>
                  <p className="font-semibold text-slate-900">Nombre comercial</p>
                  <p>{perfil.tienda.nombre_comercial}</p>
                </div>
                <div>
                  <p className="font-semibold text-slate-900">RUC</p>
                  <p>{perfil.tienda.ruc}</p>
                </div>
                <div>
                  <p className="font-semibold text-slate-900">Dirección</p>
                  <p>{perfil.tienda.direccion}</p>
                </div>
              </>
            ) : null}

            <div className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3">
              <span className="font-semibold text-slate-900">Estado</span>
              <span className="rounded-full bg-emerald-500 px-3 py-1 text-xs font-semibold text-white">
                {perfil.estado}
              </span>
            </div>

            <div>
              <p className="font-semibold text-slate-900">Miembro desde</p>
              <p>{formatDate(perfil.miembro_desde)}</p>
            </div>
          </div>

          {profileMessage ? <p className="mt-6 text-sm text-sky-700">{profileMessage}</p> : null}

          <button
            className="mt-6 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
            onClick={handleOpenEditProfile}
            type="button"
          >
            Editar perfil
          </button>

          <button
            className="mt-4 w-full rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
            onClick={handleLogout}
            type="button"
          >
            Cerrar sesión
          </button>
        </aside>

        <main className="space-y-6">
          <section
            className="rounded-[32px] border border-slate-200 bg-white p-6 shadow-sm"
            ref={activeListingsRef}
          >
            <div className="mb-5 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-700">
                  Sección 1
                </p>
                <h2 className="mt-2 text-2xl font-black text-slate-900">Resumen de anuncios</h2>
              </div>
              <div className="flex flex-wrap gap-3">
                <Link
                  className="rounded-full bg-slate-900 px-4 py-2 text-sm font-semibold text-white"
                  to="/anuncios/crear"
                >
                  Publicar nuevo anuncio
                </Link>
                <button
                  className="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
                  onClick={handleViewMyListings}
                  type="button"
                >
                  Ver mis anuncios
                </button>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              <MetricaCard
                color="verde"
                subtitulo={
                  anuncios.activos.limite_maximo === null
                    ? 'Publicaciones disponibles sin tope'
                    : `${anuncios.activos.disponibles} espacios disponibles`
                }
                titulo="Anuncios activos"
                valor={`${anuncios.activos.total} / ${
                  anuncios.activos.limite_maximo === null ? 'Sin límite' : anuncios.activos.limite_maximo
                }`}
              />
              <MetricaCard
                color="azul"
                titulo="Anuncios inactivos"
                valor={anuncios.inactivos.total}
              />
              <MetricaCard
                color="amarillo"
                titulo="Anuncios vendidos"
                valor={anuncios.vendidos.total}
              />
            </div>
          </section>

          <section className="rounded-[32px] border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-5">
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-700">
                Sección 2
              </p>
              <h2 className="mt-2 text-2xl font-black text-slate-900">Reputación</h2>
            </div>

            {calificaciones_pendientes > 0 ? (
              <div className="mb-5 rounded-[24px] border border-amber-200 bg-amber-50 px-5 py-4 text-sm text-amber-800">
                Tienes {calificaciones_pendientes} calificación(es) pendiente(s). Ve a tu historial
                para calificar.{' '}
                <Link className="font-semibold underline" to="/usuario/historial">
                  Ir al historial
                </Link>
              </div>
            ) : null}

            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-[24px] bg-slate-50 p-5">
                <p className="text-sm font-semibold text-slate-900">Como vendedor</p>
                <div className="mt-4">
                  {reputacion_vendedor.calificacion_promedio === null ? (
                    <p className="text-sm text-slate-500">Sin calificaciones aún</p>
                  ) : (
                    <Estrellas puntaje={reputacion_vendedor.calificacion_promedio} tamano="lg" />
                  )}
                </div>
                <div className="mt-5 space-y-2 text-sm text-slate-600">
                  <p>Total calificaciones: {reputacion_vendedor.total_calificaciones}</p>
                  <p>Total ventas: {reputacion_vendedor.total_ventas}</p>
                </div>
              </div>

              <div className="rounded-[24px] bg-slate-50 p-5">
                <p className="text-sm font-semibold text-slate-900">Como comprador</p>
                <div className="mt-4">
                  {reputacion_comprador.calificacion_promedio === null ? (
                    <p className="text-sm text-slate-500">Sin calificaciones aún</p>
                  ) : (
                    <Estrellas puntaje={reputacion_comprador.calificacion_promedio} tamano="lg" />
                  )}
                </div>
                <div className="mt-5 space-y-2 text-sm text-slate-600">
                  <p>Total calificaciones: {reputacion_comprador.total_calificaciones}</p>
                  <p>Total compras: {reputacion_comprador.total_compras}</p>
                </div>
              </div>
            </div>
          </section>

          <section className="rounded-[32px] border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-5 flex items-center justify-between gap-4">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-700">
                  Sección 3
                </p>
                <h2 className="mt-2 text-2xl font-black text-slate-900">Mis anuncios activos</h2>
              </div>

              {perfilPublico?.total_anuncios_activos > 6 ? (
                <button
                  className="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
                  onClick={() => setShowAllActive(true)}
                  type="button"
                >
                  {showAllActive ? 'Mostrando todos' : 'Ver todos'}
                </button>
              ) : null}
            </div>

            {accionError ? <p className="mb-4 text-sm text-rose-700">{accionError}</p> : null}
            {perfilPublicoError ? (
              <p className="mb-4 text-sm text-amber-700">{perfilPublicoError}</p>
            ) : null}

            {anunciosActivos.length === 0 ? (
              <div className="rounded-[24px] bg-slate-50 px-5 py-10 text-center text-sm text-slate-500">
                Aún no tienes anuncios activos.
              </div>
            ) : (
              <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
                {visibleActiveListings.map((anuncio) => (
                  <div className="space-y-3" key={anuncio.id}>
                    <AnuncioCard anuncio={anuncio} />
                    <div className="flex gap-3">
                      <Link
                        className="flex-1 rounded-2xl border border-slate-200 px-4 py-3 text-center text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
                        to={`/anuncios/${anuncio.id}/editar`}
                      >
                        Editar
                      </Link>
                      <button
                        className="flex-1 rounded-2xl border border-slate-200 px-4 py-3 text-sm font-semibold text-rose-600 transition hover:bg-rose-50"
                        disabled={loadingActionId === anuncio.id}
                        onClick={() => handleDesactivar(anuncio.id)}
                        type="button"
                      >
                        {loadingActionId === anuncio.id ? 'Desactivando...' : 'Desactivar'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="rounded-[32px] border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-5 flex items-center justify-between gap-4">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-700">
                  Sección 4
                </p>
                <h2 className="mt-2 text-2xl font-black text-slate-900">Mis anuncios inactivos</h2>
              </div>
            </div>

            {anunciosInactivos.length === 0 ? (
              <div className="rounded-[24px] bg-slate-50 px-5 py-10 text-center text-sm text-slate-500">
                No tienes anuncios inactivos.
              </div>
            ) : (
              <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
                {anunciosInactivos.map((anuncio) => (
                  <div className="space-y-3" key={anuncio.id}>
                    <AnuncioCard anuncio={anuncio} />
                    <button
                      className="w-full rounded-2xl border border-sky-200 bg-sky-50 px-4 py-3 text-sm font-semibold text-sky-700 transition hover:bg-sky-100 disabled:cursor-not-allowed disabled:opacity-60"
                      disabled={loadingActionId === anuncio.id}
                      onClick={() => handleReactivar(anuncio.id)}
                      type="button"
                    >
                      {loadingActionId === anuncio.id ? 'Reactivando...' : 'Reactivar'}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="rounded-[32px] border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-5">
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-700">
                Sección 5
              </p>
              <h2 className="mt-2 text-2xl font-black text-slate-900">Moderación de mis anuncios</h2>
            </div>

            {casosModeracion.length === 0 ? (
              <div className="rounded-[24px] bg-slate-50 px-5 py-10 text-center text-sm text-slate-500">
                No tienes anuncios reportados, bloqueados o con apelación registrada.
              </div>
            ) : (
              <div className="space-y-4">
                {casosModeracion.map((caso) => (
                  <article className="rounded-[24px] border border-slate-200 p-5" key={caso.anuncio_id}>
                    <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                      <div>
                        <p className="text-lg font-bold text-slate-900">{caso.titulo}</p>
                        <p className="mt-2 text-sm text-slate-600">
                          {caso.estado_caso === 'REPORTADO_EN_REVISION'
                            ? `Motivo del reporte: ${caso.motivo_reporte || 'En revision administrativa.'}`
                            : `Motivo del bloqueo: ${caso.motivo_bloqueo || 'Sin detalle administrativo.'}`}
                        </p>
                        <p className="mt-1 text-xs text-slate-500">
                          {caso.estado_caso === 'REPORTADO_EN_REVISION'
                            ? `Ultimo reporte el ${formatDateTime(caso.ultimo_reporte_at)}`
                            : `Bloqueado el ${formatDateTime(caso.bloqueado_at)}`}
                        </p>
                      </div>

                      <div className="flex flex-col items-start gap-2 md:items-end">
                        <span
                          className={`rounded-full px-3 py-1 text-xs font-semibold ${
                            caso.estado_caso === 'REPORTADO_EN_REVISION'
                              ? 'bg-amber-50 text-amber-700'
                              : 'bg-rose-50 text-rose-700'
                          }`}
                        >
                          {caso.estado_caso === 'REPORTADO_EN_REVISION' ? 'REPORTADO' : caso.estado_anuncio}
                        </span>
                        {caso.apelacion ? (
                          <span className="rounded-full bg-sky-50 px-3 py-1 text-xs font-semibold text-sky-700">
                            Apelación {caso.apelacion.estado.toLowerCase()}
                          </span>
                        ) : null}
                        <button
                          className="rounded-2xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
                          disabled={moderationLoading}
                          onClick={() => handleOpenModerationCase(caso.anuncio_id)}
                          type="button"
                        >
                          {moderationLoading ? 'Cargando...' : 'Ver caso'}
                        </button>
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </section>

          <section className="rounded-[32px] border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-5">
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-700">
                Sección 6
              </p>
              <h2 className="mt-2 text-2xl font-black text-slate-900">Accesos rápidos</h2>
            </div>

            <div className="grid gap-3">
              <Link
                className="rounded-2xl border border-slate-200 px-4 py-4 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
                to="/usuario/historial"
              >
                Mi historial de transacciones
              </Link>
              {publicProfileId ? (
                <Link
                  className="rounded-2xl border border-slate-200 px-4 py-4 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
                  to={`/usuarios/${publicProfileId}/perfil`}
                >
                  Mi perfil público
                </Link>
              ) : (
                <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-4 text-sm font-semibold text-amber-700">
                  Tu perfil público estará disponible cuando se identifique correctamente tu cuenta.
                </div>
              )}
              {esAdmin() ? (
                <Link
                  className="rounded-2xl border border-slate-200 px-4 py-4 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
                  to="/admin/reportados"
                >
                  Panel de administración
                </Link>
              ) : null}
            </div>
          </section>
        </main>
      </div>

      {editOpen ? (
        <Modal onClose={() => setEditOpen(false)} title="Editar perfil">
          <form className="space-y-6" onSubmit={handleSaveProfile}>
            <div className="grid gap-5 md:grid-cols-2">
              {perfil.es_tienda_verificada ? (
                <>
                  <div className="space-y-2 md:col-span-2">
                    <label className="text-sm font-medium text-slate-700" htmlFor="nombre_comercial">
                      Nombre comercial
                    </label>
                    <input
                      className={`w-full rounded-2xl border px-4 py-3 text-sm outline-none transition ${
                        editErrors.nombre_comercial
                          ? 'border-rose-400'
                          : 'border-slate-200 focus:border-sky-400'
                      }`}
                      id="nombre_comercial"
                      onChange={(event) => handleEditFieldChange('nombre_comercial', event.target.value)}
                      value={editForm.nombre_comercial}
                    />
                    {editErrors.nombre_comercial ? (
                      <p className="text-sm text-rose-600">{editErrors.nombre_comercial}</p>
                    ) : null}
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700" htmlFor="telefono">
                      Teléfono
                    </label>
                    <input
                      className={`w-full rounded-2xl border px-4 py-3 text-sm outline-none transition ${
                        editErrors.telefono ? 'border-rose-400' : 'border-slate-200 focus:border-sky-400'
                      }`}
                      id="telefono"
                      onChange={(event) => handleEditFieldChange('telefono', event.target.value)}
                      value={editForm.telefono}
                    />
                    {editErrors.telefono ? <p className="text-sm text-rose-600">{editErrors.telefono}</p> : null}
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700" htmlFor="correo_readonly">
                      Correo
                    </label>
                    <input
                      className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-500"
                      id="correo_readonly"
                      readOnly
                      value={perfil.correo}
                    />
                  </div>

                  <div className="space-y-2 md:col-span-2">
                    <label className="text-sm font-medium text-slate-700" htmlFor="direccion">
                      Dirección
                    </label>
                    <input
                      className={`w-full rounded-2xl border px-4 py-3 text-sm outline-none transition ${
                        editErrors.direccion ? 'border-rose-400' : 'border-slate-200 focus:border-sky-400'
                      }`}
                      id="direccion"
                      onChange={(event) => handleEditFieldChange('direccion', event.target.value)}
                      value={editForm.direccion}
                    />
                    {editErrors.direccion ? <p className="text-sm text-rose-600">{editErrors.direccion}</p> : null}
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700" htmlFor="ruc_readonly">
                      RUC
                    </label>
                    <input
                      className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-500"
                      id="ruc_readonly"
                      readOnly
                      value={perfil.tienda?.ruc ?? ''}
                    />
                  </div>

                  <div className="rounded-[24px] border border-amber-200 bg-amber-50 px-4 py-4 text-sm text-amber-800">
                    Correo y RUC forman parte de tus datos verificados. Si en el futuro necesitas cambiarlos,
                    conviene hacerlo con un flujo de revisión separado.
                  </div>
                </>
              ) : (
                <>
                  <div className="space-y-2 md:col-span-2">
                    <label className="text-sm font-medium text-slate-700" htmlFor="nombre">
                      Nombre
                    </label>
                    <input
                      className={`w-full rounded-2xl border px-4 py-3 text-sm outline-none transition ${
                        editErrors.nombre ? 'border-rose-400' : 'border-slate-200 focus:border-sky-400'
                      }`}
                      id="nombre"
                      onChange={(event) => handleEditFieldChange('nombre', event.target.value)}
                      value={editForm.nombre}
                    />
                    {editErrors.nombre ? <p className="text-sm text-rose-600">{editErrors.nombre}</p> : null}
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700" htmlFor="telefono">
                      Teléfono
                    </label>
                    <input
                      className={`w-full rounded-2xl border px-4 py-3 text-sm outline-none transition ${
                        editErrors.telefono ? 'border-rose-400' : 'border-slate-200 focus:border-sky-400'
                      }`}
                      id="telefono"
                      onChange={(event) => handleEditFieldChange('telefono', event.target.value)}
                      value={editForm.telefono}
                    />
                    {editErrors.telefono ? <p className="text-sm text-rose-600">{editErrors.telefono}</p> : null}
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700" htmlFor="correo_readonly">
                      Correo
                    </label>
                    <input
                      className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-500"
                      id="correo_readonly"
                      readOnly
                      value={perfil.correo}
                    />
                  </div>
                </>
              )}
            </div>

            {profileMessage ? <p className="text-sm text-rose-700">{profileMessage}</p> : null}

            <div className="flex flex-col gap-3 sm:flex-row">
              <button
                className="flex-1 rounded-2xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
                onClick={() => setEditOpen(false)}
                type="button"
              >
                Cancelar
              </button>
              <button
                className="flex-1 rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
                disabled={savingProfile}
                type="submit"
              >
                {savingProfile ? 'Guardando...' : 'Guardar cambios'}
              </button>
            </div>
          </form>
        </Modal>
      ) : null}

      {moderationModalOpen ? (
        <Modal onClose={() => setModerationModalOpen(false)} title="Caso de moderación">
          <div className="space-y-5">
            <div className="rounded-[24px] bg-slate-50 p-4 text-sm text-slate-700">
              <p className="font-semibold text-slate-900">{moderationDetail?.titulo}</p>
              <p className="mt-1">Anuncio #{moderationDetail?.anuncio_id}</p>
              <p className="mt-2">
                {moderationDetail?.estado_caso === 'REPORTADO_EN_REVISION'
                  ? 'Estado: Reportado y en revision administrativa.'
                  : `Bloqueado por: ${moderationDetail?.motivo_bloqueo || 'Sin detalle administrativo.'}`}
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-500">
                  Reportes recibidos
                </h3>
                <div className="mt-3 space-y-3">
                  {(moderationDetail?.reportes ?? []).map((reporte) => (
                    <article className="rounded-[20px] border border-slate-200 p-4" key={reporte.reporte_id}>
                      <div className="flex flex-wrap items-center justify-between gap-3">
                        <span className="rounded-full bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-700">
                          {reporte.motivo}
                        </span>
                        <span className="text-xs text-slate-500">
                          {formatDateTime(reporte.created_at)}
                        </span>
                      </div>
                      <div className="mt-3 rounded-2xl bg-slate-50 p-4 text-sm leading-6 text-slate-700">
                        {reporte.detalle?.trim() || 'El reporte no incluyó detalle adicional.'}
                      </div>
                      {reporte.evidencias?.length > 0 ? (
                        <div className="mt-3 grid gap-3 sm:grid-cols-2">
                          {reporte.evidencias.map((evidencia) => (
                            <a
                              className="block overflow-hidden rounded-2xl border border-slate-200"
                              href={formatImageUrl(evidencia.ruta_relativa)}
                              key={evidencia.id}
                              rel="noreferrer"
                              target="_blank"
                            >
                              <img
                                alt={`Evidencia reporte ${evidencia.id}`}
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
              </div>

              {moderationDetail?.apelacion_actual ? (
                <div className="rounded-[24px] border border-sky-200 bg-sky-50 p-4 text-sm text-sky-900">
                  <p className="font-semibold">
                    Tu apelación actual: {moderationDetail.apelacion_actual.estado}
                  </p>
                  <p className="mt-2 leading-6">{moderationDetail.apelacion_actual.mensaje}</p>
                  {moderationDetail.apelacion_actual.respuesta_admin ? (
                    <p className="mt-3 text-sm text-slate-700">
                      Respuesta admin: {moderationDetail.apelacion_actual.respuesta_admin}
                    </p>
                  ) : null}
                </div>
              ) : null}

              {moderationDetail?.estado_caso === 'REPORTADO_EN_REVISION' && !moderationDetail?.apelacion_actual ? (
                <div className="space-y-4 rounded-[24px] border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
                  <div>
                    <p className="font-semibold">Apelación disponible cuando exista bloqueo</p>
                    <p className="mt-2 leading-6">
                      Tu anuncio está en revisión administrativa. Ya puedes ver el motivo y las evidencias del
                      reporte, pero la apelación solo se habilita si el administrador decide bloquear el anuncio.
                    </p>
                  </div>
                  <button
                    className="w-full rounded-2xl bg-slate-300 px-4 py-3 text-sm font-semibold text-slate-600 opacity-90"
                    disabled
                    type="button"
                  >
                    Apelar anuncio
                  </button>
                </div>
              ) : null}

              {moderationDetail?.puede_apelar ? (
                <form className="space-y-4 rounded-[24px] border border-slate-200 p-4" onSubmit={handleSubmitAppeal}>
                  <div>
                    <h3 className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-500">
                      Presentar apelación
                    </h3>
                    <p className="mt-2 text-sm text-slate-600">
                      Explica por qué el anuncio debería rehabilitarse y adjunta hasta 3 imágenes.
                    </p>
                  </div>

                  <div className="space-y-2">
                    <textarea
                      className="min-h-32 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none transition focus:border-sky-400"
                      maxLength={1500}
                      onChange={(event) => setAppealMessage(event.target.value)}
                      placeholder="Describe tu descargo y aporta contexto verificable."
                      required
                      value={appealMessage}
                    />
                    <div className="flex justify-between text-xs text-slate-500">
                      <span>Mínimo 10 caracteres.</span>
                      <span>{appealMessage.length}/1500</span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <input
                      accept="image/png,image/jpeg"
                      className="block w-full text-sm text-slate-600 file:mr-4 file:rounded-full file:border-0 file:bg-slate-900 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-white"
                      multiple
                      onChange={(event) => setAppealFiles(Array.from(event.target.files ?? []).slice(0, 3))}
                      type="file"
                    />
                    <p className="text-xs text-slate-500">JPG o PNG, máximo 3 archivos de 5MB.</p>
                  </div>

                  {appealError ? <p className="text-sm text-rose-700">{appealError}</p> : null}
                  {appealSuccess ? <p className="text-sm text-emerald-700">{appealSuccess}</p> : null}

                  <button
                    className="w-full rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
                    disabled={submittingAppeal || appealMessage.trim().length < 10}
                    type="submit"
                  >
                    {submittingAppeal ? 'Enviando apelación...' : 'Enviar apelación'}
                  </button>
                </form>
              ) : null}
            </div>
          </div>
        </Modal>
      ) : null}
    </div>
  )
}

export default Panel

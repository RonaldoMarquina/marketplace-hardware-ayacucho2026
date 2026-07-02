import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../../api/axios'
import AnuncioCard from '../../components/ui/AnuncioCard'
import Estrellas from '../../components/ui/Estrellas'
import MetricaCard from '../../components/ui/MetricaCard'
import SkeletonCard from '../../components/ui/SkeletonCard'
import { useAuth } from '../../hooks/useAuth'
import { formatDate } from '../../utils/format'

const avatarPalette = [
  'from-sky-500 to-cyan-400',
  'from-emerald-500 to-lime-400',
  'from-amber-500 to-orange-400',
  'from-fuchsia-500 to-pink-400',
]

const getAvatarGradient = (name = '') =>
  avatarPalette[Math.abs(name.length) % avatarPalette.length]

const Panel = () => {
  const navigate = useNavigate()
  const { usuario, logout, esAdmin } = useAuth()
  const [panel, setPanel] = useState(null)
  const [perfilPublico, setPerfilPublico] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const [accionError, setAccionError] = useState('')
  const [perfilPublicoError, setPerfilPublicoError] = useState('')
  const [loadingActionId, setLoadingActionId] = useState(null)

  useEffect(() => {
    const fetchPanel = async () => {
      setCargando(true)
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
        } else {
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
        }
      } catch (requestError) {
        setError(
          requestError.response?.data?.mensaje ||
            requestError.response?.data?.message ||
            'No se pudo cargar el panel.'
        )
      } finally {
        setCargando(false)
      }
    }

    if (!usuario) {
      setCargando(false)
      return
    }

    fetchPanel()
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

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const handleDesactivar = async (anuncioId) => {
    setLoadingActionId(anuncioId)
    setAccionError('')

    try {
      await api.patch(`/anuncios/${anuncioId}/desactivar`)
      setPerfilPublico((current) =>
        current
          ? {
              ...current,
              anuncios_activos: current.anuncios_activos.filter((item) => item.id !== anuncioId),
              total_anuncios_activos: Math.max(0, current.total_anuncios_activos - 1),
            }
          : current,
      )
      setPanel((current) =>
        current
          ? {
              ...current,
              anuncios: {
                ...current.anuncios,
                activos: {
                  ...current.anuncios.activos,
                  total: Math.max(0, current.anuncios.activos.total - 1),
                  disponibles:
                    current.anuncios.activos.disponibles === null
                      ? null
                      : current.anuncios.activos.disponibles + 1,
                },
                inactivos: {
                  total: current.anuncios.inactivos.total + 1,
                },
              },
            }
          : current,
      )
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
      setPanel((current) =>
        current
          ? {
              ...current,
              anuncios: {
                ...current.anuncios,
                activos: {
                  ...current.anuncios.activos,
                  total: current.anuncios.activos.total + 1,
                  disponibles:
                    current.anuncios.activos.disponibles === null
                      ? null
                      : Math.max(0, current.anuncios.activos.disponibles - 1),
                },
                inactivos: {
                  total: Math.max(0, current.anuncios.inactivos.total - 1),
                  items: current.anuncios.inactivos.items.filter((item) => item.id !== anuncioId),
                },
              },
            }
          : current,
      )
      setPerfilPublico((current) => {
        if (!current) return current

        const reactivated = panel?.anuncios?.inactivos?.items?.find((item) => item.id === anuncioId)
        if (!reactivated) {
          return current
        }

        return {
          ...current,
          anuncios_activos: [
            {
              ...reactivated,
              vendedor_nombre: current.nombre,
              es_tienda_verificada: current.es_tienda_verificada,
            },
            ...current.anuncios_activos,
          ],
          total_anuncios_activos: current.total_anuncios_activos + 1,
        }
      })
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

          <button
            className="mt-8 w-full rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
            onClick={handleLogout}
            type="button"
          >
            Cerrar sesión
          </button>
        </aside>

        <main className="space-y-6">
          <section className="rounded-[32px] border border-slate-200 bg-white p-6 shadow-sm">
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
                  className="cursor-not-allowed rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-400"
                  disabled
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
                  className="cursor-not-allowed rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-400"
                  disabled
                  type="button"
                >
                  Ver todos
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
                {anunciosActivos.slice(0, 6).map((anuncio) => (
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
              <h2 className="mt-2 text-2xl font-black text-slate-900">Accesos rápidos</h2>
            </div>

            <div className="grid gap-3">
              <Link
                className="rounded-2xl border border-slate-200 px-4 py-4 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
                to="/usuario/historial"
              >
                Mi historial de transacciones
              </Link>
              <Link
                className="rounded-2xl border border-slate-200 px-4 py-4 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
                to={`/usuarios/${usuario?.id}/perfil`}
              >
                Mi perfil público
              </Link>
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
    </div>
  )
}

export default Panel

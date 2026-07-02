import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import api from '../../api/axios'
import AnuncioCard from '../../components/ui/AnuncioCard'
import Estrellas from '../../components/ui/Estrellas'
import SkeletonCard from '../../components/ui/SkeletonCard'
import { formatDate } from '../../utils/format'

const avatarPalette = [
  'from-sky-500 to-cyan-400',
  'from-emerald-500 to-lime-400',
  'from-amber-500 to-orange-400',
  'from-fuchsia-500 to-pink-400',
]

const getAvatarGradient = (name = '') =>
  avatarPalette[Math.abs(name.length) % avatarPalette.length]

const Perfil = () => {
  const { id } = useParams()
  const [perfil, setPerfil] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchPerfil = async () => {
      setCargando(true)
      setError('')

      try {
        const response = await api.get(`/usuarios/${id}/perfil`)
        setPerfil(response.data.data)
      } catch (requestError) {
        if (requestError.response?.status === 404) {
          setError('NOT_FOUND')
        } else {
          setError(
            requestError.response?.data?.mensaje ||
              requestError.response?.data?.message ||
              'No se pudo cargar el perfil.'
          )
        }
      } finally {
        setCargando(false)
      }
    }

    fetchPerfil()
  }, [id])

  const anuncios = useMemo(
    () =>
      (perfil?.anuncios_activos ?? []).map((anuncio) => ({
        ...anuncio,
        vendedor_nombre: perfil?.nombre,
        es_tienda_verificada: perfil?.es_tienda_verificada,
      })),
    [perfil],
  )

  if (cargando) {
    return (
      <div className="min-h-screen bg-[linear-gradient(180deg,#f8fafc_0%,#ecfeff_35%,#f8fafc_100%)] px-4 py-8">
        <div className="mx-auto max-w-6xl space-y-6">
          <div className="rounded-[32px] border border-slate-200 bg-white p-8 shadow-sm">
            <div className="h-28 w-28 animate-pulse rounded-full bg-slate-200" />
            <div className="mt-5 h-8 w-72 animate-pulse rounded-full bg-slate-200" />
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            {Array.from({ length: 2 }, (_, index) => (
              <div className="h-40 animate-pulse rounded-[24px] bg-slate-200" key={index} />
            ))}
          </div>
          <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
            {Array.from({ length: 3 }, (_, index) => (
              <SkeletonCard key={index} />
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (error === 'NOT_FOUND') {
    return (
      <div className="px-4 py-12">
        <div className="mx-auto max-w-xl rounded-[32px] border border-slate-200 bg-white p-8 text-center shadow-sm">
          <h1 className="text-3xl font-black text-slate-900">Usuario no encontrado</h1>
          <p className="mt-3 text-sm text-slate-600">
            El perfil solicitado no existe o ya no está disponible públicamente.
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

  if (!perfil) {
    return <div className="px-4 py-12 text-center text-sm text-rose-700">{error}</div>
  }

  return (
    <div className="min-h-screen bg-[linear-gradient(180deg,#f8fafc_0%,#ecfeff_35%,#f8fafc_100%)] px-4 py-8">
      <div className="mx-auto max-w-6xl space-y-6">
        <header className="rounded-[32px] border border-slate-200 bg-white p-8 shadow-sm">
          <div className="flex flex-col gap-6 md:flex-row md:items-center">
            <div
              className={`flex h-28 w-28 items-center justify-center rounded-full bg-gradient-to-br ${getAvatarGradient(
                perfil.nombre,
              )} text-5xl font-black text-white`}
            >
              {perfil.nombre?.charAt(0)?.toUpperCase() ?? 'U'}
            </div>

            <div>
              <div className="flex flex-wrap items-center gap-3">
                <h1 className="text-4xl font-black tracking-tight text-slate-900">{perfil.nombre}</h1>
                {perfil.es_tienda_verificada ? (
                  <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                    ✓ Tienda Verificada
                  </span>
                ) : null}
              </div>

              {perfil.tienda ? (
                <div className="mt-3 text-sm text-slate-600">
                  <p className="font-semibold text-slate-900">{perfil.tienda.nombre_comercial}</p>
                  <p className="mt-1">{perfil.tienda.direccion}</p>
                </div>
              ) : null}

              <p className="mt-4 text-sm text-slate-500">
                Miembro desde {formatDate(perfil.miembro_desde)}
              </p>
            </div>
          </div>
        </header>

        <section className="grid gap-4 md:grid-cols-2">
          <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-sm font-semibold text-slate-900">Como vendedor</p>
            <div className="mt-4">
              {perfil.reputacion_vendedor.calificacion_promedio === null ? (
                <p className="text-sm text-slate-500">Sin calificaciones aún</p>
              ) : (
                <Estrellas puntaje={perfil.reputacion_vendedor.calificacion_promedio} tamano="lg" />
              )}
            </div>
            <div className="mt-5 space-y-2 text-sm text-slate-600">
              <p>Total calificaciones: {perfil.reputacion_vendedor.total_calificaciones}</p>
              <p>Total ventas: {perfil.reputacion_vendedor.total_ventas}</p>
            </div>
          </div>

          <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-sm font-semibold text-slate-900">Como comprador</p>
            <div className="mt-4">
              {perfil.reputacion_comprador.calificacion_promedio === null ? (
                <p className="text-sm text-slate-500">Sin calificaciones aún</p>
              ) : (
                <Estrellas puntaje={perfil.reputacion_comprador.calificacion_promedio} tamano="lg" />
              )}
            </div>
            <div className="mt-5 space-y-2 text-sm text-slate-600">
              <p>Total calificaciones: {perfil.reputacion_comprador.total_calificaciones}</p>
              <p>Total compras: {perfil.reputacion_comprador.total_compras}</p>
            </div>
          </div>
        </section>

        <section className="rounded-[32px] border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-5">
            <h2 className="text-2xl font-black text-slate-900">Anuncios de {perfil.nombre}</h2>
          </div>

          {anuncios.length === 0 ? (
            <div className="rounded-[24px] bg-slate-50 px-5 py-10 text-center text-sm text-slate-500">
              Este usuario no tiene anuncios activos
            </div>
          ) : (
            <>
              <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
                {anuncios.map((anuncio) => (
                  <AnuncioCard anuncio={anuncio} key={anuncio.id} />
                ))}
              </div>

              {perfil.total_anuncios_activos > 10 ? (
                <p className="mt-5 text-sm text-slate-500">
                  Y {perfil.total_anuncios_activos - 10} anuncios más
                </p>
              ) : null}
            </>
          )}
        </section>
      </div>
    </div>
  )
}

export default Perfil

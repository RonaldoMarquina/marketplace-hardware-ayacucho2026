import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import api from '../../api/axios'
import AnuncioCard from '../../components/ui/AnuncioCard'
import Paginacion from '../../components/ui/Paginacion'
import SkeletonCard from '../../components/ui/SkeletonCard'

const skeletonItems = Array.from({ length: 8 }, (_, index) => index)

const Feed = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const [anuncios, setAnuncios] = useState([])
  const [paginacion, setPaginacion] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')

  const page = Math.max(1, Number(searchParams.get('page') || '1'))

  useEffect(() => {
    const fetchFeed = async () => {
      setCargando(true)
      setError('')

      try {
        const response = await api.get('/anuncios', {
          params: { page, limit: 20 },
        })

        setAnuncios(response.data.data ?? [])
        setPaginacion(response.data.paginacion ?? null)
      } catch (requestError) {
        setError(
          requestError.response?.data?.mensaje ||
            requestError.response?.data?.message ||
            'No se pudo cargar el feed.'
        )
      } finally {
        setCargando(false)
      }
    }

    fetchFeed()
  }, [page])

  const handlePageChange = (nextPage) => {
    setSearchParams(nextPage > 1 ? { page: String(nextPage) } : {})
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <div className="min-h-screen bg-[linear-gradient(180deg,#f8fafc_0%,#eef2ff_38%,#f8fafc_100%)] px-4 py-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-8 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-700">
              Marketplace
            </p>
            <h1 className="mt-2 text-4xl font-black tracking-tight text-slate-900">
              Hardware en Ayacucho
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">
              Explora componentes, perifericos y setups completos publicados por usuarios y
              tiendas verificadas de la comunidad.
            </p>
          </div>
        </div>

        {error ? (
          <div className="rounded-[28px] border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-700">
            {error}
          </div>
        ) : null}

        {cargando ? (
          <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
            {skeletonItems.map((item) => (
              <SkeletonCard key={item} />
            ))}
          </div>
        ) : anuncios.length === 0 ? (
          <div className="rounded-[32px] border border-slate-200 bg-white px-6 py-14 text-center shadow-sm">
            <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-slate-100 text-slate-400">
              <svg
                aria-hidden="true"
                className="h-10 w-10"
                fill="none"
                stroke="currentColor"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="1.6"
                viewBox="0 0 24 24"
              >
                <path d="M4 6.5h16A1.5 1.5 0 0 1 21.5 8v8A1.5 1.5 0 0 1 20 17.5H4A1.5 1.5 0 0 1 2.5 16V8A1.5 1.5 0 0 1 4 6.5Z" />
                <path d="m5 15 4-4 3 3 3-3 4 4" />
                <circle cx="9" cy="9.5" r="1.2" />
              </svg>
            </div>
            <h2 className="mt-6 text-2xl font-bold text-slate-900">
              No hay anuncios disponibles por el momento
            </h2>
            <p className="mt-3 text-sm text-slate-600">
              Vuelve pronto o publica el primer producto de esta categoría local.
            </p>
          </div>
        ) : (
          <>
            <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
              {anuncios.map((anuncio) => (
                <AnuncioCard anuncio={anuncio} key={anuncio.id} />
              ))}
            </div>

            <Paginacion onCambiarPagina={handlePageChange} paginacion={paginacion} />
          </>
        )}
      </div>
    </div>
  )
}

export default Feed

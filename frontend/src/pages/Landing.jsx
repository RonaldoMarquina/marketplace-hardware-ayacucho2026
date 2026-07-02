import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api/axios'
import AnuncioCard from '../components/ui/AnuncioCard'
import SkeletonCard from '../components/ui/SkeletonCard'

const categories = [
  {
    key: 'COMPONENTES',
    label: 'COMPONENTES',
    icon: (
      <svg aria-hidden="true" className="h-10 w-10" fill="none" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24">
        <rect height="12" rx="2" width="12" x="6" y="6" />
        <path d="M9 2v3M15 2v3M9 19v3M15 19v3M22 9h-3M22 15h-3M5 9H2M5 15H2" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    key: 'PERIFERICOS',
    label: 'PERIFERICOS',
    icon: (
      <svg aria-hidden="true" className="h-10 w-10" fill="none" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24">
        <rect height="7" rx="2" width="18" x="3" y="9" />
        <path d="M8 6.5h8M7 12h.01M10 12h.01M13 12h.01M16 12h.01" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    key: 'MONITORES',
    label: 'MONITORES',
    icon: (
      <svg aria-hidden="true" className="h-10 w-10" fill="none" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24">
        <rect height="11" rx="2" width="18" x="3" y="4.5" />
        <path d="M9 20h6M12 15.5V20" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    key: 'PORTATILES',
    label: 'PORTATILES',
    icon: (
      <svg aria-hidden="true" className="h-10 w-10" fill="none" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24">
        <rect height="10" rx="2" width="14" x="5" y="5" />
        <path d="M2.5 18.5h19" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    key: 'GABINETES',
    label: 'GABINETES',
    icon: (
      <svg aria-hidden="true" className="h-10 w-10" fill="none" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24">
        <rect height="16" rx="2" width="10" x="7" y="4" />
        <circle cx="12" cy="9" r="1" />
        <path d="M10 14h4" strokeLinecap="round" />
      </svg>
    ),
  },
]

const benefits = [
  {
    title: 'Vendedores locales',
    description: 'Vendedores locales y comercio mas cercano.',
    accent: 'text-rose-500',
    icon: (
      <svg aria-hidden="true" className="h-11 w-11" fill="none" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24">
        <path d="M12 21s7-4.35 7-11a7 7 0 1 0-14 0c0 6.65 7 11 7 11Z" />
        <circle cx="12" cy="10" r="2.5" />
      </svg>
    ),
  },
  {
    title: 'Contacto directo',
    description: 'Contacta directo, sin comisiones ni costos extra por anuncio.',
    accent: 'text-emerald-500',
    icon: (
      <svg aria-hidden="true" className="h-11 w-11" fill="none" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24">
        <path d="M20 11.5A8.5 8.5 0 0 1 7.6 19l-3.1 1 1-3.1A8.5 8.5 0 1 1 20 11.5Z" />
        <path d="M9.5 9.5c.4 1.6 2.4 3.6 4 4" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    title: 'Tiendas verificadas',
    description: 'Tiendas verificadas y mayor confianza para tus compras.',
    accent: 'text-sky-500',
    icon: (
      <svg aria-hidden="true" className="h-11 w-11" fill="none" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24">
        <path d="m9 12 2 2 4-4" strokeLinecap="round" strokeLinejoin="round" />
        <circle cx="12" cy="12" r="8.5" />
      </svg>
    ),
  },
]

const SectionShell = ({ children, className = '' }) => (
  <section className={`rounded-[24px] border border-white/8 p-5 md:p-6 ${className}`}>{children}</section>
)

const Landing = () => {
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const [recentAds, setRecentAds] = useState([])
  const [loadingRecentAds, setLoadingRecentAds] = useState(true)
  const [recentAdsError, setRecentAdsError] = useState('')
  const [activeListings, setActiveListings] = useState(0)

  useEffect(() => {
    const fetchRecentAds = async () => {
      setLoadingRecentAds(true)
      setRecentAdsError('')

      try {
        const response = await api.get('/anuncios', {
          params: { page: 1, limit: 8 },
        })

        setRecentAds(response.data.data ?? [])
        setActiveListings(response.data.paginacion?.total ?? 0)
      } catch (requestError) {
        setRecentAds([])
        setActiveListings(0)
        setRecentAdsError(
          requestError.response?.data?.mensaje ||
            requestError.response?.data?.message ||
            'No se pudieron cargar las publicaciones recientes.'
        )
      } finally {
        setLoadingRecentAds(false)
      }
    }

    fetchRecentAds()
  }, [])

  const shouldShowRecentAds = useMemo(
    () => loadingRecentAds || recentAds.length > 0,
    [loadingRecentAds, recentAds.length],
  )

  const handleSearch = (event) => {
    event.preventDefault()
    const trimmed = query.trim()
    navigate(trimmed ? `/buscar?q=${encodeURIComponent(trimmed)}` : '/buscar')
  }

  return (
    <div className="min-h-screen bg-[#171c27] px-3 pb-3 pt-4 text-white md:px-4">
      <div className="mx-auto max-w-[1500px] rounded-[28px] border border-white/8 bg-[linear-gradient(180deg,#1b2230_0%,#202837_100%)] p-3 shadow-[0_30px_100px_-55px_rgba(0,0,0,0.85)]">
        <div className="space-y-3">
          <SectionShell className="bg-[radial-gradient(circle_at_top_left,#134e4a_0%,transparent_35%),linear-gradient(135deg,#111827_0%,#0f172a_100%)] shadow-inner">
            <div className="grid gap-8 xl:grid-cols-[1.1fr_0.9fr] xl:items-center">
              <div>
                <h1 className="max-w-lg text-4xl font-black leading-tight text-white md:text-5xl">
                  El marketplace de hardware para Ayacucho
                </h1>
                <p className="mt-5 max-w-xl text-sm leading-7 text-slate-300 md:text-base">
                  Compra y vende componentes, perifericos y equipos de tecnologia con vendedores de tu region.
                </p>

                <div className="mt-7 flex flex-col gap-3 sm:flex-row">
                  <button
                    className="inline-flex items-center justify-center rounded-full bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
                    onClick={() => navigate('/feed')}
                    type="button"
                  >
                    Explorar anuncios
                  </button>
                  <button
                    className="inline-flex items-center justify-center rounded-full border border-cyan-400/45 px-5 py-3 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-400/10"
                    onClick={() => navigate('/login')}
                    type="button"
                  >
                    Publicar anuncio
                  </button>
                </div>

                <form className="mt-7 rounded-[22px] border border-white/10 bg-white/6 p-3 backdrop-blur" onSubmit={handleSearch}>
                  <label className="mb-3 block text-sm font-semibold text-slate-200" htmlFor="landing-search">
                    Quiese estas buscando?
                  </label>
                  <div className="flex flex-col gap-3 sm:flex-row">
                    <input
                      className="w-full rounded-2xl border border-white/10 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-cyan-400"
                      id="landing-search"
                      onChange={(event) => setQuery(event.target.value)}
                      placeholder="Que estas buscando? Ej: RTX 4070, Teclado mecanico..."
                      type="text"
                      value={query}
                    />
                    <button
                      className="rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
                      type="submit"
                    >
                      Buscar
                    </button>
                  </div>
                </form>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="rounded-[24px] border border-white/10 bg-white/10 p-5 backdrop-blur">
                  <p className="text-sm font-semibold uppercase tracking-[0.16em] text-sky-200">Publicaciones activas</p>
                  <p className="mt-4 text-5xl font-black text-white">{activeListings}</p>
                  <p className="mt-3 text-sm leading-6 text-slate-300">
                    Anuncios visibles hoy para compradores de Ayacucho y alrededores.
                  </p>
                </div>
                <div className="rounded-[24px] border border-white/10 bg-white/10 p-5 backdrop-blur">
                  <p className="text-sm font-semibold uppercase tracking-[0.16em] text-sky-200">Tiendas verificadas</p>
                  <p className="mt-4 text-2xl font-black text-white">Compra con mas confianza</p>
                  <p className="mt-3 text-sm leading-6 text-slate-300">
                    Identifica vendedores verificados y habla directo con ellos por WhatsApp.
                  </p>
                </div>
                <div className="rounded-[24px] border border-white/10 bg-white/10 p-5 backdrop-blur sm:col-span-2">
                  <p className="text-sm font-semibold uppercase tracking-[0.16em] text-sky-200">Rapido y local</p>
                  <p className="mt-4 text-2xl font-black text-white">Componentes, perifericos y equipos</p>
                  <p className="mt-3 text-sm leading-6 text-slate-300">
                    Desde procesadores y GPUs hasta escritorios gamer, todo en una sola vitrina regional.
                  </p>
                </div>
              </div>
            </div>
          </SectionShell>

          <SectionShell className="bg-[#161d29]">
            <div className="mb-5 flex items-center justify-between gap-4">
              <h2 className="text-3xl font-black text-white">Explora por categoria</h2>
              <Link className="text-sm font-semibold text-cyan-300 transition hover:text-cyan-200" to="/buscar">
                Ver todas
              </Link>
            </div>

            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
              {categories.map((category) => (
                <Link
                  className="group rounded-[22px] border border-white/8 bg-[#f8fafc] p-5 text-slate-900 transition hover:-translate-y-1 hover:border-cyan-300/60 hover:shadow-lg"
                  key={category.key}
                  to={`/buscar?categoria=${category.key}`}
                >
                  <div className="text-slate-700 transition group-hover:text-cyan-600">{category.icon}</div>
                  <p className="mt-4 text-sm font-black tracking-[0.08em] text-slate-900">{category.label}</p>
                </Link>
              ))}
            </div>
          </SectionShell>

          <SectionShell className="bg-[linear-gradient(180deg,#f8fafc_0%,#eef6ff_100%)] text-slate-900">
            <h2 className="mb-5 text-3xl font-black text-slate-900">Publicaciones recientes</h2>

            {recentAdsError ? (
              <div className="rounded-[18px] border border-rose-300/20 bg-rose-500/10 px-4 py-4 text-sm text-rose-200">
                {recentAdsError}
              </div>
            ) : shouldShowRecentAds ? (
              <>
                {loadingRecentAds ? (
                  <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                    {Array.from({ length: 8 }, (_, index) => (
                      <SkeletonCard key={index} />
                    ))}
                  </div>
                ) : (
                  <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                    {recentAds.map((anuncio) => (
                      <div className="[&_.group]:rounded-[20px] [&_.group]:border-slate-200 [&_.group]:bg-white [&_.group]:shadow-sm [&_.group:hover]:shadow-lg [&_.group_h3]:min-h-[2.7rem] [&_.group_h3]:text-sm" key={anuncio.id}>
                        <AnuncioCard anuncio={anuncio} />
                      </div>
                    ))}
                  </div>
                )}

                {!loadingRecentAds ? (
                  <div className="mt-6 text-center">
                    <Link
                      className="inline-flex rounded-full bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
                      to="/feed"
                    >
                      Ver todos los anuncios
                    </Link>
                  </div>
                ) : null}
              </>
            ) : null}
          </SectionShell>

          <div className="grid gap-3 xl:grid-cols-[1.25fr_0.75fr]">
            <SectionShell className="bg-[#161d29]">
              <h2 className="text-3xl font-black text-white">Por que HardwareAyacucho?</h2>

              <div className="mt-5 grid gap-3 sm:grid-cols-3">
                {benefits.map((benefit) => (
                  <article className="rounded-[22px] bg-[#f8fafc] p-4 text-center text-slate-900" key={benefit.title}>
                    <div className={`mx-auto w-fit ${benefit.accent}`}>{benefit.icon}</div>
                    <h3 className="mt-3 text-sm font-black">{benefit.title}</h3>
                    <p className="mt-2 text-xs leading-5 text-slate-600">{benefit.description}</p>
                  </article>
                ))}
              </div>
            </SectionShell>

            <SectionShell className="bg-[linear-gradient(135deg,#d1fae5_0%,#e0f2fe_55%,#cffafe_100%)] text-slate-900">
              <h2 className="text-center text-3xl font-black">Estadisticas</h2>

              <div className="mt-6 grid gap-5 text-center">
                <div>
                  <p className="text-4xl font-black">{activeListings}</p>
                  <p className="mt-2 text-sm text-slate-700">Anuncios activos</p>
                </div>
                <div>
                  <p className="text-4xl font-black">10</p>
                  <p className="mt-2 text-sm text-slate-700">Categorias disponibles</p>
                </div>
                <div>
                  <p className="text-4xl font-black">Ayacucho</p>
                  <p className="mt-2 text-sm text-slate-700">Peru</p>
                </div>
              </div>
            </SectionShell>
          </div>

          <SectionShell className="bg-[radial-gradient(circle_at_bottom_left,#115e59_0%,transparent_35%),linear-gradient(135deg,#111827_0%,#172033_100%)]">
            <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr] xl:items-center">
              <div>
                <h2 className="text-3xl font-black text-white">Tienes algo para vender?</h2>
                <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300">
                  Publica tu anuncio gratis en minutos y llega a compradores de Ayacucho.
                </p>
              </div>

              <div className="flex flex-col gap-3 sm:flex-row xl:justify-end">
                <Link
                  className="inline-flex items-center justify-center rounded-full bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
                  to="/register"
                >
                  Crear cuenta gratis
                </Link>
                <Link
                  className="inline-flex items-center justify-center rounded-full border border-cyan-400/35 px-5 py-3 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-400/10"
                  to="/login"
                >
                  Ya tengo cuenta
                </Link>
              </div>
            </div>
          </SectionShell>

          <SectionShell className="bg-[#161d29]">
            <Link className="text-3xl font-black tracking-tight text-white" to="/">
              HardwareAyacucho
            </Link>
            <p className="mt-3 text-sm leading-6 text-slate-300">
              El marketplace de hardware de Ayacucho, Peru.
            </p>

            <div className="mt-5 flex flex-wrap gap-x-5 gap-y-3 text-sm text-slate-300">
              <Link className="transition hover:text-cyan-300" to="/feed">Explorar anuncios</Link>
              <Link className="transition hover:text-cyan-300" to="/login">Publicar anuncio</Link>
              <Link className="transition hover:text-cyan-300" to="/register">Crear cuenta</Link>
              <Link className="transition hover:text-cyan-300" to="/register/tienda">Registrar tienda</Link>
            </div>

            <p className="mt-6 text-xs text-slate-400">
              © 2026 HardwareAyacucho. Proyecto universitario - UNSCH.
            </p>
          </SectionShell>
        </div>
      </div>
    </div>
  )
}

export default Landing

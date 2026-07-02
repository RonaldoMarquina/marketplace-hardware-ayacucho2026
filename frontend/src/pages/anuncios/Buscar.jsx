import { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import api from '../../api/axios'
import AnuncioCard from '../../components/ui/AnuncioCard'
import Paginacion from '../../components/ui/Paginacion'
import SkeletonCard from '../../components/ui/SkeletonCard'
import {
  CATEGORIAS_SUBCATEGORIAS,
  getSpecLabel,
  getSubcategoriesForCategory,
  getTaxonomyLabel,
  normalizeTaxonomyValue,
} from '../../utils/especificaciones'

const skeletonItems = Array.from({ length: 8 }, (_, index) => index)

const emptyPair = () => ({ id: crypto.randomUUID(), key: '', value: '' })

const readSpecsFromParams = (params) => {
  const entries = []

  for (const [key, value] of params.entries()) {
    if (key.startsWith('specs[') && key.endsWith(']')) {
      const specKey = key.slice(6, -1)
      entries.push({
        id: crypto.randomUUID(),
        key: specKey,
        value,
      })
    }
  }

  return entries.length > 0 ? entries : [emptyPair()]
}

const getFormFromParams = (params) => ({
  q: params.get('q') ?? '',
  categoria: params.get('categoria') ?? '',
  subcategoria: params.get('subcategoria') ?? '',
  condicion: params.get('condicion') ?? '',
  precio_min: params.get('precio_min') ?? '',
  precio_max: params.get('precio_max') ?? '',
  order_by: params.get('order_by') ?? 'reciente',
})

const buildSearchParamsFromState = (form, specPairs, page = 1) => {
  const params = new URLSearchParams()

  ;['q', 'categoria', 'subcategoria', 'condicion', 'precio_min', 'precio_max', 'order_by'].forEach(
    (key) => {
      const value = form[key]
      if (value) {
        params.set(key, value)
      }
    },
  )

  specPairs.forEach((pair) => {
    if (pair.key.trim() && pair.value.trim()) {
      params.set(`specs[${pair.key.trim()}]`, pair.value.trim())
    }
  })

  if (page > 1) {
    params.set('page', String(page))
  }

  return params
}

const buildChips = (filters) => {
  const chips = []

  Object.entries(filters ?? {}).forEach(([key, value]) => {
    if (key === 'specs' && value) {
      Object.entries(value).forEach(([specKey, specValue]) => {
        chips.push({
          id: `spec-${specKey}`,
          label: `${getSpecLabel(specKey)}: ${specValue}`,
          type: 'spec',
          key: specKey,
        })
      })
      return
    }

    if (!value || key === 'order_by') {
      return
    }

    const labelMap = {
      q: `Búsqueda: ${value}`,
      categoria: `Categoría: ${getTaxonomyLabel(value)}`,
      subcategoria: `Subcategoría: ${getTaxonomyLabel(value)}`,
      condicion: `Condición: ${getTaxonomyLabel(value)}`,
      precio_min: `Desde S/ ${value}`,
      precio_max: `Hasta S/ ${value}`,
    }

    chips.push({
      id: key,
      label: labelMap[key] ?? `${key}: ${value}`,
      type: 'field',
      key,
    })
  })

  return chips
}

const Buscar = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const [form, setForm] = useState(getFormFromParams(searchParams))
  const [specPairs, setSpecPairs] = useState(readSpecsFromParams(searchParams))
  const [resultados, setResultados] = useState([])
  const [paginacion, setPaginacion] = useState(null)
  const [filtrosAplicados, setFiltrosAplicados] = useState({})
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const [filterError, setFilterError] = useState('')
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false)

  const subcategorias = useMemo(
    () => getSubcategoriesForCategory(form.categoria),
    [form.categoria],
  )

  useEffect(() => {
    setForm(getFormFromParams(searchParams))
    setSpecPairs(readSpecsFromParams(searchParams))
  }, [searchParams])

  useEffect(() => {
    const fetchSearchResults = async () => {
      setCargando(true)
      setError('')

      const requestParams = Object.fromEntries(searchParams.entries())

      try {
        const response = await api.get('/anuncios/buscar', {
          params: requestParams,
        })

        setResultados(response.data.data ?? [])
        setPaginacion(response.data.paginacion ?? null)
        setFiltrosAplicados(response.data.filtros_aplicados ?? {})
      } catch (requestError) {
        setResultados([])
        setPaginacion(null)
        setFiltrosAplicados({})
        setError(
          requestError.response?.data?.mensaje ||
            requestError.response?.data?.message ||
            'No se pudo realizar la búsqueda.'
        )
      } finally {
        setCargando(false)
      }
    }

    fetchSearchResults()
  }, [searchParams])

  const handleFieldChange = (event) => {
    const { name, value } = event.target

    setForm((current) => {
      if (name === 'categoria') {
        return {
          ...current,
          categoria: normalizeTaxonomyValue(value),
          subcategoria: '',
        }
      }

      return {
        ...current,
        [name]: ['categoria', 'subcategoria', 'condicion'].includes(name)
          ? normalizeTaxonomyValue(value)
          : value,
      }
    })

    if (name === 'categoria') {
      setSpecPairs([emptyPair()])
    }

    setFilterError('')
  }

  const updateSpecPair = (id, field, value) => {
    setSpecPairs((current) =>
      current.map((pair) =>
        pair.id === id
          ? {
              ...pair,
              [field]: field === 'key' ? value.trim().toLowerCase().replace(/\s+/g, '_') : value,
            }
          : pair,
      ),
    )
  }

  const addSpecPair = () => {
    setSpecPairs((current) => (current.length >= 10 ? current : [...current, emptyPair()]))
  }

  const removeSpecPair = (id) => {
    setSpecPairs((current) => {
      const nextPairs = current.filter((pair) => pair.id !== id)
      return nextPairs.length > 0 ? nextPairs : [emptyPair()]
    })
  }

  const handleSubmit = (event) => {
    event.preventDefault()

    if (
      form.precio_min &&
      form.precio_max &&
      Number(form.precio_min) > Number(form.precio_max)
    ) {
      setFilterError('El precio mínimo no puede ser mayor que el precio máximo.')
      return
    }

    setFilterError('')
    setMobileFiltersOpen(false)
    setSearchParams(buildSearchParamsFromState(form, specPairs))
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const clearFilters = () => {
    setForm({
      q: '',
      categoria: '',
      subcategoria: '',
      condicion: '',
      precio_min: '',
      precio_max: '',
      order_by: 'reciente',
    })
    setSpecPairs([emptyPair()])
    setFilterError('')
    setSearchParams({})
  }

  const handleRemoveChip = (chip) => {
    const params = new URLSearchParams(searchParams)

    if (chip.type === 'spec') {
      params.delete(`specs[${chip.key}]`)
    } else {
      params.delete(chip.key)
    }

    params.delete('page')
    setSearchParams(params)
  }

  const handlePageChange = (nextPage) => {
    const params = new URLSearchParams(searchParams)

    if (nextPage > 1) {
      params.set('page', String(nextPage))
    } else {
      params.delete('page')
    }

    setSearchParams(params)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const chips = buildChips(filtrosAplicados)

  const FiltersContent = (
    <form className="space-y-5" onSubmit={handleSubmit}>
      <div className="space-y-2">
        <label className="text-sm font-medium text-slate-700" htmlFor="q">
          Búsqueda
        </label>
        <input
          className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-sky-400"
          id="q"
          name="q"
          onChange={handleFieldChange}
          placeholder="Ej. Ryzen, monitor 144hz, RTX"
          type="text"
          value={form.q}
        />
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium text-slate-700" htmlFor="categoria">
          Categoría
        </label>
        <select
          className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-sky-400"
          id="categoria"
          name="categoria"
          onChange={handleFieldChange}
          value={form.categoria}
        >
          <option value="">Todas</option>
          {Object.keys(CATEGORIAS_SUBCATEGORIAS).map((categoria) => (
            <option key={categoria} value={categoria}>
              {getTaxonomyLabel(categoria)}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium text-slate-700" htmlFor="subcategoria">
          Subcategoría
        </label>
        <select
          className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-sky-400"
          id="subcategoria"
          name="subcategoria"
          onChange={handleFieldChange}
          value={form.subcategoria}
        >
          <option value="">Todas</option>
          {subcategorias.map((subcategoria) => (
            <option key={subcategoria} value={subcategoria}>
              {getTaxonomyLabel(subcategoria)}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium text-slate-700" htmlFor="condicion">
          Condición
        </label>
        <select
          className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-sky-400"
          id="condicion"
          name="condicion"
          onChange={handleFieldChange}
          value={form.condicion}
        >
          <option value="">Todas</option>
          {['NUEVO', 'COMO_NUEVO', 'USADO', 'PARA_REPUESTOS'].map((condicion) => (
            <option key={condicion} value={condicion}>
              {getTaxonomyLabel(condicion)}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-700" htmlFor="precio_min">
            Precio mínimo
          </label>
          <input
            className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-sky-400"
            id="precio_min"
            min="0"
            name="precio_min"
            onChange={handleFieldChange}
            type="number"
            value={form.precio_min}
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-700" htmlFor="precio_max">
            Precio máximo
          </label>
          <input
            className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-sky-400"
            id="precio_max"
            min="0"
            name="precio_max"
            onChange={handleFieldChange}
            type="number"
            value={form.precio_max}
          />
        </div>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium text-slate-700" htmlFor="order_by">
          Ordenar por
        </label>
        <select
          className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-sky-400"
          id="order_by"
          name="order_by"
          onChange={handleFieldChange}
          value={form.order_by}
        >
          <option value="reciente">Más reciente</option>
          <option value="precio_asc">Precio menor</option>
          <option value="precio_desc">Precio mayor</option>
        </select>
      </div>

      <div className="space-y-4 rounded-[28px] border border-sky-100 bg-gradient-to-br from-sky-50 to-white p-4 shadow-sm ring-1 ring-sky-50">
        <div className="flex flex-col gap-3 rounded-[22px] bg-white/80 p-4 shadow-sm ring-1 ring-slate-100 sm:flex-row sm:items-start sm:justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="flex h-7 w-7 items-center justify-center rounded-full bg-sky-600 text-xs font-black text-white">
                T
              </span>
              <h3 className="text-sm font-bold uppercase tracking-[0.14em] text-slate-900">
                Filtros técnicos
              </h3>
            </div>
            <p className="max-w-sm text-xs leading-5 text-slate-500">
              Agrega pares clave-valor para buscar atributos concretos, por ejemplo socket = AM4 o
              vram_gb = 12.
            </p>
          </div>

          <button
            className="inline-flex items-center justify-center rounded-full border border-sky-200 bg-sky-50 px-4 py-2 text-xs font-semibold text-sky-700 transition hover:bg-sky-100"
            onClick={addSpecPair}
            type="button"
          >
            Agregar filtro técnico
          </button>
        </div>

        <div className="space-y-3">
          {specPairs.map((pair, index) => (
            <div
              className="rounded-[22px] border border-slate-200 bg-white p-3 shadow-sm"
              key={pair.id}
            >
              <div className="mb-3 flex items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <span className="rounded-full bg-slate-100 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-600">
                    Filtro {index + 1}
                  </span>
                  <span className="text-xs text-slate-400">Clave y valor</span>
                </div>
                <button
                  className="rounded-full border border-slate-200 px-3 py-2 text-xs font-semibold text-rose-600 transition hover:bg-rose-50"
                  onClick={() => removeSpecPair(pair.id)}
                  type="button"
                >
                  Eliminar
                </button>
              </div>

              <div className="grid gap-3 md:grid-cols-[1fr_1fr]">
                <div className="space-y-1.5">
                  <label className="text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500">
                    Clave técnica
                  </label>
                  <input
                    className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-sky-400 focus:bg-white"
                    onChange={(event) => updateSpecPair(pair.id, 'key', event.target.value)}
                    placeholder="socket"
                    type="text"
                    value={pair.key}
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500">
                    Valor buscado
                  </label>
                  <input
                    className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-sky-400 focus:bg-white"
                    onChange={(event) => updateSpecPair(pair.id, 'value', event.target.value)}
                    placeholder="AM4"
                    type="text"
                    value={pair.value}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {filterError ? (
        <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {filterError}
        </div>
      ) : null}

      <div className="flex flex-col gap-3">
        <button
          className="w-full rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
          type="submit"
        >
          Buscar
        </button>
        <button
          className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
          onClick={clearFilters}
          type="button"
        >
          Limpiar filtros
        </button>
      </div>
    </form>
  )

  return (
    <div className="min-h-screen bg-[linear-gradient(180deg,#f8fafc_0%,#ecfeff_32%,#f8fafc_100%)] px-4 py-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-8 flex items-start justify-between gap-4">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-700">
              Búsqueda avanzada
            </p>
            <h1 className="mt-2 text-4xl font-black tracking-tight text-slate-900">
              Encuentra la pieza exacta
            </h1>
          </div>

          <button
            className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm md:hidden"
            onClick={() => setMobileFiltersOpen(true)}
            type="button"
          >
            Filtros
          </button>
        </div>

        <div className="grid gap-6 lg:grid-cols-[320px_minmax(0,1fr)]">
          <aside className="hidden self-start rounded-[28px] border border-slate-200 bg-white p-5 shadow-sm lg:block">
            {FiltersContent}
          </aside>

          <section className="space-y-6">
            <div className="rounded-[28px] border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <p className="text-sm font-medium text-slate-700">
                  {paginacion?.total ?? 0} resultados encontrados
                </p>

                <div className="flex flex-wrap gap-2">
                  {chips.map((chip) => (
                    <button
                      className="rounded-full bg-slate-100 px-3 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-200"
                      key={chip.id}
                      onClick={() => handleRemoveChip(chip)}
                      type="button"
                    >
                      {chip.label} ×
                    </button>
                  ))}
                </div>
              </div>

              {error ? (
                <div className="mt-4 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
                  {error}
                </div>
              ) : null}
            </div>

            {cargando ? (
              <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
                {skeletonItems.map((item) => (
                  <SkeletonCard key={item} />
                ))}
              </div>
            ) : resultados.length === 0 ? (
              <div className="rounded-[28px] border border-slate-200 bg-white px-6 py-14 text-center shadow-sm">
                <h2 className="text-2xl font-bold text-slate-900">Sin coincidencias</h2>
                <p className="mt-3 text-sm text-slate-600">
                  Ajusta los filtros o elimina algunas especificaciones para ampliar la búsqueda.
                </p>
              </div>
            ) : (
              <>
                <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
                  {resultados.map((anuncio) => (
                    <AnuncioCard anuncio={anuncio} key={anuncio.id} />
                  ))}
                </div>
                <Paginacion onCambiarPagina={handlePageChange} paginacion={paginacion} />
              </>
            )}
          </section>
        </div>
      </div>

      {mobileFiltersOpen ? (
        <div className="fixed inset-0 z-40 bg-slate-950/50 px-4 py-6 lg:hidden">
          <div className="mx-auto h-full max-w-lg overflow-y-auto rounded-[28px] bg-white p-5 shadow-2xl">
            <div className="mb-5 flex items-center justify-between">
              <h2 className="text-lg font-bold text-slate-900">Filtros</h2>
              <button
                className="rounded-full bg-slate-100 px-3 py-2 text-sm font-semibold text-slate-700"
                onClick={() => setMobileFiltersOpen(false)}
                type="button"
              >
                Cerrar
              </button>
            </div>
            {FiltersContent}
          </div>
        </div>
      ) : null}
    </div>
  )
}

export default Buscar

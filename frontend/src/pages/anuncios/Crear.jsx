import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../api/axios'
import { useAuth } from '../../hooks/useAuth'
import {
  CATEGORIAS_SUBCATEGORIAS,
  ESPECIFICACIONES,
  getSpecFieldType,
  getSpecLabel,
  getSubcategoriesForCategory,
  getTaxonomyLabel,
  normalizeTaxonomyValue,
  sanitizeSpecsPayload,
} from '../../utils/especificaciones'

const imageTypes = ['image/jpeg', 'image/png', 'image/webp']
const videoTypes = ['video/mp4']
const maxImageSize = 10 * 1024 * 1024
const maxVideoSize = 30 * 1024 * 1024

const buildEmptyForm = () => ({
  titulo: '',
  categoria: '',
  subcategoria: '',
  condicion: '',
  precio: '',
  descripcion: '',
})

const buildPreview = (file) => ({
  id: crypto.randomUUID(),
  file,
  url: URL.createObjectURL(file),
})

const reorderItems = (items, fromId, toId) => {
  const fromIndex = items.findIndex((item) => item.id === fromId)
  const toIndex = items.findIndex((item) => item.id === toId)

  if (fromIndex === -1 || toIndex === -1) {
    return items
  }

  const nextItems = [...items]
  const [moved] = nextItems.splice(fromIndex, 1)
  nextItems.splice(toIndex, 0, moved)
  return nextItems
}

const validateImageFiles = (files, currentCount = 0) => {
  const nextFiles = Array.from(files)

  if (currentCount + nextFiles.length > 8) {
    return { error: 'Solo puedes tener hasta 8 imágenes por anuncio.', files: [] }
  }

  for (const file of nextFiles) {
    if (!imageTypes.includes(file.type)) {
      return { error: 'Solo se permiten imágenes JPG, PNG o WEBP.', files: [] }
    }
    if (file.size > maxImageSize) {
      return { error: 'Cada imagen debe pesar como máximo 10MB.', files: [] }
    }
  }

  return { error: '', files: nextFiles }
}

const validateVideoFile = (file, hasExistingVideo = false) => {
  if (!file) {
    return { error: '' }
  }

  if (hasExistingVideo) {
    return { error: 'Solo puedes tener un video por anuncio.' }
  }

  if (!videoTypes.includes(file.type)) {
    return { error: 'Solo se permite un video MP4.' }
  }

  if (file.size > maxVideoSize) {
    return { error: 'El video debe pesar como máximo 30MB.' }
  }

  return { error: '' }
}

const Field = ({ children, label }) => (
  <div className="space-y-2">
    <label className="text-sm font-medium text-slate-700">{label}</label>
    {children}
  </div>
)

const inputClassName =
  'w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none transition focus:border-sky-400'

const SpecInputs = ({ errors, specs, subcategoria, onSpecChange }) => {
  const fields = ESPECIFICACIONES[subcategoria] ?? []

  if (!subcategoria || fields.length === 0) {
    return null
  }

  return (
    <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-5">
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-700">
          Sección 2
        </p>
        <h2 className="mt-2 text-2xl font-black text-slate-900">Especificaciones técnicas</h2>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {fields.map((field) => {
          const fieldType = getSpecFieldType(field)

          if (fieldType === 'boolean') {
            return (
              <label
                className="flex items-center justify-between rounded-2xl border border-slate-200 px-4 py-3"
                key={field}
              >
                <span className="text-sm font-medium text-slate-700">{getSpecLabel(field)}</span>
                <input
                  checked={Boolean(specs[field])}
                  onChange={(event) => onSpecChange(field, event.target.checked)}
                  type="checkbox"
                />
              </label>
            )
          }

          return (
            <Field key={field} label={getSpecLabel(field)}>
              <input
                className={inputClassName}
                min={fieldType === 'number' ? '0' : undefined}
                onChange={(event) => onSpecChange(field, event.target.value)}
                type={fieldType === 'number' ? 'number' : 'text'}
                value={specs[field] ?? ''}
              />
              {errors[field] ? <p className="text-sm text-rose-600">{errors[field]}</p> : null}
            </Field>
          )
        })}
      </div>
    </section>
  )
}

const ImagePreviewGrid = ({ images, onRemove, onReorder }) => {
  const [draggingId, setDraggingId] = useState(null)

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {images.map((image, index) => (
        <div
          className="overflow-hidden rounded-[24px] border border-slate-200 bg-white"
          draggable
          key={image.id}
          onDragOver={(event) => event.preventDefault()}
          onDragStart={() => setDraggingId(image.id)}
          onDrop={() => {
            if (draggingId) {
              onReorder(draggingId, image.id)
            }
            setDraggingId(null)
          }}
        >
          <img alt={image.file.name} className="aspect-[4/3] w-full object-cover" src={image.url} />
          <div className="space-y-3 p-3">
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">
              {index === 0 ? 'Principal' : `Imagen ${index + 1}`}
            </p>
            <p className="truncate text-sm text-slate-700">{image.file.name}</p>
            <button
              className="w-full rounded-2xl border border-slate-200 px-3 py-2 text-sm font-semibold text-rose-600 transition hover:bg-rose-50"
              onClick={() => onRemove(image.id)}
              type="button"
            >
              Eliminar
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}

const Crear = () => {
  const navigate = useNavigate()
  const { usuario } = useAuth()
  const [form, setForm] = useState(buildEmptyForm())
  const [specs, setSpecs] = useState({})
  const [imagenes, setImagenes] = useState([])
  const [video, setVideo] = useState(null)
  const [errors, setErrors] = useState({})
  const [generalError, setGeneralError] = useState('')
  const [warning, setWarning] = useState('')
  const [loading, setLoading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  const subcategorias = useMemo(
    () => getSubcategoriesForCategory(form.categoria),
    [form.categoria],
  )

  useEffect(() => {
    const fetchPanel = async () => {
      if (!usuario || usuario.rol !== 'USER_ESTANDAR') {
        return
      }

      try {
        const response = await api.get('/usuarios/me/panel')
        const activos = response.data.data?.anuncios?.activos

        if (activos?.limite_maximo === 25) {
          setWarning(
            `Tienes ${activos.total} anuncios activos y ${activos.disponibles} espacios disponibles antes de alcanzar el límite.`
          )
        }
      } catch {
        setWarning('')
      }
    }

    fetchPanel()
  }, [usuario])

  useEffect(
    () => () => {
      imagenes.forEach((image) => URL.revokeObjectURL(image.url))
      if (video?.url) URL.revokeObjectURL(video.url)
    },
    [imagenes, video],
  )

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

      if (name === 'subcategoria' || name === 'condicion') {
        return {
          ...current,
          [name]: normalizeTaxonomyValue(value),
        }
      }

      return {
        ...current,
        [name]: value,
      }
    })

    if (name === 'categoria') {
      setSpecs({})
    }

    setErrors((current) => ({ ...current, [name]: '' }))
    setGeneralError('')
  }

  const handleSpecChange = (field, value) => {
    setSpecs((current) => ({
      ...current,
      [field]: value,
    }))
  }

  const handleImageSelection = (files) => {
    const validation = validateImageFiles(files, imagenes.length)

    if (validation.error) {
      setGeneralError(validation.error)
      return
    }

    setGeneralError('')
    setImagenes((current) => [...current, ...validation.files.map(buildPreview)])
  }

  const handleVideoSelection = (file) => {
    const validation = validateVideoFile(file, Boolean(video))

    if (validation.error) {
      setGeneralError(validation.error)
      return
    }

    setGeneralError('')
    if (video?.url) URL.revokeObjectURL(video.url)
    setVideo(file ? buildPreview(file) : null)
  }

  const validateForm = () => {
    const nextErrors = {}

    if (!form.titulo.trim()) nextErrors.titulo = 'El título es obligatorio.'
    if (!form.categoria) nextErrors.categoria = 'Selecciona una categoría.'
    if (!form.subcategoria) nextErrors.subcategoria = 'Selecciona una subcategoría.'
    if (!form.condicion) nextErrors.condicion = 'Selecciona una condición.'
    if (!form.precio || Number(form.precio) <= 0) nextErrors.precio = 'Ingresa un precio válido.'
    if (!form.descripcion.trim()) nextErrors.descripcion = 'La descripción es obligatoria.'

    return nextErrors
  }

  const uploadMedia = async (anuncioId) => {
    const mediaFiles = [...imagenes.map((image) => image.file)]

    if (video?.file) {
      mediaFiles.push(video.file)
    }

    if (mediaFiles.length === 0) {
      return
    }

    const payload = new FormData()
    mediaFiles.forEach((file) => payload.append('media', file))

    await api.post(`/anuncios/${anuncioId}/media`, payload, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (!progressEvent.total) return
        setUploadProgress(Math.round((progressEvent.loaded * 100) / progressEvent.total))
      },
    })
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    const nextErrors = validateForm()

    if (Object.keys(nextErrors).length > 0) {
      setErrors(nextErrors)
      return
    }

    setLoading(true)
    setGeneralError('')
    setUploadProgress(0)

    try {
      const response = await api.post('/anuncios', {
        ...form,
        categoria: form.categoria,
        subcategoria: form.subcategoria,
        condicion: form.condicion,
        precio: form.precio,
        descripcion: form.descripcion.trim(),
        titulo: form.titulo.trim(),
        especificaciones: sanitizeSpecsPayload(specs),
      })

      const anuncioId = response.data.data.id

      try {
        await uploadMedia(anuncioId)
      } catch {
        navigate(`/anuncios/${anuncioId}`, { replace: true })
        return
      }

      navigate(`/anuncios/${anuncioId}`, { replace: true })
    } catch (requestError) {
      if (requestError.response?.data?.data) {
        setErrors(requestError.response.data.data)
      }

      setGeneralError(
        requestError.response?.data?.mensaje ||
          requestError.response?.data?.message ||
          'No se pudo publicar el anuncio.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[linear-gradient(180deg,#f8fafc_0%,#ecfeff_30%,#f8fafc_100%)] px-4 py-8">
      <div className="mx-auto max-w-5xl space-y-6">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-700">
            Publicar anuncio
          </p>
          <h1 className="mt-2 text-4xl font-black tracking-tight text-slate-900">
            Comparte tu hardware con la comunidad
          </h1>
        </div>

        {warning ? (
          <div className="rounded-[28px] border border-amber-200 bg-amber-50 px-5 py-4 text-sm text-amber-800">
            {warning}
          </div>
        ) : null}

        <form className="space-y-6" onSubmit={handleSubmit}>
          <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-5">
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-700">
                Sección 1
              </p>
              <h2 className="mt-2 text-2xl font-black text-slate-900">Información básica</h2>
            </div>

            <div className="grid gap-5">
              <Field label="Título">
                <div className="space-y-2">
                  <input
                    className={inputClassName}
                    maxLength={100}
                    name="titulo"
                    onChange={handleFieldChange}
                    type="text"
                    value={form.titulo}
                  />
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span>{errors.titulo ?? ''}</span>
                    <span>{form.titulo.length}/100</span>
                  </div>
                </div>
              </Field>

              <div className="grid gap-5 md:grid-cols-2">
                <Field label="Categoría">
                  <select
                    className={inputClassName}
                    name="categoria"
                    onChange={handleFieldChange}
                    value={form.categoria}
                  >
                    <option value="">Selecciona</option>
                    {Object.keys(CATEGORIAS_SUBCATEGORIAS).map((categoria) => (
                      <option key={categoria} value={categoria}>
                        {getTaxonomyLabel(categoria)}
                      </option>
                    ))}
                  </select>
                  {errors.categoria ? <p className="text-sm text-rose-600">{errors.categoria}</p> : null}
                </Field>

                <Field label="Subcategoría">
                  <select
                    className={inputClassName}
                    name="subcategoria"
                    onChange={handleFieldChange}
                    value={form.subcategoria}
                  >
                    <option value="">Selecciona</option>
                    {subcategorias.map((subcategoria) => (
                      <option key={subcategoria} value={subcategoria}>
                        {getTaxonomyLabel(subcategoria)}
                      </option>
                    ))}
                  </select>
                  {errors.subcategoria ? (
                    <p className="text-sm text-rose-600">{errors.subcategoria}</p>
                  ) : null}
                </Field>
              </div>

              <div className="grid gap-5 md:grid-cols-[220px_minmax(0,1fr)]">
                <Field label="Condición">
                  <select
                    className={inputClassName}
                    name="condicion"
                    onChange={handleFieldChange}
                    value={form.condicion}
                  >
                    <option value="">Selecciona</option>
                    {['NUEVO', 'COMO_NUEVO', 'USADO', 'PARA_REPUESTOS'].map((condicion) => (
                      <option key={condicion} value={condicion}>
                        {getTaxonomyLabel(condicion)}
                      </option>
                    ))}
                  </select>
                </Field>

                <Field label="Precio">
                  <div className="flex overflow-hidden rounded-2xl border border-slate-200">
                    <span className="flex items-center bg-slate-50 px-4 text-sm font-semibold text-slate-500">
                      S/
                    </span>
                    <input
                      className="w-full px-4 py-3 text-sm outline-none"
                      min="0"
                      name="precio"
                      onChange={handleFieldChange}
                      step="0.01"
                      type="number"
                      value={form.precio}
                    />
                  </div>
                  {errors.precio ? <p className="text-sm text-rose-600">{errors.precio}</p> : null}
                </Field>
              </div>

              <Field label="Descripción">
                <textarea
                  className={`${inputClassName} min-h-36 resize-y`}
                  name="descripcion"
                  onChange={handleFieldChange}
                  value={form.descripcion}
                />
                {errors.descripcion ? (
                  <p className="text-sm text-rose-600">{errors.descripcion}</p>
                ) : null}
              </Field>
            </div>
          </section>

          <SpecInputs
            errors={errors}
            onSpecChange={handleSpecChange}
            specs={specs}
            subcategoria={form.subcategoria}
          />

          <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-5">
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-700">
                Sección 3
              </p>
              <h2 className="mt-2 text-2xl font-black text-slate-900">Imágenes y video</h2>
            </div>

            <div className="space-y-6">
              <div
                className="rounded-[24px] border border-dashed border-slate-300 bg-slate-50 p-6 text-center"
                onDragOver={(event) => event.preventDefault()}
                onDrop={(event) => {
                  event.preventDefault()
                  handleImageSelection(event.dataTransfer.files)
                }}
              >
                <p className="text-sm font-semibold text-slate-900">
                  Arrastra imágenes aquí o selecciónalas manualmente
                </p>
                <p className="mt-2 text-sm text-slate-500">
                  Hasta 8 imágenes JPG, PNG o WEBP de 10MB cada una.
                </p>
                <label className="mt-4 inline-flex cursor-pointer rounded-full bg-slate-900 px-4 py-2 text-sm font-semibold text-white">
                  Seleccionar imágenes
                  <input
                    accept=".jpg,.jpeg,.png,.webp"
                    className="hidden"
                    multiple
                    onChange={(event) => handleImageSelection(event.target.files)}
                    type="file"
                  />
                </label>
              </div>

              {imagenes.length > 0 ? (
                <ImagePreviewGrid
                  images={imagenes}
                  onRemove={(id) =>
                    setImagenes((current) => {
                      const image = current.find((item) => item.id === id)
                      if (image) URL.revokeObjectURL(image.url)
                      return current.filter((item) => item.id !== id)
                    })
                  }
                  onReorder={(fromId, toId) => setImagenes((current) => reorderItems(current, fromId, toId))}
                />
              ) : null}

              <div className="rounded-[24px] border border-dashed border-slate-300 bg-slate-50 p-6 text-center">
                <p className="text-sm font-semibold text-slate-900">Video opcional del producto</p>
                <p className="mt-2 text-sm text-slate-500">Solo 1 archivo MP4 de hasta 30MB.</p>
                <label className="mt-4 inline-flex cursor-pointer rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700">
                  Seleccionar video
                  <input
                    accept=".mp4"
                    className="hidden"
                    onChange={(event) => handleVideoSelection(event.target.files?.[0])}
                    type="file"
                  />
                </label>

                {video ? (
                  <div className="mt-5 space-y-3 rounded-[24px] border border-slate-200 bg-white p-4 text-left">
                    <video className="aspect-video w-full rounded-2xl object-cover" controls src={video.url} />
                    <div className="flex items-center justify-between gap-3">
                      <p className="truncate text-sm text-slate-700">{video.file.name}</p>
                      <button
                        className="rounded-full border border-slate-200 px-3 py-2 text-sm font-semibold text-rose-600"
                        onClick={() => {
                          URL.revokeObjectURL(video.url)
                          setVideo(null)
                        }}
                        type="button"
                      >
                        Eliminar
                      </button>
                    </div>
                  </div>
                ) : null}
              </div>
            </div>
          </section>

          {generalError ? (
            <div className="rounded-[24px] border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-700">
              {generalError}
            </div>
          ) : null}

          {loading && uploadProgress > 0 ? (
            <div className="rounded-[24px] border border-slate-200 bg-white p-4 shadow-sm">
              <div className="h-3 overflow-hidden rounded-full bg-slate-100">
                <div
                  className="h-full rounded-full bg-sky-500 transition-all"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
              <p className="mt-2 text-sm text-slate-600">Subiendo archivos: {uploadProgress}%</p>
            </div>
          ) : null}

          <button
            className="w-full rounded-[24px] bg-slate-900 px-5 py-4 text-base font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
            disabled={loading}
            type="submit"
          >
            {loading ? 'Publicando...' : 'Publicar anuncio'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default Crear

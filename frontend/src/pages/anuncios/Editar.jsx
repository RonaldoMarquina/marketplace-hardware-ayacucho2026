import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import api from '../../api/axios'
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
import { formatImageUrl } from '../../utils/format'

const imageTypes = ['image/jpeg', 'image/png', 'image/webp']
const videoTypes = ['video/mp4']
const maxImageSize = 10 * 1024 * 1024
const maxVideoSize = 30 * 1024 * 1024

const inputClassName =
  'w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none transition focus:border-sky-400'

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
  if (!file) return { error: '' }
  if (hasExistingVideo) return { error: 'Solo puedes tener un video por anuncio.' }
  if (!videoTypes.includes(file.type)) return { error: 'Solo se permite un video MP4.' }
  if (file.size > maxVideoSize) return { error: 'El video debe pesar como máximo 30MB.' }
  return { error: '' }
}

const buildSpecPatch = (original, current) => {
  const originalSpecs = original ?? {}
  const currentSpecs = sanitizeSpecsPayload(current)
  const keys = new Set([...Object.keys(originalSpecs), ...Object.keys(currentSpecs)])
  const patch = {}

  keys.forEach((key) => {
    const originalValue = originalSpecs[key]
    const currentValue = currentSpecs[key]

    if (!(key in currentSpecs)) {
      patch[key] = null
      return
    }

    if (JSON.stringify(originalValue) !== JSON.stringify(currentValue)) {
      patch[key] = currentValue
    }
  })

  return patch
}

const Field = ({ children, label }) => (
  <div className="space-y-2">
    <label className="text-sm font-medium text-slate-700">{label}</label>
    {children}
  </div>
)

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

const Editar = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [originalAnuncio, setOriginalAnuncio] = useState(null)
  const [form, setForm] = useState({
    titulo: '',
    categoria: '',
    subcategoria: '',
    condicion: '',
    precio: '',
    descripcion: '',
  })
  const [specs, setSpecs] = useState({})
  const [currentMedia, setCurrentMedia] = useState([])
  const [newImages, setNewImages] = useState([])
  const [newVideo, setNewVideo] = useState(null)
  const [errors, setErrors] = useState({})
  const [generalError, setGeneralError] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [mediaAction, setMediaAction] = useState('')
  const [mediaOrderDirty, setMediaOrderDirty] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  const subcategorias = useMemo(
    () => getSubcategoriesForCategory(form.categoria),
    [form.categoria],
  )

  useEffect(() => {
    const fetchDetalle = async () => {
      setLoading(true)

      try {
        const response = await api.get(`/anuncios/${id}`)
        const data = response.data.data

        if (!data.es_propietario || data.estado_propietario?.estado !== 'ACTIVO') {
          navigate('/', { replace: true })
          return
        }

        setOriginalAnuncio(data)
        setCurrentMedia(data.media ?? [])
        setForm({
          titulo: data.titulo ?? '',
          categoria: data.categoria ?? '',
          subcategoria: data.subcategoria ?? '',
          condicion: data.condicion ?? '',
          precio: String(data.precio ?? ''),
          descripcion: data.descripcion ?? '',
        })
        setSpecs(data.especificaciones ?? {})
      } catch {
        navigate('/', { replace: true })
      } finally {
        setLoading(false)
      }
    }

    fetchDetalle()
  }, [id, navigate])

  useEffect(
    () => () => {
      newImages.forEach((image) => URL.revokeObjectURL(image.url))
      if (newVideo?.url) URL.revokeObjectURL(newVideo.url)
    },
    [newImages, newVideo],
  )

  const imageCount = currentMedia.filter((item) => item.tipo_media === 'imagen').length + newImages.length
  const hasExistingVideo =
    currentMedia.some((item) => item.tipo_media === 'video') || Boolean(newVideo)

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

  const handleNewImages = (files) => {
    const validation = validateImageFiles(files, imageCount)

    if (validation.error) {
      setGeneralError(validation.error)
      return
    }

    setNewImages((current) => [...current, ...validation.files.map(buildPreview)])
    setGeneralError('')
  }

  const handleNewVideo = (file) => {
    const validation = validateVideoFile(file, hasExistingVideo)

    if (validation.error) {
      setGeneralError(validation.error)
      return
    }

    if (newVideo?.url) URL.revokeObjectURL(newVideo.url)
    setNewVideo(file ? buildPreview(file) : null)
    setGeneralError('')
  }

  const refreshDetalle = async () => {
    const response = await api.get(`/anuncios/${id}`)
    const data = response.data.data
    setOriginalAnuncio(data)
    setCurrentMedia(data.media ?? [])
    setMediaOrderDirty(false)
  }

  const handleDeleteMedia = async (mediaId) => {
    setMediaAction(`delete-${mediaId}`)
    setGeneralError('')

    try {
      await api.delete(`/anuncios/${id}/media/${mediaId}`)
      await refreshDetalle()
    } catch (requestError) {
      setGeneralError(
        requestError.response?.data?.mensaje ||
          requestError.response?.data?.message ||
          'No se pudo eliminar la media.'
      )
    } finally {
      setMediaAction('')
    }
  }

  const handleReplaceMedia = async (mediaId, file) => {
    if (!file) return

    setMediaAction(`replace-${mediaId}`)
    setGeneralError('')

    try {
      const payload = new FormData()
      payload.append('media', file)
      await api.put(`/anuncios/${id}/media/${mediaId}`, payload, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      await refreshDetalle()
    } catch (requestError) {
      setGeneralError(
        requestError.response?.data?.mensaje ||
          requestError.response?.data?.message ||
          'No se pudo reemplazar la media.'
      )
    } finally {
      setMediaAction('')
    }
  }

  const handleSaveOrder = async () => {
    const imageIds = currentMedia.filter((item) => item.tipo_media === 'imagen').map((item) => item.id)

    setMediaAction('order')
    setGeneralError('')

    try {
      await api.patch(`/anuncios/${id}/media/orden`, {
        orden: imageIds,
      })
      await refreshDetalle()
    } catch (requestError) {
      setGeneralError(
        requestError.response?.data?.mensaje ||
          requestError.response?.data?.message ||
          'No se pudo guardar el orden de las imágenes.'
      )
    } finally {
      setMediaAction('')
    }
  }

  const uploadNewMedia = async () => {
    const files = [...newImages.map((image) => image.file)]
    if (newVideo?.file) files.push(newVideo.file)
    if (files.length === 0) return

    const payload = new FormData()
    files.forEach((file) => payload.append('media', file))

    await api.post(`/anuncios/${id}/media`, payload, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (!progressEvent.total) return
        setUploadProgress(Math.round((progressEvent.loaded * 100) / progressEvent.total))
      },
    })
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

  const handleSubmit = async (event) => {
    event.preventDefault()
    const nextErrors = validateForm()

    if (Object.keys(nextErrors).length > 0) {
      setErrors(nextErrors)
      return
    }

    if (!originalAnuncio) return

    setSaving(true)
    setGeneralError('')
    setUploadProgress(0)

    try {
      const patch = {}
      const currentSpecs = sanitizeSpecsPayload(specs)

      ;['titulo', 'categoria', 'subcategoria', 'condicion', 'precio', 'descripcion'].forEach((field) => {
        const originalValue =
          field === 'precio' ? String(originalAnuncio[field] ?? '') : String(originalAnuncio[field] ?? '')
        const currentValue = String(form[field] ?? '')

        if (currentValue !== originalValue) {
          patch[field] = field === 'titulo' || field === 'descripcion' ? currentValue.trim() : currentValue
        }
      })

      const specPatch = buildSpecPatch(originalAnuncio.especificaciones ?? {}, currentSpecs)
      if (Object.keys(specPatch).length > 0) {
        patch.especificaciones = specPatch
      }

      if (Object.keys(patch).length > 0) {
        await api.patch(`/anuncios/${id}`, patch)
      }

      try {
        await uploadNewMedia()
      } catch {
        navigate(`/anuncios/${id}`, { replace: true })
        return
      }

      navigate(`/anuncios/${id}`, { replace: true })
    } catch (requestError) {
      if (requestError.response?.data?.data) {
        setErrors(requestError.response.data.data)
      }

      setGeneralError(
        requestError.response?.data?.mensaje ||
          requestError.response?.data?.message ||
          'No se pudo actualizar el anuncio.'
      )
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <div className="px-4 py-12 text-center text-sm text-slate-600">Cargando anuncio...</div>
  }

  return (
    <div className="min-h-screen bg-[linear-gradient(180deg,#f8fafc_0%,#eef2ff_30%,#f8fafc_100%)] px-4 py-8">
      <div className="mx-auto max-w-5xl space-y-6">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-700">
              Editar anuncio
            </p>
            <h1 className="mt-2 text-4xl font-black tracking-tight text-slate-900">
              Ajusta la publicación antes de volver al feed
            </h1>
          </div>

          <Link
            className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm"
            to={`/anuncios/${id}`}
          >
            Volver al detalle
          </Link>
        </div>

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
                Sección adicional
              </p>
              <h2 className="mt-2 text-2xl font-black text-slate-900">Gestión de media</h2>
            </div>

            <div className="space-y-6">
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {currentMedia.map((media) => (
                  <div className="overflow-hidden rounded-[24px] border border-slate-200 bg-white" key={media.id}>
                    {media.tipo_media === 'video' ? (
                      <video className="aspect-video w-full object-cover" controls src={formatImageUrl(media.ruta_relativa)} />
                    ) : (
                      <img
                        alt={`Media ${media.id}`}
                        className="aspect-[4/3] w-full object-cover"
                        draggable
                        onDragOver={(event) => event.preventDefault()}
                        onDragStart={(event) => event.dataTransfer.setData('text/plain', String(media.id))}
                        onDrop={(event) => {
                          const fromId = Number(event.dataTransfer.getData('text/plain'))
                          if (!fromId || media.tipo_media !== 'imagen') return
                          setCurrentMedia((current) => reorderItems(current, fromId, media.id))
                          setMediaOrderDirty(true)
                        }}
                        src={formatImageUrl(media.ruta_relativa)}
                      />
                    )}

                    <div className="space-y-3 p-4">
                      <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">
                        {media.tipo_media === 'video'
                          ? 'Video'
                          : media.es_principal
                            ? 'Imagen principal'
                            : `Imagen ${media.orden + 1}`}
                      </p>

                      <div className="flex flex-wrap gap-2">
                        <button
                          className="rounded-2xl border border-slate-200 px-3 py-2 text-sm font-semibold text-rose-600"
                          disabled={mediaAction === `delete-${media.id}`}
                          onClick={() => handleDeleteMedia(media.id)}
                          type="button"
                        >
                          {mediaAction === `delete-${media.id}` ? 'Eliminando...' : 'Eliminar'}
                        </button>

                        <label className="rounded-2xl border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-700">
                          Reemplazar
                          <input
                            accept={media.tipo_media === 'video' ? '.mp4' : '.jpg,.jpeg,.png,.webp'}
                            className="hidden"
                            onChange={(event) => handleReplaceMedia(media.id, event.target.files?.[0])}
                            type="file"
                          />
                        </label>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {mediaOrderDirty ? (
                <button
                  className="rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white"
                  disabled={mediaAction === 'order'}
                  onClick={handleSaveOrder}
                  type="button"
                >
                  {mediaAction === 'order' ? 'Guardando orden...' : 'Guardar orden'}
                </button>
              ) : null}

              <div className="space-y-6 rounded-[24px] bg-slate-50 p-5">
                <div
                  className="rounded-[24px] border border-dashed border-slate-300 bg-white p-6 text-center"
                  onDragOver={(event) => event.preventDefault()}
                  onDrop={(event) => {
                    event.preventDefault()
                    handleNewImages(event.dataTransfer.files)
                  }}
                >
                  <p className="text-sm font-semibold text-slate-900">Agregar nuevas imágenes</p>
                  <p className="mt-2 text-sm text-slate-500">
                    Puedes completar hasta 8 imágenes en total.
                  </p>
                  <label className="mt-4 inline-flex cursor-pointer rounded-full bg-slate-900 px-4 py-2 text-sm font-semibold text-white">
                    Seleccionar imágenes
                    <input
                      accept=".jpg,.jpeg,.png,.webp"
                      className="hidden"
                      multiple
                      onChange={(event) => handleNewImages(event.target.files)}
                      type="file"
                    />
                  </label>
                </div>

                {newImages.length > 0 ? (
                  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    {newImages.map((image) => (
                      <div className="overflow-hidden rounded-[24px] border border-slate-200 bg-white" key={image.id}>
                        <img alt={image.file.name} className="aspect-[4/3] w-full object-cover" src={image.url} />
                        <div className="space-y-3 p-3">
                          <p className="truncate text-sm text-slate-700">{image.file.name}</p>
                          <button
                            className="w-full rounded-2xl border border-slate-200 px-3 py-2 text-sm font-semibold text-rose-600"
                            onClick={() =>
                              setNewImages((current) => {
                                const target = current.find((item) => item.id === image.id)
                                if (target) URL.revokeObjectURL(target.url)
                                return current.filter((item) => item.id !== image.id)
                              })
                            }
                            type="button"
                          >
                            Eliminar
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : null}

                <div className="rounded-[24px] border border-dashed border-slate-300 bg-white p-6 text-center">
                  <p className="text-sm font-semibold text-slate-900">Agregar video</p>
                  <p className="mt-2 text-sm text-slate-500">Solo un MP4 si el anuncio aún no tiene video.</p>
                  <label className="mt-4 inline-flex cursor-pointer rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700">
                    Seleccionar video
                    <input
                      accept=".mp4"
                      className="hidden"
                      onChange={(event) => handleNewVideo(event.target.files?.[0])}
                      type="file"
                    />
                  </label>

                  {newVideo ? (
                    <div className="mt-5 space-y-3 rounded-[24px] border border-slate-200 bg-slate-50 p-4 text-left">
                      <video className="aspect-video w-full rounded-2xl object-cover" controls src={newVideo.url} />
                      <div className="flex items-center justify-between gap-3">
                        <p className="truncate text-sm text-slate-700">{newVideo.file.name}</p>
                        <button
                          className="rounded-full border border-slate-200 px-3 py-2 text-sm font-semibold text-rose-600"
                          onClick={() => {
                            URL.revokeObjectURL(newVideo.url)
                            setNewVideo(null)
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
            </div>
          </section>

          {generalError ? (
            <div className="rounded-[24px] border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-700">
              {generalError}
            </div>
          ) : null}

          {saving && uploadProgress > 0 ? (
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
            disabled={saving}
            type="submit"
          >
            {saving ? 'Guardando...' : 'Guardar cambios'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default Editar

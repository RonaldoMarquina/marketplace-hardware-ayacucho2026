import { useMemo, useState } from 'react'

const sizeMap = {
  sm: 'h-4 w-4',
  md: 'h-5 w-5',
  lg: 'h-6 w-6',
}

const Estrella = ({ activa, className, onClick, onMouseEnter, onMouseLeave }) => (
  <button
    className={`transition ${className}`}
    onClick={onClick}
    onMouseEnter={onMouseEnter}
    onMouseLeave={onMouseLeave}
    type="button"
  >
    <svg
      aria-hidden="true"
      fill={activa ? 'currentColor' : 'none'}
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="1.6"
      viewBox="0 0 24 24"
    >
      <path d="m12 3.75 2.8 5.67 6.26.91-4.53 4.42 1.07 6.23L12 18l-5.6 2.98 1.07-6.23-4.53-4.42 6.26-.91L12 3.75Z" />
    </svg>
  </button>
)

const Estrellas = ({
  puntaje = null,
  interactivo = false,
  onCambiar,
  tamano = 'md',
}) => {
  const [hoverValue, setHoverValue] = useState(null)
  const displayValue = useMemo(
    () => (hoverValue ?? puntaje ?? 0),
    [hoverValue, puntaje],
  )

  const starSize = sizeMap[tamano] ?? sizeMap.md

  return (
    <div className="flex items-center gap-2">
      <div className="flex items-center gap-1 text-amber-400">
        {Array.from({ length: 5 }, (_, index) => {
          const value = index + 1

          return (
            <Estrella
              activa={value <= displayValue}
              className={`${starSize} ${
                interactivo ? 'cursor-pointer hover:scale-110' : 'cursor-default'
              } ${value <= displayValue ? 'text-amber-400' : 'text-slate-300'}`}
              key={value}
              onClick={
                interactivo && onCambiar
                  ? () => {
                      onCambiar(value)
                    }
                  : undefined
              }
              onMouseEnter={interactivo ? () => setHoverValue(value) : undefined}
              onMouseLeave={interactivo ? () => setHoverValue(null) : undefined}
            />
          )
        })}
      </div>

      {puntaje === null ? (
        <span className="text-sm text-slate-500">Sin calificaciones</span>
      ) : tamano !== 'sm' ? (
        <span className="text-sm font-medium text-slate-700">{Number(puntaje).toFixed(1)}</span>
      ) : null}
    </div>
  )
}

export default Estrellas

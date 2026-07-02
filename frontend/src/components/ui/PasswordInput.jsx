import { useId, useState } from 'react'

const EyeIcon = ({ open }) => (
  <svg
    aria-hidden="true"
    className="h-5 w-5"
    fill="none"
    stroke="currentColor"
    strokeLinecap="round"
    strokeLinejoin="round"
    strokeWidth="1.8"
    viewBox="0 0 24 24"
  >
    <path d="M2.25 12s3.75-6.75 9.75-6.75S21.75 12 21.75 12 18 18.75 12 18.75 2.25 12 2.25 12Z" />
    <circle cx="12" cy="12" r="3" />
    {!open && <path d="M3 3l18 18" />}
  </svg>
)

const PasswordInput = ({
  value,
  onChange,
  placeholder,
  name,
  error,
  disabled = false,
  autoComplete = 'current-password',
}) => {
  const [visible, setVisible] = useState(false)
  const inputId = useId()

  return (
    <div className="space-y-2">
      <div
        className={`flex items-center rounded-2xl border bg-white px-4 ${
          error ? 'border-rose-400' : 'border-slate-200'
        }`}
      >
        <input
          autoComplete={autoComplete}
          className="w-full bg-transparent py-3 text-sm text-slate-900 outline-none placeholder:text-slate-400"
          disabled={disabled}
          id={inputId}
          name={name}
          onChange={onChange}
          placeholder={placeholder}
          type={visible ? 'text' : 'password'}
          value={value}
        />
        <button
          aria-controls={inputId}
          aria-label={visible ? 'Ocultar contraseña' : 'Mostrar contraseña'}
          className="ml-3 text-slate-500 transition hover:text-slate-700 disabled:cursor-not-allowed"
          disabled={disabled}
          onClick={() => setVisible((current) => !current)}
          type="button"
        >
          <EyeIcon open={visible} />
        </button>
      </div>

      {error ? <p className="text-sm text-rose-600">{error}</p> : null}
    </div>
  )
}

export default PasswordInput

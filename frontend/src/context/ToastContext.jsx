import { createContext, useCallback, useMemo, useState } from 'react'
import Toast from '../components/ui/Toast'

export const ToastContext = createContext()

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([])

  const removeToast = useCallback((id) => {
    setToasts((current) => current.filter((toast) => toast.id !== id))
  }, [])

  const showToast = useCallback((mensaje, tipo = 'info', duracion = 3000) => {
    const id = crypto.randomUUID()
    setToasts((current) => [...current, { id, mensaje, tipo, duracion }])
    return id
  }, [])

  const value = useMemo(
    () => ({
      showToast,
      removeToast,
    }),
    [removeToast, showToast],
  )

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed bottom-4 right-4 z-[90] flex w-full max-w-sm flex-col gap-3">
        {toasts.map((toast) => (
          <Toast
            duracion={toast.duracion}
            key={toast.id}
            mensaje={toast.mensaje}
            onClose={() => removeToast(toast.id)}
            tipo={toast.tipo}
          />
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export default ToastContext

export const isValidEmail = (correo) => {
  if (typeof correo !== 'string') {
    return false
  }

  const email = correo.trim()
  if (!email || email.includes(' ')) {
    return false
  }

  const atIndex = email.indexOf('@')
  if (atIndex <= 0 || atIndex !== email.lastIndexOf('@')) {
    return false
  }

  const localPart = email.slice(0, atIndex)
  const domainPart = email.slice(atIndex + 1)

  if (!localPart || !domainPart || domainPart.startsWith('.') || domainPart.endsWith('.')) {
    return false
  }

  const domainLabels = domainPart.split('.')
  if (domainLabels.length < 2) {
    return false
  }

  return domainLabels.every((label) => label.length > 0)
}

export const isValidPassword = (password) =>
  /^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/.test(password)

export const isValidPhone = (telefono) => /^\d{9}$/.test(telefono)

export const isValidRUC = (ruc) => /^\d{11}$/.test(ruc)

export const isValidPrice = (precio) =>
  /^(?:0|[1-9]\d*)(?:\.\d{1,2})?$/.test(String(precio))

export const passwordError = (password) => {
  if (!password || password.length < 8) {
    return 'La contraseña debe tener al menos 8 caracteres.'
  }

  if (!/[A-Z]/.test(password)) {
    return 'La contraseña debe incluir al menos una mayúscula.'
  }

  if (!/\d/.test(password)) {
    return 'La contraseña debe incluir al menos un número.'
  }

  if (!/[^A-Za-z0-9]/.test(password)) {
    return 'La contraseña debe incluir al menos un carácter especial.'
  }

  return null
}

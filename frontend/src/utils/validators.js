export const isValidEmail = (correo) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo)

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

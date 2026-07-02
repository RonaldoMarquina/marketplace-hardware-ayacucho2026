# Prompt Codex — Fase 2: Autenticación

Lee los archivos `docs/FRONTEND_CONTEXT.md` y este prompt completo antes de escribir cualquier línea de código. Respeta la estructura de carpetas y convenciones definidas en el contexto.

## Tarea

Implementa todos los flujos de autenticación. Las páginas ya existen como placeholders — reemplázalas con implementaciones reales.

---

## Página 1: `src/pages/auth/Login.jsx`

### UI
- Logo o nombre "HardwareAyacucho" centrado arriba
- Card centrada con:
  - Input correo (type email)
  - Input password (type password, con toggle show/hide)
  - Botón "Ingresar" (full width)
  - Link "¿Olvidaste tu contraseña?" → `/recuperar-password`
  - Link "¿No tienes cuenta? Crear cuenta" → `/register`
- Mostrar error general debajo del botón si el backend responde error

### Lógica
1. Validar con `isValidEmail` de `validators.js` antes de llamar al backend.
2. Llamar `POST /auth/login` con `{ correo, password }` usando `src/api/axios.js`.
3. Si responde 200:
   - Llamar `login(token, { id, nombre, correo, rol, es_tienda_verificada, estado })` del AuthContext.
   - Redirigir según rol:
     - `ADMIN` → `/admin/reportados`
     - cualquier otro → `/`
4. Si responde 403 con `error: "CUENTA_NO_VERIFICADA"` → mostrar mensaje con link a reenviar verificación.
5. Si responde 403 con `error: "CUENTA_EN_REVISION"` → mostrar mensaje explicando que está en revisión.
6. Si responde 403 con `error: "CUENTA_BLOQUEADA"` → mostrar mensaje de cuenta suspendida.
7. Si responde 429 → mostrar `disponible_en` formateado con `formatDateTime`.
8. Si responde 401 → mostrar "Correo o contraseña incorrectos."
9. Deshabilitar botón y mostrar "Ingresando..." mientras hay request en curso.

---

## Página 2: `src/pages/auth/Register.jsx`

### UI
- Card centrada con:
  - Input nombre (text)
  - Input correo (type email)
  - Input password (type password, con toggle show/hide)
  - Input confirmar password (type password, con toggle show/hide)
  - Input teléfono (text, placeholder "987654321")
  - Botón "Crear cuenta" (full width)
  - Link "¿Ya tienes cuenta? Ingresar" → `/login`
  - Link "¿Tienes una tienda? Regístrala aquí" → `/register/tienda`
- Mostrar requisitos de password en tiempo real (checklist pequeña):
  - ✅ Mínimo 8 caracteres
  - ✅ Al menos 1 mayúscula
  - ✅ Al menos 1 número
  - ✅ Al menos 1 carácter especial
- Mostrar error por campo si la validación falla

### Lógica
1. Validar todos los campos con `validators.js` antes de llamar al backend.
2. Validar que `password === confirmar password`.
3. Llamar `POST /auth/register` con `{ nombre, correo, password, telefono }`.
4. Si responde 201 → redirigir a `/verificar-email` con state `{ correo }`.
5. Si responde 409 con correo duplicado → mostrar error en campo correo.
6. Si responde 409 con teléfono duplicado → mostrar error en campo teléfono.
7. Si responde 422 → mostrar error del campo correspondiente.
8. Deshabilitar botón mientras hay request en curso.

---

## Página 3: `src/pages/auth/RegisterTienda.jsx`

### UI
- Card más ancha centrada con título "Registrar Tienda":
  - Input nombre completo del propietario (text)
  - Input nombre comercial (text)
  - Input RUC (text, maxLength 11)
  - Input dirección (text)
  - Input teléfono (text)
  - Input correo (type email)
  - Input password (type password, con toggle show/hide)
  - Input confirmar password (type password, con toggle show/hide)
  - Input file para documento de identidad (JPG/PNG, max 5MB)
    - Mostrar nombre del archivo seleccionado
    - Mostrar error si supera 5MB o formato incorrecto
  - Botón "Registrar tienda" (full width)
  - Link "¿Ya tienes cuenta? Ingresar" → `/login`
- Checklist de password igual que Register.jsx

### Lógica
1. Validar todos los campos con `validators.js`.
2. Validar `isValidRUC` para el RUC.
3. Validar archivo: solo JPG/PNG, max 5MB — validación en frontend antes de enviar.
4. Construir `FormData` con todos los campos.
5. Llamar `POST /auth/register/tienda` con `Content-Type: multipart/form-data`.
6. Si responde 201 → redirigir a `/verificar-email` con state `{ correo, esTienda: true }`.
7. Manejar errores 409 por campo (correo, teléfono, RUC, nombre_comercial).
8. Si responde 413 → mostrar "El documento supera el tamaño máximo de 5MB."
9. Si responde 415 → mostrar "Solo se permiten archivos JPG o PNG."
10. Deshabilitar botón mientras hay request en curso.

---

## Página 4: `src/pages/auth/VerificarEmail.jsx`

### UI
- Card centrada con ícono de correo:
  - Título "Revisa tu correo"
  - Si `state.esTienda === true` → mostrar mensaje adicional:
    "Tu solicitud de tienda será revisada por un administrador una vez que verifiques tu correo."
  - Correo al que se envió (desde `location.state.correo`)
  - Botón "Reenviar correo de verificación"
  - Contador de espera: deshabilitar botón 60 segundos tras cada reenvío
  - Link "Volver al inicio" → `/`

### Lógica
1. Al montar: verificar si hay `token` en query params (`?token=XXXX`).
2. Si hay token → llamar `GET /auth/verify-email?token={token}` automáticamente.
3. Si responde 200:
   - Si `estado === "ACTIVO"` → mostrar "¡Cuenta activada! Ya puedes ingresar." + link a `/login`.
   - Si `estado === "EN_REVISION"` → mostrar "Correo verificado. Espera la aprobación del administrador."
4. Si responde 404 → mostrar "Enlace inválido o inexistente."
5. Si responde 409 → mostrar "Este enlace ya fue usado."
6. Si responde 410 → mostrar "Enlace expirado." + botón de reenvío.
7. Botón reenvío → llamar `POST /auth/verify-email/resend` con `{ correo }`.
8. Si responde 429 → mostrar `disponible_en` y deshabilitar botón.

---

## Página 5: `src/pages/auth/RecuperarPassword.jsx`

### UI
- Card centrada con:
  - Título "Recuperar contraseña"
  - Input correo (type email)
  - Botón "Enviar enlace"
  - Link "Volver al login" → `/login`
- Tras enviar exitosamente → reemplazar el form con mensaje:
  "Si el correo está registrado y la cuenta está activa, recibirás un enlace en los próximos minutos."

### Lógica
1. Validar formato correo con `isValidEmail`.
2. Llamar `POST /auth/password/forgot` con `{ correo }`.
3. Siempre mostrar el mensaje de éxito tras respuesta 200 — nunca revelar si el correo existe.
4. Si responde 429 → mostrar `disponible_en` formateado.
5. Deshabilitar botón mientras hay request en curso.

---

## Página 6: `src/pages/auth/ResetPassword.jsx`

### UI
- Card centrada con:
  - Título "Nueva contraseña"
  - Input password (type password, con toggle show/hide)
  - Input confirmar password (type password, con toggle show/hide)
  - Checklist de requisitos de password en tiempo real
  - Botón "Cambiar contraseña"
- Tras éxito → mostrar "Contraseña actualizada. Ya puedes ingresar." + link a `/login`

### Lógica
1. Al montar: leer `token` de query params (`?token=XXXX`).
2. Si no hay token → redirigir a `/recuperar-password`.
3. Validar `isValidPassword` y que ambos passwords coincidan.
4. Llamar `POST /auth/password/reset` con `{ token, password }`.
5. Si responde 200 → mostrar mensaje de éxito.
6. Si responde 404 → "Enlace inválido."
7. Si responde 409 con token usado → "Este enlace ya fue usado."
8. Si responde 410 → "Enlace expirado." + link a `/recuperar-password`.
9. Si responde 409 con password igual → "La nueva contraseña debe ser diferente a la actual."
10. Deshabilitar botón mientras hay request en curso.

---

## Página 7: `src/pages/auth/CuentaPendiente.jsx`

### UI
- Card centrada con:
  - Ícono de reloj o advertencia
  - Título según estado del usuario:
    - `PENDIENTE_VERIFICACION` → "Verifica tu correo electrónico"
    - `EN_REVISION` → "Tu cuenta está en revisión"
    - cualquier otro → "Acceso restringido"
  - Mensaje explicativo según estado
  - Botón "Cerrar sesión" que llama `logout()` y redirige a `/login`

---

## Componente compartido: `src/components/ui/PasswordInput.jsx`

Crea un componente reutilizable para inputs de password:
- Props: `value`, `onChange`, `placeholder`, `name`, `error`
- Toggle interno show/hide con ícono de ojo
- Muestra `error` debajo si existe
- Se usa en Login, Register, RegisterTienda y ResetPassword

---

## Convenciones para esta fase

- Usar Tailwind CSS para todos los estilos — sin CSS externo.
- Todos los formularios con estado local `useState` — sin librerías de forms.
- Todos los errores del backend se leen desde `error.response.data.mensaje` o
  `error.response.data.error`.
- El botón de submit siempre muestra estado de carga: texto cambia a "Cargando..."
  y se deshabilita durante el request.
- No usar `alert()` ni `console.log()` en producción.
- Importar siempre axios desde `src/api/axios.js`.
- Importar siempre helpers desde `src/utils/format.js` y `src/utils/validators.js`.

---

## Verificación final

Cuando termines verifica que:
- [ ] `/login` permite ingresar con credenciales válidas y redirige correctamente
- [ ] `/login` muestra error diferenciado por cada tipo de 403
- [ ] `/register` crea cuenta y redirige a `/verificar-email`
- [ ] `/register/tienda` envía multipart/form-data correctamente
- [ ] `/verificar-email?token=XXX` verifica el token automáticamente al cargar
- [ ] `/recuperar-password` siempre muestra mensaje genérico tras enviar
- [ ] `/reset-password?token=XXX` cambia la contraseña correctamente
- [ ] El botón de submit se deshabilita durante todos los requests
- [ ] No hay errores en consola del navegador
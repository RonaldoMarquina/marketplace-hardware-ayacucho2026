# Prompt Codex — Fase 1: Base del proyecto

Lee el archivo `docs/FRONTEND_CONTEXT.md` antes de escribir cualquier línea de código.
Respeta estrictamente la estructura de carpetas, convenciones y orden definidos ahí.

## Tarea

Crea los archivos base del proyecto en este orden exacto. No saltes ninguno.
No crees páginas ni componentes visuales todavía — solo la infraestructura base.

---

## Archivo 1: `src/api/axios.js`

Crea una instancia de Axios con:
- `baseURL`: `http://localhost:5000/api/v1`
- `headers`: `Content-Type: application/json`
- Interceptor de request: lee el token desde `localStorage.getItem('token')` y si
  existe agrega el header `Authorization: Bearer {token}` automáticamente.
- Interceptor de response: si el servidor responde 401, elimina el token de
  localStorage con `localStorage.removeItem('token')` y redirige a `/login`.
- Exportar la instancia como `export default api`.

---

## Archivo 2: `src/context/AuthContext.jsx`

Crea un contexto de autenticación con:

### Estado inicial
```js
{
  usuario: null,      // objeto con id, nombre, correo, rol, es_tienda_verificada, estado
  token: null,        // string JWT
  cargando: true      // true mientras se verifica el token al montar
}
```

### Funciones expuestas en el contexto
- `login(token, datosUsuario)` → guarda token en localStorage, actualiza estado
- `logout()` → elimina token de localStorage, resetea estado a null
- `esAdmin()` → retorna `true` si `usuario.rol === 'ADMIN'`
- `esTienda()` → retorna `true` si `usuario.es_tienda_verificada === true`
- `esActivo()` → retorna `true` si `usuario.estado === 'ACTIVO'`

### Al montar el provider
- Leer token de localStorage.
- Si existe → parsear el payload del JWT (base64 decode de la segunda parte).
- Si el token no está expirado (`exp > Date.now() / 1000`) → restaurar sesión con
  los datos del payload.
- Si está expirado → llamar `logout()`.
- En ambos casos setear `cargando: false` al terminar.

### Exportar
- `export const AuthContext = createContext()`
- `export const AuthProvider = ({ children })` como componente wrapper
- `export default AuthContext`

---

## Archivo 3: `src/hooks/useAuth.js`

Hook simple que consume AuthContext:
```js
import { useContext } from 'react'
import AuthContext from '../context/AuthContext'

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth debe usarse dentro de AuthProvider')
  return context
}
```

---

## Archivo 4: `src/components/layout/ProtectedRoute.jsx`

Componente que protege rutas según rol y estado:

### Props
- `children` — componente a renderizar si pasa la validación
- `requiereAdmin` — boolean, default `false`
- `requiereActivo` — boolean, default `true`

### Lógica
1. Si `cargando === true` → mostrar un `<div>Cargando...</div>` (spinner después).
2. Si no hay `usuario` → redirigir a `/login` con `<Navigate to="/login" replace />`.
3. Si `requiereActivo` y `usuario.estado !== 'ACTIVO'` → redirigir a `/cuenta-pendiente`.
4. Si `requiereAdmin` y `usuario.rol !== 'ADMIN'` → redirigir a `/` con 
   `<Navigate to="/" replace />`.
5. Si pasa todo → renderizar `{children}`.

---

## Archivo 5: `src/routes/AppRoutes.jsx`

Define todas las rutas de la aplicación con React Router v6.
Usa `<BrowserRouter>`, `<Routes>` y `<Route>`.

### Rutas públicas (sin ProtectedRoute)

/                          → pages/anuncios/Feed.jsx (placeholder por ahora)
/buscar                    → pages/anuncios/Buscar.jsx (placeholder)
/anuncios/:id              → pages/anuncios/Detalle.jsx (placeholder)
/login                     → pages/auth/Login.jsx (placeholder)
/register                  → pages/auth/Register.jsx (placeholder)
/register/tienda           → pages/auth/RegisterTienda.jsx (placeholder)
/verificar-email           → pages/auth/VerificarEmail.jsx (placeholder)
/recuperar-password        → pages/auth/RecuperarPassword.jsx (placeholder)
/reset-password            → pages/auth/ResetPassword.jsx (placeholder)
/usuarios/:id/perfil       → pages/usuario/Perfil.jsx (placeholder)
/cuenta-pendiente          → pages/auth/CuentaPendiente.jsx (placeholder)

### Rutas protegidas (con ProtectedRoute requiereActivo=true)

/anuncios/crear            → pages/anuncios/Crear.jsx (placeholder)
/anuncios/:id/editar       → pages/anuncios/Editar.jsx (placeholder)
/usuario/panel             → pages/usuario/Panel.jsx (placeholder)
/usuario/historial         → pages/usuario/Historial.jsx (placeholder)

### Rutas admin (con ProtectedRoute requiereAdmin=true)

/admin/reportados          → pages/admin/Reportados.jsx (placeholder)
/admin/usuarios            → pages/admin/Usuarios.jsx (placeholder)

### Ruta 404

→ componente inline con <h1>404 - Página no encontrada</h1>

### Placeholders
Para cada página que aún no existe crea un componente mínimo:
```jsx
const NombrePagina = () => <div className="p-8 text-center">NombrePagina — en construcción</div>
```
Créalos dentro de sus carpetas correspondientes en `src/pages/`.

---

## Archivo 6: `src/utils/format.js`

```js
// Formatea precio en soles peruanos
// Ejemplo: formatPrice(450) → "S/ 450.00"
export const formatPrice = (precio) => { ... }

// Formatea fecha en español peruano
// Ejemplo: formatDate("2026-06-20T14:30:00") → "20/06/2026"
export const formatDate = (fecha) => { ... }

// Formatea fecha con hora
// Ejemplo: formatDateTime("2026-06-20T14:30:00") → "20/06/2026 14:30"
export const formatDateTime = (fecha) => { ... }

// Formatea calificacion_promedio con 1 decimal
// Si es null retorna "Sin calificaciones"
// Ejemplo: formatRating(4.833) → "4.8"
export const formatRating = (rating) => { ... }

// Retorna la URL completa de una imagen del backend
// Si ruta_relativa es null retorna una imagen placeholder
// Ejemplo: formatImageUrl("/uploads/anuncios/15/abc.jpg") → "http://localhost:5000/uploads/anuncios/15/abc.jpg"
export const formatImageUrl = (rutaRelativa) => { ... }
```

---

## Archivo 7: `src/utils/validators.js`

```js
// Valida email con regex básico
export const isValidEmail = (correo) => { ... }

// Valida password: mín 8 chars, 1 mayúscula, 1 número, 1 carácter especial
export const isValidPassword = (password) => { ... }

// Valida teléfono peruano: exactamente 9 dígitos numéricos
export const isValidPhone = (telefono) => { ... }

// Valida RUC peruano: exactamente 11 dígitos numéricos
export const isValidRUC = (ruc) => { ... }

// Valida precio: decimal positivo con máximo 2 decimales
export const isValidPrice = (precio) => { ... }

// Retorna mensaje de error de password o null si es válido
export const passwordError = (password) => { ... }
```

---

## Archivo 8: `src/main.jsx`

Actualiza el archivo existente para envolver la app con `AuthProvider`:

```jsx
import { AuthProvider } from './context/AuthContext'
import AppRoutes from './routes/AppRoutes'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  </StrictMode>
)
```

---

## Verificación final

Cuando termines todos los archivos verifica que:
- [ ] `npm run dev` corre sin errores
- [ ] La ruta `/` muestra el placeholder del Feed
- [ ] La ruta `/login` muestra el placeholder de Login
- [ ] La ruta `/usuario/panel` redirige a `/login` si no hay token
- [ ] La ruta `/admin/reportados` redirige a `/` si no hay token de admin
- [ ] No hay imports circulares
- [ ] No hay console.error en la consola del navegador
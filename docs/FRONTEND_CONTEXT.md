# Contexto del Proyecto: HardwareAyacucho Frontend

## ¿Qué es el proyecto?

HardwareAyacucho es un marketplace C2C (consumer to consumer) de hardware y tecnología
para la región de Ayacucho, Perú. Permite a usuarios estándar y tiendas verificadas
publicar, buscar y contactar anuncios de componentes, periféricos, monitores y más.

## Stack tecnológico

- React.js + React Router v6
- Tailwind CSS
- Axios
- Vite

## Backend

- API REST en Flask (Python)
- Base URL: `http://localhost:5000/api/v1`
- Autenticación: JWT Bearer Token
  - Se obtiene en `POST /auth/login`
  - Se envía en header: `Authorization: Bearer {token}`
  - Expira en 8 horas
  - Se almacena en localStorage bajo la clave `token`

## Estructura de carpetas (respetar siempre)

src/
├── api/
│   ├── axios.js
│   ├── auth.js
│   ├── anuncios.js
│   ├── usuarios.js
│   └── transacciones.js
├── assets/
├── components/
│   ├── ui/
│   └── layout/
├── context/
│   └── AuthContext.jsx
├── hooks/
│   └── useAuth.js
├── pages/
│   ├── auth/
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   └── RecuperarPassword.jsx
│   ├── anuncios/
│   │   ├── Feed.jsx
│   │   ├── Detalle.jsx
│   │   ├── Crear.jsx
│   │   └── Editar.jsx
│   ├── usuario/
│   │   ├── Panel.jsx
│   │   ├── Perfil.jsx
│   │   └── Historial.jsx
│   └── admin/
│       ├── Reportados.jsx
│       └── Usuarios.jsx
├── routes/
│   └── AppRoutes.jsx
└── utils/
├── format.js
└── validators.js

## Roles y acceso

| Rol               | Descripción                                              |
|-------------------|----------------------------------------------------------|
| USER_ESTANDAR     | Puede publicar hasta 25 anuncios, comprar y vender       |
| TIENDA_VERIFICADA | Sin límite de anuncios, tiene perfil de tienda           |
| ADMIN             | Accede a rutas /admin, modera anuncios y usuarios        |
| Visitante         | Solo puede ver feed, búsqueda y detalle sin JWT          |

El campo `es_tienda_verificada: boolean` reemplaza al rol crudo en todas las respuestas
públicas. El campo `rol` crudo solo aparece en login y panel propio.

## Estados de cuenta

| Estado                  | Puede login | Puede publicar |
|-------------------------|-------------|----------------|
| ACTIVO                  | ✅          | ✅             |
| PENDIENTE_VERIFICACION  | ❌          | ❌             |
| EN_REVISION             | ❌          | ❌             |
| BLOQUEADO               | ❌          | ❌             |

## Estados del anuncio

| Estado   | Visible en feed | Editable | Terminal |
|----------|-----------------|----------|----------|
| ACTIVO   | ✅              | ✅       | ❌       |
| INACTIVO | ❌              | ✅       | ❌       |
| VENDIDO  | ❌              | ❌       | ✅       |
| BLOQUEADO| ❌              | ❌       | ✅ admin |

## Endpoints principales por módulo

### Auth
- `POST /auth/register` — registro usuario estándar
- `POST /auth/register/tienda` — registro tienda (multipart/form-data)
- `POST /auth/login` — login, retorna JWT
- `GET  /auth/verify-email?token=` — verificar correo
- `POST /auth/verify-email/resend` — reenviar verificación
- `POST /auth/password/forgot` — solicitar reset de contraseña
- `POST /auth/password/reset` — confirmar nueva contraseña

### Anuncios
- `GET    /anuncios` — feed público paginado
- `GET    /anuncios/buscar` — búsqueda con filtros técnicos
- `GET    /anuncios/:id` — detalle público (JWT opcional)
- `POST   /anuncios` — crear anuncio 🔒
- `PATCH  /anuncios/:id` — editar anuncio 🔒
- `PATCH  /anuncios/:id/desactivar` — desactivar 🔒
- `PATCH  /anuncios/:id/reactivar` — reactivar 🔒
- `PATCH  /anuncios/:id/vendido` — marcar vendido con comprador_id 🔒
- `POST   /anuncios/:id/media` — subir imágenes/video 🔒
- `PATCH  /anuncios/:id/media/orden` — reordenar imágenes 🔒
- `DELETE /anuncios/:id/media/:media_id` — eliminar media 🔒
- `PUT    /anuncios/:id/media/:media_id` — reemplazar media 🔒
- `GET    /anuncios/:id/contacto` — URL WhatsApp 🔒
- `POST   /anuncios/:id/reportar` — reportar anuncio 🔒

### Usuarios
- `GET  /usuarios/:id/perfil` — perfil público
- `GET  /usuarios/me/panel` — panel privado 🔒
- `GET  /usuarios/me/transacciones` — historial 🔒

### Transacciones
- `POST /transacciones/:id/calificar/vendedor` — calificar vendedor 🔒
- `POST /transacciones/:id/calificar/comprador` — calificar comprador 🔒

### Admin 🔒 ADMIN
- `GET   /admin/anuncios/reportados`
- `PATCH /admin/anuncios/:id/bloquear`
- `PATCH /admin/anuncios/:id/desbloquear`
- `GET   /admin/usuarios`
- `GET   /admin/usuarios/:id`
- `PATCH /admin/usuarios/:id/activar`
- `PATCH /admin/usuarios/:id/rechazar`
- `PATCH /admin/usuarios/:id/bloquear`
- `PATCH /admin/usuarios/:id/desbloquear`

## Convenciones de respuesta del backend

- Paginación siempre con: `total`, `pagina_actual`, `total_paginas`, `limit`,
  `tiene_siguiente`, `tiene_anterior`
- Sin resultados → 200 con `data: []`, nunca 404
- `imagen_principal` puede ser `null` → el frontend debe manejar fallback
- `updated_at` puede ser `null` si nunca fue editado
- `calificacion_promedio` puede ser `null` si no tiene calificaciones — no es lo mismo que 0
- `telefono` del vendedor: `null` sin JWT, valor real con JWT
- Media del anuncio: imágenes con `orden ASC`, video siempre al final con `orden: null`

## Convenciones del frontend

- Todos los imports de axios van desde `src/api/axios.js`, nunca directamente desde axios
- El token JWT se lee siempre desde `localStorage.getItem('token')`
- Los interceptors de axios en `axios.js` agregan el header Authorization automáticamente
- Las rutas protegidas usan el componente `ProtectedRoute` en `AppRoutes.jsx`
- Los precios se formatean siempre con 2 decimales y símbolo `S/` (soles peruanos)
- Las fechas se formatean en español peruano: `dd/mm/yyyy`
- Los errores del backend se leen desde `error.response.data`
- Las imágenes del backend se sirven desde `http://localhost:5000{ruta_relativa}`
- Nunca hardcodear la baseURL fuera de `axios.js`

## Categorías y subcategorías válidas

COMPONENTES        → Procesador, Placa Madre, RAM, GPU, Almacenamiento, Fuente Poder
REFRIGERACION      → Aire, Líquida AIO, Custom Loop, Pasta Térmica
GABINETES          → Case, Ventiladores, Soportes GPU, Filtros
PERIFERICOS        → Teclado, Mouse, Auriculares, Mousepad, Micrófono, Webcam
MONITORES          → Monitor, Soportes VESA, Cables
REDES              → Tarjeta Red, Router, Adaptadores, UPS
MOBILIARIO         → Silla Gamer, Escritorio, Accesorios
ALMACENAMIENTO_EXTERNO → SSD Externo, HDD Externo, Externos, NAS
ACCESORIOS         → Cables, Limpieza, Organizadores, RGB
PORTATILES         → Laptop, Tablet

## Condiciones válidas

`NUEVO` | `COMO_NUEVO` | `USADO` | `PARA_REPUESTOS`

## Archivos base que Codex debe crear primero

En este orden exacto antes de cualquier página:

1. `src/api/axios.js` — instancia Axios con baseURL e interceptor JWT
2. `src/context/AuthContext.jsx` — estado global de autenticación
3. `src/hooks/useAuth.js` — hook para consumir AuthContext
4. `src/routes/AppRoutes.jsx` — todas las rutas con ProtectedRoute
5. `src/components/layout/Navbar.jsx` — navegación principal
6. `src/utils/format.js` — formatPrice, formatDate
7. `src/utils/validators.js` — validaciones de formularios
# STACK.md - HardwareAyacucho

## Frontend

- React
- React Router
- Vite
- Tailwind CSS
- Axios

Configuracion relevante:

- `VITE_API_ORIGIN` para resolver API REST y URLs de imagenes contra el backend

## Backend

- Python 3.14
- Flask
- SQLAlchemy
- Flask-Migrate
- Flask-JWT-Extended
- Marshmallow
- Flask-CORS
- Flask-WTF
- bcrypt

## Base de Datos

- MySQL
- Charset `utf8mb4`
- Collation `utf8mb4_unicode_ci`

## Calidad y Validacion

- PyTest
- pytest-cov
- Pylint
- SonarQube
- Postman

## Arquitectura

Arquitectura por capas:

```text
Frontend
  -> API REST
  -> Routes
  -> Controllers
  -> Services
  -> Repositories
  -> Models
  -> MySQL
```

## Correo transaccional

El backend ya soporta tres tipos principales de correo:

- verificacion de cuenta
- recuperacion de contrasena
- aviso al vendedor o tienda cuando un anuncio recibe un reporte

## Convenciones clave

- Backend Python: `snake_case`
- Clases: `PascalCase`
- JSON de la API: `snake_case` salvo decisiones heredadas del frontend cuando
  aplique
- Endpoints REST bajo `/api/v1`
- Secrets y configuracion sensible via `.env`

## Variables de entorno base

```text
SECRET_KEY
JWT_SECRET_KEY
DATABASE_URL
UPLOAD_FOLDER
MAX_CONTENT_LENGTH
FRONTEND_URL
VITE_API_ORIGIN
EMAIL_DELIVERY_MODE
EMAIL_PUBLIC_PRODUCTION
EMAIL_FROM
EMAIL_SUBJECT_PREFIX
SMTP_HOST
SMTP_PORT
SMTP_USERNAME
SMTP_PASSWORD
SMTP_USE_TLS
SMTP_USE_SSL
SMTP_TIMEOUT_SECONDS
```

## Restricciones tecnicas

- La logica de negocio vive en `services/`
- Los controladores no deben consultar la base de datos directamente
- La persistencia vive en `repositories/` y modelos ORM
- Toda respuesta de API debe ser JSON
- Toda funcionalidad nueva debe incluir pruebas automatizadas
- La carpeta de uploads debe resolverse de forma estable aun cuando
  `UPLOAD_FOLDER` se declare como ruta relativa del workspace

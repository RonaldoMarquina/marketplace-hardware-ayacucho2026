# STACK.md

# STACK.md — HardwareAyacucho

## Frontend

- React.js + React Router  
- Tailwind CSS  
- Axios  

## Backend

- Python 3.x + Flask  
- SQLAlchemy + Flask-Migrate  
- Flask-JWT-Extended  
- Flask-CORS  
- Marshmallow  
- bcrypt (cost=10)  

## Base de Datos

- MySQL — charset utf8mb4_unicode_ci  

## Autenticación

- JWT HS256 — vigencia 8h — secret en `.env`  

## Testing

- PyTest  
- Postman  

## Calidad

- Pylint  
- Bandit  

# Arquitectura

Arquitectura por capas.

```
Frontend
      │
 REST API
      │
Routes
      │
Controllers
      │
Services
      │
Repositories
      │
Models
      │
MySQL
```

# Estructura del Backend

```
backend/
│
├── app/
│   ├── routes/
│   ├── controllers/
│   ├── services/
│   ├── repositories/
│   ├── models/
│   ├── schemas/
│   ├── validators/
│   ├── middleware/
│   ├── utils/
│   ├── config/
│   └── tests/
│
├── migrations/
├── uploads/
├── requirements.txt
└── run.py
```

# Principios

- Arquitectura REST.
- Separación por capas.
- Código reutilizable.
- Responsabilidad única.
- Baja dependencia entre módulos.
- Validaciones centralizadas.
- Manejo centralizado de errores.

# Convenciones

- Backend: snake_case
- Clases: PascalCase
- JSON: camelCase
- Endpoints: kebab-case

# Dependencias Obligatorias

- Flask
- SQLAlchemy
- Flask-JWT-Extended
- Flask-Migrate
- Flask-CORS
- Marshmallow
- bcrypt
- PyMySQL
- python-dotenv
- Pillow

# Variables de Entorno

```
SECRET_KEY
JWT_SECRET_KEY
DATABASE_URL
UPLOAD_FOLDER
MAX_CONTENT_LENGTH
```

# Restricciones

- No modificar la arquitectura.
- No acceder directamente a la base de datos desde los controladores.
- Toda lógica de negocio pertenece a Services.
- Toda consulta a la base de datos pertenece a Repositories.
- Toda validación pertenece a Validators o Schemas.
- Toda respuesta debe ser JSON.
- Toda funcionalidad nueva debe incluir pruebas unitarias.
```
# Arquitectura y Metodología de Software — HardwareAyacucho

## Introducción

Este documento describe la **metodología de diseño de software** y la **arquitectura general** utilizada en el proyecto HardwareAyacucho, un marketplace clasificado para la compra y venta de hardware en Ayacucho, Perú.

---

## 1. METODOLOGÍA DE DISEÑO DE SOFTWARE

### 1.1 Enfoque General

Se utiliza una **metodología ágil iterativa** basada en **Historias de Usuario (HU)**, donde cada HU representa una funcionalidad completa con flujo end-to-end:

```
Diseño → Desarrollo → Testing → Documentación → Entrega
```

Cada HU incluye:
- **Frontend:** Interfaz de usuario
- **Backend:** API REST, lógica de negocio
- **Testing:** Pruebas automatizadas (PyTest + Postman)
- **Documentación:** Guías de usuario y API

### 1.2 Principios Clave de Diseño

#### **1. Separación de Responsabilidades (SoC)**
Cada componente tiene una única responsabilidad bien definida:
- Routes → Definir endpoints
- Controllers → Procesar requests
- Services → Implementar lógica
- Repositories → Acceder a datos
- Models → Definir entidades

#### **2. DRY (Don't Repeat Yourself)**
- Código reutilizable en Services
- Validadores centralizados
- Funciones de utilidad en `utils/`

#### **3. KISS (Keep It Simple, Stupid)**
- Funciones pequeñas y cohesivas
- Evitar complejidad innecesaria
- Nombres descriptivos y claros

#### **4. SOLID**

| Principio | Aplicación |
|-----------|-----------|
| **S** - Single Responsibility | Cada clase/función hace una cosa |
| **O** - Open/Closed | Abierto a extensión, cerrado a modificación |
| **L** - Liskov Substitution | Subclases son sustituibles |
| **I** - Interface Segregation | Interfaces específicas, no genéricas |
| **D** - Dependency Inversion | Depender de abstracciones, no concreciones |

#### **5. Validación Centralizada**
- Schemas (Marshmallow) para estructura JSON
- Validators para lógica de negocio
- Middleware para autenticación

#### **6. Manejo Centralizado de Errores**
- Códigos de error estandarizados
- Respuestas JSON uniformes
- Excepciones capturadas en Controllers

---

## 2. ARQUITECTURA DEL PROYECTO

### 2.1 Arquitectura General: Layered (Por Capas)

```
┌─────────────────────────────────────────┐
│         FRONTEND (React)                │
│  ├─ Components                          │
│  ├─ Pages                               │
│  ├─ Hooks Custom                        │
│  ├─ Context (estado global)             │
│  └─ Services (API calls con Axios)      │
└────────────────┬────────────────────────┘
                 │ HTTP REST (/api/v1)
┌────────────────▼────────────────────────┐
│         BACKEND (Flask + Python)        │
├─────────────────────────────────────────┤
│  ┌─ ROUTES (Endpoints REST)            │
│  │                                      │
│  └─▶ @app.route('/api/v1/...')        │
│                                         │
│  ┌─ CONTROLLERS (Request/Response)     │
│  │                                      │
│  └─▶ def get_anuncio(id): ...         │
│                                         │
│  ┌─ SERVICES (Lógica de Negocio)      │
│  │                                      │
│  └─▶ def obtener_anuncio_con_fotos()  │
│                                         │
│  ┌─ REPOSITORIES (Acceso a BD)        │
│  │                                      │
│  └─▶ def get_anuncio_by_id(id)        │
│                                         │
│  ┌─ MODELS (Entidades ORM)            │
│  │                                      │
│  └─▶ class Anuncio(db.Model)          │
│                                         │
│  ┌─ MIDDLEWARE (Seguridad)            │
│  │                                      │
│  └─▶ @verify_token                    │
│                                         │
│  ┌─ UTILS (Funciones Reutilizables)   │
│  │                                      │
│  └─▶ def generar_jwt(), validar_email()│
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│    MYSQL DATABASE (utf8mb4_unicode_ci)  │
│  ├─ usuarios                            │
│  ├─ anuncios                            │
│  ├─ imagenes_anuncio                    │
│  ├─ calificaciones                      │
│  ├─ transacciones                       │
│  ├─ contactos_log                       │
│  ├─ reportes                            │
│  ├─ admin_logs                          │
│  └─ tokens_verificacion                 │
└─────────────────────────────────────────┘
```

### 2.2 Flujo de Datos (Request-Response)

```
1. Cliente HTTP (Frontend)
   ↓
2. Route Handler (@app.route)
   ↓
3. Middleware (JWT, CORS, validación)
   ↓
4. Controller (parsear request)
   ↓
5. Service (lógica de negocio)
   ↓
6. Repository (queries SQL con SQLAlchemy)
   ↓
7. MySQL (persistencia)
   ↓
8. Repository (retorna datos)
   ↓
9. Service (procesa datos)
   ↓
10. Controller (prepara respuesta JSON)
   ↓
11. Route (devuelve HTTP response)
   ↓
12. Frontend (procesa JSON, actualiza UI)
```

### 2.3 Componentes Principales

#### **Frontend**
- **Framework:** React.js + React Router
- **Estilos:** Tailwind CSS
- **HTTP Client:** Axios
- **Estado:** Context API
- **Estructura:**
  ```
  src/
  ├─ components/      (componentes reutilizables)
  ├─ pages/          (vistas/pantallas)
  ├─ hooks/          (custom hooks)
  ├─ context/        (estado global)
  ├─ api/            (servicios HTTP)
  ├─ utils/          (funciones auxiliares)
  └─ routes/         (definición de rutas)
  ```

#### **Backend**
- **Framework:** Flask (microframework ligero)
- **ORM:** SQLAlchemy
- **Autenticación:** JWT HS256 (8h)
- **Base de Datos:** Flask-Migrate (Alembic)
- **Validación:** Marshmallow
- **Seguridad:** bcrypt (cost=10), Flask-CORS
- **Herramientas:** Pylint, Bandit

#### **Base de Datos**
- **Motor:** MySQL 8.0+
- **Charset:** utf8mb4_unicode_ci (soporta emojis y caracteres especiales)
- **Tablas:** Normalizadas a 3FN
- **ORM:** SQLAlchemy (no SQL puro)

### 2.4 Estructura de Directorios (Backend)

```
backend/
│
├── app/
│   ├── __init__.py              (inicialización de Flask)
│   ├── config.py                (configuraciones por env)
│   │
│   ├── routes/                  (definición de endpoints)
│   │   ├── admin.py
│   │   ├── auth.py
│   │   ├── anuncios.py
│   │   ├── transacciones.py
│   │   └── usuarios.py
│   │
│   ├── controllers/             (manejo de requests)
│   │   ├── admin_controller.py
│   │   ├── auth_controller.py
│   │   ├── anuncio_controller.py
│   │   ├── transaccion_controller.py
│   │   └── usuario_controller.py
│   │
│   ├── services/                (lógica de negocio)
│   │   ├── auth_service.py
│   │   ├── anuncio_service.py
│   │   ├── usuario_service.py
│   │   └── email_service.py
│   │
│   ├── repositories/            (acceso a datos)
│   │   ├── auth_repository.py
│   │   ├── anuncio_repository.py
│   │   ├── usuario_repository.py
│   │   └── transaccion_repository.py
│   │
│   ├── models/                  (entidades ORM)
│   │   ├── __init__.py
│   │   ├── usuario.py
│   │   ├── anuncio.py
│   │   ├── media_anuncio.py
│   │   ├── calificacion.py
│   │   ├── transaccion.py
│   │   ├── reporte.py
│   │   ├── tienda.py
│   │   └── token_verificacion.py
│   │
│   ├── schemas/                 (validación Marshmallow)
│   │   ├── usuario_schema.py
│   │   ├── anuncio_schema.py
│   │   ├── transaccion_schema.py
│   │   └── media_anuncio_schema.py
│   │
│   ├── validators/              (lógica de validación)
│   │   ├── usuario_validator.py
│   │   ├── anuncio_validator.py
│   │   └── email_validator.py
│   │
│   ├── middleware/              (interceptores)
│   │   ├── auth.py              (@verify_token)
│   │   ├── error_handler.py      (manejo de errores)
│   │   └── cors.py
│   │
│   ├── utils/                   (funciones reutilizables)
│   │   ├── jwt_utils.py
│   │   ├── email_utils.py
│   │   ├── file_utils.py
│   │   ├── validators_utils.py
│   │   └── constants.py
│   │
│   └── tests/                   (pruebas)
│       ├── conftest.py
│       └── test_*.py
│
├── migrations/                  (versionado de BD)
├── uploads/                     (archivos subidos)
├── requirements.txt
├── run.py
└── pytest.ini
```

---

## 3. PATRONES DE DISEÑO UTILIZADOS

### 3.1 MVC (Model-View-Controller) Extendido

```
Model       → ORM SQLAlchemy (modelos.py)
View        → Templates/JSON responses
Controller  → Controllers que usan Services
Service     → Lógica de negocio
Repository  → Acceso a datos
```

### 3.2 Repository Pattern

Abstrae el acceso a datos mediante interfaces consistentes:

```python
# En Repository
def get_anuncio_by_id(anuncio_id):
    return db.session.query(Anuncio).filter_by(id=anuncio_id).first()

# En Service
def obtener_anuncio(anuncio_id):
    anuncio = anuncio_repository.get_anuncio_by_id(anuncio_id)
    if not anuncio:
        raise ValueError("Anuncio no encontrado")
    return anuncio

# En Controller
def get_anuncio(anuncio_id):
    try:
        anuncio = anuncio_service.obtener_anuncio(anuncio_id)
        return jsonify(success=True, data=anuncio)
    except ValueError as e:
        return jsonify(success=False, error=str(e)), 404
```

### 3.3 Service Locator Pattern

Services centralizan la lógica:

```python
# En routes/anuncios.py
@anuncios_bp.route('/<int:anuncio_id>', methods=['GET'])
def get_anuncio_detalle(anuncio_id):
    # El controller delega al service
    return anuncio_controller.get_anuncio_detalle(anuncio_id)

# En controllers/anuncio_controller.py
def get_anuncio_detalle(anuncio_id):
    anuncio = anuncio_service.obtener_anuncio_con_fotos(anuncio_id)
    return jsonify(success=True, data=anuncio_schema.dump(anuncio))

# En services/anuncio_service.py
def obtener_anuncio_con_fotos(anuncio_id):
    anuncio = anuncio_repository.get_anuncio_by_id(anuncio_id)
    # Lógica de negocio compleja aquí
    return anuncio
```

### 3.4 Factory Pattern (JWT)

```python
# En utils/jwt_utils.py
def generar_token(usuario_id, rol):
    """Factory de JWT tokens"""
    payload = {
        'usuario_id': usuario_id,
        'rol': rol,
        'exp': datetime.utcnow() + timedelta(hours=8)
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'])
```

### 3.5 Middleware Pattern

```python
# En middleware/auth.py
def verify_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'])
            request.usuario = {'id': payload['usuario_id'], 'rol': payload['rol']}
        except:
            return jsonify(success=False, error='UNAUTHORIZED'), 401
        return f(*args, **kwargs)
    return decorated

# En routes
@anuncios_bp.route('', methods=['POST'])
@verify_token
def crear_anuncio():
    usuario_id = request.usuario['id']  # Disponible tras middleware
    ...
```

---

## 4. PATRONES REST

### 4.1 Convenciones de Endpoints

```
GET    /api/v1/anuncios              # Listar
GET    /api/v1/anuncios/{id}         # Obtener uno
POST   /api/v1/anuncios              # Crear
PUT    /api/v1/anuncios/{id}         # Reemplazar
PATCH  /api/v1/anuncios/{id}         # Actualizar parcial
DELETE /api/v1/anuncios/{id}         # Eliminar (borrado lógico)
```

### 4.2 Respuestas Estándar

**Éxito (200/201):**
```json
{
  "success": true,
  "message": "Operación realizada correctamente.",
  "data": {
    "id": 1,
    "titulo": "RTX 4090",
    "precio": 5000
  }
}
```

**Error (4xx/5xx):**
```json
{
  "success": false,
  "error": "VALIDATION_ERROR",
  "message": "El precio debe ser mayor a 0."
}
```

### 4.3 Códigos HTTP Utilizados

| Código | Significado | Caso de Uso |
|--------|------------|-----------|
| 200 | OK | Consulta exitosa |
| 201 | Created | Recurso creado |
| 204 | No Content | Eliminación exitosa |
| 400 | Bad Request | Solicitud inválida |
| 401 | Unauthorized | Sin autenticación |
| 403 | Forbidden | Sin permisos (rol insuficiente) |
| 404 | Not Found | Recurso no existe |
| 409 | Conflict | Conflicto (ej: email duplicado) |
| 415 | Unsupported Media Type | Archivo no válido |
| 422 | Unprocessable Entity | Validación fallida |
| 500 | Internal Server Error | Error del servidor |

### 4.4 Paginación

```
GET /api/v1/anuncios?page=1&limit=20

Respuesta:
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150
  }
}
```

### 4.5 Filtrado y Ordenamiento

```
GET /api/v1/anuncios?categoria=gpu&estado=activo&sort=precio&order=asc
```

---

## 5. CONVENCIONES DE CÓDIGO

### 5.1 Nomenclatura

| Elemento | Formato | Ejemplo |
|----------|---------|---------|
| Variables | snake_case | `usuario_id`, `es_activo` |
| Funciones | snake_case | `obtener_usuario()`, `validar_email()` |
| Clases | PascalCase | `Usuario`, `AnuncioService` |
| Constantes | UPPER_SNAKE_CASE | `MAX_FILE_SIZE`, `JWT_EXPIRY` |
| Archivos | snake_case | `usuario_service.py` |
| Endpoints | kebab-case | `/api/v1/user-profile`, `/api/v1/anuncios-activos` |
| JSON (Frontend) | camelCase | `{ userId, userName, isActive }` |

### 5.2 Estructura de Funciones

```python
def obtener_anuncio(anuncio_id: int) -> dict:
    """
    Obtiene un anuncio por su ID.
    
    Args:
        anuncio_id: ID del anuncio a consultar
        
    Returns:
        dict: Anuncio con sus imágenes y detalles
        
    Raises:
        ValueError: Si el anuncio no existe
    """
    # 1. Validar entrada
    if not isinstance(anuncio_id, int) or anuncio_id <= 0:
        raise ValueError("ID debe ser un entero positivo")
    
    # 2. Acceder a datos
    anuncio = anuncio_repository.get_anuncio_by_id(anuncio_id)
    
    # 3. Validar resultado
    if not anuncio:
        raise ValueError(f"Anuncio {anuncio_id} no encontrado")
    
    # 4. Procesar y retornar
    return {
        'id': anuncio.id,
        'titulo': anuncio.titulo,
        'precio': anuncio.precio
    }
```

### 5.3 Estructura de Classes

```python
class AnuncioService:
    """Servicio de gestión de anuncios."""
    
    def __init__(self, anuncio_repo: AnuncioRepository):
        """Inyección de dependencias."""
        self.repo = anuncio_repo
    
    def crear_anuncio(self, datos: dict) -> Anuncio:
        """Crear nuevo anuncio (lógica de negocio)."""
        # Validar
        # Procesar
        # Guardar
        pass
    
    def actualizar_anuncio(self, anuncio_id: int, datos: dict) -> Anuncio:
        """Actualizar anuncio."""
        pass
    
    def eliminar_anuncio(self, anuncio_id: int) -> bool:
        """Eliminar anuncio (borrado lógico)."""
        pass
```

---

## 6. SEGURIDAD

### 6.1 Autenticación: JWT (JSON Web Tokens)

```python
# En auth_service.py
def login(email: str, password: str) -> str:
    usuario = usuario_repository.get_by_email(email)
    
    if not usuario or not bcrypt.checkpw(password.encode(), usuario.password_hash):
        raise ValueError("Credenciales inválidas")
    
    if usuario.estado != 'ACTIVO':
        raise ValueError("Usuario no verificado")
    
    token = generar_token(usuario.id, usuario.rol)
    return token

# Token estructura:
{
  "usuario_id": 5,
  "rol": "USER_ESTANDAR",
  "exp": "2026-07-02T16:00:00Z"
}
```

**Características:**
- Algoritmo: HS256
- Vigencia: 8 horas
- Secret guardado en `.env`
- No refresh token (MVP)

### 6.2 Autorización: Control de Acceso

```python
# Middleware verifica rol
@app.route('/api/v1/admin/reportes', methods=['GET'])
@verify_token
def listar_reportes_admin():
    usuario = request.usuario
    if usuario['rol'] != 'ADMIN':
        return jsonify(success=False, error='FORBIDDEN'), 403
    # ...
```

### 6.3 Hashing de Contraseñas

```python
# En usuario_service.py
import bcrypt

def registrar_usuario(email, password):
    salt = bcrypt.gensalt(rounds=10)
    password_hash = bcrypt.hashpw(password.encode(), salt)
    
    usuario = Usuario(email=email, password_hash=password_hash)
    usuario_repository.save(usuario)
    return usuario
```

**Características:**
- bcrypt con cost=10
- Never store plain passwords
- Salt único por usuario

### 6.4 Otras Medidas de Seguridad

- **CORS:** Whitelist de orígenes permitidos
- **Validación de entrada:** Schemas + Validators
- **SQL Injection:** SQLAlchemy ORM (parameterized queries)
- **HTTPS:** En producción
- **Rate Limiting:** Considerar para MVP v2
- **Bandit:** Escaneo de vulnerabilidades en código

---

## 7. TESTING Y CALIDAD

### 7.1 Estrategia de Testing

**Pirámide de Testing:**
```
            ▲
            │ Manual (UI/UX)
            │
       E2E  │ (opcional MVP)
            │
     ▲      │
     │      │ Integration Tests
     │      │ (PyTest + Postman)
  Testing   │
     │      ├─────────────────
     │      │ Unit Tests
     ▼      │ (PyTest)
           ▼
        Base
```

### 7.2 PyTest: Pruebas Unitarias e Integración

**Estructura:**
```
tests/
├── conftest.py            # Fixtures globales
├── test_login.py          # HU-04 (autenticación)
├── test_publicar_anuncio.py  # HU-05
├── test_busqueda_anuncios.py # HU-09/10
├── test_moderacion_anuncios.py # HU-13
└── ...
```

**Convención de nombres:**
```python
def test_{escenario}_{resultado_esperado}():
    """Nombrado describiendo qué se prueba."""
    pass

# Ejemplos:
def test_login_credenciales_validas_retorna_token():
    pass

def test_crear_anuncio_sin_titulo_retorna_400():
    pass

def test_publicar_anuncio_crea_imagen_principal():
    pass
```

**Fixtures compartidas (conftest.py):**
```python
@pytest.fixture
def app():
    """Aplicación Flask para testing."""
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Cliente HTTP para requests."""
    return app.test_client()

@pytest.fixture
def token_usuario(client):
    """JWT válido de usuario estándar."""
    # Registra, verifica y retorna token
    pass

@pytest.fixture
def token_admin(client):
    """JWT válido de admin."""
    pass
```

### 7.3 Postman: Pruebas de API

- **Colecciones organizadas por HU**
- Requests con variables de entorno
- Tests de respuesta (status, body, headers)
- Ejemplos de requests/responses

### 7.4 Herramientas de Calidad

| Herramienta | Propósito | Comando |
|-----------|---------|---------|
| **PyTest** | Tests unitarios | `pytest` |
| **Pylint** | Análisis de código | `pylint app/` |
| **Bandit** | Seguridad | `bandit -r app/` |
| **Coverage** | Cobertura | `pytest --cov=app` |

---

## 8. DESARROLLO DE UNA NUEVA FUNCIONALIDAD

### 8.1 Checklist: Agregar una Característica

1. **Diseño:**
   - [ ] Crear/actualizar HU en `/docs/hu/HU-XX.md`
   - [ ] Definir modelo de datos (entidad, campos)
   - [ ] Diseñar endpoints REST

2. **Backend:**
   - [ ] Crear/actualizar Model en `models/`
   - [ ] Crear Migration (`flask db migrate`)
   - [ ] Crear Schema en `schemas/`
   - [ ] Crear Repository en `repositories/`
   - [ ] Crear Service en `services/`
   - [ ] Crear Controller en `controllers/`
   - [ ] Definir Routes en `routes/`

3. **Frontend:**
   - [ ] Crear componentes en `components/`
   - [ ] Crear página en `pages/`
   - [ ] Agregar servicio API en `api/`
   - [ ] Actualizar rutas en `routes/`
   - [ ] Diseñar UI con Tailwind

4. **Testing:**
   - [ ] Escribir tests unitarios (PyTest)
   - [ ] Escribir tests integración (PyTest)
   - [ ] Crear colección Postman
   - [ ] Verificar cobertura (target 80%+)

5. **Documentación:**
   - [ ] Documentar endpoints en `API_GUIDE.md`
   - [ ] Documentar cambios en base de datos (`DATABASE.md`)
   - [ ] Ejemplo de uso en README

### 8.2 Ejemplo: Agregar Filtro de Precio

**1. Model (models/anuncio.py):**
```python
# No hay cambio (precio ya existe)
class Anuncio(db.Model):
    precio = db.Column(db.Float, nullable=False)
```

**2. Repository (repositories/anuncio_repository.py):**
```python
def get_anuncios_by_rango_precio(min_precio, max_precio):
    return db.session.query(Anuncio).filter(
        Anuncio.precio >= min_precio,
        Anuncio.precio <= max_precio
    ).all()
```

**3. Service (services/anuncio_service.py):**
```python
def filtrar_anuncios(min_precio=None, max_precio=None):
    if min_precio and max_precio:
        return anuncio_repository.get_anuncios_by_rango_precio(
            min_precio, max_precio
        )
    return anuncio_repository.get_all_anuncios()
```

**4. Controller (controllers/anuncio_controller.py):**
```python
def filtrar_anuncios_por_precio():
    min_precio = request.args.get('min', type=float)
    max_precio = request.args.get('max', type=float)
    
    anuncios = anuncio_service.filtrar_anuncios(min_precio, max_precio)
    return jsonify(success=True, data=anuncio_schema.dump(anuncios, many=True))
```

**5. Route (routes/anuncios.py):**
```python
@anuncios_bp.route('', methods=['GET'])
def listar_anuncios():
    return anuncio_controller.filtrar_anuncios_por_precio()
```

**6. Test (tests/test_filtro_precio.py):**
```python
def test_filtrar_anuncios_por_rango_precio(client, token_usuario):
    # Crear anuncios de prueba
    # GET /api/v1/anuncios?min=1000&max=5000
    # Verificar que retorna solo anuncios en rango
    pass
```

---

## 9. CICLO DE VIDA DE UN COMMIT

### 9.1 Formato de Commits (Conventional Commits)

```
tipo: descripción corta (máx 50 caracteres)

Descripción más detallada si es necesario.
Explica el qué y el porqué, no el cómo.

Closes #123
```

**Tipos permitidos:**
- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `refactor:` Cambio de código sin nueva funcionalidad
- `test:` Agregar/modificar tests
- `docs:` Cambios en documentación
- `perf:` Mejoras de rendimiento
- `ci:` Cambios en CI/CD

**Ejemplos:**
```
feat: agregar filtro de precio en búsqueda

Permite a usuarios filtrar anuncios por rango de precio.
Implementa endpoint GET /api/v1/anuncios?min=X&max=Y

fix: validar JWT expirado en middleware

El middleware no capturaba excepciones de token expirado.
Ahora retorna 401 Unauthorized correctamente.

test: cobertura para servicio de anuncios

Agrega tests para casos edge de creación/actualización.
Cobertura sube de 75% a 88%.
```

---

## 10. HERRAMIENTAS Y CONFIGURACIÓN

### 10.1 Tecnologías por Capa

**Frontend:**
- React 18.x
- React Router 6.x
- Tailwind CSS 3.x
- Axios 1.x
- Node.js 18.x (LTS)

**Backend:**
- Python 3.9+
- Flask 2.x
- SQLAlchemy 2.x
- Flask-Migrate (Alembic)
- Flask-JWT-Extended 4.x
- Marshmallow 3.x
- bcrypt 4.x
- PyMySQL 1.x

**Base de Datos:**
- MySQL 8.0+
- Charset: utf8mb4_unicode_ci

**Testing:**
- PyTest 7.x
- Postman 10.x

**Code Quality:**
- Pylint 2.x
- Bandit 1.x

### 10.2 Variables de Entorno (.env)

```bash
# Flask
FLASK_ENV=development
SECRET_KEY=<clave-aleatoria-segura>
JWT_SECRET_KEY=<clave-aleatoria-segura>

# Base de Datos
DATABASE_URL=mysql://usuario:password@localhost:3306/hardware_ayacucho

# Upload
UPLOAD_FOLDER=./uploads
MAX_CONTENT_LENGTH=10485760  # 10MB

# Email (si aplica)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_contraseña_app

# Frontend
VITE_API_BASE_URL=http://localhost:5000/api/v1
```

---

## 11. MEJORES PRÁCTICAS

### 11.1 Desarrollo

- ✅ Escribir tests antes o junto con el código (TDD opcional)
- ✅ Usar type hints en Python
- ✅ Documentar funciones complejas con docstrings
- ✅ Mantener funciones pequeñas (< 20 líneas idealmente)
- ✅ Usar nombres descriptivos y en español/inglés consistente
- ✅ Evitar variables globales
- ✅ No hardcodear valores (usar .env)

### 11.2 Commits

- ✅ Commits frecuentes y pequeños
- ✅ Mensajes claros y descriptivos
- ✅ Una funcionalidad por commit
- ✅ No mezclar refactoring con nuevas features

### 11.3 Code Review

- ✅ Revisar antes de mergear a main
- ✅ Asegurar cumplimiento de convenciones
- ✅ Verificar que hay tests
- ✅ Comprobar que pasan todas las pruebas

### 11.4 Documentación

- ✅ Mantener README actualizado
- ✅ Documentar endpoints en API_GUIDE.md
- ✅ Actualizar DATABASE.md si hay cambios
- ✅ Documentar configuración especial

---

## 12. RECURSOS Y REFERENCIAS

### 12.1 Documentación del Proyecto

- [PROJECT.md](PROJECT.md) — Descripción general
- [STACK.md](STACK.md) — Stack tecnológico
- [API_GUIDE.md](API_GUIDE.md) — API REST
- [CODING_STYLE.md](CODING_STYLE.md) — Convenciones
- [DATABASE.md](DATABASE.md) — Esquema BD
- [TESTING.md](TESTING.md) — Estrategia de testing
- [SECURITY.md](SECURITY.md) — Seguridad
- [FRONTEND_CONTEXT.md](FRONTEND_CONTEXT.md) — Frontend

### 12.2 Historias de Usuario

- [HU-01 al HU-21](hu/) — Funcionalidades del MVP

### 12.3 Enlaces Externos

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [PyTest Guide](https://docs.pytest.org/)
- [React Documentation](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [REST API Best Practices](https://restfulapi.net/)

---

## 13. CONCLUSIÓN

La arquitectura y metodología de HardwareAyacucho está diseñada para:

✅ **Mantenibilidad:** Capas claras y separadas  
✅ **Escalabilidad:** Fácil agregar nuevas features  
✅ **Testabilidad:** Código testeable y cubierto  
✅ **Seguridad:** Autenticación y autorización robustas  
✅ **Calidad:** Convenciones y herramientas automatizadas  
✅ **Documentación:** Código autodocumentado y guías  

Cualquier nuevo desarrollador puede onboardearse rápidamente siguiendo esta guía.

---

**Versión:** 1.0  
**Fecha:** Julio 2026  
**Mantenedor:** Equipo de Desarrollo HardwareAyacucho

# TESTING.md — HardwareAyacucho

## Herramientas

- **PyTest** — tests unitarios e integración (backend)
- **Postman** — tests de endpoints REST (colecciones por HU)


## Estructura de Tests

```
tests/
├── conftest.py          # Fixtures globales (app, db, cliente, tokens)
├── auth/
│   ├── test_hu01.py     # Registro usuario estándar
│   ├── test_hu02.py     # Registro tienda
│   ├── test_hu03.py     # Verificación de correo
│   └── test_hu04.py     # Login / JWT
├── anuncios/
│   ├── test_hu05.py     # Publicar anuncio
│   ├── test_hu06.py     # Carga de imágenes
│   ├── test_hu07.py     # Edición de anuncio
│   ├── test_hu08.py     # Estados / borrado lógico
│   ├── test_hu09.py     # Feed principal
│   ├── test_hu10.py     # Filtrado técnico
│   └── test_hu11.py     # Vista detallada
├── contacto/
│   └── test_hu12.py     # WhatsApp URL
└── admin/
    └── test_hu13.py     # Moderación
```

## Fixtures Base (conftest.py)

```python
import pytest
from app import create_app, db as _db

@pytest.fixture(scope="session")
def app():
    app = create_app("testing")  # BD en memoria o test DB
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def token_usuario(client):
    # Crea usuario ACTIVO y retorna JWT
    pass

@pytest.fixture
def token_admin(client):
    # Crea usuario con rol ADMIN y retorna JWT
    pass

@pytest.fixture
def token_tienda(client):
    # Crea tienda ACTIVO y retorna JWT
    pass
```

## Convención de Tests

```python
# Nombre: test_{escenario}_{resultado_esperado}
def test_login_credenciales_invalidas_retorna_401():
    pass

def test_publicar_anuncio_sin_jwt_retorna_401():
    pass

def test_feed_sin_anuncios_retorna_lista_vacia():
    pass
```

## Casos por HU

### HU-01 Registro Usuario
- ✅ Registro exitoso → 201
- ❌ Correo duplicado → 409
- ❌ Teléfono con formato inválido → 400
- ❌ Password débil → 422
- ❌ Campos vacíos → 400

### HU-02 Registro Tienda
- ✅ Registro exitoso con documento → 201, estado `EN_REVISION`
- ❌ RUC duplicado → 409
- ❌ RUC con formato inválido (≠ 11 dígitos) → 422
- ❌ Documento > 5MB → 413
- ❌ Formato de archivo inválido → 415
- ❌ Sin documento adjunto → 400

### HU-03 Verificación de Correo
- ✅ Token válido → 200, estado `ACTIVO`
- ❌ Token inexistente → 404
- ❌ Token ya usado → 409
- ❌ Token expirado → 410
- ✅ Reenvío exitoso → 200
- ❌ Reenvío con cuenta ya activa → 409

### HU-04 Login
- ✅ Login exitoso → 200 + JWT
- ❌ Correo inexistente → 401 (mismo mensaje que password incorrecto)
- ❌ Password incorrecto → 401
- ❌ Cuenta `PENDIENTE_VERIFICACION` → 403
- ❌ Cuenta `BLOQUEADA` → 403

### HU-05 Publicar Anuncio
- ✅ Publicación exitosa → 201
- ❌ Sin JWT → 401
- ❌ Cuenta no verificada → 403
- ❌ Más de 10 anuncios activos (USER_ESTANDAR) → 403
- ❌ Precio ≤ 0 → 422
- ❌ Título > 100 chars → 422
- ❌ Categoría fuera de ENUM → 422

### HU-06 Imágenes
- ✅ Subida exitosa → 201, primera imagen `es_principal=true`
- ❌ Imagen > 2MB → 413
- ❌ Formato GIF → 415
- ❌ Anuncio ya tiene 5 imágenes → 409
- ❌ Anuncio no pertenece al usuario → 403
- ❌ Sin archivos adjuntos → 400

### HU-07 Editar Anuncio
- ✅ Edición exitosa → 200
- ❌ Body vacío → 400
- ❌ `categoria` en body → 422
- ❌ Anuncio VENDIDO → 409
- ❌ No es propietario → 403

### HU-08 Estados
- ✅ ACTIVO → VENDIDO
- ✅ ACTIVO → INACTIVO
- ✅ INACTIVO → ACTIVO
- ❌ VENDIDO → cualquier estado → 409
- ❌ BLOQUEADO → cualquier acción del vendedor → 403
- ❌ Reactivar con 10 anuncios activos → 403

### HU-09 Feed
- ✅ Feed paginado → 200
- ✅ Sin anuncios → 200 con `data: []`
- ✅ Página fuera de rango → 200 con `data: []`
- ❌ `limit` > 50 → 400
- ❌ `page` negativo → 400

### HU-10 Filtrado
- ✅ Filtro por categoría → 200
- ✅ Filtro por spec_key + spec_value → 200
- ✅ spec_key inexistente → 200 con `data: []`
- ❌ `precio_min` > `precio_max` → 400
- ❌ `spec_key` sin `spec_value` → 400
- ❌ Categoría fuera de ENUM → 422

### HU-11 Detalle
- ✅ Visitante → `telefono: null`
- ✅ Autenticado → `telefono` visible
- ✅ Tienda → incluye objeto `tienda`
- ✅ Propietario ve su INACTIVO → 200
- ❌ Tercero ve INACTIVO → 404
- ❌ Anuncio BLOQUEADO → 404

### HU-12 Contacto WhatsApp
- ✅ URL generada correctamente con prefijo `51`
- ❌ Sin JWT → 401
- ❌ Autocontacto → 409
- ❌ Anuncio no ACTIVO → 404
- ❌ Vendedor sin teléfono → 422

### HU-13 Moderación
- ✅ Reporte exitoso → 201
- ✅ Bloqueo en transacción → anuncio BLOQUEADO + reportes REVISADO
- ✅ Desbloqueo → anuncio ACTIVO
- ❌ Autoreporte → 409
- ❌ Reporte duplicado PENDIENTE → 409
- ❌ No ADMIN en `/admin/*` → 403
- ❌ Bloquear sin `motivo_admin` → 400

---

## Ejecución

```bash
# Todos los tests
pytest

# Por módulo
pytest tests/auth/

# Por HU
pytest tests/auth/test_hu01.py

# Con cobertura
pytest --cov=app --cov-report=term-missing

# Verbose
pytest -v
```

---

## Reglas

- Cada test es independiente — no depende del orden de ejecución.
- BD de test aislada — nunca correr tests contra BD de producción.
- Sin llamadas reales a servicios externos (correo, WhatsApp) — usar mocks.
- Todo endpoint debe tener al menos el caso exitoso y los errores definidos en su HU.
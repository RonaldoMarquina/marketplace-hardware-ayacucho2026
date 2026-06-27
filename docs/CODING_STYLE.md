# CODING_STYLE.md

# Convenciones de Código

## Arquitectura

```
Routes
→ Controllers
→ Services
→ Repositories
→ Models
→ MySQL
```

# Responsabilidades

- **Routes:** Definir endpoints.
- **Controllers:** Recibir solicitudes y devolver respuestas.
- **Services:** Implementar la lógica de negocio.
- **Repositories:** Acceder a la base de datos.
- **Models:** Definir entidades.
- **Schemas/Validators:** Validar datos.
- **Utils:** Funciones reutilizables.

# Convenciones

| Elemento | Formato |
|----------|---------|
| Variables | snake_case |
| Funciones | snake_case |
| Clases | PascalCase |
| Constantes | UPPER_CASE |
| JSON | camelCase |
| Endpoints | kebab-case |

# Principios

- Responsabilidad única.
- Código reutilizable.
- Funciones pequeñas.
- Evitar duplicación (DRY).
- Mantener simplicidad (KISS).

# Reglas

- No lógica de negocio en Controllers.
- No acceso directo a MySQL desde Controllers.
- Reutilizar Services antes de crear nuevos.
- Validar datos antes de procesarlos.
- Manejo centralizado de excepciones.
- Respuestas siempre en JSON.

# Calidad

- Cumplir Pylint.
- Cumplir Bandit.
- Eliminar código muerto.
- Documentar funciones complejas.
- Mantener nombres descriptivos.

# Estructura de Archivos

```
routes/
controllers/
services/
repositories/
models/
schemas/
validators/
middleware/
utils/
tests/
```

# Commits

Formato:

```
tipo: descripción
```

Ejemplos:

```
feat: registro de usuarios
fix: validación de RUC
refactor: servicio de anuncios
test: pruebas de autenticación
docs: actualizar API
```
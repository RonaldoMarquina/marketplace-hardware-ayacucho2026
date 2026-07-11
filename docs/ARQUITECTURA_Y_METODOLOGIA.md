# Arquitectura y Metodologia de Software

## Vision general

HardwareAyacucho se desarrolla con un enfoque iterativo basado en historias de
usuario y con una adopcion hibrida de SDD. Cada HU se implementa de extremo a
extremo, integrando interfaz, backend, persistencia, pruebas y documentacion.

Ciclo de vida aplicado:

```text
Analisis -> Diseno -> Programacion -> Pruebas -> Despliegue
```

Dentro de ese ciclo, SDD se entiende como la capa de especificacion que guia
los cambios funcionales y tecnicos antes o junto a la implementacion.

## Metodologia de trabajo

- desarrollo incremental por HU
- analisis y diseno apoyados en especificaciones del proyecto
- programacion asistida por IA como apoyo de implementacion, no como reemplazo
  de la especificacion
- validacion funcional con PyTest y Postman
- control de calidad con Pylint y SonarQube
- trazabilidad documental en `docs/` y adopcion hibrida con OpenSpec

## SDD aplicado al proyecto

En este proyecto, Spec Driven Development se materializa mediante una
combinacion de especificacion manual y especificacion operativa.

Capas de especificacion usadas:

- `docs/hu/` y documentos funcionales como base manual del sistema
- `openspec/` como capa operativa real de especificaciones incrementales
- `docs/openspec/` como capa explicativa para trazabilidad academica
- asistentes IA como Codex y GitHub Copilot para acelerar implementacion,
  refactor y documentacion tecnica

Esta decision sigue un enfoque brownfield: no se rehace el sistema desde cero,
sino que se organiza la base existente y se gobiernan los cambios nuevos con
especificaciones mas formales.

## Principios de diseno

- separacion de responsabilidades
- codigo reutilizable
- validacion centralizada
- manejo uniforme de errores
- bajo acoplamiento entre capas

## Arquitectura del sistema

El proyecto sigue una arquitectura por capas.

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

## Capas principales

### Frontend

- React
- React Router
- Axios
- Tailwind CSS

Responsabilidades:

- interfaz de usuario
- navegacion
- consumo de API
- gestion de estado de sesion en cliente

### Backend

- Flask
- SQLAlchemy
- Marshmallow
- Flask-JWT-Extended

Responsabilidades:

- exponer endpoints REST
- aplicar reglas de negocio
- validar entradas
- controlar autenticacion y autorizacion
- coordinar persistencia y respuestas JSON

### Base de datos

- MySQL
- esquema principal documentado en `docs/database.sql`

Responsabilidades:

- persistencia transaccional
- integridad referencial
- soporte a anuncios, usuarios, tiendas, reportes, transacciones y
  calificaciones

## Estructura logica del backend

```text
backend/app/
  routes/         definicion de endpoints
  controllers/    entrada y salida HTTP
  services/       logica de negocio
  repositories/   acceso a datos
  models/         entidades ORM
  schemas/        validacion y serializacion
  middleware/     controles transversales
  utils/          funciones auxiliares
```

## Flujo de una solicitud

```text
Cliente -> Route -> Controller -> Service -> Repository -> Model/DB
```

Luego la respuesta vuelve por la misma cadena hasta retornar JSON al cliente.

## Seguridad aplicada a la arquitectura

- JWT en rutas protegidas
- control de rol `ADMIN` en endpoints administrativos
- secretos fuera del repositorio
- validacion de archivos y entradas
- trazabilidad administrativa mediante logs de moderacion y administracion

## Estrategia de calidad

- pruebas unitarias para helpers y validaciones puntuales
- pruebas de integracion para flujos HTTP y reglas de negocio
- cobertura automatizada con `pytest-cov`
- analisis estatico con Pylint
- revision complementaria con SonarQube

## Relacion con OpenSpec

El proyecto adopta un enfoque hibrido:

- `docs/` conserva la base documental del sistema ya implementado
- `openspec/` contiene la especificacion operativa canonica para cambios
  incrementales
- `docs/openspec/` documenta esa adopcion para trazabilidad academica

## Conclusion

La arquitectura elegida prioriza mantenibilidad, claridad de capas, facilidad de
prueba y crecimiento incremental. Esto permite que nuevas funcionalidades se
incorporen sin romper la separacion entre interfaz, logica de negocio y acceso a
datos.

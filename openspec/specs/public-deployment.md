# OS-04 - Despliegue Publico

## Objetivo

Definir la topologia, configuracion minima y validacion operativa para publicar
la plataforma en un entorno academico de bajo costo con servicios externos
reales.

## Reglas funcionales clave

- el frontend publico se despliega en `Vercel`
- el backend publico se despliega en `Render`
- la base remota principal se mantiene en `TiDB Cloud`
- los medios publicos se almacenan fuera del disco efimero del backend
- la salida publica requiere checklist funcional posterior al despliegue

## Reglas tecnicas clave

- `FRONTEND_URL` y `VITE_API_ORIGIN` deben apuntar a URLs publicas reales
- la produccion publica requiere secretos y configuracion real de correo
- las rutas SPA del frontend deben resolverse correctamente en hosting estatico
- la documentacion debe declarar limitaciones del stack gratuito

## Escenarios normativos

### Topologia y URLs reales

#### Scenario: Public topology is documented
- **WHEN** the team prepares the public deployment package
- **THEN** the project MUST document which platform hosts the frontend, which
  platform hosts the backend and which remote database instance is the source of
  truth

#### Scenario: Public services use real URLs
- **WHEN** the frontend and backend are deployed publicly
- **THEN** the frontend MUST consume the backend through a public API base URL
  and the backend MUST expose configuration aligned with that public frontend
  origin

### Configuracion minima de produccion

#### Scenario: Backend public production variables are required
- **WHEN** the backend is prepared for public production
- **THEN** the deployment checklist MUST include `DATABASE_URL`,
  `FRONTEND_URL`, app secrets, JWT secrets and real email configuration as
  required environment variables

#### Scenario: Frontend public production variables are required
- **WHEN** the frontend is prepared for public production
- **THEN** the deployment checklist MUST include the public backend API URL and
  any environment values needed to reach authenticated and public routes without
  localhost fallbacks

### Validacion post-release

#### Scenario: Core public flows are validated after release
- **WHEN** a new public deployment is completed
- **THEN** the team MUST validate at least registration, email verification,
  login, protected access, ad creation and public browsing against the deployed
  environment

#### Scenario: Admin and moderation paths are validated after release
- **WHEN** the public deployment includes administrative capabilities
- **THEN** the team MUST validate admin login, moderation access and at least
  one protected administrative workflow against the deployed environment

### Limitaciones aceptadas del stack gratuito

#### Scenario: Media persistence limitation is declared
- **WHEN** the backend stores uploads on local runtime disk without external
  object storage
- **THEN** the deployment documentation MUST state that uploaded media may not
  remain durable across restarts or redeploys

#### Scenario: Free-tier operational limits are declared
- **WHEN** the platform is released using low-cost or free hosting services
- **THEN** the project MUST document that availability, cold starts or resource
  limits can affect the public demo experience

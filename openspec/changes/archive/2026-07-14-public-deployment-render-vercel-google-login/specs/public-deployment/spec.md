## ADDED Requirements

### Requirement: Public deployment topology must be defined end-to-end
The system MUST define a public deployment topology that connects the Vercel
frontend, the Render backend and TiDB Cloud as the remote primary database for
the academic production environment.

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

### Requirement: Public deployment must declare minimum production configuration
The system MUST define the minimum environment configuration required to start
the backend and frontend safely in a public production context.

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

### Requirement: Public deployment must include post-release validation
The system MUST define a post-release validation path that proves the public
environment works as an integrated platform, not only as isolated services.

#### Scenario: Core public flows are validated after release
- **WHEN** a new public deployment is completed
- **THEN** the team MUST validate at least registration, email verification,
  login, protected access, ad creation and public browsing against the deployed
  environment

#### Scenario: Admin and moderation paths are validated after release
- **WHEN** the public deployment includes administrative capabilities
- **THEN** the team MUST validate admin login, moderation access and at least
  one protected administrative workflow against the deployed environment

### Requirement: Low-cost deployment limitations must be explicit
The system MUST document operational limitations that remain acceptable for a
low-cost academic public deployment.

#### Scenario: Media persistence limitation is declared
- **WHEN** the backend stores uploads on local runtime disk without external
  object storage
- **THEN** the deployment documentation MUST state that uploaded media may not
  remain durable across restarts or redeploys

#### Scenario: Free-tier operational limits are declared
- **WHEN** the platform is released using low-cost or free hosting services
- **THEN** the project MUST document that availability, cold starts or resource
  limits can affect the public demo experience

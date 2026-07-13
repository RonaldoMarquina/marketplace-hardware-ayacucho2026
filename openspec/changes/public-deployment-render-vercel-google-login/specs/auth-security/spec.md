## ADDED Requirements

### Requirement: Public production authentication must align with deployed URLs
The authentication system MUST use production-safe public URLs and environment
configuration when the platform is exposed on the public internet.

#### Scenario: Auth flows use public frontend origin
- **WHEN** the backend generates links or redirects for verification, password
  recovery or authenticated navigation in public production
- **THEN** those flows MUST use the configured public frontend URL instead of
  localhost or development-only origins

#### Scenario: Public auth configuration is reviewed before release
- **WHEN** the deployment checklist for public production is reviewed
- **THEN** the project MUST verify that JWT secrets, app secrets, frontend
  origin and email configuration are set for the real public environment

### Requirement: Google login may extend but must not replace baseline auth
The system MAY add Google login as an optional authentication method, but it
MUST preserve the existing email-and-password flow as a valid baseline for
public production unless a later change explicitly deprecates it.

#### Scenario: Public production can launch without Google login
- **WHEN** the platform is ready for public deployment with working email,
  verification and credential login
- **THEN** the absence of Google login MUST NOT block the public release

#### Scenario: Optional Google login coexists with current accounts
- **WHEN** Google login is later introduced for public production
- **THEN** the integration MUST coexist with the current authentication model
  and MUST NOT require removal of the existing credential-based login path

### Requirement: Google login must use production-safe OAuth configuration
If Google login is implemented, the system MUST require production-safe OAuth
configuration tied to the real deployed environment.

#### Scenario: Google login requires public callback configuration
- **WHEN** Google login is enabled in a public deployment
- **THEN** the system MUST use callback URLs and allowed origins that match the
  real deployed frontend and backend domains

#### Scenario: Google secrets stay outside the repository
- **WHEN** Google login is configured for any environment
- **THEN** OAuth client secrets MUST be supplied through deployment environment
  variables or provider-managed secret storage and MUST NOT be committed to the
  repository

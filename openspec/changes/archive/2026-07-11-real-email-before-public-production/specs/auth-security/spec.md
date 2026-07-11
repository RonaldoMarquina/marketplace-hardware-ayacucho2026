## MODIFIED Requirements

### Requirement: Account lifecycle and credential protection
The platform SHALL enforce verified email ownership before granting access to
normal user accounts and SHALL support secure account recovery for active users.

#### Scenario: Successful email verification delivery is required for public production
- **WHEN** a user registration or store registration creates an email
  verification token in a public production environment
- **THEN** the system MUST attempt delivery through a configured real email
  provider instead of relying only on application logs

#### Scenario: Password reset delivery uses a real email channel
- **WHEN** an active account requests password recovery in a public production
  environment
- **THEN** the system MUST attempt delivery of the reset link through the
  configured real email provider

#### Scenario: Testing avoids external email delivery
- **WHEN** automated tests execute registration, verification resend or password
  reset flows
- **THEN** the system MUST avoid sending real emails and MUST keep the flows
  testable without external provider credentials

#### Scenario: Public production without email configuration is not considered ready
- **WHEN** the deployment checklist or technical documentation is reviewed for a
  public production release
- **THEN** the project MUST treat real transactional email configuration as a
  prerequisite for public launch of the current authentication flows

#### Scenario: Google login remains out of scope for this change
- **WHEN** this change is implemented
- **THEN** the system MUST preserve current authentication behavior without
  requiring social login, leaving Google login for a later change

## MODIFIED Requirements

### Requirement: Account lifecycle and credential protection
The platform SHALL enforce verified email ownership before granting access to
normal user accounts and SHALL support secure account recovery for active users.

#### Scenario: Reset tokens reduce impact of database disclosure
- **WHEN** the system issues a password reset token
- **THEN** the reset flow MUST avoid persisting the reusable plain token value
  in a way that would let a database reader directly use it

#### Scenario: Password reset invalidates prior authenticated sessions
- **WHEN** a password reset completes successfully
- **THEN** the system MUST invalidate or reject authentication tokens issued
  before the credential change

#### Scenario: Password reset remains non-enumerating
- **WHEN** a password recovery request is sent for an unknown, inactive or
  blocked account
- **THEN** the API MUST keep a generic external response that does not confirm
  whether the account is recoverable

#### Scenario: Reset flow emits security audit signals
- **WHEN** password reset is requested, rate-limited, completed or rejected
- **THEN** the system MUST record enough operational evidence to investigate
  abuse without exposing secrets in logs

#### Scenario: Recovery hardening stays independent from Google login
- **WHEN** this security hardening is implemented
- **THEN** the current email-based recovery flow MUST be protected without
  requiring social login as a prerequisite

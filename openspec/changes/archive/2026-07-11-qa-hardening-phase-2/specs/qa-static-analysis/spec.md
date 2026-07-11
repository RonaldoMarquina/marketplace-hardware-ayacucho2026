## MODIFIED Requirements

### Requirement: Unified QA hardening sequence
The project SHALL provide an official local entry point for the complete QA
hardening flow.

#### Scenario: Unified local QA command is available
- **WHEN** a collaborator needs to run the full backend QA hardening flow
- **THEN** the repository MUST define a script or command that executes the
  approved sequence for tests, coverage, static analysis and SonarQube

#### Scenario: Fast and full validations are distinguished
- **WHEN** the QA workflow is documented
- **THEN** the repository MUST differentiate between a lightweight local
  validation path and a complete validation path before deployment

### Requirement: Security hardening guidance is traceable
The project SHALL keep its methodology aligned with the implemented QA flow.

#### Scenario: Methodology reflects current QA hardening
- **WHEN** a reviewer inspects architecture or methodology documentation
- **THEN** the declared quality strategy MUST mention `Bandit` and the unified
  QA hardening flow as part of the current project practice

#### Scenario: Full QA validation result is reproducible
- **WHEN** the official QA hardening command is executed in a prepared local
  environment
- **THEN** the expected result and any environment-dependent limitations MUST be
  documented for future collaborators

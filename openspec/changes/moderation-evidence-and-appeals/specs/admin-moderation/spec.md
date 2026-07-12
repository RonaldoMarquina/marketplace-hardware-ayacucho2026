## MODIFIED Requirements

### Requirement: Moderation cases evolve in phases
The platform SHALL evolve announcement moderation through phased capabilities so
that evidence quality, fairness of review and operational prioritization can
improve without forcing a single oversized redesign.

#### Scenario: Phase 1 enriches the original report
- **WHEN** phase 1 is implemented
- **THEN** a report MUST support reason, descriptive detail and reporter
  evidence, and administrators MUST be able to review that richer case context

#### Scenario: Phase 2 enables defense and appeal
- **WHEN** phase 2 is implemented
- **THEN** a seller or verified store affected by moderation MUST be able to
  submit a traceable appeal or defense with supporting evidence under defined
  rules

#### Scenario: Phase 3 improves prioritization without replacing human review
- **WHEN** phase 3 is implemented
- **THEN** the platform MAY compute trust, abuse or severity signals for admins,
  but final moderation decisions MUST remain under administrative control

### Requirement: Administrative decisions stay auditable
The platform SHALL keep moderation decisions understandable and auditable even
as richer evidence and appeals are introduced.

#### Scenario: Resolution captures administrative reason
- **WHEN** an administrator resolves a moderation case
- **THEN** the system MUST persist the administrative reason and relevant case
  state transition metadata

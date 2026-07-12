## MODIFIED Requirements

### Requirement: Report flows can mature beyond a simple reason code
The marketplace SHALL support the phased evolution of report flows from a simple
reason code to richer user input and later appeal-related interactions.

#### Scenario: Phase 1 lets a user send a richer report
- **WHEN** phase 1 is implemented and an authenticated non-owner reports an
  announcement
- **THEN** the platform MUST allow the user to provide a structured reason,
  descriptive detail and limited supporting evidence

#### Scenario: Phase 2 lets the affected seller respond
- **WHEN** phase 2 is implemented and a report results in a moderation action
- **THEN** the seller or verified store MUST be able to view the case outcome
  and submit a response or appeal under platform rules

#### Scenario: Phase 3 stays optional for deployment readiness
- **WHEN** the team is preparing deployment or public production
- **THEN** the advanced prioritization and abuse-signals layer of phase 3 MUST
  be treated as an enhancement, not as a prerequisite for basic moderation

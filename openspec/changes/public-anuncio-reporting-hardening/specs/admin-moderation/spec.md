## MODIFIED Requirements

### Requirement: Announcement reporting and moderation entrypoint
The platform SHALL provide a usable public entrypoint for authenticated users to
report suspicious announcements while preserving administrative review as the
only authority that changes moderation state.

#### Scenario: Authenticated buyer sees a report action in announcement detail
- **WHEN** an authenticated active user opens the detail of an announcement they
  do not own
- **THEN** the UI MUST expose a visible `Reportar anuncio` action connected to
  the reporting flow

#### Scenario: Owner does not see a self-report path
- **WHEN** the owner opens their own announcement detail
- **THEN** the UI MUST NOT expose a reporting action for that announcement

#### Scenario: Report flow communicates manual review
- **WHEN** a user starts a report from the UI
- **THEN** the platform MUST explain that the report is reviewed by
  administration and does not automatically block the announcement

#### Scenario: Duplicate or abusive reports stay constrained
- **WHEN** a user tries to report the same active announcement twice in the same
  cycle or exceeds the daily report limit
- **THEN** the system MUST reject the action with a controlled response and the
  UI MUST show a clear explanatory message

## MODIFIED Requirements

### Requirement: Public announcement detail actions
The public announcement detail SHALL expose safe user actions appropriate to the
viewer, including contact and moderation-related actions when applicable.

#### Scenario: Non-owner authenticated user can contact and report
- **WHEN** an authenticated user views an active announcement they do not own
- **THEN** the detail page MUST offer both a contact action and a report action
  without exposing owner-only management controls

#### Scenario: Anonymous visitor is redirected before reporting
- **WHEN** a visitor without an authenticated session tries to start the report
  flow
- **THEN** the platform MUST require login before allowing the report request to
  be submitted

#### Scenario: Reporting uses valid predefined reasons
- **WHEN** the user submits a report from the detail page
- **THEN** the UI MUST restrict the selection to the predefined reasons
  supported by the backend contract

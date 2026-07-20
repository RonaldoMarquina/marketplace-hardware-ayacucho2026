## ADDED Requirements

### Requirement: Landing footer presents only marketplace branding
The public landing page SHALL present the HardwareAyacucho copyright in its footer without describing the product as `Proyecto universitario` or associating that footer label with `UNSCH`.

#### Scenario: Visitor reaches the landing footer
- **WHEN** a visitor opens the public landing page and reaches its footer
- **THEN** the footer MUST display the HardwareAyacucho copyright
- **AND** it MUST NOT display `Proyecto universitario - UNSCH.`

#### Scenario: Existing footer navigation remains available
- **WHEN** the academic label is removed from the landing footer
- **THEN** the existing footer navigation links and marketplace description MUST remain unchanged

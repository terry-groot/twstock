## ADDED Requirements

### Requirement: Price parsing handles multiple formats consistently
The system SHALL parse prices from different APIs (TWSE, Taifex) and convert them to float, handling missing/invalid values gracefully.

#### Scenario: Missing price returns None
- **WHEN** API response has no price or returns "-"
- **THEN** system returns None (not throws error) so rendering can display "--"

#### Scenario: String prices are converted
- **WHEN** API returns price as "123.45"
- **THEN** system converts to float 123.45

### Requirement: Alert checking enforces alert priority
The system SHALL check price alerts in order (exact limit hit > approaching limit) and return highest priority alert first.

#### Scenario: Exact limit hit takes priority
- **WHEN** price exactly reaches upper limit
- **THEN** alert shows red "達上限" not yellow "接近上限"

#### Scenario: Both upper and lower conditions trigger
- **WHEN** price triggers both upper-limit-approach and lower-limit-approach simultaneously (edge case)
- **THEN** both alerts are included in result, sorted by severity

### Requirement: CJK character formatting produces aligned columns
The system SHALL correctly measure CJK character widths and format strings for aligned terminal display.

#### Scenario: Chinese names align in table
- **WHEN** table contains "台積電" (6 bytes, 3 wide) and "中華電" (6 bytes, 3 wide)
- **THEN** columns align correctly without visual misalignment

#### Scenario: Mixed ASCII and CJK align
- **WHEN** table contains "TSMC" (4 bytes, 4 wide) and "台積電" (6 bytes, 3 wide)
- **THEN** columns still align correctly

### Requirement: Beep alert works across platforms
The system SHALL produce audible alert on Windows (using winsound), macOS/Linux (using system beep).

#### Scenario: Windows beep plays
- **WHEN** alert condition is triggered on Windows
- **THEN** winsound.Beep(1000, 500) produces sound

#### Scenario: Unix beep works
- **WHEN** alert condition is triggered on macOS/Linux
- **THEN** console beep character is output

## ADDED Requirements

### Requirement: Unit tests cover utility functions
The system SHALL have unit tests for all utility functions (parsing, formatting, alert logic) with 100% code coverage.

#### Scenario: Price parsing tests all edge cases
- **WHEN** unit tests are run
- **THEN** price parser is tested with: None, "-", empty string, valid float, invalid string, scientific notation

#### Scenario: Alert logic tests priority
- **WHEN** unit tests are run
- **THEN** alert checker is tested with: no alerts, upper only, lower only, both, margin edge cases

### Requirement: Integration tests validate data sources
The system SHALL have integration tests that mock API responses and verify data source behavior end-to-end.

#### Scenario: Stock source handles API response correctly
- **WHEN** stock data source integration test runs with mocked TWSE API
- **THEN** it correctly parses response and returns standardized data structure

#### Scenario: Error handling is tested
- **WHEN** integration test mocks an API timeout
- **THEN** stock source correctly retries and eventually returns error state

### Requirement: Configuration loading is tested
The system SHALL have tests for configuration loading with valid and invalid JSON files.

#### Scenario: Invalid JSON fails gracefully
- **WHEN** configuration test tries to load malformed JSON
- **THEN** system raises clear error without crashing

#### Scenario: Legacy config migration is tested
- **WHEN** test runs migration with old format files
- **THEN** new unified format is correctly created

### Requirement: UI rendering is tested
The system SHALL have tests that verify terminal output formatting and CJK alignment.

#### Scenario: Table columns align with mixed content
- **WHEN** render test creates table with ASCII and CJK names
- **THEN** output is pixel-perfect with correct column widths

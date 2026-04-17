## ADDED Requirements

### Requirement: Structured logging captures all events
The system SHALL log all events (data fetch, alerts, errors, state changes) with consistent structure for debugging and monitoring.

#### Scenario: API fetch is logged
- **WHEN** data is fetched from an API
- **THEN** log entry contains: timestamp, source name, asset count, response time

#### Scenario: Alert is logged
- **WHEN** an alert condition is triggered
- **THEN** log entry contains: timestamp, asset ID, alert type (upper/lower), current price, threshold

#### Scenario: Error is logged with context
- **WHEN** an API call fails
- **THEN** log entry contains: timestamp, error type, source name, error message, retry attempt number

### Requirement: Logging verbosity is configurable
The system SHALL support different logging levels (DEBUG, INFO, WARNING, ERROR) controlled via configuration.

#### Scenario: Debug mode shows all events
- **WHEN** logging level is set to DEBUG
- **THEN** every API call, cache hit, and state change is logged

#### Scenario: Error mode shows only critical issues
- **WHEN** logging level is set to ERROR
- **THEN** only failed API calls and alert conditions are logged

### Requirement: Logs can be written to file or console
The system SHALL support writing logs to both console (for immediate visibility) and file (for archival).

#### Scenario: Console shows critical messages, file has full history
- **WHEN** monitor is running with file logging enabled
- **THEN** only errors appear on console, but all events are written to log file

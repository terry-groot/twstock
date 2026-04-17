## ADDED Requirements

### Requirement: Monitor framework manages multiple data sources
The monitoring system SHALL support multiple concurrent data sources (stocks, futures, etc.) through a pluggable architecture. Each data source implements a consistent interface.

#### Scenario: Monitor processes stock and futures data simultaneously
- **WHEN** monitor is started with stock and futures configured
- **THEN** both data sources are polled on their respective intervals and rendered together

#### Scenario: New data source can be added without modifying core
- **WHEN** a developer implements the DataSource interface
- **THEN** the monitor automatically recognizes and uses the new source

### Requirement: Core monitoring loop maintains responsiveness
The monitor SHALL maintain a responsive user experience by handling data fetch, alert checking, and rendering asynchronously without blocking.

#### Scenario: Monitor responds to Ctrl+C even during API call
- **WHEN** user presses Ctrl+C while waiting for API response
- **THEN** monitor exits cleanly within 1 second

### Requirement: Monitor supports querying specific assets
The monitor SHALL allow querying asset status programmatically for integration with other tools.

#### Scenario: Get current price for a stock
- **WHEN** monitor's `get_asset_data("2330")` is called
- **THEN** system returns latest price object with all fields populated

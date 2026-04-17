## ADDED Requirements

### Requirement: Data sources implement consistent interface
The system SHALL require all data sources to implement a common interface with `fetch()` returning consistent asset data structure.

#### Scenario: Stock source returns standard format
- **WHEN** stock data source's `fetch()` is called
- **THEN** it returns dict with asset IDs as keys and `AssetData` objects with fields: `price`, `open`, `high`, `low`, `volume`, `time`

#### Scenario: Futures source returns standard format
- **WHEN** futures data source's `fetch()` is called
- **THEN** it returns same structure as stock source (same fields, compatible types)

### Requirement: Data sources report their metadata
The system SHALL allow querying data source properties (name, interval, enabled).

#### Scenario: Query source capabilities
- **WHEN** monitor inspects a data source
- **THEN** it can determine: name, default polling interval, supported asset types

### Requirement: Data source errors don't crash monitor
The system SHALL catch and handle exceptions from individual data sources so one source's failure doesn't affect others.

#### Scenario: One source fails while others succeed
- **WHEN** futures API throws exception
- **THEN** stocks data source still fetches and renders normally, futures shows error state

### Requirement: New data sources are auto-discovered
The system SHALL scan for and load data source plugins automatically without requiring code changes.

#### Scenario: Developer adds new source module
- **WHEN** new file `market_monitor/sources/crypto.py` is created implementing interface
- **THEN** monitor automatically discovers and loads it on next restart

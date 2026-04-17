## ADDED Requirements

### Requirement: Single configuration file manages all asset monitors
The system SHALL use a single `monitor_config.json` file that contains both stock and futures asset configurations with a unified schema.

#### Scenario: Configuration contains both stocks and futures
- **WHEN** `monitor_config.json` is loaded
- **THEN** it contains separate `stocks` and `futures` arrays with identical schema structure

#### Scenario: Disabled assets are skipped
- **WHEN** an asset has `"enabled": false`
- **THEN** the monitor does not fetch or display that asset

### Requirement: Configuration validation prevents startup errors
The system SHALL validate configuration at startup and provide clear error messages for invalid values.

#### Scenario: Invalid asset configuration is rejected
- **WHEN** an asset has missing required fields (e.g., no `id`)
- **THEN** monitor exits with clear error message naming the invalid asset

#### Scenario: Invalid price thresholds are caught
- **WHEN** upper threshold is less than lower threshold
- **THEN** monitor warns user and ignores invalid thresholds

### Requirement: Backward compatibility migration preserves existing configs
The system SHALL detect legacy configuration format (separate `config.json` and `futures_config.json`) and migrate to new unified format.

#### Scenario: Old configs are automatically migrated
- **WHEN** legacy config files exist but new unified config doesn't
- **THEN** system automatically merges them, creates `monitor_config.json`, and backs up originals

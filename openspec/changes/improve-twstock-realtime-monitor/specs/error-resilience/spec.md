## ADDED Requirements

### Requirement: Transient API errors are retried automatically
The system SHALL retry failed API calls with exponential backoff for transient errors (network timeout, rate limiting).

#### Scenario: Network timeout triggers retry
- **WHEN** API call times out (no response within timeout)
- **THEN** system waits `retry_backoff_seconds`, multiplying by 2 for each attempt, up to `retry_max_attempts`

#### Scenario: Retry limit is respected
- **WHEN** API fails on all retry attempts
- **THEN** system displays "無法取得" (unavailable) for that asset and moves to next interval

### Requirement: Permanent errors are distinguished from transient
The system SHALL distinguish between errors that will never succeed (bad configuration, invalid asset code) and errors that might succeed on retry.

#### Scenario: Invalid asset code is not retried
- **WHEN** API returns "asset not found" error
- **THEN** system logs warning once, skips that asset, and does not retry

#### Scenario: Rate limit error is retried
- **WHEN** API returns rate limit error (429, 503)
- **THEN** system retries with exponential backoff

### Requirement: Graceful degradation shows partial data when some APIs fail
The system SHALL continue displaying available data and clearly indicate which sources have failed.

#### Scenario: Futures API down, stocks still shown
- **WHEN** futures data source fails persistently
- **THEN** monitor displays all stocks normally and shows status message about futures unavailable

### Requirement: Monitor survives API unavailability longer than polling interval
The system SHALL cache the last successful response and display it if next fetch fails, preventing blank/error displays.

#### Scenario: Display stale data when API temporarily down
- **WHEN** last successful fetch was 2 minutes ago but current fetch fails
- **THEN** display cached data with timestamp indicating staleness

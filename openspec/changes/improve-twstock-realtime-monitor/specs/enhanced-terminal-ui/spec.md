## ADDED Requirements

### Requirement: Terminal UI displays unified stocks and futures data
The system SHALL render both stocks and futures in a single, cohesive terminal display without requiring separate monitors.

#### Scenario: Stocks and futures display together
- **WHEN** monitor is running with both stocks and futures configured
- **THEN** terminal shows combined table with both types of assets, clearly labeled by type

#### Scenario: UI adapts to number of assets
- **WHEN** number of monitored assets changes
- **THEN** table layout automatically adjusts (may use multiple sections if needed)

### Requirement: Error states are displayed clearly
The system SHALL show meaningful messages when data is unavailable while maintaining readable display.

#### Scenario: Failed asset shows "無法取得"
- **WHEN** API fails to fetch price for specific asset
- **THEN** table row shows "--" for price fields and "無法取得" in status, with YELLOW color

#### Scenario: Stale data is indicated
- **WHEN** cached data is displayed due to API failure
- **THEN** timestamp indicator shows how long ago data was last updated

### Requirement: Status messages provide actionable feedback
The system SHALL display clear status messages about monitor health without cluttering the display.

#### Scenario: Retry status is shown
- **WHEN** monitor is retrying a failed API call
- **THEN** status message shows "重試中 (X/Y)" indicating attempt number

#### Scenario: Rate limit indication is visible
- **WHEN** API returns rate limit response
- **THEN** user sees clear message: "API 速率限制中，將在 X 秒後重試"

### Requirement: Terminal UI handles rapid updates cleanly
The system SHALL update the display without flickering or tearing, maintaining a professional appearance.

#### Scenario: Screen clears and redraws atomically
- **WHEN** monitor updates display every interval
- **THEN** no partial renders are visible, content appears stable

#### Scenario: Resize handling
- **WHEN** terminal is resized while monitor is running
- **THEN** display adapts gracefully (or shows message to restart)

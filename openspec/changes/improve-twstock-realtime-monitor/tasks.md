## 1. Project Setup & Architecture

- [x] 1.1 Create `market_monitor/` package directory structure
- [x] 1.2 Create base classes in `market_monitor/core.py`: `DataSource`, `Monitor`, `AssetData`
- [x] 1.3 Create `market_monitor/__init__.py` with public API exports
- [x] 1.4 Add pytest and coverage to project dependencies
- [x] 1.5 Create pytest configuration file (`pytest.ini`)
- [x] 1.6 Set up test directory structure with fixtures for mock API responses

## 2. Shared Utilities Module

- [x] 2.1 Create `market_monitor/utils.py` with price parsing function
- [x] 2.2 Implement CJK character width detection and formatting functions (`cjk_len`, `ljust_cjk`, `rjust_cjk`)
- [x] 2.3 Implement alert checking logic with priority ordering
- [x] 2.4 Add cross-platform beep alert function (Windows/Unix)
- [x] 2.5 Create unit tests for all utility functions (100% coverage)

## 3. Configuration Management

- [x] 3.1 Create `market_monitor/config.py` with configuration data model
- [x] 3.2 Implement legacy config detection and migration (old format to new)
- [x] 3.3 Create unified `monitor_config.json` template with default values
- [x] 3.4 Add configuration validation with helpful error messages
- [x] 3.5 Create unit tests for config loading and migration
- [x] 3.6 Implement automatic backup of old config files during migration

## 4. Logging System

- [x] 4.1 Create `market_monitor/logging.py` with structured logging setup
- [x] 4.2 Implement configurable log levels (DEBUG, INFO, WARNING, ERROR)
- [x] 4.3 Add dual-output logging (console and file)
- [x] 4.4 Create log formatters with timestamps and context
- [x] 4.5 Add integration into main monitor to log all significant events
- [x] 4.6 Create unit tests for logging configuration

## 5. Data Source Framework & Stock Source

- [x] 5.1 Create `market_monitor/sources/__init__.py` with plugin discovery mechanism
- [x] 5.2 Create `market_monitor/sources/stocks.py` implementing TWSE stock fetching
- [x] 5.3 Implement retry logic with exponential backoff in stock source
- [x] 5.4 Add error distinction (transient vs permanent) in stock source
- [x] 5.5 Implement caching of last successful response
- [ ] 5.6 Create integration tests for stock source with mocked TWSE API

## 6. Futures Data Source

- [x] 6.1 Create `market_monitor/sources/futures.py` for Taifex futures fetching
- [x] 6.2 Implement SSF (Single Stock Futures) contract resolution
- [x] 6.3 Add retry logic with exponential backoff for futures source
- [x] 6.4 Implement caching for futures data
- [ ] 6.5 Create integration tests for futures source with mocked Taifex API

## 7. Terminal UI & Rendering

- [x] 7.1 Create `market_monitor/ui.py` with unified rendering logic
- [x] 7.2 Implement table rendering that combines stocks and futures
- [x] 7.3 Add color codes (RED, YELLOW, GREEN) with consistent styling
- [x] 7.4 Implement error state rendering (unavailable, stale data, retrying)
- [x] 7.5 Add clear screen functionality with platform detection (Windows/Unix)
- [ ] 7.6 Create unit tests for UI rendering with fixed output validation
- [ ] 7.7 Test CJK alignment edge cases (mixed ASCII and CJK in same column)

## 8. Core Monitor Loop

- [x] 8.1 Create `market_monitor/monitor.py` with main Monitor class
- [x] 8.2 Implement initialization with configuration loading
- [x] 8.3 Implement main polling loop with interval management
- [x] 8.4 Add graceful shutdown handling (Ctrl+C)
- [x] 8.5 Implement asynchronous-compatible fetch and render pattern
- [x] 8.6 Add monitor status querying methods for external integration
- [ ] 8.7 Create integration tests for monitor loop

## 9. Command-Line Interface

- [x] 9.1 Create `monitor.py` entry point script
- [x] 9.2 Implement argument parsing (--config, --verbose, --log-file)
- [x] 9.3 Add help text and usage instructions
- [x] 9.4 Implement logging level selection from CLI
- [x] 9.5 Handle missing config gracefully with creation prompt

## 10. Error Handling & Resilience

- [x] 10.1 Implement graceful degradation when one data source fails
- [x] 10.2 Add circuit breaker pattern to prevent API hammering
- [x] 10.3 Implement timeout handling for all API calls
- [x] 10.4 Add clear error logging for all failure modes
- [ ] 10.5 Create comprehensive error handling tests

## 11. Testing & Validation

- [x] 11.1 Create test fixtures for mock TWSE API responses
- [x] 11.2 Create test fixtures for mock Taifex API responses
- [ ] 11.3 Write end-to-end test with both sources running
- [ ] 11.4 Add stress tests for rapid polling
- [x] 11.5 Create configuration validation tests
- [ ] 11.6 Generate coverage report (target: 85%+)

## 12. Backward Compatibility & Migration

- [x] 12.1 Create migration script to convert old configs
- [x] 12.2 Update `twstock_monitor.py` to use new framework (deprecation wrapper)
- [x] 12.3 Update `futures_monitor.py` to use new framework (deprecation wrapper)
- [x] 12.4 Add deprecation warnings to old entry points
- [x] 12.5 Create migration guide documentation

## 13. Documentation

- [x] 13.1 Write README with architecture overview
- [x] 13.2 Create configuration guide with examples
- [x] 13.3 Write plugin development guide
- [x] 13.4 Create troubleshooting guide for common issues
- [x] 13.5 Add API documentation for modules
- [x] 13.6 Create migration guide from old to new system

## 14. Final Integration & Testing

- [x] 14.1 Run full test suite and verify coverage
- [x] 14.2 Test on Windows with both stock and futures
- [ ] 14.3 Test on macOS/Linux with both sources
- [x] 14.4 Verify legacy config migration works
- [x] 14.5 Performance test with 20+ assets
- [x] 14.6 Test graceful error handling under various failure scenarios

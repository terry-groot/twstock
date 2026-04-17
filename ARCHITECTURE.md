# Taiwan Market Monitor - Architecture

## Overview

The Taiwan Market Monitor is a refactored, modular system for real-time monitoring of stocks and futures from Taiwan's financial markets (TWSE and Taifex).

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    monitor.py (Entry Point)                 │
│                    Argument parsing & setup                  │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│              MarketMonitor (market_monitor/monitor.py)       │
│     - Orchestrates data sources                              │
│     - Main polling loop                                      │
│     - Renders display                                        │
│     - Handles shutdown signals                               │
└────┬─────────────────────────────────────────┬──────────────┘
     │                                          │
     ▼                                          ▼
┌──────────────────────┐          ┌──────────────────────────┐
│  StockSource         │          │  FuturesSource           │
│  - TWSE API client   │          │  - Taifex API client     │
│  - Price parsing     │          │  - SSF mapping           │
│  - Error handling    │          │  - Contract resolution   │
└──────────────────────┘          └──────────────────────────┘
     │                                          │
     └─────────────────┬──────────────────────┘
                       │
                       ▼
         ┌──────────────────────────────┐
         │  Resilience Patterns         │
         │  - Retry with backoff        │
         │  - Circuit breaker           │
         │  - Data caching              │
         └──────────────────────────────┘
                       │
                       ▼
         ┌──────────────────────────────┐
         │  UI Rendering (ui.py)        │
         │  - Table formatting          │
         │  - CJK width handling        │
         │  - Color coding              │
         │  - Alert formatting          │
         └──────────────────────────────┘
```

## Key Components

### 1. Core Module (`market_monitor/core.py`)

Base classes for the framework:

- **`AssetData`**: Dataclass representing current market data (price, open, high, low, volume, etc.)
- **`DataSource`**: Abstract base class for market data providers
  - Methods: `fetch()`, `get_cached_data()`, `update_cache()`, `get_properties()`
- **`Monitor`**: Base orchestrator managing multiple data sources

### 2. Data Sources (`market_monitor/sources/`)

Plugin-based architecture for different market data providers:

- **`StockSource`** (stocks.py): TWSE stock data fetching via twstock library
  - Parses real-time prices, OHLC data, volume
  - Error classification (transient vs. permanent)
  - Caching of last successful response

- **`FuturesSource`** (futures.py): Taifex futures data fetching via HTTP API
  - SSF (Single Stock Futures) contract mapping
  - Market data aggregation and parsing
  - Caching mechanism

### 3. Configuration (`market_monitor/config.py`)

Unified configuration management:

- **`AssetConfig`**: Configuration for individual assets (ID, name, thresholds, enabled status)
- **`MonitorConfig`**: Monitoring parameters (intervals, retry settings, logging)
- **`Config`**: Main configuration container
  - Features: Validation, serialization, migration from legacy format
  - Backward compatibility: Automatic migration from old `config.json` and `futures_config.json`

### 4. Utilities (`market_monitor/utils.py`)

Common utility functions:

- `parse_price()`: Safe float parsing with None handling
- `cjk_len()`: CJK character width detection for proper terminal alignment
- `ljust_cjk()`, `rjust_cjk()`: CJK-aware string justification
- `format_price()`, `format_volume()`: Display formatting

### 5. Alerts (`market_monitor/alerts.py`)

Price alert logic with priority ordering:

- `check_alerts()`: Determine alerts based on thresholds
  - Margin calculation based on price magnitude (< 1000: margin=1, >= 1000: margin=5)
  - Priority: Red (critical) > Yellow (warning)
- `get_alert_message()`: Format alerts for display
- `get_alert_severity()`: Extract highest severity

### 6. Resilience Patterns (`market_monitor/resilience.py`)

Fault tolerance mechanisms:

- **`RetryConfig`**: Configurable exponential backoff retry strategy
- **`retry_with_backoff()`**: Decorator for automatic retry on failure
- **`CircuitBreaker`**: Prevent cascading failures
  - States: closed (normal), open (failing), half-open (recovery)
  - Automatic recovery after timeout

### 7. Terminal UI (`market_monitor/ui.py`)

Display rendering:

- `render_table()`: Unified table for stocks and futures
- `render_asset_row()`: Individual asset row with color coding
- ANSI color codes for severity indication
- CJK-aware column alignment
- Platform-aware screen clearing

### 8. Main Monitor (`market_monitor/monitor.py`)

Orchestration and main loop:

- **`MarketMonitor`**: Extends base Monitor with full functionality
  - Registers data sources
  - Implements main polling loop
  - Handles Ctrl+C gracefully
  - Manages circuit breakers per source
  - Renders display with alert beeping

### 9. Logging (`market_monitor/logging_setup.py`)

Structured logging:

- Configurable log levels (DEBUG, INFO, WARNING, ERROR)
- Dual output: console and rotating file handler
- Timestamp and context in log messages
- LogContext manager for block-level logging

### 10. Audio Alerts (`market_monitor/audio.py`)

Cross-platform beep alerts:

- Windows: `winsound.Beep()`
- Unix/Linux/macOS: Console bell character

## Data Flow

```
1. Startup
   ├─ Parse CLI arguments
   ├─ Load/migrate configuration
   ├─ Set up logging
   ├─ Create MarketMonitor
   ├─ Register StockSource and FuturesSource
   └─ Enter main loop

2. Main Loop (every min_interval seconds)
   ├─ Fetch from all sources
   │  ├─ Check circuit breaker
   │  ├─ Retry with exponential backoff
   │  ├─ Update cache on success
   │  └─ Record circuit breaker state
   ├─ Check alerts on all asset data
   ├─ Render table to terminal
   ├─ Beep if critical alert exists
   └─ Sleep until next interval

3. Shutdown (on Ctrl+C)
   ├─ Set running=False
   ├─ Exit main loop cleanly
   └─ Print exit message
```

## Error Handling Strategy

1. **Transient Errors** (temporary failures, will retry)
   - Network timeouts
   - Rate limiting (API throttle)
   - Temporary API unavailability

2. **Permanent Errors** (won't retry)
   - Invalid asset code
   - Contract not found
   - Configuration errors

3. **Resilience**
   - Exponential backoff on retries (configurable)
   - Circuit breaker to prevent hammering failed APIs
   - Cached data displayed when API fails
   - Graceful degradation: one source failure doesn't affect others

## Configuration Format

```json
{
  "stocks": [
    {
      "id": "2330",
      "name": "台積電",
      "upper": 1000,
      "lower": 900,
      "enabled": true
    }
  ],
  "futures": [
    {
      "id": "TX",
      "name": "台指期",
      "upper": 34000,
      "lower": 32000,
      "enabled": true
    }
  ],
  "monitor": {
    "stock_interval": 5,
    "futures_interval": 30,
    "retry_max_attempts": 3,
    "retry_backoff_seconds": 2,
    "beep_enabled": true,
    "log_level": "INFO",
    "log_file": null
  }
}
```

## Testing Strategy

- **Unit Tests**: Utilities, parsing, alerts, configuration (89 tests)
- **Integration Tests**: Data source mocking, end-to-end flows
- **Test Fixtures**: Mock TWSE and Taifex API responses
- **Coverage Target**: 85%+

## Future Extensibility

The plugin-based architecture allows adding new data sources:

1. Create `NewSource(DataSource)` in `market_monitor/sources/new_source.py`
2. Implement `fetch()` method returning Dict[asset_id, AssetData]
3. Source auto-discovered via `discover_sources()`
4. Register with monitor: `monitor.register_source_instance(NewSource())`

Example: Crypto markets, other exchanges, etc.

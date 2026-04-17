# Configuration Guide

## Default Configuration

When you first run the monitor, it automatically creates `monitor_config.json` with defaults if it doesn't exist:

```bash
python monitor.py
```

This generates:

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
    },
    {
      "id": "2330",
      "name": "台積電期",
      "upper": 1900,
      "lower": 1760,
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

## Configuration Reference

### Stock Configuration

```json
{
  "stocks": [
    {
      "id": "2330",           // TWSE stock code (required)
      "name": "台積電",        // Display name (required)
      "upper": 1000,          // Upper alert threshold (optional)
      "lower": 900,           // Lower alert threshold (optional)
      "enabled": true         // Include in monitoring (default: true)
    },
    {
      "id": "0050",
      "name": "台灣50",
      "upper": 150,
      "lower": 130,
      "enabled": true
    }
  ]
}
```

### Futures Configuration

```json
{
  "futures": [
    {
      "id": "TX",             // Contract code (required)
      "name": "台指期",        // Display name (required)
      "upper": 34000,         // Upper alert threshold (optional)
      "lower": 32000,         // Lower alert threshold (optional)
      "enabled": true         // Include in monitoring (default: true)
    },
    {
      "id": "2330",           // Or stock code for SSF (Single Stock Futures)
      "name": "台積電期",      // Display name
      "upper": 1900,
      "lower": 1760,
      "enabled": true
    }
  ]
}
```

### Monitor Settings

```json
{
  "monitor": {
    "stock_interval": 5,           // Fetch interval for stocks in seconds (default: 5)
    "futures_interval": 30,        // Fetch interval for futures in seconds (default: 30)
    "retry_max_attempts": 3,       // Retry attempts on API failure (default: 3)
    "retry_backoff_seconds": 2,    // Initial backoff in seconds, increases exponentially (default: 2)
    "beep_enabled": true,          // Sound alert on critical (red) threshold breach (default: true)
    "log_level": "INFO",           // Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)
    "log_file": null               // Path to log file, or null to disable file logging (default: null)
  }
}
```

## Examples

### Example 1: Multiple Stocks Only (No Futures)

```json
{
  "stocks": [
    { "id": "2330", "name": "台積電", "upper": 1000, "lower": 900, "enabled": true },
    { "id": "2454", "name": "聯發科", "upper": 1500, "lower": 1200, "enabled": true },
    { "id": "3034", "name": "聯詠", "upper": 500, "lower": 350, "enabled": true },
    { "id": "0050", "name": "台灣50", "upper": 150, "lower": 130, "enabled": true }
  ],
  "futures": [],
  "monitor": {
    "stock_interval": 5,
    "retry_max_attempts": 3,
    "retry_backoff_seconds": 2,
    "beep_enabled": true,
    "log_level": "INFO"
  }
}
```

### Example 2: Futures Only with Fast Polling

```json
{
  "stocks": [],
  "futures": [
    { "id": "TX", "name": "台指期", "upper": 34000, "lower": 32000, "enabled": true },
    { "id": "MTX", "name": "小台", "upper": 17000, "lower": 16000, "enabled": true },
    { "id": "2330", "name": "台積電期", "upper": 1900, "lower": 1760, "enabled": true }
  ],
  "monitor": {
    "stock_interval": 10,
    "futures_interval": 10,     // Fast polling
    "retry_max_attempts": 5,
    "retry_backoff_seconds": 1,
    "beep_enabled": true,
    "log_level": "DEBUG",       // Debug logging
    "log_file": "monitor.log"
  }
}
```

### Example 3: Stocks with Debug Logging

```json
{
  "stocks": [
    { "id": "2330", "name": "台積電", "upper": 1000, "lower": 900, "enabled": true },
    { "id": "2454", "name": "聯發科", "enabled": false }  // Disabled
  ],
  "futures": [
    { "id": "TX", "name": "台指期", "upper": 34000, "lower": 32000, "enabled": true }
  ],
  "monitor": {
    "stock_interval": 3,
    "futures_interval": 30,
    "retry_max_attempts": 3,
    "retry_backoff_seconds": 2,
    "beep_enabled": true,
    "log_level": "DEBUG",                    // Enable debug logging
    "log_file": "logs/monitor_debug.log"    // Save to file
  }
}
```

## Alert Thresholds

The monitor alerts on price movements:

### Alert Logic

- **Red Alert (Critical)**: Price exactly hits threshold
  - Upper: `price >= upper_threshold`
  - Lower: `price <= lower_threshold`
  
- **Yellow Alert (Warning)**: Price approaching threshold
  - Upper: `price >= upper_threshold - margin`
  - Lower: `price <= lower_threshold + margin`
  - **Margin calculation**: 
    - For prices >= 1000: margin = 5
    - For prices < 1000: margin = 1

### Alert Examples

For stock with `upper: 1000, lower: 900`:

| Price | Alert | Color | Reason |
|-------|-------|-------|--------|
| 899 | ▼ 接近下限 900 | Yellow | 899 <= 901 (900 + 1) |
| 900 | ⚠ 已達下限 900! | Red | 900 <= 900 |
| 950 | ✓ | Green | No alert |
| 1000 | ⚠ 已達上限 1000! | Red | 1000 >= 1000 |
| 999 | ▲ 接近上限 1000 | Yellow | 999 >= 999 (1000 - 1) |

For futures with `upper: 34000, lower: 32000`:

| Price | Alert | Color | Reason |
|-------|-------|-------|--------|
| 31995 | ▼ 接近下限 32000 | Yellow | 31995 <= 32005 (32000 + 5) |
| 32000 | ⚠ 已達下限 32000! | Red | 32000 <= 32000 |
| 33000 | ✓ | Green | No alert |
| 34000 | ⚠ 已達上限 34000! | Red | 34000 >= 34000 |
| 33996 | ▲ 接近上限 34000 | Yellow | 33996 >= 33995 (34000 - 5) |

## Logging Configuration

### Log Levels

- **DEBUG**: All events (API calls, data parsing, cache hits, etc.)
- **INFO**: Important events (monitor start, API failures, retries)
- **WARNING**: Warning conditions (circuit breaker state, config issues)
- **ERROR**: Error events (critical failures, exceptions)

### Example: Enable Debug with File Logging

```json
{
  "monitor": {
    "log_level": "DEBUG",
    "log_file": "monitor_debug.log"
  }
}
```

Logs are rotated when they exceed 10MB, with 5 backup files kept.

## Migration from Legacy Configuration

If you're using the old separate config files:

1. Rename or backup:
   - `config.json` → `config.json.old`
   - `futures_config.json` → `futures_config.json.old`

2. Run the monitor - it auto-migrates:
   ```bash
   python monitor.py
   ```

3. New `monitor_config.json` is created with merged configuration

4. Old files are backed up as `.backup`

## Disabling Alerts

To disable alerts on a specific asset, omit upper/lower thresholds:

```json
{
  "id": "2330",
  "name": "台積電",
  "enabled": true
  // No upper/lower thresholds
}
```

## Disabling Assets

To temporarily disable an asset without removing it:

```json
{
  "id": "2330",
  "name": "台積電",
  "upper": 1000,
  "lower": 900,
  "enabled": false  // Will not be monitored
}
```

## Valid Stock and Futures Codes

### Common Taiwan Stocks (2-4 digit codes)
- 2330: Taiwan Semiconductor Manufacturing Company (TSMC)
- 2454: MediaTek
- 3034: Novatek Microelectronics
- 0050: Taiwan Index Fund
- And many others

### Common Taiwan Futures Contracts
- TX: Taiwan Index Futures (台指期)
- MTX: Micro Index Futures (小台)
- TF: 10Y Bond Futures (金融債期貨)
- Individual stock futures: CDF, C2DF, CCDF, etc. (use stock code like "2330")

For complete lists, check TWSE and Taifex websites.

## Validation

The monitor validates configuration at startup:

```bash
$ python monitor.py --config bad_config.json
Configuration validation failed:
Stock TEST: upper threshold cannot be less than lower (1000 < 2000)
stock_interval must be at least 1 second
```

Fix the configuration and try again.

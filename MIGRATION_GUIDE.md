# Migration Guide: From Legacy Monitors to New Framework

## Overview

The new `monitor.py` replaces the old `twstock_monitor.py` and `futures_monitor.py`. The migration is automatic and transparent.

## What's Changing

| Aspect | Old | New |
|--------|-----|-----|
| **Entry Point** | `python twstock_monitor.py` or `python futures_monitor.py` | `python monitor.py` |
| **Configuration** | Two separate files: `config.json` and `futures_config.json` | Single file: `monitor_config.json` |
| **Display** | Two separate terminals for stocks and futures | Single unified display |
| **Architecture** | Monolithic, duplicated code | Modular, plugin-based |
| **Error Handling** | Basic error handling | Retry logic, circuit breakers, graceful degradation |
| **Testing** | No automated tests | 89+ unit tests, extensible test framework |
| **Logging** | Basic console output | Structured logging with file output option |

## Automatic Migration Path

The new system detects legacy configurations and migrates automatically:

```bash
$ python monitor.py
Migrating legacy configuration...
Migrating legacy configuration files, migrating...
[INFO] market_monitor: Market monitor started
[INFO] market_monitor: 載入設定完成，開始監控...
  台灣股票期貨即時報價監控  |  更新時間: 2026-04-12 09:48:54  |  按 Ctrl+C 結束
════════════════════════════════════════════════════════════════════════════════
...
```

### What Happens During Migration

1. **Detection**
   - Checks for old `config.json` and `futures_config.json`
   - If neither exists but `monitor_config.json` exists, uses new format

2. **Backup**
   - Old files are backed up: `config.json.backup` and `futures_config.json.backup`
   - Original files remain intact

3. **Conversion**
   - Old `stocks` array merged with old `contracts` array
   - Configuration restructured to new schema
   - Settings preserved (intervals, thresholds, etc.)

4. **Output**
   - New `monitor_config.json` created
   - Ready for immediate use

## Step-by-Step Migration

### For Users with Old System

1. **Backup your old configuration (optional)**
   ```bash
   cp config.json config.json.old
   cp futures_config.json futures_config.json.old
   ```

2. **Run the new monitor**
   ```bash
   python monitor.py
   ```

3. **Verify migration succeeded**
   ```bash
   ls -la *.json
   # You should see:
   # monitor_config.json (new)
   # config.json.backup (backup)
   # futures_config.json.backup (backup)
   ```

4. **Check the new configuration**
   ```bash
   cat monitor_config.json
   ```

5. **Delete old files (when confident)**
   ```bash
   rm config.json futures_config.json
   ```

## Configuration Changes

### Old Format (Legacy)

```json
// config.json
{
  "interval": 5,
  "stocks": [
    {"id": "2330", "name": "台積電", "upper": 1000, "lower": 900}
  ]
}

// futures_config.json
{
  "interval": 30,
  "contracts": [
    {"id": "TX", "name": "台灣指數期貨", "upper": 34000, "lower": 32000}
  ]
}
```

### New Format (Unified)

```json
// monitor_config.json
{
  "stocks": [
    {"id": "2330", "name": "台積電", "upper": 1000, "lower": 900, "enabled": true}
  ],
  "futures": [
    {"id": "TX", "name": "台灣指數期貨", "upper": 34000, "lower": 32000, "enabled": true}
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

## Legacy Scripts Removed

The old `twstock_monitor.py` and `futures_monitor.py` scripts have been removed. All functionality is now consolidated in:

```bash
python monitor.py
```

If you have old scripts from a previous version, the configuration will be automatically migrated when you run the new monitor.

## Behavior Changes

### Positive Changes

1. **Unified Display**
   - Stocks and futures shown together
   - No need to switch terminals

2. **Better Error Handling**
   - Retries on transient failures
   - One source failing doesn't affect others
   - Graceful degradation with cached data

3. **Logging**
   - Optional file logging for debugging
   - Structured logging with timestamps
   - Different log levels available

4. **Performance**
   - Smarter polling intervals
   - Efficient caching
   - No duplicate API calls

5. **Reliability**
   - Circuit breaker prevents API hammering
   - Automatic recovery from failures
   - Better handling of network issues

### Compatibility Notes

- **Configuration**: Old format automatically converted
- **Display**: Similar layout but unified (stocks + futures together)
- **Thresholds**: Same alert logic and margin calculations
- **Performance**: Comparable or better than before

### Breaking Changes

- Old command-line arguments not supported (not applicable - no args in old version)
- Old scripts (twstock_monitor.py, futures_monitor.py) deprecated
- No GUI or web interface (stays terminal-based)

## Troubleshooting Migration

### Problem: "Configuration validation failed"

**Cause**: Invalid old configuration

**Solution**:
1. Check old `config.json` and `futures_config.json` for syntax errors
2. Fix the JSON (ensure valid JSON format)
3. Delete `monitor_config.json` if it was partially created
4. Run again: `python monitor.py`

### Problem: Configuration not migrating

**Cause**: Files in wrong location or old system wasn't properly stopped

**Solution**:
```bash
# Make sure you're in the right directory
pwd  # Should show the project directory

# Check for old files
ls config.json futures_config.json

# If files exist and migration isn't working, manually migrate
python -c "
from market_monitor.config import migrate_legacy_config
migrate_legacy_config('config.json', 'futures_config.json', 'monitor_config.json')
"
```

### Problem: Data not showing up after migration

**Cause**: Assets disabled in new configuration

**Solution**:
```bash
# Edit monitor_config.json and ensure assets have "enabled": true
nano monitor_config.json

# Check that asset IDs are correct for your market
# (Stock IDs: 4 digits; Futures codes: TX, MTX, etc.)
```

## New Features Available

After migration, you have access to new features:

### 1. Logging to File

```json
{
  "monitor": {
    "log_level": "DEBUG",
    "log_file": "logs/monitor.log"
  }
}
```

### 2. More Granular Intervals

```json
{
  "monitor": {
    "stock_interval": 3,      // Check stocks every 3 seconds
    "futures_interval": 15    // Check futures every 15 seconds
  }
}
```

### 3. Better Retry Behavior

```json
{
  "monitor": {
    "retry_max_attempts": 5,
    "retry_backoff_seconds": 1
  }
}
```

### 4. Debug Logging

```bash
python monitor.py --verbose --log-file debug.log
```

## For Developers

### Old Code Path (REMOVED)

Legacy monitoring code has been completely replaced:
- `twstock_monitor.py` → Now a wrapper
- `futures_monitor.py` → Now a wrapper
- Duplicated logic → Consolidated into modular components

### New Code Path (ACTIVE)

All functionality now goes through:
1. `monitor.py` (entry point)
2. `market_monitor/` (framework)
3. Specific sources in `market_monitor/sources/`

### Testing

New system includes comprehensive testing:
```bash
# Run all tests
pytest tests/ -v

# Run specific test class
pytest tests/test_config.py::TestConfigValidation -v

# With coverage
pytest tests/ --cov=market_monitor
```

## Timeline

- **Now**: Automatic migration available
- **Next release**: Deprecation warnings increased
- **Future release**: Legacy wrappers removed
- **Final**: Old format support removed

## Getting Help

1. **Check CONFIG_GUIDE.md** for configuration questions
2. **Check ARCHITECTURE.md** for technical details
3. **Run tests** to verify your setup: `pytest tests/`
4. **Enable debug logging** to diagnose issues: `python monitor.py --verbose`

## Summary

Migration is **automatic and transparent**. Simply run:

```bash
python monitor.py
```

Old configuration is preserved, converted, and backed up. The new system provides better reliability, error handling, and logging while maintaining compatibility with your existing setup.

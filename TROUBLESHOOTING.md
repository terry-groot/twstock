# Troubleshooting Guide

## Common Issues and Solutions

### Stock Data Issues

#### Problem: "無法取得" (Cannot obtain) for all stocks

**Symptoms:**
- All stock rows show "無法取得"
- The monitor runs but displays `--` for all prices

**Causes:**
- Network connectivity issue
- TWSE API is down or rate-limited
- Invalid stock codes in configuration

**Solutions:**

1. Check network connectivity:
   ```bash
   ping openapi.twse.com.tw
   ```

2. Verify stock codes are valid:
   ```bash
   # Valid formats: "2330", "3231", etc.
   python -c "from market_monitor.sources.stocks import StockSource; print(StockSource().fetch(['2330']))"
   ```

3. Check logs for detailed errors:
   ```bash
   python monitor.py --verbose --log-file monitor.log
   tail -f monitor.log
   ```

4. If API is rate-limited, increase polling interval:
   ```json
   {
     "monitor": {
       "intervals": {
         "stock": 30
       }
     }
   }
   ```

---

#### Problem: Only some stocks show data

**Symptoms:**
- Some assets display prices while others show "無法取得"
- Different assets succeed/fail on each run

**Causes:**
- Invalid stock codes mixed with valid ones
- API timeout on specific codes
- Network intermittency

**Solutions:**

1. Validate each stock code individually:
   ```python
   from market_monitor.sources.stocks import StockSource
   source = StockSource()
   
   codes = ["2330", "9999", "1234"]
   for code in codes:
       result = source.fetch([code])
       print(f"{code}: {result[code]}")
   ```

2. Check which codes are valid on TWSE:
   - Visit: https://www.twse.com.tw/

3. Increase timeout for slow connections:
   ```json
   {
     "monitor": {
       "network": {
         "timeout": 15
       }
     }
   }
   ```

---

### Futures Data Issues

#### Problem: Futures data always shows "--"

**Symptoms:**
- SSF and index futures show no data
- "無法取得" appears for all futures

**Causes:**
- SSF contract mapping API is down
- Futures market is closed
- Taifex API access issue

**Solutions:**

1. Check if Taifex API is accessible:
   ```bash
   curl "https://openapi.taifex.com.tw/v1/marketdata"
   ```

2. Verify market hours (futures trade during day and night):
   - Day session: 9:00-13:30 (Monday-Friday)
   - Night session: 15:00-5:00 (Monday-Friday)

3. Check SSF contract availability:
   ```python
   from market_monitor.sources.futures import FuturesSource
   source = FuturesSource()
   if source.build_ssf_map():
       print("SSF map built successfully")
   else:
       print("Failed to build SSF map - check network/API")
   ```

---

#### Problem: Performance is slow

**Symptoms:**
- Monitor lags when updating
- CPU usage is high
- Response time between updates is long

**Causes:**
- Too many assets being monitored
- Polling interval too short
- Network latency
- Low system resources

**Solutions:**

1. Increase polling intervals:
   ```json
   {
     "monitor": {
       "intervals": {
         "stock": 10,
         "futures": 60
       }
     }
   }
   ```

2. Monitor fewer assets:
   - Set `"enabled": false` for non-critical assets

3. Check system resources:
   ```bash
   # Windows
   tasklist | find "python"
   
   # Unix
   ps aux | grep python
   ```

4. Use verbose logging to identify slow operations:
   ```bash
   python monitor.py --verbose --log-file debug.log
   ```

---

### Configuration Issues

#### Problem: "Config validation failed"

**Symptoms:**
- Error message on startup
- Cannot start monitor

**Causes:**
- Invalid JSON in config file
- Missing required fields
- Invalid threshold values

**Solutions:**

1. Validate JSON syntax:
   ```bash
   python -m json.tool monitor_config.json
   ```

2. Check required fields are present:
   ```json
   {
     "monitor": {
       "intervals": {
         "stock": 5,
         "futures": 30
       }
     },
     "assets": [
       {
         "id": "2330",
         "name": "台積電",
         "enabled": true
       }
     ]
   }
   ```

3. Validate threshold values:
   - Upper threshold must be > lower threshold
   - Thresholds must be positive numbers

---

#### Problem: "Cannot find config file"

**Symptoms:**
- Error on startup even though file exists
- Monitor cannot load configuration

**Causes:**
- Wrong file path
- File in wrong directory
- File permissions issue

**Solutions:**

1. Check file exists in correct location:
   ```bash
   ls -la monitor_config.json
   ```

2. Specify full path:
   ```bash
   python monitor.py --config /full/path/to/monitor_config.json
   ```

3. Check file permissions:
   ```bash
   # Unix
   chmod 644 monitor_config.json
   ```

---

### Alert and Notification Issues

#### Problem: No beep sound on alerts

**Symptoms:**
- Price hits threshold but no sound
- Logs show alerts but no audio feedback

**Causes:**
- Sound is disabled in system
- Audio output not configured
- Platform-specific audio issue

**Solutions:**

1. Check sound is enabled:
   - Windows: Check volume in system tray
   - Unix/macOS: Check speakers are connected

2. Test beep manually:
   ```python
   from market_monitor.audio import beep_alert
   beep_alert()  # Should produce a beep
   ```

3. Check audio configuration in logs:
   ```bash
   python monitor.py --verbose | grep -i audio
   ```

---

#### Problem: Alerts trigger when they shouldn't

**Symptoms:**
- "WARNING" or "ALERT" shows incorrectly
- Alert message doesn't match price

**Causes:**
- Threshold values set too close to current price
- Price data is stale
- Margin calculation issue

**Solutions:**

1. Review threshold values:
   ```json
   {
     "id": "2330",
     "upper": 650,
     "lower": 550
   }
   ```

2. Check price data freshness:
   - Look for "stale data" warnings in output
   - Verify data source is updating

3. Understand margin calculation:
   - Price < 1000: margin = 1
   - Price >= 1000: margin = 5
   - "Approaching limit" = price within margin of threshold

---

### Logging Issues

#### Problem: Logs not being created

**Symptoms:**
- --log-file flag doesn't create file
- No log output appears

**Causes:**
- Invalid file path
- Directory doesn't exist
- Insufficient permissions

**Solutions:**

1. Create log directory:
   ```bash
   mkdir -p logs
   ```

2. Use absolute path:
   ```bash
   python monitor.py --log-file /full/path/to/monitor.log
   ```

3. Check directory permissions:
   ```bash
   # Unix
   chmod 755 logs/
   ```

---

#### Problem: Too much log output

**Symptoms:**
- Log files grow very large
- Performance impact from logging

**Causes:**
- Log level set to DEBUG
- Verbose mode enabled
- Log rotation not configured

**Solutions:**

1. Use appropriate log level:
   ```bash
   python monitor.py                    # INFO level (default)
   python monitor.py --verbose          # DEBUG level (verbose)
   ```

2. Implement log rotation:
   - Logs are automatically rotated after 10MB
   - Old logs are compressed and kept for 7 days

---

### Command-Line Issues

#### Problem: "Command not found: monitor.py"

**Symptoms:**
- Error when trying to run monitor
- Command is not recognized

**Solutions:**

1. Run with explicit Python:
   ```bash
   python monitor.py
   python3 monitor.py
   ```

2. Make script executable:
   ```bash
   chmod +x monitor.py
   ./monitor.py
   ```

3. Check Python path:
   ```bash
   which python
   python --version
   ```

---

#### Problem: Module import errors

**Symptoms:**
- "ModuleNotFoundError: No module named 'twstock'"
- "Cannot import market_monitor"

**Solutions:**

1. Install dependencies:
   ```bash
   pip install twstock
   ```

2. Check Python path:
   ```bash
   python -c "import sys; print(sys.path)"
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

---

### Legacy Migration Issues

#### Problem: "Old config not migrated"

**Symptoms:**
- Still using old format configuration
- Cannot use new monitor.py with old config

**Causes:**
- Migration not triggered automatically
- Config file in wrong location

**Solutions:**

1. Manually trigger migration:
   ```python
   from market_monitor.config import migrate_legacy_config
   migrate_legacy_config(
       old_stocks_path="config.json",
       old_futures_path="futures_config.json",
       new_path="monitor_config.json"
   )
   ```

2. Verify migration worked:
   ```bash
   ls -la monitor_config.json
   cat monitor_config.json
   ```

3. Back up old configs first:
   ```bash
   cp config.json config.json.bak
   cp futures_config.json futures_config.json.bak
   ```

---

### Getting Help

If your issue isn't listed above:

1. **Check the logs:**
   ```bash
   python monitor.py --verbose --log-file debug.log
   ```

2. **Review documentation:**
   - [Architecture Guide](ARCHITECTURE.md)
   - [Configuration Guide](CONFIG_GUIDE.md)
   - [Migration Guide](MIGRATION_GUIDE.md)

3. **Report an issue:**
   - Include full error message
   - Include configuration (without sensitive data)
   - Include logs from the error event

---

## Performance Tuning

### Optimal Configuration for Different Scenarios

**Light Monitoring (1-5 assets):**
```json
{
  "monitor": {
    "intervals": {
      "stock": 5,
      "futures": 30
    }
  }
}
```

**Medium Monitoring (5-20 assets):**
```json
{
  "monitor": {
    "intervals": {
      "stock": 10,
      "futures": 60
    }
  }
}
```

**Heavy Monitoring (20+ assets):**
```json
{
  "monitor": {
    "intervals": {
      "stock": 30,
      "futures": 120
    },
    "network": {
      "timeout": 20
    }
  }
}
```

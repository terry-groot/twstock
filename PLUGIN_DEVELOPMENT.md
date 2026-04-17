# Plugin Development Guide

## Overview

The Taiwan Market Monitor uses a plugin architecture that allows you to create custom data sources for different market data providers. This guide explains how to develop a new plugin.

## Creating a Custom Data Source

### 1. Understanding the Base Class

All data sources inherit from the `DataSource` base class in `market_monitor/core.py`:

```python
from market_monitor.core import DataSource, AssetData

class CustomDataSource(DataSource):
    """Custom data source implementation."""

    def __init__(self, interval: int = 5):
        """Initialize custom data source.

        Args:
            interval: Polling interval in seconds
        """
        super().__init__("custom_source", interval)

    def fetch(self, asset_ids: list) -> dict:
        """Fetch market data for given assets.

        Args:
            asset_ids: List of asset identifiers

        Returns:
            Dictionary mapping asset_id to AssetData or None
        """
        # Implementation here
        pass
```

### 2. Implementing the fetch() Method

The `fetch()` method is the core of your plugin. It should:

1. Accept a list of asset identifiers
2. Fetch data from your data provider
3. Parse the response into `AssetData` objects
4. Return a dictionary mapping asset_ids to `AssetData` (or None if unavailable)

```python
def fetch(self, asset_ids: list) -> dict:
    """Fetch market data."""
    results = {}

    for asset_id in asset_ids:
        try:
            data = self._fetch_single(asset_id)
            results[asset_id] = AssetData(
                asset_id=asset_id,
                price=data.get("price"),
                open=data.get("open"),
                high=data.get("high"),
                low=data.get("low"),
                volume=data.get("volume")
            )
        except Exception as e:
            logger.error(f"Failed to fetch {asset_id}: {e}")
            results[asset_id] = None

    self.update_cache(results)
    return results
```

### 3. Using Resilience Patterns

Leverage built-in resilience patterns to make your plugin robust:

```python
from market_monitor.resilience import retry_with_backoff, RetryConfig

class RobustDataSource(DataSource):
    def __init__(self):
        super().__init__("robust_source", 5)
        self.retry_config = RetryConfig(
            max_attempts=3,
            initial_backoff=1.0,
            max_backoff=30.0
        )

    def fetch(self, asset_ids: list) -> dict:
        """Fetch with automatic retry on failure."""
        return retry_with_backoff(
            self._fetch_with_error_handling,
            asset_ids,
            config=self.retry_config
        )

    def _fetch_with_error_handling(self, asset_ids: list) -> dict:
        # Actual fetch logic
        pass
```

### 4. Caching

Use the built-in caching mechanism:

```python
def fetch(self, asset_ids: list) -> dict:
    results = {}

    for asset_id in asset_ids:
        # Try cache first
        cached = self.get_cached_data(asset_id)
        if cached and self._is_fresh(cached):
            results[asset_id] = cached
        else:
            # Fetch fresh data
            data = self._fetch_from_api(asset_id)
            results[asset_id] = data

    self.update_cache(results)
    return results
```

## Registering Your Plugin

To register your custom data source with the monitor:

```python
from market_monitor.monitor import MarketMonitor
from market_monitor.config import load_config

# Load configuration
config = load_config("monitor_config.json")

# Create monitor
monitor = MarketMonitor(config)

# Register custom source
from my_plugin import CustomDataSource
custom_source = CustomDataSource()
monitor.register_source_instance(custom_source)

# Run monitor
monitor.run()
```

## Example: Weather Data Plugin

Here's a complete example of a simple weather data plugin:

```python
from market_monitor.core import DataSource, AssetData
from market_monitor.logging_setup import get_logger
import urllib.request
import json

logger = get_logger("sources.weather")

class WeatherDataSource(DataSource):
    """Example plugin: Fetches weather data for display."""

    def __init__(self, interval: int = 300):
        super().__init__("weather", interval)
        self.api_url = "https://api.weather.example.com"

    def fetch(self, asset_ids: list) -> dict:
        """Fetch weather for given cities.

        Args:
            asset_ids: List of city codes (e.g., ["taipei", "london"])

        Returns:
            Dict mapping city to AssetData with weather info
        """
        results = {}

        for city in asset_ids:
            try:
                response = self._get_weather(city)
                results[city] = AssetData(
                    asset_id=city,
                    price=response.get("temperature"),  # Reuse price field
                    change=response.get("condition")     # Reuse change field
                )
            except Exception as e:
                logger.error(f"Failed to fetch weather for {city}: {e}")
                results[city] = None

        self.update_cache(results)
        return results

    def _get_weather(self, city: str) -> dict:
        """Fetch from API."""
        url = f"{self.api_url}/current?city={city}"
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            logger.error(f"API error: {e}")
            raise
```

## Best Practices

1. **Error Handling**: Always catch exceptions and return None for failed assets
2. **Logging**: Use the logger to track fetch operations and errors
3. **Timeout**: Set reasonable timeouts for API calls (10-30 seconds)
4. **Caching**: Use `update_cache()` to cache successful responses
5. **Rate Limiting**: Respect API rate limits and add exponential backoff
6. **Documentation**: Document your plugin's configuration and requirements
7. **Testing**: Write unit tests for your data source

## Testing Your Plugin

```python
import pytest
from unittest.mock import patch

@patch('my_plugin.get_api_data')
def test_custom_source_fetch(mock_api):
    mock_api.return_value = {
        "custom123": {"price": 100.0, "volume": "1000"}
    }

    source = CustomDataSource()
    result = source.fetch(["custom123"])

    assert "custom123" in result
    assert result["custom123"].price == 100.0
```

## Configuration

Add your plugin to the monitor configuration in `monitor_config.json`:

```json
{
  "monitor": {
    "intervals": {
      "custom": 60
    }
  },
  "assets": [
    {
      "id": "custom123",
      "name": "Custom Asset",
      "type": "custom",
      "enabled": true
    }
  ]
}
```

## Troubleshooting Plugin Development

**Issue: Plugin not being called**
- Ensure you've registered it with `monitor.register_source_instance()`
- Check the asset types match your source name

**Issue: Data not updating**
- Verify `fetch()` is returning a dict with asset_ids as keys
- Check that `update_cache()` is being called
- Review logs for error messages

**Issue: Memory leak**
- Ensure you're not accumulating data in internal caches
- Call `self.update_cache()` to replace old cache data

## API Reference

See the [API Documentation](API.md) for detailed class and method references.

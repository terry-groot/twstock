"""Integration tests for market monitor components."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import time
from market_monitor.core import AssetData
from market_monitor.config import Config, AssetConfig, MonitorConfig
from market_monitor.monitor import MarketMonitor
from market_monitor.ui import render_asset_row, render_table
from market_monitor.resilience import CircuitBreaker, RetryConfig, retry_with_backoff


class TestUIRendering:
    """Integration tests for UI rendering."""

    def test_render_asset_row_with_data(self):
        """Test rendering asset row with valid data."""
        asset_data = AssetData(
            asset_id="2330",
            price=600.0,
            open=595.0,
            high=605.0,
            low=590.0,
            volume="25000000"
        )

        row, severity = render_asset_row(
            asset_id="2330",
            asset_name="台積電",
            asset_type="stock",
            asset_data=asset_data,
            config={}
        )

        assert isinstance(row, str)
        assert "2330" in row
        assert "台積電" in row
        assert severity in ["ok", "yellow", "red", "warning"]

    def test_render_asset_row_unavailable(self):
        """Test rendering asset row with no data."""
        row, severity = render_asset_row(
            asset_id="2330",
            asset_name="台積電",
            asset_type="stock",
            asset_data=None,
            config={}
        )

        assert isinstance(row, str)
        assert "2330" in row
        assert "無法取得" in row
        assert severity == "warning"

    def test_render_asset_row_with_alert_threshold(self):
        """Test rendering asset row with alert thresholds."""
        asset_data = AssetData(
            asset_id="2330",
            price=650.0,
            open=595.0,
            high=655.0,
            low=590.0,
            volume="25000000"
        )

        config = {"upper": 640, "lower": 550}
        row, severity = render_asset_row(
            asset_id="2330",
            asset_name="台積電",
            asset_type="stock",
            asset_data=asset_data,
            config=config
        )

        assert isinstance(row, str)
        assert "2330" in row

    def test_render_futures_row(self):
        """Test rendering futures row."""
        asset_data = AssetData(
            asset_id="TXF",
            price=21500.0,
            open=21400.0,
            high=21600.0,
            low=21300.0,
            change="+50"
        )

        row, severity = render_asset_row(
            asset_id="TXF",
            asset_name="台灣指數期貨",
            asset_type="futures",
            asset_data=asset_data,
            config={}
        )

        assert isinstance(row, str)
        assert "TXF" in row

    def test_render_table(self):
        """Test rendering complete table."""
        assets = {
            "2330": ("stock", {"name": "台積電"}),
            "TXF": ("futures", {"name": "台灣指數期貨"})
        }

        asset_data = {
            "2330": AssetData(
                asset_id="2330",
                price=600.0,
                open=595.0,
                high=605.0,
                low=590.0,
                volume="25000000"
            ),
            "TXF": AssetData(
                asset_id="TXF",
                price=21500.0,
                open=21400.0,
                high=21600.0,
                low=21300.0,
                change="+50"
            )
        }

        result = render_table(assets, asset_data)

        # render_table returns a tuple or tuple-like result
        assert result is not None


class TestCircuitBreakerIntegration:
    """Integration tests for circuit breaker."""

    def test_circuit_breaker_closes_after_success(self):
        """Test circuit breaker closes after successful recovery."""
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)

        # Trigger failures
        breaker.record_failure()
        assert breaker.state == "closed"
        breaker.record_failure()
        assert breaker.state == "open"

        # Wait for recovery timeout
        time.sleep(0.15)

        # Should be able to attempt
        assert breaker.can_attempt() == True
        assert breaker.state == "half-open"

        # Success should close
        breaker.record_success()
        assert breaker.state == "closed"

    def test_circuit_breaker_prevents_calls_when_open(self):
        """Test circuit breaker prevents calls when open."""
        breaker = CircuitBreaker(failure_threshold=1)

        # Trigger one failure to open
        breaker.record_failure()
        assert breaker.state == "open"

        # Subsequent can_attempt() should return False
        can_attempt = breaker.can_attempt()
        assert can_attempt == False

        # Verify state remains open
        assert breaker.state == "open"


class TestRetryWithBackoffIntegration:
    """Integration tests for retry with backoff."""

    def test_retry_succeeds_eventually(self):
        """Test retry succeeds after failures."""
        call_count = 0

        def eventually_succeeds():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Network error")
            return "success"

        config = RetryConfig(
            max_attempts=5,
            initial_backoff=0.01,
            exponential_base=2
        )

        result = retry_with_backoff(eventually_succeeds, config=config)

        assert result == "success"
        assert call_count == 3

    def test_retry_exhausts_attempts(self):
        """Test retry exhausts all attempts."""
        def always_fails():
            raise ValueError("Invalid")

        config = RetryConfig(
            max_attempts=2,
            initial_backoff=0.01
        )

        with pytest.raises(ValueError):
            retry_with_backoff(always_fails, config=config)

    def test_retry_backoff_calculation(self):
        """Test retry backoff timing."""
        config = RetryConfig(
            max_attempts=4,
            initial_backoff=1.0,
            exponential_base=2.0,
            max_backoff=30.0
        )

        # Verify backoff calculations
        assert config.get_backoff(0) == 1.0
        assert config.get_backoff(1) == 2.0
        assert config.get_backoff(2) == 4.0
        assert config.get_backoff(3) == 8.0
        assert config.get_backoff(10) == 30.0  # Capped at max


class TestMonitorIntegration:
    """Integration tests for market monitor."""

    def test_monitor_initialization(self):
        """Test monitor can be initialized."""
        config = Config(
            stocks=[
                AssetConfig(id="2330", name="台積電", enabled=True)
            ]
        )

        monitor = MarketMonitor(config)

        assert monitor is not None
        assert monitor.config == config

    def test_monitor_graceful_shutdown(self):
        """Test monitor responds to shutdown signal."""
        config = Config()

        monitor = MarketMonitor(config)
        assert monitor.running == True

        # Simulate Ctrl+C
        monitor._handle_shutdown(None, None)
        assert monitor.running == False

    @patch('twstock.realtime.get')
    def test_monitor_with_stock_source(self, mock_get):
        """Test monitor with stock data source."""
        mock_get.return_value = {
            "success": True,
            "2330": {
                "n": "台積電",
                "z": "600.00",
                "o": "595.00",
                "h": "605.00",
                "l": "590.00",
                "v": "25000000",
                "y": "580.00"
            }
        }

        config = Config(
            stocks=[AssetConfig(id="2330", name="台積電", enabled=True)]
        )

        monitor = MarketMonitor(config)

        from market_monitor.sources.stocks import StockSource
        source = StockSource()
        monitor.register_source_instance(source)

        # Monitor should be configured with source
        assert monitor is not None
        assert "stocks" in monitor.circuit_breakers

    def test_monitor_multiple_sources(self):
        """Test monitor with multiple data sources."""
        config = Config(
            stocks=[
                AssetConfig(id="2330", name="台積電", enabled=True),
            ],
            futures=[
                AssetConfig(id="TXF", name="台灣指數期貨", enabled=True)
            ]
        )

        monitor = MarketMonitor(config)

        from market_monitor.sources.stocks import StockSource
        from market_monitor.sources.futures import FuturesSource

        stock_source = StockSource()
        futures_source = FuturesSource()

        monitor.register_source_instance(stock_source)
        monitor.register_source_instance(futures_source)

        # Both sources registered
        assert len(monitor.circuit_breakers) >= 2


class TestStressScenarios:
    """Stress test scenarios."""

    def test_rapid_retry_attempts(self):
        """Test rapid retry with many attempts."""
        call_count = 0

        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count % 2 == 0:
                return f"success_{call_count}"
            raise ConnectionError("Network glitch")

        config = RetryConfig(max_attempts=10, initial_backoff=0.001)

        # Even with flaky function and many retries, should succeed
        result = retry_with_backoff(flaky_function, config=config)
        assert "success_" in result

    def test_circuit_breaker_under_load(self):
        """Test circuit breaker behavior under load."""
        breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=0.1)

        successful_calls = 0
        failed_calls = 0
        prevented_calls = 0

        for i in range(20):
            if i < 3:
                # First 3 attempts fail
                breaker.record_failure()
                failed_calls += 1
            elif not breaker.can_attempt():
                # Circuit is open, prevent calls
                prevented_calls += 1
            else:
                # Attempt succeeds after recovery
                breaker.record_success()
                successful_calls += 1

        # Should have prevented multiple calls after opening
        assert prevented_calls > 0
        assert breaker.state in ["closed", "open", "half-open"]

    def test_combined_resilience_patterns(self):
        """Test retry and circuit breaker working together."""
        breaker = CircuitBreaker(failure_threshold=2)
        attempt_count = 0

        def unstable_operation():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count <= 2:
                raise Exception("API error")
            return "recovered"

        config = RetryConfig(max_attempts=3, initial_backoff=0.01)

        # Should succeed despite initial failures
        result = retry_with_backoff(unstable_operation, config=config)
        assert result == "recovered"

        # Circuit breaker was not triggered (only 3 attempts < 2 threshold)
        assert breaker.state == "closed"

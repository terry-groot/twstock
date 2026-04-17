"""Unit tests for market_monitor.alerts module."""

import pytest
from market_monitor.alerts import (
    check_alerts,
    has_critical_alert,
    get_alert_message,
    get_alert_severity,
)


class TestCheckAlerts:
    """Tests for check_alerts function."""

    def test_no_alerts_when_price_safe(self):
        """Test no alerts when price is within safe range."""
        alerts = check_alerts("2330", 850.0, upper_threshold=1000, lower_threshold=800)
        assert alerts == []

    def test_upper_limit_hit(self):
        """Test alert when upper limit is hit."""
        alerts = check_alerts("2330", 1000.0, upper_threshold=1000)
        assert len(alerts) == 1
        assert alerts[0][0] == "red"
        assert "達上限" in alerts[0][1]

    def test_lower_limit_hit(self):
        """Test alert when lower limit is hit."""
        alerts = check_alerts("2330", 800.0, lower_threshold=800)
        assert len(alerts) == 1
        assert alerts[0][0] == "red"
        assert "達下限" in alerts[0][1]

    def test_approaching_upper_limit_low_price(self):
        """Test approaching upper limit with price < 1000 (margin = 1)."""
        alerts = check_alerts("2330", 99.0, upper_threshold=100)
        assert len(alerts) == 1
        assert alerts[0][0] == "yellow"
        assert "接近上限" in alerts[0][1]

    def test_approaching_lower_limit_low_price(self):
        """Test approaching lower limit with price < 1000 (margin = 1)."""
        alerts = check_alerts("2330", 101.0, lower_threshold=100)
        assert len(alerts) == 1
        assert alerts[0][0] == "yellow"
        assert "接近下限" in alerts[0][1]

    def test_approaching_upper_limit_high_price(self):
        """Test approaching upper limit with price >= 1000 (margin = 5)."""
        alerts = check_alerts("2330", 1996.0, upper_threshold=2000)
        assert len(alerts) == 1
        assert alerts[0][0] == "yellow"
        assert "接近上限" in alerts[0][1]

    def test_approaching_lower_limit_high_price(self):
        """Test approaching lower limit with price >= 1000 (margin = 5)."""
        alerts = check_alerts("2330", 1005.0, lower_threshold=1000)
        assert len(alerts) == 1
        assert alerts[0][0] == "yellow"
        assert "接近下限" in alerts[0][1]

    def test_both_limits_triggered(self):
        """Test when both upper and lower limits are hit."""
        alerts = check_alerts("2330", 1000.0, upper_threshold=1000, lower_threshold=1000)
        assert len(alerts) == 2
        assert all(a[0] == "red" for a in alerts)

    def test_none_price_returns_no_alerts(self):
        """Test None price returns no alerts."""
        alerts = check_alerts("2330", None, upper_threshold=1000)
        assert alerts == []

    def test_only_upper_threshold(self):
        """Test with only upper threshold."""
        alerts = check_alerts("2330", 1000.0, upper_threshold=1000)
        assert len(alerts) == 1
        assert "上限" in alerts[0][1]

    def test_only_lower_threshold(self):
        """Test with only lower threshold."""
        alerts = check_alerts("2330", 800.0, lower_threshold=800)
        assert len(alerts) == 1
        assert "下限" in alerts[0][1]

    def test_no_thresholds(self):
        """Test with no thresholds."""
        alerts = check_alerts("2330", 850.0)
        assert alerts == []

    def test_alert_priority_order(self):
        """Test that red alerts come before yellow alerts."""
        alerts = check_alerts("2330", 999.0, upper_threshold=1000, lower_threshold=900)
        # Should have yellow approaching upper, not lower
        assert len(alerts) == 1
        assert alerts[0][0] == "yellow"


class TestHasCriticalAlert:
    """Tests for has_critical_alert function."""

    def test_has_critical_alert_true(self):
        """Test detecting critical (red) alert."""
        alerts = [("red", "已達上限")]
        assert has_critical_alert(alerts) is True

    def test_has_critical_alert_false(self):
        """Test no critical alert."""
        alerts = [("yellow", "接近上限")]
        assert has_critical_alert(alerts) is False

    def test_empty_alerts(self):
        """Test empty alert list."""
        assert has_critical_alert([]) is False

    def test_multiple_alerts_with_red(self):
        """Test multiple alerts with at least one red."""
        alerts = [("yellow", "接近上限"), ("red", "已達下限")]
        assert has_critical_alert(alerts) is True


class TestGetAlertMessage:
    """Tests for get_alert_message function."""

    def test_no_alerts_returns_check(self):
        """Test no alerts returns OK."""
        assert get_alert_message([]) == "OK"

    def test_single_alert(self):
        """Test single alert message."""
        alerts = [("red", "[UPPER] 已達上限 1000!")]
        assert get_alert_message(alerts) == "[UPPER] 已達上限 1000!"

    def test_multiple_alerts_joined(self):
        """Test multiple alerts are joined."""
        alerts = [("red", "[UPPER] 已達上限 1000!"), ("yellow", "[LOW] 接近下限 800")]
        message = get_alert_message(alerts)
        assert "已達上限" in message
        assert "接近下限" in message
        assert "  " in message  # Double space separator


class TestGetAlertSeverity:
    """Tests for get_alert_severity function."""

    def test_no_alerts_returns_none(self):
        """Test no alerts returns None."""
        assert get_alert_severity([]) is None

    def test_red_alert_returns_red(self):
        """Test red alert returns red."""
        alerts = [("red", "已達上限")]
        assert get_alert_severity(alerts) == "red"

    def test_yellow_alert_returns_yellow(self):
        """Test yellow alert returns yellow."""
        alerts = [("yellow", "接近上限")]
        assert get_alert_severity(alerts) == "yellow"

    def test_mixed_alerts_returns_red(self):
        """Test mixed alerts returns red (highest priority)."""
        alerts = [("yellow", "接近上限"), ("red", "已達下限")]
        assert get_alert_severity(alerts) == "red"

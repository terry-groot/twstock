"""Unit tests for market_monitor.utils module."""

import pytest
from market_monitor.utils import (
    parse_price,
    cjk_len,
    ljust_cjk,
    rjust_cjk,
    format_price,
    format_volume,
)


class TestParsePrice:
    """Tests for parse_price function."""

    def test_parse_valid_float_string(self):
        """Test parsing valid float string."""
        assert parse_price("123.45") == 123.45

    def test_parse_integer_string(self):
        """Test parsing integer string."""
        assert parse_price("100") == 100.0

    def test_parse_float_value(self):
        """Test parsing float value."""
        assert parse_price(99.99) == 99.99

    def test_parse_integer_value(self):
        """Test parsing integer value."""
        assert parse_price(100) == 100.0

    def test_parse_none_returns_none(self):
        """Test None input returns None."""
        assert parse_price(None) is None

    def test_parse_dash_returns_none(self):
        """Test dash returns None."""
        assert parse_price("-") is None

    def test_parse_empty_string_returns_none(self):
        """Test empty string returns None."""
        assert parse_price("") is None

    def test_parse_invalid_string_returns_none(self):
        """Test invalid string returns None."""
        assert parse_price("invalid") is None

    def test_parse_scientific_notation(self):
        """Test scientific notation."""
        assert parse_price("1.23e2") == 123.0


class TestCJKLen:
    """Tests for cjk_len function."""

    def test_ascii_only(self):
        """Test ASCII-only string."""
        assert cjk_len("TSMC") == 4

    def test_cjk_only(self):
        """Test CJK-only string."""
        assert cjk_len("台積電") == 6  # 3 CJK chars * 2 width

    def test_mixed_ascii_and_cjk(self):
        """Test mixed ASCII and CJK."""
        assert cjk_len("台積電TSMC") == 10  # 6 + 4

    def test_empty_string(self):
        """Test empty string."""
        assert cjk_len("") == 0

    def test_single_ascii_char(self):
        """Test single ASCII character."""
        assert cjk_len("A") == 1

    def test_single_cjk_char(self):
        """Test single CJK character."""
        assert cjk_len("中") == 2

    def test_numbers_and_symbols(self):
        """Test numbers and symbols."""
        assert cjk_len("2330 (NT$)") == 10


class TestCJKFormatting:
    """Tests for CJK-aware formatting functions."""

    def test_ljust_cjk_ascii(self):
        """Test ljust_cjk with ASCII."""
        result = ljust_cjk("ABC", 5)
        assert cjk_len(result) == 5
        assert result.startswith("ABC")

    def test_ljust_cjk_mixed(self):
        """Test ljust_cjk with mixed content."""
        result = ljust_cjk("台積", 8)
        assert cjk_len(result) == 8
        assert result.startswith("台積")

    def test_rjust_cjk_ascii(self):
        """Test rjust_cjk with ASCII."""
        result = rjust_cjk("ABC", 5)
        assert cjk_len(result) == 5
        assert result.endswith("ABC")

    def test_rjust_cjk_mixed(self):
        """Test rjust_cjk with mixed content."""
        result = rjust_cjk("台積", 8)
        assert cjk_len(result) == 8
        assert result.endswith("台積")

    def test_no_padding_needed(self):
        """Test when no padding is needed."""
        assert ljust_cjk("ABC", 3) == "ABC"
        assert rjust_cjk("ABC", 3) == "ABC"


class TestFormatPrice:
    """Tests for format_price function."""

    def test_format_valid_price(self):
        """Test formatting valid price."""
        assert format_price(123.456) == "123.5"
        assert format_price(123.456, 2) == "123.46"

    def test_format_none_price(self):
        """Test formatting None price."""
        assert format_price(None) == "--"

    def test_format_zero(self):
        """Test formatting zero."""
        assert format_price(0.0) == "0.0"

    def test_format_large_price(self):
        """Test formatting large price."""
        assert format_price(1000.0) == "1000.0"


class TestFormatVolume:
    """Tests for format_volume function."""

    def test_format_valid_volume(self):
        """Test formatting valid volume."""
        assert format_volume("15000000") == "15000000"
        assert format_volume(15000000) == "15000000"

    def test_format_none_volume(self):
        """Test formatting None volume."""
        assert format_volume(None) == "--"

    def test_format_empty_string_volume(self):
        """Test formatting empty string volume."""
        assert format_volume("") == "--"

    def test_format_dash_volume(self):
        """Test formatting dash volume."""
        assert format_volume("-") == "--"

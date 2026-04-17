"""Utility functions for market monitoring."""

from typing import Optional


def parse_price(value: any) -> Optional[float]:
    """Parse price from API response value.

    Handles various formats including:
    - None or empty values
    - String representations of numbers
    - Dash (-) indicating no value
    - Float/int values

    Args:
        value: Value from API response

    Returns:
        Parsed float value or None for missing/invalid values
    """
    if value is None or value == "" or value == "-":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def cjk_len(text: str) -> int:
    """Calculate display width of string accounting for CJK characters.

    CJK characters (Chinese, Japanese, Korean) are typically 2 columns wide
    in terminal display, while ASCII characters are 1 column wide.

    Args:
        text: String to measure

    Returns:
        Display width in columns
    """
    return sum(2 if ord(c) > 127 else 1 for c in text)


def ljust_cjk(text: str, width: int) -> str:
    """Left-justify string with CJK-aware padding.

    Args:
        text: String to pad
        width: Target display width

    Returns:
        Padded string
    """
    return text + ' ' * max(width - cjk_len(text), 0)


def rjust_cjk(text: str, width: int) -> str:
    """Right-justify string with CJK-aware padding.

    Args:
        text: String to pad
        width: Target display width

    Returns:
        Padded string
    """
    return ' ' * max(width - cjk_len(text), 0) + text


def format_price(price: Optional[float], decimals: int = 1) -> str:
    """Format price for display.

    Args:
        price: Price value or None
        decimals: Number of decimal places

    Returns:
        Formatted price string or "--" for None
    """
    if price is None:
        return "--"
    return f"{price:.{decimals}f}"


def format_volume(volume: any) -> str:
    """Format volume for display.

    Args:
        volume: Volume value from API

    Returns:
        Volume string or "--" for None/empty
    """
    if not volume or volume == "-":
        return "--"
    return str(volume)

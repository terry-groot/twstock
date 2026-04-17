"""Alert checking logic for monitoring."""

from typing import List, Tuple, Optional, Dict


def check_alerts(
    asset_id: str,
    price: Optional[float],
    upper_threshold: Optional[float] = None,
    lower_threshold: Optional[float] = None
) -> List[Tuple[str, str]]:
    """Check for price alerts based on thresholds.

    Priority order (highest to lowest):
    1. Exact limit hit (red) - upper or lower
    2. Approaching limit (yellow) - upper or lower

    Args:
        asset_id: Asset identifier
        price: Current price or None
        upper_threshold: Upper price threshold
        lower_threshold: Lower price threshold

    Returns:
        List of (severity, message) tuples, ordered by priority
        Severity: 'red' (critical) or 'yellow' (warning)
    """
    if price is None:
        return []

    alerts = []

    # Determine margin based on price magnitude
    margin = 5 if price >= 1000 else 1

    # Check upper threshold (higher priority)
    if upper_threshold:
        if price >= upper_threshold:
            alerts.append(("red", f"[UPPER] 已達上限 {upper_threshold}!"))
        elif price >= upper_threshold - margin:
            alerts.append(("yellow", f"[HIGH] 接近上限 {upper_threshold}"))

    # Check lower threshold
    if lower_threshold:
        if price <= lower_threshold:
            alerts.append(("red", f"[LOWER] 已達下限 {lower_threshold}!"))
        elif price <= lower_threshold + margin:
            alerts.append(("yellow", f"[LOW] 接近下限 {lower_threshold}"))

    # Sort by severity: red first, then yellow
    red_alerts = [a for a in alerts if a[0] == "red"]
    yellow_alerts = [a for a in alerts if a[0] == "yellow"]
    return red_alerts + yellow_alerts


def has_critical_alert(alerts: List[Tuple[str, str]]) -> bool:
    """Check if any alert is critical (red).

    Args:
        alerts: List of alert tuples from check_alerts

    Returns:
        True if any red alert exists
    """
    return any(alert[0] == "red" for alert in alerts)


def get_alert_message(alerts: List[Tuple[str, str]]) -> str:
    """Get formatted alert message for display.

    Args:
        alerts: List of alert tuples

    Returns:
        Formatted alert message or "OK" if no alerts
    """
    if not alerts:
        return "OK"
    return "  ".join(alert[1] for alert in alerts)


def get_alert_severity(alerts: List[Tuple[str, str]]) -> Optional[str]:
    """Get highest severity level from alerts.

    Args:
        alerts: List of alert tuples

    Returns:
        'red' if any red alert, 'yellow' if only yellow alerts, None otherwise
    """
    if not alerts:
        return None
    return "red" if has_critical_alert(alerts) else "yellow"

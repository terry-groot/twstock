"""Terminal UI rendering for market monitor."""

import os
import sys
import datetime
from typing import List, Dict, Tuple, Optional
from market_monitor.core import AssetData
from market_monitor.utils import ljust_cjk, rjust_cjk, cjk_len, format_price
from market_monitor.alerts import check_alerts, get_alert_message, get_alert_severity

# ANSI color codes
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RESET = "\033[0m"


def clear_screen() -> None:
    """Clear terminal screen (Windows/Unix compatible)."""
    os.system("cls" if os.name == "nt" else "clear")


def get_color_code(severity: Optional[str]) -> str:
    """Get ANSI color code for alert severity.

    Args:
        severity: Alert severity ('red', 'yellow', None)

    Returns:
        ANSI color code
    """
    if severity == "red":
        return RED
    elif severity == "yellow":
        return YELLOW
    return GREEN


def render_asset_row(
    asset_id: str,
    asset_name: str,
    asset_type: str,
    asset_data: Optional[AssetData],
    config: Dict = None,
) -> Tuple[str, str]:
    """Render a single asset row.

    Args:
        asset_id: Asset identifier
        asset_name: Display name
        asset_type: Asset type ('stock' or 'futures')
        asset_data: Asset market data or None if unavailable
        config: Asset configuration dict

    Returns:
        Tuple of (colored_row, severity)
    """
    config = config or {}
    color = GREEN
    status = "OK"

    if asset_data is None:
        # Unavailable
        row = (
            f"{ljust_cjk(asset_id, 6)} {ljust_cjk(asset_name, 10)}"
            f" {rjust_cjk('--', 8)} {rjust_cjk('--', 8)} {rjust_cjk('--', 8)} {rjust_cjk('--', 8)} {rjust_cjk('--', 8)}  無法取得"
        )
        color = YELLOW
        status = "warning"
    else:
        # Check alerts
        alerts = check_alerts(
            asset_id,
            asset_data.price,
            upper_threshold=config.get("upper"),
            lower_threshold=config.get("lower"),
        )

        # Determine color
        severity = get_alert_severity(alerts)
        color = get_color_code(severity)
        status = severity or "ok"

        # Format prices
        price_str = format_price(asset_data.price)
        open_str = format_price(asset_data.open)
        high_str = format_price(asset_data.high)
        low_str = format_price(asset_data.low)
        change = asset_data.change or "--"

        # Build row (unified format for both stocks and futures)
        row = (
            f"{ljust_cjk(asset_id, 6)} {ljust_cjk(asset_name, 10)}"
            f" {rjust_cjk(price_str, 8)} {rjust_cjk(open_str, 8)} {rjust_cjk(high_str, 8)} {rjust_cjk(low_str, 8)} {rjust_cjk(change, 8)}  "
            f"{get_alert_message(alerts)}"
        )

    return f"{color}{row}{RESET}", status


def render_table(
    assets: Dict[str, Tuple[str, any]],
    asset_data: Dict[str, Optional[AssetData]],
) -> str:
    """Render complete market data table.

    Args:
        assets: Dict of asset_id -> (asset_type, config) tuples
        asset_data: Dict of asset_id -> AssetData (or None)

    Returns:
        Formatted table string
    """
    clear_screen()

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = "=" * 80
    output = []
    output.append(line)
    output.append(f"  台灣股票期貨即時報價監控  |  更新時間: {now}  |  按 Ctrl+C 結束")
    output.append(line)

    # Header (use CJK-aware alignment for all columns)
    header = (
        f"{ljust_cjk('代號', 6)} {ljust_cjk('名稱', 10)}"
        f" {rjust_cjk('現價', 8)} {rjust_cjk('開盤', 8)} {rjust_cjk('最高', 8)} {rjust_cjk('最低', 8)} {rjust_cjk('漲跌', 8)}  狀態"
    )
    output.append(header)
    output.append("-" * 80)

    # Asset rows
    has_critical = False
    for asset_id in sorted(assets.keys()):
        asset_type, config = assets[asset_id]
        data = asset_data.get(asset_id)
        row, severity = render_asset_row(asset_id, config.get("name", asset_id), asset_type, data, config)
        output.append(row)

        if severity == "red":
            has_critical = True

    output.append(line)
    output.append("  ※ 資料為延遲報價（非即時）")

    return "\n".join(output), has_critical


def render_error_message(message: str) -> None:
    """Render an error message to console.

    Args:
        message: Error message to display
    """
    print(f"{RED}[錯誤] {message}{RESET}", file=sys.stderr)


def render_warning_message(message: str) -> None:
    """Render a warning message to console.

    Args:
        message: Warning message to display
    """
    print(f"{YELLOW}[警告] {message}{RESET}", file=sys.stderr)


def render_info_message(message: str) -> None:
    """Render an info message to console.

    Args:
        message: Info message to display
    """
    print(f"{GREEN}[資訊] {message}{RESET}")

"""TWSE stock market data source."""

import twstock
from typing import List, Dict, Optional
from market_monitor.core import DataSource, AssetData
from market_monitor.utils import parse_price, format_volume
from market_monitor.logging_setup import get_logger

logger = get_logger("sources.stocks")


class StockSource(DataSource):
    """Data source for Taiwan stock exchange (TWSE) stocks."""

    def __init__(self, interval: int = 5):
        """Initialize stock data source.

        Args:
            interval: Polling interval in seconds (default 5)
        """
        super().__init__("stocks", interval)
        self.transient_errors = {"timeout", "rate_limit", "connection"}
        self.permanent_errors = {"not_found", "invalid_code"}

    def fetch(self, asset_ids: List[str]) -> Dict[str, Optional[AssetData]]:
        """Fetch current stock prices from TWSE API.

        Args:
            asset_ids: List of stock IDs to fetch

        Returns:
            Dictionary mapping stock_id to AssetData (None if fetch failed)
        """
        if not asset_ids:
            return {}

        try:
            logger.debug(f"Fetching {len(asset_ids)} stocks from TWSE")
            data = twstock.realtime.get(asset_ids)

            if not data or not data.get("success"):
                logger.warning(
                    f"TWSE API failed: rtcode={data.get('rtcode') if data else 'None'}, "
                    f"msg={data.get('rtmessage') if data else 'No response'}"
                )
                return {sid: None for sid in asset_ids}

            results = {}
            for sid in asset_ids:
                info = data.get(sid)
                if not info or not info.get("success"):
                    logger.debug(f"Failed to fetch stock {sid}")
                    results[sid] = None
                    continue

                try:
                    rt = info["realtime"]
                    asset_data = AssetData(
                        asset_id=sid,
                        price=parse_price(rt.get("latest_trade_price")),
                        open=parse_price(rt.get("open")),
                        high=parse_price(rt.get("high")),
                        low=parse_price(rt.get("low")),
                        volume=format_volume(rt.get("accumulate_trade_volume")),
                        time=info.get("info", {}).get("time")
                    )
                    results[sid] = asset_data
                    logger.debug(f"Stock {sid}: {asset_data.price}")
                except Exception as e:
                    logger.error(f"Failed to parse stock {sid}: {e}")
                    results[sid] = None

            # Update cache with successful fetches
            self.update_cache(results)
            return results

        except Exception as e:
            logger.error(f"Stock fetch exception: {e}")
            return {sid: None for sid in asset_ids}

    def is_transient_error(self, error: str) -> bool:
        """Check if error is transient (will retry).

        Args:
            error: Error type

        Returns:
            True if error is transient
        """
        return any(transient in error.lower() for transient in self.transient_errors)

    def is_permanent_error(self, error: str) -> bool:
        """Check if error is permanent (won't retry).

        Args:
            error: Error type

        Returns:
            True if error is permanent
        """
        return any(permanent in error.lower() for permanent in self.permanent_errors)

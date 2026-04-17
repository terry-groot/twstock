"""Taifex futures market data source."""

import urllib.request
import json
from typing import List, Dict, Optional
from market_monitor.core import DataSource, AssetData
from market_monitor.utils import parse_price, format_volume
from market_monitor.logging_setup import get_logger

logger = get_logger("sources.futures")

TAIFEX_BASE = "https://openapi.taifex.com.tw/v1"


class FuturesSource(DataSource):
    """Data source for Taiwan futures exchange (Taifex) contracts."""

    def __init__(self, interval: int = 30):
        """Initialize futures data source.

        Args:
            interval: Polling interval in seconds (default 30)
        """
        super().__init__("futures", interval)
        self.ssf_map: Dict[str, str] = {}  # stock_code -> contract_symbol
        self.market_data: Dict[str, Dict] = {}  # contract -> data

    def fetch_json(self, url: str, timeout: int = 10) -> Optional[any]:
        """Fetch JSON from URL.

        Args:
            url: URL to fetch
            timeout: Request timeout in seconds

        Returns:
            Parsed JSON or None if failed
        """
        try:
            req = urllib.request.Request(
                url,
                headers={"Accept": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def build_ssf_map(self) -> bool:
        """Build mapping of stock codes to futures contracts.

        Returns:
            True if successful
        """
        try:
            data = self.fetch_json(f"{TAIFEX_BASE}/SSFLists")
            if not data:
                return False

            self.ssf_map = {item["StockCode"]: item["Contract"] for item in data}
            logger.info(f"Built SSF map with {len(self.ssf_map)} entries")
            return True
        except Exception as e:
            logger.error(f"Failed to build SSF map: {e}")
            return False

    def fetch_market_data(self) -> bool:
        """Fetch latest market data for all futures contracts.

        Returns:
            True if successful
        """
        try:
            data = self.fetch_json(f"{TAIFEX_BASE}/DailyMarketReportFut")
            if not data:
                return False

            self.market_data = {}
            for item in data:
                if item.get("TradingSession") != "一般":
                    continue

                code = item["Contract"]
                month = item.get("ContractMonth(Week)", "")

                # Keep only the nearest (smallest) month per contract
                if code not in self.market_data or month < self.market_data[code]["month"]:
                    self.market_data[code] = {
                        "month": month,
                        "price": parse_price(item.get("Last")),
                        "open": parse_price(item.get("Open")),
                        "high": parse_price(item.get("High")),
                        "low": parse_price(item.get("Low")),
                        "volume": format_volume(item.get("Volume")),
                        "bid": parse_price(item.get("BestBid")),
                        "ask": parse_price(item.get("BestAsk")),
                        "change": item.get("Change", ""),
                    }

            logger.debug(f"Fetched market data for {len(self.market_data)} contracts")
            return True
        except Exception as e:
            logger.error(f"Failed to fetch market data: {e}")
            return False

    def resolve_contract(self, contract_id: str) -> Optional[str]:
        """Resolve a contract ID to its symbol.

        Args:
            contract_id: Contract ID (e.g., "TX" or "2330")

        Returns:
            Contract symbol or None if not found
        """
        if contract_id.isdigit():
            # Stock code - look up in SSF map
            return self.ssf_map.get(contract_id)
        else:
            # Direct contract code
            return contract_id

    def fetch(self, asset_ids: List[str]) -> Dict[str, Optional[AssetData]]:
        """Fetch current futures prices.

        Args:
            asset_ids: List of contract IDs to fetch

        Returns:
            Dictionary mapping contract_id to AssetData (None if fetch failed)
        """
        if not asset_ids:
            return {}

        # Fetch SSF map if needed
        if not self.ssf_map:
            if not self.build_ssf_map():
                logger.warning("Failed to build SSF map")
                return {aid: None for aid in asset_ids}

        # Fetch market data
        if not self.fetch_market_data():
            logger.warning("Failed to fetch market data")
            return {aid: None for aid in asset_ids}

        results = {}
        for asset_id in asset_ids:
            sym = self.resolve_contract(asset_id)
            if sym is None:
                logger.debug(f"Failed to resolve contract {asset_id}")
                results[asset_id] = None
                continue

            market_data = self.market_data.get(sym)
            if market_data is None:
                logger.debug(f"No market data for {asset_id} (symbol: {sym})")
                results[asset_id] = None
                continue

            try:
                asset_data = AssetData(
                    asset_id=asset_id,
                    price=market_data["price"],
                    open=market_data["open"],
                    high=market_data["high"],
                    low=market_data["low"],
                    bid=market_data["bid"],
                    ask=market_data["ask"],
                    change=market_data["change"],
                    volume=market_data["volume"],
                )
                results[asset_id] = asset_data
                logger.debug(f"Futures {asset_id}: {asset_data.price}")
            except Exception as e:
                logger.error(f"Failed to parse futures {asset_id}: {e}")
                results[asset_id] = None

        # Update cache
        self.update_cache(results)
        return results

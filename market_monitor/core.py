"""Core classes for market monitoring framework."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional, List
from datetime import datetime


@dataclass
class AssetData:
    """Represents current market data for an asset."""
    asset_id: str
    price: Optional[float] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    volume: Optional[str] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    change: Optional[str] = None
    time: Optional[str] = None
    timestamp: Optional[datetime] = None


class DataSource(ABC):
    """Abstract base class for market data sources."""

    def __init__(self, name: str, interval: int = 5):
        """Initialize data source.

        Args:
            name: Name of the data source (e.g., 'stocks', 'futures')
            interval: Default polling interval in seconds
        """
        self.name = name
        self.interval = interval
        self._cache: Dict[str, AssetData] = {}
        self._last_fetch_time: Optional[datetime] = None

    @abstractmethod
    def fetch(self, asset_ids: List[str]) -> Dict[str, Optional[AssetData]]:
        """Fetch current market data for given assets.

        Args:
            asset_ids: List of asset identifiers to fetch

        Returns:
            Dictionary mapping asset_id to AssetData (or None if fetch failed)
        """
        pass

    def get_cached_data(self, asset_id: str) -> Optional[AssetData]:
        """Get cached data for an asset.

        Args:
            asset_id: Asset identifier

        Returns:
            Cached AssetData if available, None otherwise
        """
        return self._cache.get(asset_id)

    def update_cache(self, data: Dict[str, Optional[AssetData]]) -> None:
        """Update internal cache with new data.

        Args:
            data: Dictionary of asset data to cache
        """
        self._cache.update({k: v for k, v in data.items() if v is not None})
        self._last_fetch_time = datetime.now()

    def get_properties(self) -> Dict[str, any]:
        """Get source properties for introspection.

        Returns:
            Dictionary with name, interval, and other metadata
        """
        return {
            'name': self.name,
            'interval': self.interval,
            'cached_assets': len(self._cache),
            'last_fetch_time': self._last_fetch_time
        }


class Monitor:
    """Main monitoring framework that orchestrates multiple data sources."""

    def __init__(self, config: Dict = None):
        """Initialize monitor with configuration.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.data_sources: Dict[str, DataSource] = {}
        self.asset_data: Dict[str, AssetData] = {}

    def register_source(self, source: DataSource) -> None:
        """Register a data source with the monitor.

        Args:
            source: DataSource instance to register
        """
        self.data_sources[source.name] = source

    def unregister_source(self, name: str) -> None:
        """Unregister a data source.

        Args:
            name: Name of the source to unregister
        """
        if name in self.data_sources:
            del self.data_sources[name]

    def get_asset_data(self, asset_id: str) -> Optional[AssetData]:
        """Get current data for a specific asset.

        Args:
            asset_id: Asset identifier

        Returns:
            AssetData if available, None otherwise
        """
        return self.asset_data.get(asset_id)

    def get_source_properties(self) -> Dict[str, Dict]:
        """Get properties for all registered sources.

        Returns:
            Dictionary mapping source names to their properties
        """
        return {name: source.get_properties() for name, source in self.data_sources.items()}

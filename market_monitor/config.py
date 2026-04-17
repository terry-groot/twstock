"""Configuration management for market monitor."""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field


@dataclass
class AssetConfig:
    """Configuration for a single asset."""
    id: str
    name: str
    upper: Optional[float] = None
    lower: Optional[float] = None
    enabled: bool = True


@dataclass
class MonitorConfig:
    """Configuration for monitoring intervals and behavior."""
    stock_interval: int = 5
    futures_interval: int = 30
    retry_max_attempts: int = 3
    retry_backoff_seconds: int = 2
    beep_enabled: bool = True
    log_level: str = "INFO"
    log_file: Optional[str] = None


@dataclass
class Config:
    """Main configuration container."""
    stocks: List[AssetConfig] = field(default_factory=list)
    futures: List[AssetConfig] = field(default_factory=list)
    monitor: MonitorConfig = field(default_factory=MonitorConfig)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "stocks": [asdict(s) for s in self.stocks],
            "futures": [asdict(f) for f in self.futures],
            "monitor": asdict(self.monitor)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create Config from dictionary."""
        stocks = [AssetConfig(**s) for s in data.get("stocks", [])]
        futures = [AssetConfig(**f) for f in data.get("futures", [])]
        monitor_data = data.get("monitor", {})
        monitor = MonitorConfig(**monitor_data)
        return cls(stocks=stocks, futures=futures, monitor=monitor)

    def validate(self) -> List[str]:
        """Validate configuration.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check stocks
        for stock in self.stocks:
            if not stock.id:
                errors.append("Stock must have 'id'")
            if stock.upper and stock.lower and stock.upper < stock.lower:
                errors.append(f"Stock {stock.id}: upper threshold cannot be less than lower")

        # Check futures
        for future in self.futures:
            if not future.id:
                errors.append("Future must have 'id'")
            if future.upper and future.lower and future.upper < future.lower:
                errors.append(f"Future {future.id}: upper threshold cannot be less than lower")

        # Check monitor settings
        if self.monitor.stock_interval < 1:
            errors.append("stock_interval must be at least 1 second")
        if self.monitor.futures_interval < 1:
            errors.append("futures_interval must be at least 1 second")
        if self.monitor.retry_max_attempts < 1:
            errors.append("retry_max_attempts must be at least 1")
        if self.monitor.retry_backoff_seconds < 0:
            errors.append("retry_backoff_seconds must be non-negative")

        return errors

    def get_all_assets(self) -> Dict[str, tuple]:
        """Get all assets with their type.

        Returns:
            Dictionary mapping asset_id to (type, config) tuple
        """
        assets = {}
        for stock in self.stocks:
            if stock.enabled:
                assets[stock.id] = ("stock", stock)
        for future in self.futures:
            if future.enabled:
                assets[future.id] = ("futures", future)
        return assets


def load_config(path: str = "monitor_config.json") -> Config:
    """Load configuration from file.

    Args:
        path: Path to configuration file

    Returns:
        Loaded configuration

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config is invalid
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    config = Config.from_dict(data)
    errors = config.validate()
    if errors:
        raise ValueError(f"Configuration validation failed:\n" + "\n".join(errors))

    return config


def save_config(config: Config, path: str = "monitor_config.json") -> None:
    """Save configuration to file.

    Args:
        config: Configuration to save
        path: Path to save to
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config.to_dict(), f, ensure_ascii=False, indent=2)


def create_default_config(path: str = "monitor_config.json") -> Config:
    """Create and save default configuration.

    Args:
        path: Path to save default config

    Returns:
        Created default configuration
    """
    config = Config(
        stocks=[
            AssetConfig(id="2330", name="台積電", upper=1000, lower=900)
        ],
        futures=[
            AssetConfig(id="TX", name="台指期", upper=34000, lower=32000),
            AssetConfig(id="2330", name="台積電期", upper=1900, lower=1760)
        ]
    )
    save_config(config, path)
    return config


def migrate_legacy_config(old_stocks_path: str = "config.json",
                         old_futures_path: str = "futures_config.json",
                         new_path: str = "monitor_config.json") -> Optional[Config]:
    """Migrate legacy configuration format to new unified format.

    Args:
        old_stocks_path: Path to old stocks config
        old_futures_path: Path to old futures config
        new_path: Path to save new unified config

    Returns:
        Migrated config if migration occurred, None otherwise
    """
    stocks_exists = os.path.exists(old_stocks_path)
    futures_exists = os.path.exists(old_futures_path)

    if not stocks_exists and not futures_exists:
        return None

    # Backup old files
    if stocks_exists:
        backup_path = f"{old_stocks_path}.backup"
        shutil.copy(old_stocks_path, backup_path)

    if futures_exists:
        backup_path = f"{old_futures_path}.backup"
        shutil.copy(old_futures_path, backup_path)

    # Load old configs
    stocks = []
    futures = []

    if stocks_exists:
        with open(old_stocks_path, "r", encoding="utf-8") as f:
            old_config = json.load(f)
        stocks = [AssetConfig(**s) for s in old_config.get("stocks", [])]

    if futures_exists:
        with open(old_futures_path, "r", encoding="utf-8") as f:
            old_config = json.load(f)
        futures = [AssetConfig(**c) for c in old_config.get("contracts", [])]

    # Create new config
    config = Config(stocks=stocks, futures=futures)
    save_config(config, new_path)

    return config

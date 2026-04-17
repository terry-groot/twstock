# API Documentation

## Core Classes

### AssetData

Represents current market data for an asset.

```python
from market_monitor.core import AssetData

@dataclass
class AssetData:
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
```

**Attributes:**
- `asset_id`: Asset identifier (e.g., "2330", "TXF")
- `price`: Current price
- `open`: Opening price
- `high`: Daily high
- `low`: Daily low
- `volume`: Trading volume as string
- `bid`: Bid price (if available)
- `ask`: Ask price (if available)
- `change`: Price change as string
- `time`: Last update time as string
- `timestamp`: Last update timestamp

---

### DataSource

Abstract base class for market data providers.

```python
from market_monitor.core import DataSource, AssetData
from typing import List, Dict, Optional

class DataSource(ABC):
    def __init__(self, name: str, interval: int = 5):
        """Initialize data source.
        
        Args:
            name: Name of the data source
            interval: Default polling interval in seconds
        """
        self.name = name
        self.interval = interval

    @abstractmethod
    def fetch(self, asset_ids: List[str]) -> Dict[str, Optional[AssetData]]:
        """Fetch current market data for given assets.
        
        Args:
            asset_ids: List of asset identifiers
            
        Returns:
            Dictionary mapping asset_id to AssetData (or None if failed)
        """
        pass

    def get_cached_data(self, asset_id: str) -> Optional[AssetData]:
        """Get cached data for an asset.
        
        Args:
            asset_id: Asset identifier
            
        Returns:
            Cached AssetData if available
        """
        pass

    def update_cache(self, data: Dict[str, Optional[AssetData]]) -> None:
        """Update internal cache with new data.
        
        Args:
            data: Dictionary of asset data
        """
        pass

    def get_properties(self) -> Dict[str, any]:
        """Get source properties.
        
        Returns:
            Dictionary with name, interval, and metadata
        """
        pass
```

---

### Monitor

Base monitor class for orchestrating data sources.

```python
from market_monitor.core import Monitor
from market_monitor.config import Config

class Monitor(ABC):
    def __init__(self, config: Config):
        """Initialize monitor.
        
        Args:
            config: Configuration object
        """
        self.config = config

    def register_source(self, source_type: str, source: DataSource) -> None:
        """Register a data source by type.
        
        Args:
            source_type: Source type identifier
            source: DataSource instance
        """
        pass

    def register_source_instance(self, source: DataSource) -> None:
        """Register a data source instance.
        
        Args:
            source: DataSource instance
        """
        pass

    @abstractmethod
    def run(self) -> None:
        """Start the main monitoring loop."""
        pass
```

---

## Configuration Classes

### AssetConfig

Configuration for an individual asset.

```python
from market_monitor.config import AssetConfig

@dataclass
class AssetConfig:
    asset_id: str
    name: Optional[str] = None
    enabled: bool = True
    upper: Optional[float] = None
    lower: Optional[float] = None
```

**Attributes:**
- `asset_id`: Asset identifier (required)
- `name`: Display name
- `enabled`: Whether asset is monitored
- `upper`: Upper price threshold for alerts
- `lower`: Lower price threshold for alerts

---

### MonitorConfig

Monitoring parameters.

```python
from market_monitor.config import MonitorConfig

@dataclass
class MonitorConfig:
    stock_interval: int = 5
    futures_interval: int = 30
    retry_max_attempts: int = 3
    retry_initial_backoff: float = 1.0
```

**Attributes:**
- `stock_interval`: Stock polling interval in seconds
- `futures_interval`: Futures polling interval in seconds
- `retry_max_attempts`: Maximum retry attempts
- `retry_initial_backoff`: Initial retry backoff in seconds

---

### Config

Main configuration container.

```python
from market_monitor.config import Config, load_config, create_default_config

class Config:
    def __init__(
        self,
        monitor: MonitorConfig,
        assets: List[AssetConfig]
    ):
        """Initialize configuration.
        
        Args:
            monitor: Monitor configuration
            assets: List of asset configurations
        """
        self.monitor = monitor
        self.assets = assets

    def get_all_assets(self, only_enabled: bool = False) -> List[AssetConfig]:
        """Get all assets (optionally only enabled ones).
        
        Args:
            only_enabled: Filter to enabled assets only
            
        Returns:
            List of asset configurations
        """
        pass

    def to_dict(self) -> Dict:
        """Convert configuration to dictionary."""
        pass

    @classmethod
    def from_dict(cls, data: Dict) -> 'Config':
        """Create configuration from dictionary."""
        pass
```

**Functions:**

```python
def load_config(path: str) -> Config:
    """Load configuration from JSON file.
    
    Args:
        path: Path to configuration file
        
    Returns:
        Config object
        
    Raises:
        ValueError: If configuration is invalid
        FileNotFoundError: If file doesn't exist
    """
    pass

def create_default_config(path: str = "monitor_config.json") -> Config:
    """Create and save default configuration.
    
    Args:
        path: Path to save configuration
        
    Returns:
        Default Config object
    """
    pass

def migrate_legacy_config(
    old_stocks_path: str = "config.json",
    old_futures_path: str = "futures_config.json",
    new_path: str = "monitor_config.json"
) -> Optional[Config]:
    """Migrate legacy configuration to new format.
    
    Args:
        old_stocks_path: Path to old stocks config
        old_futures_path: Path to old futures config
        new_path: Path to save new config
        
    Returns:
        Migrated Config object or None if no legacy config found
    """
    pass
```

---

## Utility Functions

### Price Parsing

```python
from market_monitor.utils import parse_price, format_price

def parse_price(value: any) -> Optional[float]:
    """Parse a price value from various formats.
    
    Args:
        value: Price value (string, float, int, or None)
        
    Returns:
        Parsed float price or None if invalid
        
    Examples:
        >>> parse_price("100.50")
        100.5
        >>> parse_price(100)
        100.0
        >>> parse_price(None)
        None
        >>> parse_price("-")
        None
    """
    pass

def format_price(price: Optional[float]) -> str:
    """Format a price for display.
    
    Args:
        price: Price value or None
        
    Returns:
        Formatted price string
        
    Examples:
        >>> format_price(100.5)
        '100.50'
        >>> format_price(None)
        '--'
    """
    pass

def format_volume(volume: any) -> str:
    """Format volume for display.
    
    Args:
        volume: Volume value or string
        
    Returns:
        Formatted volume string (in thousands with K suffix)
        
    Examples:
        >>> format_volume("1234567")
        '1234.6K'
    """
    pass
```

---

### CJK Character Handling

```python
from market_monitor.utils import cjk_len, ljust_cjk, rjust_cjk

def cjk_len(text: str) -> int:
    """Calculate display width of text with CJK characters.
    
    Args:
        text: Text string (may contain CJK characters)
        
    Returns:
        Display width (CJK = 2, ASCII = 1)
        
    Examples:
        >>> cjk_len("abc")
        3
        >>> cjk_len("台積電")
        6
        >>> cjk_len("台積ABC")
        8
    """
    pass

def ljust_cjk(text: str, width: int, fillchar: str = ' ') -> str:
    """Left-justify text with CJK awareness.
    
    Args:
        text: Text to justify
        width: Target display width
        fillchar: Character to fill with
        
    Returns:
        Justified string
        
    Examples:
        >>> ljust_cjk("台", 10)
        '台        '  # 2 width + 8 spaces = 10 width
    """
    pass

def rjust_cjk(text: str, width: int, fillchar: str = ' ') -> str:
    """Right-justify text with CJK awareness.
    
    Args:
        text: Text to justify
        width: Target display width
        fillchar: Character to fill with
        
    Returns:
        Justified string
    """
    pass
```

---

## Alert Functions

### Alert Checking

```python
from market_monitor.alerts import check_alerts, get_alert_message, get_alert_severity

def check_alerts(
    asset_id: str,
    price: Optional[float],
    upper_threshold: Optional[float] = None,
    lower_threshold: Optional[float] = None
) -> List[str]:
    """Check if price triggers any alerts.
    
    Args:
        asset_id: Asset identifier
        price: Current price
        upper_threshold: Upper alert threshold
        lower_threshold: Lower alert threshold
        
    Returns:
        List of alert messages
        
    Alert Types:
        - "🔴 Upper limit" (price >= upper_threshold)
        - "🟡 Approaching upper limit" (price within margin of upper)
        - "🔴 Lower limit" (price <= lower_threshold)
        - "🟡 Approaching lower limit" (price within margin of lower)
    """
    pass

def get_alert_message(alerts: List[str]) -> str:
    """Format alerts into a display message.
    
    Args:
        alerts: List of alert messages
        
    Returns:
        Formatted alert string
        
    Examples:
        >>> get_alert_message(["🔴 Upper limit"])
        '🔴 Upper limit'
        >>> get_alert_message([])
        '✓'
    """
    pass

def get_alert_severity(alerts: List[str]) -> Optional[str]:
    """Get the highest severity from alerts.
    
    Args:
        alerts: List of alert messages
        
    Returns:
        Severity level: 'red', 'yellow', or None
        
    Priority:
        - 'red' (critical) > 'yellow' (warning) > None
    """
    pass
```

---

## UI Rendering Functions

```python
from market_monitor.ui import render_table, render_asset_row, render_info_message, render_error_message

def render_table(
    assets: List[Tuple[str, str, str, Optional[AssetData], Dict]]
) -> str:
    """Render a table of assets.
    
    Args:
        assets: List of (id, name, type, data, config) tuples
        
    Returns:
        Formatted table string with colors
    """
    pass

def render_asset_row(
    asset_id: str,
    asset_name: str,
    asset_type: str,
    asset_data: Optional[AssetData],
    config: Dict = None
) -> Tuple[str, str]:
    """Render a single asset row.
    
    Args:
        asset_id: Asset identifier
        asset_name: Display name
        asset_type: Asset type (stock/futures)
        asset_data: Asset market data or None
        config: Asset configuration
        
    Returns:
        Tuple of (colored_row, severity)
    """
    pass

def render_info_message(message: str) -> None:
    """Print an info message with formatting.
    
    Args:
        message: Message text
    """
    pass

def render_error_message(message: str) -> None:
    """Print an error message with formatting.
    
    Args:
        message: Error text
    """
    pass
```

---

## Logging

### Logger Setup

```python
from market_monitor.logging_setup import setup_logging, get_logger, LogContext

def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    console: bool = True
) -> None:
    """Set up logging system.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path for logging
        console: Whether to log to console
    """
    pass

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger
        
    Examples:
        >>> logger = get_logger("market_monitor.sources.stocks")
        >>> logger.info("Fetching stocks...")
        >>> logger.error("Failed to fetch: %s", error)
    """
    pass
```

### Log Context Manager

```python
from market_monitor.logging_setup import LogContext

class LogContext:
    """Context manager for block-level logging.
    
    Usage:
        with LogContext(logger, "operation_name", level="DEBUG"):
            # Code here is logged
            do_something()
    """
    
    def __init__(
        self,
        logger: logging.Logger,
        operation: str,
        level: str = "INFO"
    ):
        """Initialize log context.
        
        Args:
            logger: Logger instance
            operation: Operation name
            level: Log level
        """
        pass
```

---

## Resilience Patterns

### Retry Configuration

```python
from market_monitor.resilience import RetryConfig, retry_with_backoff

class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_backoff: float = 1.0,
        max_backoff: float = 60.0,
        exponential_base: float = 2.0
    ):
        """Initialize retry configuration.
        
        Args:
            max_attempts: Maximum attempts
            initial_backoff: Initial backoff in seconds
            max_backoff: Maximum backoff in seconds
            exponential_base: Exponential backoff base
        """
        pass

    def get_backoff(self, attempt: int) -> float:
        """Calculate backoff for attempt number.
        
        Args:
            attempt: Attempt number (0-indexed)
            
        Returns:
            Backoff time in seconds
            
        Examples:
            >>> config = RetryConfig(initial_backoff=1, exponential_base=2)
            >>> config.get_backoff(0)  # 1 second
            1.0
            >>> config.get_backoff(1)  # 2 seconds
            2.0
            >>> config.get_backoff(2)  # 4 seconds
            4.0
        """
        pass
```

### Retry Function

```python
def retry_with_backoff(
    func: Callable,
    *args,
    config: RetryConfig = None,
    is_retryable: Optional[Callable[[Exception], bool]] = None,
    **kwargs
) -> Any:
    """Retry a function with exponential backoff.
    
    Args:
        func: Function to retry
        *args: Positional arguments
        config: RetryConfig instance
        is_retryable: Optional predicate for retryable exceptions
        **kwargs: Keyword arguments
        
    Returns:
        Function result
        
    Raises:
        Last exception if all retries exhausted
        
    Examples:
        >>> def fetch_data():
        ...     return api_call()
        >>> 
        >>> retry_with_backoff(
        ...     fetch_data,
        ...     config=RetryConfig(max_attempts=3, initial_backoff=1)
        ... )
    """
    pass
```

---

## Data Source Implementations

### StockSource

```python
from market_monitor.sources.stocks import StockSource

class StockSource(DataSource):
    """TWSE stock data source."""
    
    def __init__(self, interval: int = 5):
        """Initialize stock source.
        
        Args:
            interval: Polling interval in seconds
        """
        pass

    def fetch(self, asset_ids: List[str]) -> Dict[str, Optional[AssetData]]:
        """Fetch stock data from TWSE API."""
        pass
```

### FuturesSource

```python
from market_monitor.sources.futures import FuturesSource

class FuturesSource(DataSource):
    """Taifex futures data source."""
    
    def __init__(self, interval: int = 30):
        """Initialize futures source.
        
        Args:
            interval: Polling interval in seconds
        """
        pass

    def fetch(self, asset_ids: List[str]) -> Dict[str, Optional[AssetData]]:
        """Fetch futures data from Taifex API."""
        pass

    def build_ssf_map(self) -> bool:
        """Build SSF contract mapping."""
        pass
```

---

## Version Information

- **Framework Version**: 1.0.0
- **Python Version**: 3.8+
- **Last Updated**: 2026-04-12

---

## See Also

- [Architecture Guide](ARCHITECTURE.md)
- [Configuration Guide](CONFIG_GUIDE.md)
- [Plugin Development Guide](PLUGIN_DEVELOPMENT.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)

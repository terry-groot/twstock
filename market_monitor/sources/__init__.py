"""Data source plugins for market monitoring."""

import importlib
import inspect
from pathlib import Path
from typing import Dict, Type
from market_monitor.core import DataSource


def discover_sources() -> Dict[str, Type[DataSource]]:
    """Discover all available data sources.

    Returns:
        Dictionary mapping source names to DataSource classes
    """
    sources = {}
    sources_dir = Path(__file__).parent

    # Import each source module
    for module_file in sources_dir.glob("*.py"):
        if module_file.name.startswith("_"):
            continue

        module_name = module_file.stem
        try:
            module = importlib.import_module(f".{module_name}", package="market_monitor.sources")

            # Find DataSource subclasses in module
            for name, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, DataSource)
                    and obj is not DataSource
                    and not name.startswith("_")
                ):
                    sources[name] = obj
        except Exception:
            # Skip modules that fail to import
            pass

    return sources


def get_source(source_name: str) -> Type[DataSource]:
    """Get a specific source by name.

    Args:
        source_name: Name of the source class

    Returns:
        DataSource subclass

    Raises:
        ValueError: If source not found
    """
    sources = discover_sources()
    if source_name not in sources:
        raise ValueError(f"Unknown data source: {source_name}")
    return sources[source_name]


__all__ = ["discover_sources", "get_source"]

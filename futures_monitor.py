#!/usr/bin/env python3
"""DEPRECATED: Legacy futures monitor.

This script is deprecated. Please use:
    python monitor.py --config monitor_config.json

This wrapper is provided for backward compatibility only.
"""

import sys
import warnings
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Show deprecation warning
warnings.warn(
    "futures_monitor.py is deprecated. Please use 'python monitor.py' instead.",
    DeprecationWarning,
    stacklevel=2
)

print("⚠️  警告: futures_monitor.py 已棄用，請使用 'python monitor.py' 代替。", file=sys.stderr)

from market_monitor.config import load_config, create_default_config, migrate_legacy_config
from market_monitor.logging_setup import setup_logging
from market_monitor.monitor import MarketMonitor
from market_monitor.sources.futures import FuturesSource


def main():
    """Run legacy futures monitor using new framework."""
    import os

    # Try migration first
    old_stocks_path = "config.json"
    old_futures_path = "futures_config.json"
    new_config_path = "monitor_config.json"

    if (os.path.exists(old_stocks_path) or os.path.exists(old_futures_path)) and not os.path.exists(new_config_path):
        print("Migrating legacy configuration...")
        migrate_legacy_config(
            old_stocks_path=old_stocks_path,
            old_futures_path=old_futures_path,
            new_path=new_config_path
        )

    # Load config
    try:
        if os.path.exists(new_config_path):
            config = load_config(new_config_path)
        else:
            config = create_default_config(new_config_path)
    except Exception as e:
        print(f"Failed to load config: {e}", file=sys.stderr)
        sys.exit(1)

    # Set up logging
    setup_logging(level="INFO")

    # Create monitor and run
    try:
        monitor = MarketMonitor(config)
        futures_source = FuturesSource(interval=config.monitor.futures_interval)
        monitor.register_source_instance(futures_source)
        monitor.run()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

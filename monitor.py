#!/usr/bin/env python3
"""Taiwan stock and futures real-time monitor.

Usage:
    python monitor.py [--config CONFIG_FILE] [--verbose] [--log-file LOG_FILE]
"""

import sys
import argparse
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from market_monitor.config import load_config, create_default_config, migrate_legacy_config
from market_monitor.logging_setup import setup_logging
from market_monitor.monitor import MarketMonitor
from market_monitor.sources.stocks import StockSource
from market_monitor.sources.futures import FuturesSource


def parse_arguments():
    """Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Taiwan stock and futures real-time monitor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Use default config file
  %(prog)s --config my_config.json  # Use custom config file
  %(prog)s --verbose                # Enable debug logging
  %(prog)s --log-file monitor.log   # Save logs to file
        """
    )

    parser.add_argument(
        "--config",
        default="monitor_config.json",
        help="Path to configuration file (default: monitor_config.json)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose (DEBUG level) logging"
    )

    parser.add_argument(
        "--log-file",
        help="Path to log file (optional)"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )

    return parser.parse_args()


def load_or_create_config(config_path: str):
    """Load configuration or create default if missing.

    Args:
        config_path: Path to configuration file

    Returns:
        Loaded Config object

    Raises:
        SystemExit if configuration is invalid
    """
    # Try migration first
    old_stocks = "config.json"
    old_futures = "futures_config.json"

    if os.path.exists(old_stocks) or os.path.exists(old_futures):
        print("Found legacy configuration files, migrating...")
        migrate_legacy_config(old_stocks, old_futures, config_path)
        return load_config(config_path)

    # Try to load existing config
    if os.path.exists(config_path):
        try:
            return load_config(config_path)
        except Exception as e:
            print(f"Error loading config: {e}", file=sys.stderr)
            sys.exit(1)

    # Create default config
    print(f"Configuration file not found, creating default: {config_path}")
    try:
        return create_default_config(config_path)
    except Exception as e:
        print(f"Error creating default config: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point."""
    args = parse_arguments()

    # Set up logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(level=log_level, log_file=args.log_file)

    # Load configuration
    try:
        config = load_or_create_config(args.config)
    except Exception as e:
        print(f"Failed to load configuration: {e}", file=sys.stderr)
        sys.exit(1)

    # Create monitor
    try:
        monitor = MarketMonitor(config)

        # Register data sources
        stock_source = StockSource(interval=config.monitor.stock_interval)
        futures_source = FuturesSource(interval=config.monitor.futures_interval)

        monitor.register_source_instance(stock_source)
        monitor.register_source_instance(futures_source)

        # Run monitor
        monitor.run()

    except Exception as e:
        print(f"Monitor error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

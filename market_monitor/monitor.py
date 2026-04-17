"""Main monitoring loop and orchestration."""

import time
import signal
from typing import Dict, Optional, List
from dataclasses import asdict
from market_monitor.core import Monitor as BaseMonitor, DataSource, AssetData
from market_monitor.config import Config
from market_monitor.logging_setup import get_logger
from market_monitor.ui import render_table, render_info_message, render_error_message
from market_monitor.audio import beep_alert, should_beep
from market_monitor.resilience import CircuitBreaker, retry_with_backoff, RetryConfig

logger = get_logger("monitor")


class MarketMonitor(BaseMonitor):
    """Main market monitoring orchestrator."""

    def __init__(self, config: Config):
        """Initialize market monitor.

        Args:
            config: Configuration object
        """
        super().__init__(config=config.to_dict())
        self.config = config
        self.running = True
        self.last_render_time = 0
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_config = RetryConfig(
            max_attempts=config.monitor.retry_max_attempts,
            initial_backoff=config.monitor.retry_backoff_seconds,
        )

        # Set up signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signal (Ctrl+C).

        Args:
            signum: Signal number
            frame: Signal frame
        """
        logger.info("Shutdown requested")
        self.running = False

    def register_source_instance(self, source: DataSource) -> None:
        """Register a data source instance.

        Args:
            source: DataSource instance
        """
        self.register_source(source)
        # Create circuit breaker for this source
        self.circuit_breakers[source.name] = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=30
        )

    def fetch_all_sources(self) -> Dict[str, Dict[str, Optional[AssetData]]]:
        """Fetch data from all registered sources.

        Returns:
            Dictionary mapping source name to fetch results
        """
        all_data = {}

        for source_name, source in self.data_sources.items():
            # Check circuit breaker
            cb = self.circuit_breakers.get(source_name)
            if cb and not cb.can_attempt():
                logger.warning(f"Circuit breaker open for {source_name}")
                all_data[source_name] = {}
                continue

            try:
                # Get relevant asset IDs for this source
                asset_ids = [
                    aid for aid, (type_, cfg) in self.config.get_all_assets().items()
                    if type_ == ("stock" if source_name == "stocks" else "futures")
                ]

                if not asset_ids:
                    all_data[source_name] = {}
                    continue

                # Fetch with retry
                result = retry_with_backoff(
                    source.fetch,
                    asset_ids,
                    config=self.retry_config,
                )

                # Record success
                if cb:
                    cb.record_success()
                all_data[source_name] = result

            except Exception as e:
                logger.error(f"Failed to fetch from {source_name}: {e}")
                if cb:
                    cb.record_failure()
                all_data[source_name] = {}

        # Merge all data
        self.asset_data = {}
        for source_data in all_data.values():
            self.asset_data.update(source_data)

        return all_data

    def should_render(self) -> bool:
        """Determine if table should be rendered.

        Returns:
            True if enough time has passed since last render
        """
        current_time = time.time()
        # Always render on first call or after significant time
        return (self.last_render_time == 0 or
                current_time - self.last_render_time > 0.5)

    def render_display(self) -> bool:
        """Render the display and return if critical alert exists.

        Returns:
            True if critical alert exists
        """
        if not self.should_render():
            return False

        try:
            # Get all assets with config
            assets = {}
            for asset_id, (asset_type, config) in self.config.get_all_assets().items():
                # Convert AssetConfig to dict for render functions
                assets[asset_id] = (asset_type, asdict(config))

            # Render table
            table, has_critical = render_table(assets, self.asset_data)
            print(table)

            # Beep if critical alert and enabled
            if has_critical and self.config.monitor.beep_enabled:
                beep_alert()

            self.last_render_time = time.time()
            return has_critical

        except Exception as e:
            logger.error(f"Render error: {e}")
            render_error_message(f"顯示錯誤: {e}")
            return False

    def run(self) -> None:
        """Run the monitoring loop."""
        logger.info("Market monitor started")
        render_info_message("載入設定完成，開始監控...")
        time.sleep(1)

        try:
            iteration = 0
            while self.running:
                iteration += 1
                try:
                    # Fetch from all sources
                    self.fetch_all_sources()

                    # Render display
                    self.render_display()

                    # Sleep based on fastest interval
                    min_interval = min(
                        self.config.monitor.stock_interval,
                        self.config.monitor.futures_interval
                    )
                    time.sleep(min_interval)

                except KeyboardInterrupt:
                    logger.info("Keyboard interrupt")
                    break
                except Exception as e:
                    logger.error(f"Monitor loop error: {e}")
                    render_error_message(f"監控錯誤: {e}")
                    time.sleep(5)  # Wait before retry

        finally:
            logger.info("Market monitor stopped")
            print("\n監控已停止。")

    def get_status(self) -> Dict:
        """Get monitor status for external queries.

        Returns:
            Status dictionary
        """
        return {
            "running": self.running,
            "assets_monitored": len(self.asset_data),
            "sources": list(self.data_sources.keys()),
            "circuit_breakers": {
                name: cb.get_state()
                for name, cb in self.circuit_breakers.items()
            },
        }

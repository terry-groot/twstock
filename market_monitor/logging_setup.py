"""Structured logging setup for market monitor."""

import logging
import logging.handlers
from typing import Optional
from pathlib import Path


# Log level mapping
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    console_output: bool = True
) -> logging.Logger:
    """Set up structured logging for market monitor.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        console_output: Whether to output to console

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("market_monitor")
    logger.setLevel(logging.DEBUG)  # Set root to DEBUG, handlers filter
    logger.handlers = []  # Clear any existing handlers

    # Log level
    log_level = LOG_LEVELS.get(level.upper(), logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)-8s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Use rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)  # File gets everything
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get logger for a module.

    Args:
        name: Module name

    Returns:
        Configured logger instance
    """
    return logging.getLogger(f"market_monitor.{name}")


class LogContext:
    """Context manager for logging blocks of code."""

    def __init__(self, logger: logging.Logger, message: str, level: int = logging.DEBUG):
        """Initialize log context.

        Args:
            logger: Logger instance
            message: Message to log
            level: Logging level
        """
        self.logger = logger
        self.message = message
        self.level = level

    def __enter__(self):
        """Enter context."""
        self.logger.log(self.level, f"[START] {self.message}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        if exc_type is None:
            self.logger.log(self.level, f"[END] {self.message}")
        else:
            self.logger.log(self.level, f"[ERROR] {self.message}: {exc_val}")
        return False

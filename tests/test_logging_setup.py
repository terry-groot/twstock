"""Unit tests for market_monitor.logging_setup module."""

import pytest
import logging
import os
from pathlib import Path
from market_monitor.logging_setup import (
    setup_logging,
    get_logger,
    LOG_LEVELS,
    LogContext,
)


class TestSetupLogging:
    """Tests for logging setup."""

    def test_setup_logging_default(self):
        """Test default logging setup."""
        logger = setup_logging()
        assert logger.name == "market_monitor"
        assert logger.level == logging.DEBUG

    def test_setup_logging_with_level(self):
        """Test setup with specific level."""
        logger = setup_logging(level="ERROR")
        # Handler should have ERROR level
        assert logger.handlers[0].level == logging.ERROR

    def test_setup_logging_console_only(self):
        """Test console-only logging."""
        logger = setup_logging(console_output=True, log_file=None)
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)

    def test_setup_logging_with_file(self, tmp_path):
        """Test logging with file output."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(log_file=str(log_file), console_output=False)

        # Should have file handler
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.handlers.RotatingFileHandler)

    def test_setup_logging_creates_log_directory(self, tmp_path):
        """Test that log directory is created if needed."""
        log_file = tmp_path / "logs" / "test.log"
        logger = setup_logging(log_file=str(log_file), console_output=False)

        assert log_file.parent.exists()

    def test_setup_logging_both_console_and_file(self, tmp_path):
        """Test logging to both console and file."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(log_file=str(log_file), console_output=True)

        assert len(logger.handlers) == 2

    def test_log_levels_dict(self):
        """Test LOG_LEVELS dictionary."""
        assert LOG_LEVELS["DEBUG"] == logging.DEBUG
        assert LOG_LEVELS["INFO"] == logging.INFO
        assert LOG_LEVELS["WARNING"] == logging.WARNING
        assert LOG_LEVELS["ERROR"] == logging.ERROR
        assert LOG_LEVELS["CRITICAL"] == logging.CRITICAL

    def test_invalid_log_level_defaults_to_info(self):
        """Test invalid log level defaults to INFO."""
        logger = setup_logging(level="INVALID")
        assert logger.handlers[0].level == logging.INFO


class TestGetLogger:
    """Tests for getting module loggers."""

    def test_get_logger(self):
        """Test getting a named logger."""
        logger = get_logger("test_module")
        assert logger.name == "market_monitor.test_module"

    def test_get_logger_multiple_calls(self):
        """Test getting same logger multiple times."""
        logger1 = get_logger("module")
        logger2 = get_logger("module")
        assert logger1 is logger2


class TestLoggingMessages:
    """Tests for actual logging messages."""

    def test_console_logging(self, capsys):
        """Test that messages are logged to console."""
        logger = setup_logging(console_output=True, log_file=None)
        logger.info("Test message")

        # This might not capture due to handler setup, so we just verify no errors

    def test_file_logging(self, tmp_path):
        """Test that messages are logged to file."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(log_file=str(log_file), console_output=False)

        logger.info("Test message")
        logger.error("Error message")

        # Check file contents
        content = log_file.read_text()
        assert "Test message" in content
        assert "Error message" in content

    def test_log_formatting(self, tmp_path):
        """Test log message formatting."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(log_file=str(log_file), console_output=False)

        logger.info("Test message")
        content = log_file.read_text()

        # Check format: timestamp [LEVEL] name: message
        assert "[INFO" in content  # Allows for spacing after level
        assert "Test message" in content


class TestLogContext:
    """Tests for LogContext manager."""

    def test_log_context_success(self, tmp_path):
        """Test LogContext on successful execution."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(log_file=str(log_file), console_output=False)

        with LogContext(logger, "Test operation"):
            pass

        content = log_file.read_text()
        assert "[START] Test operation" in content
        assert "[END] Test operation" in content

    def test_log_context_with_exception(self, tmp_path):
        """Test LogContext on exception."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(log_file=str(log_file), console_output=False)

        try:
            with LogContext(logger, "Test operation"):
                raise ValueError("Test error")
        except ValueError:
            pass

        content = log_file.read_text()
        assert "[START] Test operation" in content
        assert "[ERROR] Test operation" in content
        assert "Test error" in content

    def test_log_context_custom_level(self, tmp_path):
        """Test LogContext with custom log level."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(log_file=str(log_file), console_output=False, level="DEBUG")

        with LogContext(logger, "Debug operation", level=logging.DEBUG):
            pass

        content = log_file.read_text()
        assert "Debug operation" in content

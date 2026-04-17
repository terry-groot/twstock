"""Unit tests for market_monitor.config module."""

import pytest
import json
import os
from pathlib import Path
from market_monitor.config import (
    AssetConfig,
    MonitorConfig,
    Config,
    load_config,
    save_config,
    create_default_config,
    migrate_legacy_config,
)


@pytest.fixture
def temp_config_file(tmp_path):
    """Create temporary config file."""
    return tmp_path / "test_config.json"


@pytest.fixture
def sample_config_data():
    """Sample configuration data."""
    return {
        "stocks": [
            {"id": "2330", "name": "台積電", "upper": 1000, "lower": 900, "enabled": True}
        ],
        "futures": [
            {"id": "TX", "name": "台指期", "upper": 34000, "lower": 32000, "enabled": True}
        ],
        "monitor": {
            "stock_interval": 5,
            "futures_interval": 30,
            "retry_max_attempts": 3,
            "retry_backoff_seconds": 2
        }
    }


class TestAssetConfig:
    """Tests for AssetConfig dataclass."""

    def test_create_asset_config(self):
        """Test creating asset configuration."""
        asset = AssetConfig(id="2330", name="台積電", upper=1000, lower=900)
        assert asset.id == "2330"
        assert asset.name == "台積電"
        assert asset.upper == 1000
        assert asset.enabled is True

    def test_asset_config_defaults(self):
        """Test default values."""
        asset = AssetConfig(id="2330", name="台積電")
        assert asset.upper is None
        assert asset.lower is None
        assert asset.enabled is True


class TestMonitorConfig:
    """Tests for MonitorConfig dataclass."""

    def test_monitor_config_defaults(self):
        """Test default monitor settings."""
        monitor = MonitorConfig()
        assert monitor.stock_interval == 5
        assert monitor.futures_interval == 30
        assert monitor.retry_max_attempts == 3


class TestConfigValidation:
    """Tests for Config validation."""

    def test_valid_config(self, sample_config_data):
        """Test valid configuration."""
        config = Config.from_dict(sample_config_data)
        errors = config.validate()
        assert errors == []

    def test_missing_asset_id(self):
        """Test validation catches missing asset ID."""
        config = Config(
            stocks=[AssetConfig(id="", name="Test")],
            futures=[]
        )
        errors = config.validate()
        assert any("must have 'id'" in e for e in errors)

    def test_invalid_threshold_order(self):
        """Test validation catches invalid threshold order."""
        config = Config(
            stocks=[AssetConfig(id="TEST", name="Test", upper=900, lower=1000)],
            futures=[]
        )
        errors = config.validate()
        assert any("upper threshold cannot be less than lower" in e for e in errors)

    def test_invalid_monitor_interval(self):
        """Test validation catches invalid intervals."""
        config = Config(
            stocks=[],
            futures=[],
            monitor=MonitorConfig(stock_interval=0)
        )
        errors = config.validate()
        assert any("stock_interval must be at least 1" in e for e in errors)


class TestConfigSerialization:
    """Tests for Config serialization/deserialization."""

    def test_to_dict(self, sample_config_data):
        """Test converting config to dictionary."""
        config = Config.from_dict(sample_config_data)
        result = config.to_dict()
        assert "stocks" in result
        assert "futures" in result
        assert "monitor" in result
        assert len(result["stocks"]) == 1

    def test_from_dict(self, sample_config_data):
        """Test creating config from dictionary."""
        config = Config.from_dict(sample_config_data)
        assert len(config.stocks) == 1
        assert config.stocks[0].id == "2330"
        assert len(config.futures) == 1

    def test_roundtrip_serialization(self, sample_config_data):
        """Test config serialization roundtrip."""
        config1 = Config.from_dict(sample_config_data)
        dict_form = config1.to_dict()
        config2 = Config.from_dict(dict_form)
        assert config1.to_dict() == config2.to_dict()


class TestLoadSaveConfig:
    """Tests for loading/saving config files."""

    def test_save_and_load_config(self, temp_config_file, sample_config_data):
        """Test saving and loading config."""
        config = Config.from_dict(sample_config_data)
        save_config(config, str(temp_config_file))

        loaded = load_config(str(temp_config_file))
        assert len(loaded.stocks) == 1
        assert loaded.stocks[0].id == "2330"

    def test_load_nonexistent_config(self):
        """Test loading nonexistent config."""
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/path.json")

    def test_load_invalid_config(self, tmp_path):
        """Test loading invalid config raises error."""
        config_file = tmp_path / "invalid.json"
        config_file.write_text(json.dumps({
            "stocks": [{"id": "2330"}],  # Missing name
            "futures": [],
            "monitor": {}
        }))

        # Should succeed in loading but AssetConfig might require name
        # or this is just JSON, so let's test with invalid data
        config_file.write_text(json.dumps({
            "stocks": [{"name": "台積電"}],  # Missing id
            "futures": [],
            "monitor": {}
        }))
        with pytest.raises(TypeError):
            load_config(str(config_file))

    def test_invalid_config_validation(self, tmp_path):
        """Test that invalid config is caught during validation."""
        config_file = tmp_path / "invalid.json"
        config_file.write_text(json.dumps({
            "stocks": [{"id": "2330", "name": "台積電", "upper": 900, "lower": 1000}],
            "futures": [],
            "monitor": {}
        }))

        with pytest.raises(ValueError):
            load_config(str(config_file))


class TestGetAllAssets:
    """Tests for getting all assets."""

    def test_get_all_assets(self, sample_config_data):
        """Test getting all assets."""
        config = Config.from_dict(sample_config_data)
        assets = config.get_all_assets()
        assert "2330" in assets  # Stock 2330
        assert "TX" in assets   # Futures TX

    def test_disabled_assets_excluded(self):
        """Test disabled assets are excluded."""
        config = Config(
            stocks=[AssetConfig(id="2330", name="台積電", enabled=False)],
            futures=[AssetConfig(id="TX", name="台指期", enabled=True)]
        )
        assets = config.get_all_assets()
        assert "2330" not in assets
        assert "TX" in assets


class TestCreateDefaultConfig:
    """Tests for creating default config."""

    def test_create_default_config(self, tmp_path):
        """Test creating default configuration."""
        config_file = tmp_path / "default.json"
        config = create_default_config(str(config_file))

        assert len(config.stocks) > 0
        assert len(config.futures) > 0
        assert config_file.exists()

        # Verify it can be loaded
        loaded = load_config(str(config_file))
        assert len(loaded.stocks) == len(config.stocks)


class TestMigrateLegacyConfig:
    """Tests for legacy config migration."""

    def test_migrate_legacy_stocks_config(self, tmp_path):
        """Test migrating legacy stocks config."""
        old_stocks = tmp_path / "config.json"
        old_stocks.write_text(json.dumps({
            "stocks": [{"id": "2330", "name": "台積電", "upper": 1000, "lower": 900, "enabled": True}]
        }))

        new_config_path = tmp_path / "monitor_config.json"
        config = migrate_legacy_config(
            old_stocks_path=str(old_stocks),
            old_futures_path=str(tmp_path / "nonexistent.json"),
            new_path=str(new_config_path)
        )

        assert config is not None
        assert len(config.stocks) == 1
        assert new_config_path.exists()

    def test_migrate_legacy_futures_config(self, tmp_path):
        """Test migrating legacy futures config."""
        old_futures = tmp_path / "futures_config.json"
        old_futures.write_text(json.dumps({
            "contracts": [{"id": "TX", "name": "台指期", "upper": 34000, "lower": 32000, "enabled": True}]
        }))

        new_config_path = tmp_path / "monitor_config.json"
        config = migrate_legacy_config(
            old_stocks_path=str(tmp_path / "nonexistent.json"),
            old_futures_path=str(old_futures),
            new_path=str(new_config_path)
        )

        assert config is not None
        assert len(config.futures) == 1

    def test_no_legacy_config_returns_none(self, tmp_path):
        """Test no migration when no legacy config exists."""
        result = migrate_legacy_config(
            old_stocks_path=str(tmp_path / "nonexistent.json"),
            old_futures_path=str(tmp_path / "nonexistent2.json"),
            new_path=str(tmp_path / "monitor_config.json")
        )
        assert result is None

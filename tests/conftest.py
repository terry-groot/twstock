"""Pytest configuration and fixtures."""

import pytest
import json
from pathlib import Path


@pytest.fixture
def twse_mock_response():
    """Mock TWSE API response."""
    return {
        "success": True,
        "rtcode": "0000",
        "rtmessage": "OK",
        "2330": {
            "success": True,
            "info": {
                "time": "13:30:00",
                "sessionStr": "上市"
            },
            "realtime": {
                "latest_trade_price": "850.00",
                "open": "845.00",
                "high": "855.00",
                "low": "840.00",
                "accumulate_trade_volume": "15000000",
                "bid": "849.50",
                "ask": "850.50"
            }
        }
    }


@pytest.fixture
def taifex_mock_response():
    """Mock Taifex API response."""
    return [
        {
            "ContractMonth(Week)": "202606",
            "Contract": "TX",
            "TradingSession": "一般",
            "Last": "34500.00",
            "Open": "34450.00",
            "High": "34600.00",
            "Low": "34400.00",
            "Volume": "150000",
            "BestBid": "34499.00",
            "BestAsk": "34501.00",
            "Change": "+50.00"
        }
    ]


@pytest.fixture
def ssf_map_mock_response():
    """Mock SSF mapping response."""
    return [
        {"StockCode": "2330", "Contract": "CDF"}
    ]


@pytest.fixture
def fixtures_dir():
    """Path to fixtures directory."""
    return Path(__file__).parent / "fixtures"

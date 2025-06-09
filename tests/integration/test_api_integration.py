"""
Integration tests for API + Engine integration
"""

import pytest
import requests
import json
from time import sleep


# Note: These tests require the API server to be running
# Run with: make api

API_BASE_URL = "http://localhost:8000"

@pytest.mark.integration
class TestAPIIntegration:
    """Test API + Engine integration"""
    
    @pytest.fixture(autouse=True)
    def check_api_server(self):
        """Check if API server is running before tests"""
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code != 200:
                pytest.skip("API server not running. Start with 'make api'")
        except requests.exceptions.RequestException:
            pytest.skip("API server not running. Start with 'make api'")
    
    def test_root_endpoint(self):
        """Test the root API endpoint"""
        response = requests.get(f"{API_BASE_URL}/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "Custom Strategy Analysis" in data["message"]
    
    def test_ticker_validation(self):
        """Test ticker validation endpoint"""
        response = requests.get(f"{API_BASE_URL}/tickers/AAPL/validate")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["symbol"] == "AAPL"
        assert data["data"]["is_valid"] == True
    
    def test_custom_strategy_creation(self):
        """Test custom strategy creation endpoint"""
        strategy_payload = {
            "name": "Integration Test Strategy",
            "symbol": "AAPL",
            "description": "Test strategy for integration",
            "indicators": [
                {"name": "EMA_12", "type": "EMA", "period": 12},
                {"name": "EMA_26", "type": "EMA", "period": 26}
            ],
            "crossover_rules": [
                {
                    "name": "EMA_Cross",
                    "fast_indicator": "EMA_12",
                    "slow_indicator": "EMA_26", 
                    "direction": "above",
                    "signal_type": "buy"
                }
            ],
            "threshold_rules": [],
            "period": "3mo"  # Shorter period for testing
        }
        
        response = requests.post(
            f"{API_BASE_URL}/strategies/custom",
            json=strategy_payload,
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "analysis" in data["data"]
        assert "strategy" in data["data"]
    
    def test_strategy_backtest(self):
        """Test strategy backtesting endpoint"""
        backtest_payload = {
            "strategy": {
                "name": "Backtest Strategy",
                "description": "Test backtest",
                "indicators": [
                    {"name": "EMA_12", "type": "EMA", "period": 12},
                    {"name": "EMA_26", "type": "EMA", "period": 26}
                ],
                "crossover_rules": [
                    {
                        "name": "EMA_Cross",
                        "fast_indicator": "EMA_12",
                        "slow_indicator": "EMA_26",
                        "direction": "above", 
                        "signal_type": "buy"
                    }
                ],
                "threshold_rules": []
            },
            "ticker": {
                "symbol": "AAPL",
                "period": "3mo",
                "interval": "1d"
            },
            "params": {
                "initial_cash": 10000,
                "commission": 0.001
            }
        }
        
        response = requests.post(
            f"{API_BASE_URL}/backtest/custom/ticker",
            json=backtest_payload,
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "backtest_results" in data["data"]
        assert "vectorbt_trusted" in data["data"] 
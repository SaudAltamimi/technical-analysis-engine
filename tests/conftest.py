"""
Pytest configuration for Technical Analysis Engine tests
"""

import pytest
import sys
from pathlib import Path

# Add src to Python path for imports
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

@pytest.fixture
def sample_strategy_config():
    """Sample strategy configuration for testing"""
    return {
        "name": "Test EMA Strategy",
        "description": "Simple test strategy",
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
    }

@pytest.fixture
def sample_symbols():
    """Sample ticker symbols for testing"""
    return ["AAPL", "MSFT", "GOOGL", "TSLA"] 
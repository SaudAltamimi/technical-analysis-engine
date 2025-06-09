"""
Utility functions for the technical analysis framework
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Union

try:
    from .config import StrategyDefinition
except ImportError:
    from config import StrategyDefinition


class StrategySerializer:
    """Serialize/deserialize strategies to/from JSON"""
    
    @staticmethod
    def save_strategy(strategy: StrategyDefinition, filepath: Union[str, Path]) -> None:
        """Save strategy to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(strategy.dict(), f, indent=2)
    
    @staticmethod
    def load_strategy(filepath: Union[str, Path]) -> StrategyDefinition:
        """Load strategy from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return StrategyDefinition(**data)


def create_sample_data(
    start_date: str = "2020-01-01",
    end_date: str = "2023-01-01", 
    initial_price: float = 100.0,
    volatility: float = 0.02,
    seed: int = 42
) -> pd.Series:
    """Create sample price data for testing"""
    np.random.seed(seed)
    dates = pd.date_range(start_date, end_date, freq='D')
    returns = np.random.normal(0, volatility, len(dates))
    prices = initial_price * np.exp(np.cumsum(returns))
    return pd.Series(prices, index=dates, name='price') 
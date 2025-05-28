"""
Signal generation logic for trading strategies
"""

import pandas as pd

try:
    from .ta_types import CrossoverDirection, ThresholdCondition
except ImportError:
    from ta_types import CrossoverDirection, ThresholdCondition


class SignalGenerator:
    """Generates trading signals from indicator values"""
    
    @staticmethod
    def crossover_signal(
        fast_values: pd.Series,
        slow_values: pd.Series, 
        direction: CrossoverDirection
    ) -> pd.Series:
        """Generate crossover signals"""
        if direction == CrossoverDirection.ABOVE:
            return (fast_values > slow_values) & (fast_values.shift(1) <= slow_values.shift(1))
        else:
            return (fast_values < slow_values) & (fast_values.shift(1) >= slow_values.shift(1))
    
    @staticmethod
    def threshold_signal(
        values: pd.Series,
        threshold: float,
        condition: ThresholdCondition
    ) -> pd.Series:
        """Generate threshold signals"""
        if condition == ThresholdCondition.ABOVE:
            return values > threshold
        else:
            return values < threshold 
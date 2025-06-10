"""
Main strategy execution engine
"""

import pandas as pd
import vectorbt as vbt
from typing import Dict

try:
    from .config import StrategyDefinition
    from .ta_types import SignalType
    from .indicators import IndicatorProtocol, IndicatorFactory, CalculatedIndicator
    from .signals import SignalGenerator
except ImportError:
    from config import StrategyDefinition
    from ta_types import SignalType
    from indicators import IndicatorProtocol, IndicatorFactory, CalculatedIndicator
    from signals import SignalGenerator


class StrategyEngine:
    """Main strategy execution engine"""
    
    def __init__(self, definition: StrategyDefinition):
        self.definition = definition
        self._indicators: Dict[str, IndicatorProtocol] = {}
        self._setup_indicators()
    
    def _setup_indicators(self) -> None:
        """Initialize all indicators"""
        for ind_def in self.definition.indicators:
            indicator = IndicatorFactory.create_indicator(ind_def)
            self._indicators[ind_def.name] = indicator
    
    def calculate_indicators(self, price_data: pd.Series) -> Dict[str, CalculatedIndicator]:
        """Calculate all indicator values"""
        results = {}
        
        for ind_def in self.definition.indicators:
            indicator = self._indicators[ind_def.name]
            values = indicator.calculate(price_data)
            
            results[ind_def.name] = CalculatedIndicator(
                name=ind_def.name,
                values=values,
                params=ind_def.params.dict()
            )
        
        return results
    
    def generate_signals(self, indicators: Dict[str, CalculatedIndicator]) -> Dict[str, pd.Series]:
        """Generate all trading signals"""
        signals = {}
        
        # Process crossover rules
        for rule in self.definition.crossover_rules:
            fast_indicator = indicators[rule.fast_indicator]
            slow_indicator = indicators[rule.slow_indicator]
            
            signal = SignalGenerator.crossover_signal(
                fast_indicator.values,
                slow_indicator.values,
                rule.direction
            )
            signals[rule.name] = signal.fillna(False)
        
        # Process threshold rules
        for rule in self.definition.threshold_rules:
            indicator = indicators[rule.indicator]
            
            signal = SignalGenerator.threshold_signal(
                indicator.values,
                rule.threshold,
                rule.condition
            )
            signals[rule.name] = signal.fillna(False)
        
        return signals
    
    def get_entry_signals(self, signals: Dict[str, pd.Series]) -> pd.Series:
        """Combine entry signals"""
        entry_rules = [
            rule.name for rule in (self.definition.crossover_rules + self.definition.threshold_rules)
            if rule.signal_type == SignalType.ENTRY
        ]
        
        if not entry_rules:
            return pd.Series(False, index=list(signals.values())[0].index)
        
        # Use AND logic for entry signals (all conditions must be met)
        combined = signals[entry_rules[0]]
        for rule_name in entry_rules[1:]:
            combined = combined & signals[rule_name]
        
        return combined
    
    def get_exit_signals(self, signals: Dict[str, pd.Series]) -> pd.Series:
        """Combine exit signals"""
        exit_rules = [
            rule.name for rule in (self.definition.crossover_rules + self.definition.threshold_rules)
            if rule.signal_type == SignalType.EXIT
        ]
        
        if not exit_rules:
            return pd.Series(False, index=list(signals.values())[0].index)
        
        combined = signals[exit_rules[0]]
        for rule_name in exit_rules[1:]:
            combined = combined | signals[rule_name]
        
        return combined
    
    def backtest(self, price_data: pd.Series, **portfolio_kwargs) -> vbt.Portfolio:
        """Run complete backtest"""
        # Calculate indicators
        indicators = self.calculate_indicators(price_data)
        
        # Generate signals
        signals = self.generate_signals(indicators)
        
        # Get entry/exit signals
        entries = self.get_entry_signals(signals)
        exits = self.get_exit_signals(signals)
        
        # Run backtest
        return vbt.Portfolio.from_signals(
            price_data,
            entries,
            exits,
            **portfolio_kwargs
        ) 
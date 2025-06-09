"""
Unit tests for the modular framework components
"""

import pytest
import pandas as pd
import numpy as np

# Import from the new engine structure
from technical_analysis_engine import (
    IndicatorType, SignalType, CrossoverDirection, ThresholdCondition,
    EMAConfig, StrategyDefinition, IndicatorDefinition, CrossoverRule
)


class TestFrameworkComponents:
    """Test the framework components"""
    
    def test_indicator_types(self):
        """Test that indicator types are accessible"""
        assert IndicatorType.EMA == "EMA"
        assert IndicatorType.SMA == "SMA"
        assert IndicatorType.RSI == "RSI"
        assert IndicatorType.MACD == "MACD"
    
    def test_signal_types(self):
        """Test signal types"""
        assert SignalType.ENTRY == "entry"
        assert SignalType.EXIT == "exit"
    
    def test_crossover_direction(self):
        """Test crossover direction types"""
        assert CrossoverDirection.ABOVE == "above"
        assert CrossoverDirection.BELOW == "below"
    
    def test_threshold_condition(self):
        """Test threshold condition types"""
        assert ThresholdCondition.ABOVE == "above"
        assert ThresholdCondition.BELOW == "below"
    
    def test_ema_config(self):
        """Test EMA configuration"""
        ema_config = EMAConfig(window=20)
        assert ema_config.window == 20
        assert hasattr(ema_config, 'window')
    
    def test_indicator_definition(self):
        """Test indicator definition creation"""
        ema_config = EMAConfig(window=20)
        indicator_def = IndicatorDefinition(
            name="ema_test",
            type=IndicatorType.EMA,
            params=ema_config
        )
        
        assert indicator_def.name == "ema_test"
        assert indicator_def.type == IndicatorType.EMA
        assert indicator_def.params == ema_config
    
    def test_crossover_rule(self):
        """Test crossover rule creation"""
        rule = CrossoverRule(
            name="test_crossover",
            fast_indicator="EMA_12",
            slow_indicator="EMA_26",
            direction=CrossoverDirection.ABOVE,
            signal_type=SignalType.ENTRY
        )
        
        assert rule.name == "test_crossover"
        assert rule.fast_indicator == "EMA_12"
        assert rule.slow_indicator == "EMA_26"
        assert rule.direction == CrossoverDirection.ABOVE
        assert rule.signal_type == SignalType.ENTRY
    
    def test_strategy_definition(self):
        """Test strategy definition creation"""
        ema_config = EMAConfig(window=20)
        indicator_def = IndicatorDefinition(
            name="ema_test",
            type=IndicatorType.EMA,
            params=ema_config
        )
        
        strategy_def = StrategyDefinition(
            name="Test Strategy",
            description="A simple test strategy",
            indicators=[indicator_def],
            crossover_rules=[],
            threshold_rules=[]
        )
        
        assert strategy_def.name == "Test Strategy"
        assert strategy_def.description == "A simple test strategy"
        assert len(strategy_def.indicators) == 1
        assert strategy_def.indicators[0] == indicator_def
        assert len(strategy_def.crossover_rules) == 0
        assert len(strategy_def.threshold_rules) == 0


def test_basic_framework_functionality():
    """Test basic framework functionality (can be run standalone)"""
    print("🚀 Testing Modular Technical Analysis Framework")
    print("=" * 50)
    
    # Test configuration models
    ema_config = EMAConfig(window=20)
    print(f"✅ EMA config created: window={ema_config.window}")
    
    # Test indicator definition
    indicator_def = IndicatorDefinition(
        name="ema_test",
        type=IndicatorType.EMA,
        params=ema_config
    )
    print(f"✅ Indicator definition created: {indicator_def.name}")
    
    # Test strategy definition
    strategy_def = StrategyDefinition(
        name="Test Strategy",
        description="A simple test strategy",
        indicators=[indicator_def],
        crossover_rules=[],
        threshold_rules=[]
    )
    print(f"✅ Strategy definition created: {strategy_def.name}")
    
    # Test types
    print(f"✅ Types working:")
    print(f"   - IndicatorType.EMA: {IndicatorType.EMA}")
    print(f"   - SignalType.ENTRY: {SignalType.ENTRY}")
    print(f"   - CrossoverDirection.ABOVE: {CrossoverDirection.ABOVE}")
    
    print("\n🎉 All basic functionality tests passed!")
    print("The modular framework structure is working correctly.")


if __name__ == "__main__":
    test_basic_framework_functionality() 
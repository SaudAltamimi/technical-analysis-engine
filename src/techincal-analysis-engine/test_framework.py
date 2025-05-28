"""
Simple test of the modular framework without VectorBT
"""

import pandas as pd
import numpy as np

# Test the framework components
from ta_types import IndicatorType, SignalType, CrossoverDirection, ThresholdCondition
from config import EMAConfig, StrategyDefinition, IndicatorDefinition, CrossoverRule
from utils import create_sample_data

def test_basic_functionality():
    """Test basic functionality without VectorBT"""
    print("🚀 Testing Modular Technical Analysis Framework")
    print("=" * 50)
    
    # Test sample data creation
    price_data = create_sample_data()
    print(f"✅ Sample data created: {len(price_data)} days")
    
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
    test_basic_functionality() 
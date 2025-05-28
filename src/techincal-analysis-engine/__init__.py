"""
Modular Technical Analysis Strategy Framework
A clean, readable, and extensible framework for building trading strategies with VectorBT
"""

import warnings
warnings.filterwarnings('ignore')

# Core types and enums
from .ta_types import (
    IndicatorType,
    SignalType,
    CrossoverDirection,
    ThresholdCondition
)

# Configuration models
from .config import (
    IndicatorParams,
    EMAConfig,
    RSIConfig,
    MACDConfig,
    IndicatorDefinition,
    CrossoverRule,
    ThresholdRule,
    StrategyDefinition
)

# Indicators
from .indicators import (
    IndicatorProtocol,
    CalculatedIndicator,
    IndicatorFactory
)

# Signal generation
from .signals import SignalGenerator

# Strategy engine
from .strategy import StrategyEngine

# Strategy builders
from .builders import StrategyBuilder

# Utilities
from .utils import StrategySerializer, create_sample_data

__all__ = [
    # Types
    'IndicatorType',
    'SignalType', 
    'CrossoverDirection',
    'ThresholdCondition',
    
    # Configuration
    'IndicatorParams',
    'EMAConfig',
    'RSIConfig', 
    'MACDConfig',
    'IndicatorDefinition',
    'CrossoverRule',
    'ThresholdRule',
    'StrategyDefinition',
    
    # Indicators
    'IndicatorProtocol',
    'CalculatedIndicator',
    'IndicatorFactory',
    
    # Signals
    'SignalGenerator',
    
    # Strategy
    'StrategyEngine',
    
    # Builders
    'StrategyBuilder',
    
    # Utils
    'StrategySerializer',
    'create_sample_data'
]

__version__ = "1.0.0" 
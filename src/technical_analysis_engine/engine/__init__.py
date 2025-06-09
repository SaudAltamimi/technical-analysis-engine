"""
Technical Analysis Engine Core
=============================

Core engine components for technical analysis, strategy building, and backtesting.

This package contains:
- Strategy definitions and configurations
- Technical indicators and calculations  
- Signal generation logic
- Strategy building utilities
"""

# Core strategy components
from .strategy import StrategyEngine
from .config import (
    StrategyDefinition, IndicatorDefinition, CrossoverRule, ThresholdRule,
    EMAConfig, SMAConfig, RSIConfig, MACDConfig, IndicatorParams
)

# Indicators and signals
from .indicators import IndicatorFactory, IndicatorProtocol
from .signals import SignalGenerator

# Types and enums
from .ta_types import IndicatorType, SignalType, CrossoverDirection, ThresholdCondition

# Strategy building
from .builders import StrategyBuilder

# Core engine
from .core import TechnicalAnalysisEngine, EngineResult

__all__ = [
    # Strategy core
    'StrategyEngine',
    'StrategyDefinition',
    'IndicatorDefinition',
    
    # Rules
    'CrossoverRule',
    'ThresholdRule',
    
    # Indicator configs
    'EMAConfig',
    'SMAConfig', 
    'RSIConfig',
    'MACDConfig',
    'IndicatorParams',
    
    # Indicators and signals
    'IndicatorFactory',
    'IndicatorProtocol',
    'SignalGenerator',
    
    # Types
    'IndicatorType',
    'SignalType',
    'CrossoverDirection',
    'ThresholdCondition',
    
    # Builders
    'StrategyBuilder',
    
    # Core engine
    'TechnicalAnalysisEngine',
    'EngineResult'
] 
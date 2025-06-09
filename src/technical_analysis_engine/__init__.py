"""
Technical Analysis Engine
=========================

Self-contained technical analysis engine with VectorBT integration and data fetching capabilities.

Architecture:
- engine/: Core engine components (strategy engine, indicators, signals, configurations)
- data_service.py: Yahoo Finance data fetching
- ticker_config.py: Ticker configuration and management
- utils.py: Utility functions

Main Components:
- TechnicalAnalysisEngine: Complete analysis engine (from engine.core)
- StrategyEngine: Core strategy execution engine (from engine.strategy)  
- YahooFinanceService: Data fetching from Yahoo Finance
- IndicatorFactory: Technical indicator calculations (from engine.indicators)
- SignalGenerator: Trading signal generation (from engine.signals)

Example standalone usage:
    from technical_analysis_engine import TechnicalAnalysisEngine
    
    # Create engine
    engine = TechnicalAnalysisEngine()
    
    # Validate symbol
    is_valid = engine.validate_symbol("AAPL")
    
    # Run complete analysis
    result = engine.analyze_symbol(
        symbol="AAPL",
        strategy_config={
            "name": "EMA Crossover",
            "indicators": [
                {"name": "EMA_12", "type": "EMA", "period": 12},
                {"name": "EMA_26", "type": "EMA", "period": 26}
            ],
            "crossover_rules": [{
                "name": "EMA_Cross",
                "fast_indicator": "EMA_12",
                "slow_indicator": "EMA_26",
                "direction": "above",
                "signal_type": "buy"
            }]
        },
        period="1y"
    )
"""

# Import core engine components from engine subdirectory
from .engine import (
    # Core engine 
    TechnicalAnalysisEngine,
    EngineResult,
    
    # Strategy engine
    StrategyEngine,
    StrategyDefinition,
    IndicatorDefinition,
    
    # Rules
    CrossoverRule,
    ThresholdRule,
    
    # Indicator configurations
    EMAConfig,
    SMAConfig,
    RSIConfig,
    MACDConfig,
    IndicatorParams,
    
    # Indicators and signals
    IndicatorFactory,
    IndicatorProtocol,
    SignalGenerator,
    
    # Types and enums
    IndicatorType,
    SignalType,
    CrossoverDirection,
    ThresholdCondition,
    
    # Builders
    StrategyBuilder
)

# Import data services from main package
from .data_service import (
    YahooFinanceService,
    TickerRequest,
    DateRangeRequest,
    PeriodEnum,
    IntervalEnum,
    DataFetchResult
)

# Import configuration utilities
from .ticker_config import TickerConfig, get_ticker_config

# Version and metadata
__version__ = "1.0.0"
__author__ = "Technical Analysis Team"
__description__ = "Self-contained technical analysis engine with VectorBT integration"

# Export all main classes and functions
__all__ = [
    # Main engine (from engine.core)
    'TechnicalAnalysisEngine',
    'EngineResult',
    
    # Core strategy components (from engine.*)
    'StrategyEngine',
    'StrategyDefinition',
    'IndicatorDefinition',
    
    # Rules (from engine.config)
    'CrossoverRule',
    'ThresholdRule',
    
    # Indicator configurations (from engine.config)
    'EMAConfig',
    'SMAConfig',
    'RSIConfig',
    'MACDConfig',
    'IndicatorParams',
    
    # Indicators and signals (from engine.*)
    'IndicatorFactory',
    'IndicatorProtocol',
    'SignalGenerator',
    
    # Types and enums (from engine.ta_types)
    'IndicatorType',
    'SignalType',
    'CrossoverDirection',
    'ThresholdCondition',
    
    # Builders (from engine.builders)
    'StrategyBuilder',
    
    # Data services (from main package)
    'YahooFinanceService',
    'TickerRequest',
    'DateRangeRequest',
    'PeriodEnum',
    'IntervalEnum',
    'DataFetchResult',
    
    # Configuration utilities (from main package)
    'TickerConfig',
    'get_ticker_config'
] 
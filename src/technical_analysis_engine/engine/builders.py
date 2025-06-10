"""
Pre-built strategy patterns and builders for technical analysis strategies.

This module provides factory methods and builders to create common technical analysis
trading strategies. It includes:

- EMA Crossover strategies
- SMA Crossover strategies  
- RSI-based strategies 
- MACD strategies
- Momentum strategies
- Combined indicator strategies
- Custom strategy builders

The builders abstract away the complexity of manually defining strategy components
and provide a clean interface for creating standardized strategy definitions.
"""

try:
    from .config import (
        StrategyDefinition, IndicatorDefinition, CrossoverRule, ThresholdRule,
        EMAConfig, SMAConfig, RSIConfig, MACDConfig
    )
    from .ta_types import IndicatorType, CrossoverDirection, SignalType, ThresholdCondition
except ImportError:
    from config import (
        StrategyDefinition, IndicatorDefinition, CrossoverRule, ThresholdRule,
        EMAConfig, SMAConfig, RSIConfig, MACDConfig
    )
    from ta_types import IndicatorType, CrossoverDirection, SignalType, ThresholdCondition


class StrategyBuilder:
    """Builder for creating common strategy patterns"""
    
    @staticmethod
    def ema_crossover(
        name: str = "EMA Crossover",
        fast_period: int = 12,
        slow_period: int = 26
    ) -> StrategyDefinition:
        """Build EMA crossover strategy"""
        return StrategyDefinition(
            name=name,
            description=f"EMA crossover strategy ({fast_period}/{slow_period})",
            indicators=[
                IndicatorDefinition(
                    name="ema_fast",
                    type=IndicatorType.EMA,
                    params=EMAConfig(window=fast_period)
                ),
                IndicatorDefinition(
                    name="ema_slow", 
                    type=IndicatorType.EMA,
                    params=EMAConfig(window=slow_period)
                )
            ],
            crossover_rules=[
                CrossoverRule(
                    name="ema_entry",
                    fast_indicator="ema_fast",
                    slow_indicator="ema_slow",
                    direction=CrossoverDirection.ABOVE,
                    signal_type=SignalType.ENTRY
                ),
                CrossoverRule(
                    name="ema_exit",
                    fast_indicator="ema_fast", 
                    slow_indicator="ema_slow",
                    direction=CrossoverDirection.BELOW,
                    signal_type=SignalType.EXIT
                )
            ]
        )
    
    @staticmethod
    def sma_crossover(
        name: str = "SMA Crossover",
        fast_period: int = 20,
        slow_period: int = 50
    ) -> StrategyDefinition:
        """Build SMA crossover strategy (classic golden cross)"""
        return StrategyDefinition(
            name=name,
            description=f"SMA crossover strategy ({fast_period}/{slow_period}) - Golden Cross pattern",
            indicators=[
                IndicatorDefinition(
                    name="sma_fast",
                    type=IndicatorType.SMA,
                    params=SMAConfig(window=fast_period)
                ),
                IndicatorDefinition(
                    name="sma_slow", 
                    type=IndicatorType.SMA,
                    params=SMAConfig(window=slow_period)
                )
            ],
            crossover_rules=[
                CrossoverRule(
                    name="sma_entry",
                    fast_indicator="sma_fast",
                    slow_indicator="sma_slow",
                    direction=CrossoverDirection.ABOVE,
                    signal_type=SignalType.ENTRY
                ),
                CrossoverRule(
                    name="sma_exit",
                    fast_indicator="sma_fast", 
                    slow_indicator="sma_slow",
                    direction=CrossoverDirection.BELOW,
                    signal_type=SignalType.EXIT
                )
            ]
        )
    
    @staticmethod
    def rsi_mean_reversion(
        name: str = "RSI Mean Reversion",
        rsi_period: int = 14,
        oversold: float = 30,
        overbought: float = 70
    ) -> StrategyDefinition:
        """Build RSI mean reversion strategy"""
        return StrategyDefinition(
            name=name,
            description=f"RSI mean reversion strategy (period={rsi_period})",
            indicators=[
                IndicatorDefinition(
                    name="rsi",
                    type=IndicatorType.RSI,
                    params=RSIConfig(window=rsi_period)
                )
            ],
            threshold_rules=[
                ThresholdRule(
                    name="rsi_entry",
                    indicator="rsi",
                    threshold=oversold,
                    condition=ThresholdCondition.BELOW,
                    signal_type=SignalType.ENTRY
                ),
                ThresholdRule(
                    name="rsi_exit",
                    indicator="rsi", 
                    threshold=overbought,
                    condition=ThresholdCondition.ABOVE,
                    signal_type=SignalType.EXIT
                )
            ]
        )
    
    @staticmethod
    def macd_momentum(
        name: str = "MACD Momentum",
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> StrategyDefinition:
        """Build MACD momentum strategy"""
        return StrategyDefinition(
            name=name,
            description=f"MACD momentum strategy ({fast_period}/{slow_period}/{signal_period})",
            indicators=[
                IndicatorDefinition(
                    name="macd",
                    type=IndicatorType.MACD,
                    params=MACDConfig(fast=fast_period, slow=slow_period, signal=signal_period)
                )
            ],
            crossover_rules=[
                CrossoverRule(
                    name="macd_entry",
                    fast_indicator="macd",
                    slow_indicator="macd",  # MACD line vs signal line
                    direction=CrossoverDirection.ABOVE,
                    signal_type=SignalType.ENTRY
                ),
                CrossoverRule(
                    name="macd_exit",
                    fast_indicator="macd",
                    slow_indicator="macd",  # MACD line vs signal line
                    direction=CrossoverDirection.BELOW,
                    signal_type=SignalType.EXIT
                )
            ]
        )
    
    @staticmethod
    def rsi_momentum(
        name: str = "RSI Momentum",
        rsi_period: int = 14,
        momentum_threshold: float = 50
    ) -> StrategyDefinition:
        """Build RSI momentum strategy (trend following)"""
        return StrategyDefinition(
            name=name,
            description=f"RSI momentum strategy - trend following (period={rsi_period})",
            indicators=[
                IndicatorDefinition(
                    name="rsi",
                    type=IndicatorType.RSI,
                    params=RSIConfig(window=rsi_period)
                )
            ],
            threshold_rules=[
                ThresholdRule(
                    name="rsi_bullish_entry",
                    indicator="rsi",
                    threshold=momentum_threshold,
                    condition=ThresholdCondition.ABOVE,
                    signal_type=SignalType.ENTRY
                ),
                ThresholdRule(
                    name="rsi_bearish_exit",
                    indicator="rsi", 
                    threshold=momentum_threshold,
                    condition=ThresholdCondition.BELOW,
                    signal_type=SignalType.EXIT
                )
            ]
        )
    
    @staticmethod
    def dual_ema_rsi(
        name: str = "Dual EMA + RSI",
        fast_ema: int = 12,
        slow_ema: int = 26,
        rsi_period: int = 14,
        rsi_oversold: float = 30,
        rsi_overbought: float = 70
    ) -> StrategyDefinition:
        """Build combined EMA crossover + RSI confirmation strategy"""
        return StrategyDefinition(
            name=name,
            description=f"Combined EMA crossover ({fast_ema}/{slow_ema}) with RSI confirmation",
            indicators=[
                IndicatorDefinition(
                    name="ema_fast",
                    type=IndicatorType.EMA,
                    params=EMAConfig(window=fast_ema)
                ),
                IndicatorDefinition(
                    name="ema_slow", 
                    type=IndicatorType.EMA,
                    params=EMAConfig(window=slow_ema)
                ),
                IndicatorDefinition(
                    name="rsi",
                    type=IndicatorType.RSI,
                    params=RSIConfig(window=rsi_period)
                )
            ],
            crossover_rules=[
                CrossoverRule(
                    name="ema_bullish_cross",
                    fast_indicator="ema_fast",
                    slow_indicator="ema_slow",
                    direction=CrossoverDirection.ABOVE,
                    signal_type=SignalType.ENTRY
                ),
                CrossoverRule(
                    name="ema_bearish_cross",
                    fast_indicator="ema_fast", 
                    slow_indicator="ema_slow",
                    direction=CrossoverDirection.BELOW,
                    signal_type=SignalType.EXIT
                )
            ],
            threshold_rules=[
                ThresholdRule(
                    name="rsi_not_overbought",
                    indicator="rsi",
                    threshold=rsi_overbought,
                    condition=ThresholdCondition.BELOW,
                    signal_type=SignalType.ENTRY
                ),
                ThresholdRule(
                    name="rsi_oversold_exit",
                    indicator="rsi", 
                    threshold=rsi_oversold,
                    condition=ThresholdCondition.BELOW,
                    signal_type=SignalType.EXIT
                )
            ]
        )
    
    @staticmethod
    def macd_rsi_confluence(
        name: str = "MACD + RSI Confluence",
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
        rsi_period: int = 14,
        rsi_oversold: float = 30,
        rsi_overbought: float = 70
    ) -> StrategyDefinition:
        """Build MACD + RSI confluence strategy for high-probability entries"""
        return StrategyDefinition(
            name=name,
            description=f"MACD + RSI confluence strategy for high-probability signals",
            indicators=[
                IndicatorDefinition(
                    name="macd",
                    type=IndicatorType.MACD,
                    params=MACDConfig(fast=macd_fast, slow=macd_slow, signal=macd_signal)
                ),
                IndicatorDefinition(
                    name="rsi",
                    type=IndicatorType.RSI,
                    params=RSIConfig(window=rsi_period)
                )
            ],
            crossover_rules=[
                CrossoverRule(
                    name="macd_bullish_cross",
                    fast_indicator="macd",
                    slow_indicator="macd",
                    direction=CrossoverDirection.ABOVE,
                    signal_type=SignalType.ENTRY
                ),
                CrossoverRule(
                    name="macd_bearish_cross",
                    fast_indicator="macd",
                    slow_indicator="macd",
                    direction=CrossoverDirection.BELOW,
                    signal_type=SignalType.EXIT
                )
            ],
            threshold_rules=[
                ThresholdRule(
                    name="rsi_oversold_confirm",
                    indicator="rsi",
                    threshold=rsi_oversold,
                    condition=ThresholdCondition.BELOW,
                    signal_type=SignalType.ENTRY
                ),
                ThresholdRule(
                    name="rsi_overbought_exit",
                    indicator="rsi", 
                    threshold=rsi_overbought,
                    condition=ThresholdCondition.ABOVE,
                    signal_type=SignalType.EXIT
                )
            ]
        )
    
    @staticmethod
    def triple_ma_trend(
        name: str = "Triple MA Trend",
        short_period: int = 9,
        medium_period: int = 21,
        long_period: int = 50
    ) -> StrategyDefinition:
        """Build triple moving average trend following strategy"""
        return StrategyDefinition(
            name=name,
            description=f"Triple MA trend following strategy ({short_period}/{medium_period}/{long_period})",
            indicators=[
                IndicatorDefinition(
                    name="ema_short",
                    type=IndicatorType.EMA,
                    params=EMAConfig(window=short_period)
                ),
                IndicatorDefinition(
                    name="ema_medium", 
                    type=IndicatorType.EMA,
                    params=EMAConfig(window=medium_period)
                ),
                IndicatorDefinition(
                    name="ema_long", 
                    type=IndicatorType.EMA,
                    params=EMAConfig(window=long_period)
                )
            ],
            crossover_rules=[
                CrossoverRule(
                    name="short_above_medium",
                    fast_indicator="ema_short",
                    slow_indicator="ema_medium",
                    direction=CrossoverDirection.ABOVE,
                    signal_type=SignalType.ENTRY
                ),
                CrossoverRule(
                    name="medium_above_long",
                    fast_indicator="ema_medium",
                    slow_indicator="ema_long",
                    direction=CrossoverDirection.ABOVE,
                    signal_type=SignalType.ENTRY
                ),
                CrossoverRule(
                    name="short_below_medium",
                    fast_indicator="ema_short", 
                    slow_indicator="ema_medium",
                    direction=CrossoverDirection.BELOW,
                    signal_type=SignalType.EXIT
                )
            ]
        )


class StrategyPresets:
    """Pre-configured strategy presets for different market conditions"""
    
    @staticmethod
    def scalping_ema() -> StrategyDefinition:
        """Fast EMA crossover for scalping"""
        return StrategyBuilder.ema_crossover(
            name="Scalping EMA",
            fast_period=5,
            slow_period=13
        )
    
    @staticmethod
    def swing_trading_sma() -> StrategyDefinition:
        """SMA crossover optimized for swing trading"""
        return StrategyBuilder.sma_crossover(
            name="Swing Trading SMA",
            fast_period=20,
            slow_period=50
        )
    
    @staticmethod
    def conservative_rsi() -> StrategyDefinition:
        """Conservative RSI mean reversion with tighter bounds"""
        return StrategyBuilder.rsi_mean_reversion(
            name="Conservative RSI",
            rsi_period=21,
            oversold=25,
            overbought=75
        )
    
    @staticmethod
    def aggressive_momentum() -> StrategyDefinition:
        """Aggressive momentum strategy combining fast indicators"""
        return StrategyBuilder.dual_ema_rsi(
            name="Aggressive Momentum",
            fast_ema=8,
            slow_ema=21,
            rsi_period=9,
            rsi_oversold=40,
            rsi_overbought=60
        )
    
    @staticmethod
    def trend_following() -> StrategyDefinition:
        """Strong trend following strategy with multiple confirmations"""
        return StrategyBuilder.triple_ma_trend(
            name="Trend Following",
            short_period=12,
            medium_period=26,
            long_period=50
        ) 
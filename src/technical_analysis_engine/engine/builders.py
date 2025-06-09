"""
Pre-built strategy patterns and builders
"""

try:
    from .config import (
        StrategyDefinition, IndicatorDefinition, CrossoverRule, ThresholdRule,
        EMAConfig, RSIConfig
    )
    from .ta_types import IndicatorType, CrossoverDirection, SignalType, ThresholdCondition
except ImportError:
    from config import (
        StrategyDefinition, IndicatorDefinition, CrossoverRule, ThresholdRule,
        EMAConfig, RSIConfig
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
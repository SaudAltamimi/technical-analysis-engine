"""
Technical Analysis Engine Core Implementation
===========================================

Main engine class for running complete technical analysis workflows.
"""

import pandas as pd
import vectorbt as vbt
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass

# Import from parent package
from ..data_service import YahooFinanceService, TickerRequest, DateRangeRequest, PeriodEnum, IntervalEnum, DataFetchResult
from ..ticker_config import get_ticker_config

# Import from engine package
from .strategy import StrategyEngine
from .config import (
    StrategyDefinition, IndicatorDefinition, CrossoverRule, ThresholdRule,
    EMAConfig, SMAConfig, RSIConfig, MACDConfig
)
from .ta_types import IndicatorType, SignalType, CrossoverDirection, ThresholdCondition


@dataclass
class EngineResult:
    """Result from the technical analysis engine"""
    symbol: str
    strategy_name: str
    data_points: int
    indicators: Dict[str, pd.Series]
    signals: Dict[str, pd.Series]
    backtest_performance: Optional[Dict[str, float]] = None
    price_data: Optional[pd.DataFrame] = None
    entry_signals: Optional[pd.Series] = None
    exit_signals: Optional[pd.Series] = None


class TechnicalAnalysisEngine:
    """
    Unified Technical Analysis Engine
    
    Self-contained engine that can fetch data, run analysis, and perform backtesting
    without requiring external APIs.
    """
    
    def __init__(self):
        """Initialize the technical analysis engine"""
        self.data_service = YahooFinanceService()
        self.ticker_config = get_ticker_config()
    
    def analyze_symbol(
        self,
        symbol: str,
        strategy_config: Dict[str, Any],
        period: str = "1y",
        interval: str = "1d"
    ) -> EngineResult:
        """
        Complete analysis of a symbol with strategy
        
        Args:
            symbol: Stock ticker symbol
            strategy_config: Strategy configuration dict
            period: Time period for data fetching
            interval: Data interval
            
        Returns:
            EngineResult with all analysis data
        """
        # Create strategy from config
        strategy = self._build_strategy_from_config(strategy_config)
        
        # Fetch data
        ticker_request = TickerRequest(
            symbol=symbol,
            period=PeriodEnum(period),
            interval=IntervalEnum(interval)
        )
        
        price_series, ohlc_df, data_info = self.data_service.fetch_by_period(ticker_request)
        
        # Run analysis
        return self._run_analysis(strategy, price_series, ohlc_df, symbol)
    
    def backtest_symbol(
        self,
        symbol: str,
        strategy_config: Dict[str, Any],
        period: str = "1y",
        interval: str = "1d",
        initial_cash: float = 10000,
        commission: float = 0.001
    ) -> EngineResult:
        """
        Complete backtesting of a symbol with strategy
        
        Args:
            symbol: Stock ticker symbol
            strategy_config: Strategy configuration dict
            period: Time period for data fetching
            interval: Data interval
            initial_cash: Starting cash amount
            commission: Commission rate
            
        Returns:
            EngineResult with analysis and backtest performance
        """
        # Get base analysis
        result = self.analyze_symbol(symbol, strategy_config, period, interval)
        
        # Add backtesting
        if result.entry_signals is not None and result.exit_signals is not None:
            # Build strategy for backtesting
            strategy = self._build_strategy_from_config(strategy_config)
            
            # Create strategy engine
            engine = StrategyEngine(strategy)
            
            # Run backtest
            ticker_request = TickerRequest(
                symbol=symbol,
                period=PeriodEnum(period),
                interval=IntervalEnum(interval)
            )
            price_series, _, _ = self.data_service.fetch_by_period(ticker_request)
            
            portfolio = engine.backtest(
                price_series,
                init_cash=initial_cash,
                fees=commission
            )
            
            # Extract performance metrics
            try:
                total_return = float(portfolio.total_return())
            except:
                total_return = 0.0
            
            try:
                # Set frequency for sharpe ratio calculation
                import vectorbt as vbt
                vbt.settings.array_wrapper['freq'] = 'D'  # Daily frequency
                sharpe_ratio = float(portfolio.sharpe_ratio()) if pd.notna(portfolio.sharpe_ratio()) else 0.0
            except:
                sharpe_ratio = 0.0
            
            try:
                max_drawdown = float(portfolio.max_drawdown())
            except:
                max_drawdown = 0.0
            
            try:
                final_value = float(portfolio.value().iloc[-1]) if len(portfolio.value()) > 0 else initial_cash
            except:
                final_value = initial_cash
            
            try:
                total_trades = len(portfolio.trades.records_readable) if hasattr(portfolio.trades, 'records_readable') else 0
            except:
                total_trades = 0
            
            result.backtest_performance = {
                "total_return": total_return,
                "sharpe_ratio": sharpe_ratio,
                "max_drawdown": max_drawdown,
                "final_value": final_value,
                "total_trades": total_trades
            }
        
        return result
    
    def _build_strategy_from_config(self, config: Dict[str, Any]) -> StrategyDefinition:
        """Build StrategyDefinition from configuration dict"""
        # Build indicators
        indicators = []
        for ind_config in config.get("indicators", []):
            ind_type = IndicatorType(ind_config["type"])
            
            # Create parameter config based on type
            if ind_type == IndicatorType.EMA:
                params = EMAConfig(window=ind_config.get("period", ind_config.get("window", 20)))
            elif ind_type == IndicatorType.SMA:
                params = SMAConfig(window=ind_config.get("period", ind_config.get("window", 20)))
            elif ind_type == IndicatorType.RSI:
                params = RSIConfig(period=ind_config.get("period", 14))
            elif ind_type == IndicatorType.MACD:
                params = MACDConfig(
                    fast=ind_config.get("fast", 12),
                    slow=ind_config.get("slow", 26),
                    signal=ind_config.get("signal", 9)
                )
            else:
                params = EMAConfig(window=20)  # Default
            
            indicators.append(IndicatorDefinition(
                name=ind_config["name"],
                type=ind_type,
                params=params
            ))
        
        # Build rules
        crossover_rules = []
        threshold_rules = []
        
        for rule in config.get("crossover_rules", []):
            crossover_rules.append(CrossoverRule(
                name=rule["name"],
                fast_indicator=rule["fast_indicator"],
                slow_indicator=rule["slow_indicator"],
                direction=CrossoverDirection(rule["direction"]),
                signal_type=SignalType.ENTRY if rule["signal_type"] in ["buy", "entry"] else SignalType.EXIT
            ))
        
        for rule in config.get("threshold_rules", []):
            threshold_rules.append(ThresholdRule(
                name=rule["name"],
                indicator=rule["indicator"],
                threshold=rule["threshold"],
                condition=ThresholdCondition(rule["condition"]),
                signal_type=SignalType.ENTRY if rule["signal_type"] in ["buy", "entry"] else SignalType.EXIT
            ))
        
        return StrategyDefinition(
            name=config.get("name", "Custom Strategy"),
            description=config.get("description", "Generated strategy"),
            indicators=indicators,
            crossover_rules=crossover_rules,
            threshold_rules=threshold_rules
        )
    
    def _run_analysis(
        self,
        strategy: StrategyDefinition,
        price_series: pd.Series,
        ohlc_df: pd.DataFrame,
        symbol: str
    ) -> EngineResult:
        """Run complete analysis on price data"""
        # Create strategy engine
        engine = StrategyEngine(strategy)
        
        # Calculate indicators
        calculated_indicators = engine.calculate_indicators(price_series)
        
        # Convert to series dict
        indicators_dict = {
            name: calc_ind.values for name, calc_ind in calculated_indicators.items()
        }
        
        # Generate signals
        signals_dict = {}
        entry_signals = None
        exit_signals = None
        
        if strategy.crossover_rules or strategy.threshold_rules:
            signals_dict = engine.generate_signals(calculated_indicators)
            entry_signals = engine.get_entry_signals(signals_dict)
            exit_signals = engine.get_exit_signals(signals_dict)
        
        return EngineResult(
            symbol=symbol,
            strategy_name=strategy.name,
            data_points=len(price_series),
            indicators=indicators_dict,
            signals=signals_dict,
            price_data=ohlc_df,
            entry_signals=entry_signals,
            exit_signals=exit_signals
        )
    
    def get_popular_tickers(self) -> List[str]:
        """Get list of popular ticker symbols"""
        tickers = self.ticker_config.get_all_tickers()
        return [ticker.get('symbol', '') for ticker in tickers if ticker.get('symbol')]
    
    def validate_symbol(self, symbol: str) -> bool:
        """Validate if a symbol exists and has data"""
        return self.data_service.validate_symbol(symbol) 
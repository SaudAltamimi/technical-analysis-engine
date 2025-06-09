"""
Service layer for technical analysis API
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

# Import from the technical analysis engine package
from technical_analysis_engine import (
    StrategyEngine, YahooFinanceService, StrategyDefinition, IndicatorDefinition,
    IndicatorType, SignalType, CrossoverDirection, ThresholdCondition, 
    TickerRequest, DateRangeRequest, PeriodEnum
)
from technical_analysis_engine.config import (
    CrossoverRule, ThresholdRule, EMAConfig, RSIConfig, MACDConfig
)
from technical_analysis_engine.data_service import DataFetchResult
from technical_analysis_engine.builders import StrategyBuilder

from models import (
    PriceDataPoint, PricePoint, IndicatorResult, IndicatorValuePoint, SignalPoint, 
    AnalysisResult, BacktestResult, EMAStrategyRequest, MultiEMAStrategyRequest,
    RSIStrategyRequest, BacktestParams, TickerInfo, DynamicStrategyDefinition, 
    ComprehensiveBacktestResult
)


class TechnicalAnalysisService:
    """Service for technical analysis operations"""
    
    def __init__(self):
        self.data_service = YahooFinanceService()
    
    @staticmethod
    def price_data_to_series(price_data: List[PriceDataPoint]) -> pd.Series:
        """Convert price data points to pandas Series"""
        timestamps = [point.timestamp for point in price_data]
        prices = [point.price for point in price_data]
        
        return pd.Series(prices, index=pd.DatetimeIndex(timestamps))
    
    @staticmethod
    def series_to_indicator_points(series: pd.Series, name: str) -> List[IndicatorValuePoint]:
        """Convert pandas Series to IndicatorValuePoint list"""
        points = []
        for timestamp, value in series.items():
            if pd.notna(value):  # Skip NaN values
                points.append(IndicatorValuePoint(
                    timestamp=timestamp.to_pydatetime(),
                    value=float(value)
                ))
        return points
    
    @staticmethod
    def ohlc_to_price_points(ohlc_df: pd.DataFrame) -> List[PricePoint]:
        """Convert OHLC DataFrame to PricePoint list"""
        points = []
        for timestamp, row in ohlc_df.iterrows():
            if pd.notna(row['Close']):  # Ensure we have valid data
                points.append(PricePoint(
                    timestamp=timestamp.to_pydatetime(),
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=int(row['Volume']) if pd.notna(row['Volume']) else None
                ))
        return points
    
    @staticmethod
    def signals_to_signal_points(
        signals: Dict[str, pd.Series], 
        signal_type: SignalType,
        rule_names: List[str],
        price_series: pd.Series = None
    ) -> List[SignalPoint]:
        """Convert signal series to SignalPoint list"""
        points = []
        
        for rule_name in rule_names:
            if rule_name in signals:
                series = signals[rule_name]
                for timestamp, signal in series.items():
                    if pd.notna(signal) and signal:  # Only include active signals
                        # Get price at signal timestamp if available
                        price = None
                        if price_series is not None and timestamp in price_series.index:
                            price = float(price_series.loc[timestamp])
                        
                        points.append(SignalPoint(
                            timestamp=timestamp.to_pydatetime(),
                            signal=bool(signal),
                            signal_type=signal_type,
                            rule_name=rule_name,
                            price=price
                        ))
        
        return points
    
    def analyze_ticker_strategy(self, strategy: DynamicStrategyDefinition, ticker_request: TickerRequest) -> AnalysisResult:
        """Analyze strategy using ticker symbol and period"""
        try:
            # Convert dynamic strategy to typed strategy
            typed_strategy = strategy.to_typed_definition()
            
            # Fetch data from Yahoo Finance
            price_series, ohlc_df, data_info = self.data_service.fetch_by_period(ticker_request)
            
            # Perform analysis
            return self._analyze_with_price_series(typed_strategy, price_series, ohlc_df, ticker_request.symbol, data_info)
            
        except Exception as e:
            raise ValueError(f"Ticker analysis failed: {str(e)}")
    
    def analyze_ticker_date_range_strategy(self, strategy: DynamicStrategyDefinition, date_range_request: DateRangeRequest) -> AnalysisResult:
        """Analyze strategy using ticker symbol and date range"""
        try:
            # Convert dynamic strategy to typed strategy
            typed_strategy = strategy.to_typed_definition()
            
            # Fetch data from Yahoo Finance
            price_series, ohlc_df, data_info = self.data_service.fetch_by_date_range(date_range_request)
            
            # Perform analysis
            return self._analyze_with_price_series(typed_strategy, price_series, ohlc_df, date_range_request.symbol, data_info)
            
        except Exception as e:
            raise ValueError(f"Date range analysis failed: {str(e)}")
    
    def analyze_strategy(
        self, 
        strategy: StrategyDefinition, 
        price_data: List[PriceDataPoint]
    ) -> AnalysisResult:
        """Perform complete technical analysis (legacy method with raw price data)"""
        
        # Convert price data to pandas Series
        price_series = self.price_data_to_series(price_data)
        
        # Create mock OHLC DataFrame from price data (all OHLC = Close price)
        ohlc_df = pd.DataFrame({
            'Open': price_series,
            'High': price_series,
            'Low': price_series,
            'Close': price_series,
            'Volume': pd.Series([0] * len(price_series), index=price_series.index)
        })
        
        # Create mock data info for compatibility
        data_info = DataFetchResult(
            symbol="CUSTOM",
            data_points=len(price_series),
            start_date=price_series.index[0].to_pydatetime(),
            end_date=price_series.index[-1].to_pydatetime(),
            price_range=(float(price_series.min()), float(price_series.max()))
        )
        
        # Perform analysis
        return self._analyze_with_price_series(strategy, price_series, ohlc_df, "CUSTOM", data_info)
    
    def _analyze_with_price_series(
        self, 
        strategy: StrategyDefinition, 
        price_series: pd.Series,
        ohlc_df: pd.DataFrame,
        symbol: str,
        data_info
    ) -> AnalysisResult:
        """Internal method to perform analysis with price series"""
        
        # Create strategy engine
        engine = StrategyEngine(strategy)
        
        # Calculate indicators
        calculated_indicators = engine.calculate_indicators(price_series)
        
        # Only generate signals if there are rules defined
        signals = {}
        entry_signals = pd.Series(False, index=price_series.index)
        exit_signals = pd.Series(False, index=price_series.index)
        
        if strategy.crossover_rules or strategy.threshold_rules:
            # Generate signals
            signals = engine.generate_signals(calculated_indicators)
            
            # Get entry and exit signals
            entry_signals = engine.get_entry_signals(signals)
            exit_signals = engine.get_exit_signals(signals)
        
        # Convert indicators to API format
        indicator_results = []
        for ind_def in strategy.indicators:
            calc_indicator = calculated_indicators[ind_def.name]
            indicator_results.append(IndicatorResult(
                name=calc_indicator.name,
                type=ind_def.type,
                params=calc_indicator.params,
                values=self.series_to_indicator_points(calc_indicator.values, calc_indicator.name)
            ))
        
        # Get rule names for each signal type (with defensive checks)
        entry_rule_names = []
        exit_rule_names = []
        
        if strategy.crossover_rules or strategy.threshold_rules:
            entry_rule_names = [
                rule.name for rule in (strategy.crossover_rules + strategy.threshold_rules)
                if rule.signal_type == SignalType.ENTRY
            ]
            
            exit_rule_names = [
                rule.name for rule in (strategy.crossover_rules + strategy.threshold_rules)
                if rule.signal_type == SignalType.EXIT
            ]
        
        # Convert signals to API format
        all_signal_points = []
        entry_signal_points = []
        exit_signal_points = []
        
        # Process all individual rule signals (only if there are rules)
        if signals:
            for rule_name, signal_series in signals.items():
                # Determine signal type for this rule
                rule_signal_type = None
                for rule in strategy.crossover_rules + strategy.threshold_rules:
                    if rule.name == rule_name:
                        rule_signal_type = rule.signal_type
                        break
                
                if rule_signal_type:
                    rule_signals = self.signals_to_signal_points(
                        {rule_name: signal_series}, 
                        rule_signal_type, 
                        [rule_name],
                        price_series
                    )
                    all_signal_points.extend(rule_signals)
        
        # Process combined entry signals
        if entry_signals is not None and not entry_signals.empty and entry_signals.any():
            entry_combined_signals = self.signals_to_signal_points(
                {"combined_entry": entry_signals},
                SignalType.ENTRY,
                ["combined_entry"],
                price_series
            )
            entry_signal_points = entry_combined_signals
        
        # Process combined exit signals
        if exit_signals is not None and not exit_signals.empty and exit_signals.any():
            exit_combined_signals = self.signals_to_signal_points(
                {"combined_exit": exit_signals},
                SignalType.EXIT,
                ["combined_exit"],
                price_series
            )
            exit_signal_points = exit_combined_signals
        
        # Convert OHLC data to price points
        price_data = self.ohlc_to_price_points(ohlc_df)
        
        return AnalysisResult(
            strategy_name=strategy.name,
            symbol=symbol,
            data_info=data_info,
            price_data=price_data,
            indicators=indicator_results,
            signals=all_signal_points,
            entry_signals=entry_signal_points,
            exit_signals=exit_signal_points
        )
    
    def backtest_ticker_strategy(self, strategy: DynamicStrategyDefinition, ticker_request: TickerRequest, params: BacktestParams) -> BacktestResult:
        """Backtest strategy using ticker symbol and period"""
        try:
            # Convert dynamic strategy to typed strategy
            typed_strategy = strategy.to_typed_definition()
            
            # Fetch data from Yahoo Finance
            price_series, _, _ = self.data_service.fetch_by_period(ticker_request)
            
            # Perform backtest
            return self._backtest_with_price_series(typed_strategy, price_series, params)
            
        except Exception as e:
            raise ValueError(f"Ticker backtest failed: {str(e)}")
    
    def backtest_ticker_date_range_strategy(self, strategy: DynamicStrategyDefinition, date_range_request: DateRangeRequest, params: BacktestParams) -> BacktestResult:
        """Backtest strategy using ticker symbol and date range"""
        try:
            # Convert dynamic strategy to typed strategy
            typed_strategy = strategy.to_typed_definition()
            
            # Fetch data from Yahoo Finance
            price_series, _, _ = self.data_service.fetch_by_date_range(date_range_request)
            
            # Perform backtest
            return self._backtest_with_price_series(typed_strategy, price_series, params)
            
        except Exception as e:
            raise ValueError(f"Date range backtest failed: {str(e)}")
    
    def backtest_strategy(
        self,
        strategy: StrategyDefinition,
        price_data: List[PriceDataPoint],
        params: BacktestParams
    ) -> BacktestResult:
        """Perform backtesting (legacy method with raw price data)"""
        
        # Convert price data to pandas Series
        price_series = self.price_data_to_series(price_data)
        
        # Perform backtest
        return self._backtest_with_price_series(strategy, price_series, params)
    
    def _backtest_with_price_series(
        self,
        strategy: StrategyDefinition,
        price_series: pd.Series,
        params: BacktestParams
    ) -> BacktestResult:
        """Internal method to perform backtesting with price series"""
        
        # Ensure the series has frequency information for vectorbt
        if price_series.index.freq is None and len(price_series) > 1:
            # Try to infer frequency
            inferred_freq = pd.infer_freq(price_series.index)
            
            if inferred_freq:
                # Use the inferred frequency
                try:
                    new_index = pd.DatetimeIndex(price_series.index, freq=inferred_freq)
                    price_series = pd.Series(price_series.values, index=new_index)
                except Exception:
                    # If that fails, just use the original series
                    pass
            else:
                # For vectorbt, we can try setting a generic frequency
                # Let's try to use the most common interval between dates
                time_diffs = price_series.index[1:] - price_series.index[:-1]
                most_common_diff = time_diffs.value_counts().index[0] if len(time_diffs) > 0 else time_diffs[0]
                
                # Convert to frequency string
                if most_common_diff.days >= 1:
                    freq = f"{most_common_diff.days}D"
                elif most_common_diff.seconds >= 3600:
                    freq = f"{most_common_diff.seconds // 3600}H"
                else:
                    freq = f"{most_common_diff.seconds // 60}T"
                
                try:
                    # Create evenly spaced index with the calculated frequency
                    start_time = price_series.index[0]
                    periods = len(price_series)
                    new_index = pd.date_range(start=start_time, periods=periods, freq=freq)
                    price_series = pd.Series(price_series.values, index=new_index)
                except Exception:
                    # Last resort: just use the original series without frequency
                    pass
        
        # Create strategy engine
        engine = StrategyEngine(strategy)
        
        # Run backtest
        portfolio = engine.backtest(
            price_series,
            init_cash=params.initial_cash,
            fees=params.commission
        )
        
        # Extract results
        total_return = portfolio.total_return()
        sharpe_ratio = portfolio.sharpe_ratio()
        max_drawdown = portfolio.max_drawdown()
        
        # Calculate win rate and trade count
        trades = portfolio.trades
        win_rate = trades.win_rate() if hasattr(trades, 'win_rate') else 0.0
        total_trades = len(trades.records_readable) if hasattr(trades, 'records_readable') else 0
        
        # Get final portfolio value
        final_value = portfolio.value().iloc[-1] if len(portfolio.value()) > 0 else params.initial_cash
        
        return BacktestResult(
            total_return=float(total_return),
            sharpe_ratio=float(sharpe_ratio) if pd.notna(sharpe_ratio) else 0.0,
            max_drawdown=float(max_drawdown),
            win_rate=float(win_rate),
            total_trades=total_trades,
            final_value=float(final_value)
        )
    
    def comprehensive_backtest_ticker_strategy(self, strategy: DynamicStrategyDefinition, ticker_request: TickerRequest, params: BacktestParams) -> ComprehensiveBacktestResult:
        """Comprehensive backtest with both VectorBT performance and analysis data"""
        try:
            # Convert dynamic strategy to typed strategy
            typed_strategy = strategy.to_typed_definition()
            
            # Fetch data from Yahoo Finance
            price_series, ohlc_df, data_info = self.data_service.fetch_by_period(ticker_request)
            
            # Perform comprehensive backtest
            return self._comprehensive_backtest_with_price_series(typed_strategy, price_series, ohlc_df, ticker_request.symbol, data_info, params)
            
        except Exception as e:
            raise ValueError(f"Comprehensive ticker backtest failed: {str(e)}")
    
    def comprehensive_backtest_ticker_date_range_strategy(self, strategy: DynamicStrategyDefinition, date_range_request: DateRangeRequest, params: BacktestParams) -> ComprehensiveBacktestResult:
        """Comprehensive backtest with date range including both VectorBT performance and analysis data"""
        try:
            # Convert dynamic strategy to typed strategy
            typed_strategy = strategy.to_typed_definition()
            
            # Fetch data from Yahoo Finance
            price_series, ohlc_df, data_info = self.data_service.fetch_by_date_range(date_range_request)
            
            # Perform comprehensive backtest
            return self._comprehensive_backtest_with_price_series(typed_strategy, price_series, ohlc_df, date_range_request.symbol, data_info, params)
            
        except Exception as e:
            raise ValueError(f"Comprehensive date range backtest failed: {str(e)}")
    
    def _comprehensive_backtest_with_price_series(
        self,
        strategy: StrategyDefinition,
        price_series: pd.Series,
        ohlc_df: pd.DataFrame,
        symbol: str,
        data_info,
        params: BacktestParams
    ) -> ComprehensiveBacktestResult:
        """Internal method for comprehensive backtesting with full analysis"""
        
        # First, get the complete analysis (indicators, signals, price data)
        analysis_result = self._analyze_with_price_series(strategy, price_series, ohlc_df, symbol, data_info)
        
        # Then, perform the VectorBT backtest
        backtest_result = self._backtest_with_price_series(strategy, price_series, params)
        
        # Create comprehensive result
        return ComprehensiveBacktestResult(
            performance=backtest_result,
            analysis=analysis_result,
            backtest_metadata={
                "engine": "VectorBT",
                "strategy_type": "custom",
                "data_points": len(price_series),
                "backtest_params": params.dict(),
                "dependency_chain": "Streamlit -> API -> TechnicalAnalysisEngine -> VectorBT"
            }
        )


class StrategyBuilderService:
    """Service for building common strategies"""
    
    def __init__(self):
        self.data_service = YahooFinanceService()
    
    def create_ema_crossover_strategy(self, request: EMAStrategyRequest) -> tuple[StrategyDefinition, TickerRequest]:
        """Create EMA crossover strategy and return strategy with ticker request"""
        strategy = StrategyBuilder.ema_crossover(
            name=request.name,
            fast_period=request.fast_period,
            slow_period=request.slow_period
        )
        
        # Update description if provided
        if request.description:
            strategy.description = request.description
        
        ticker_request = TickerRequest(
            symbol=request.symbol,
            period=request.period,
            interval=request.interval
        )
        
        return strategy, ticker_request
    
    def create_multi_ema_strategy(self, request: MultiEMAStrategyRequest) -> tuple[StrategyDefinition, TickerRequest]:
        """Create multiple EMA strategy with dynamic indicators"""
        # Sort periods to ensure proper crossover logic
        sorted_periods = sorted(request.ema_periods)
        
        # Create indicators
        indicators = []
        for i, period in enumerate(sorted_periods):
            indicators.append(IndicatorDefinition(
                name=f"ema_{period}",
                type=IndicatorType.EMA,
                params=EMAConfig(window=period)
            ))
        
        # Create crossover rules between consecutive EMAs
        crossover_rules = []
        for i in range(len(sorted_periods) - 1):
            fast_name = f"ema_{sorted_periods[i]}"
            slow_name = f"ema_{sorted_periods[i + 1]}"
            
            # Entry when fast crosses above slow
            crossover_rules.append(CrossoverRule(
                name=f"entry_{fast_name}_above_{slow_name}",
                fast_indicator=fast_name,
                slow_indicator=slow_name,
                direction=CrossoverDirection.ABOVE,
                signal_type=SignalType.ENTRY
            ))
            
            # Exit when fast crosses below slow
            crossover_rules.append(CrossoverRule(
                name=f"exit_{fast_name}_below_{slow_name}",
                fast_indicator=fast_name,
                slow_indicator=slow_name,
                direction=CrossoverDirection.BELOW,
                signal_type=SignalType.EXIT
            ))
        
        strategy = StrategyDefinition(
            name=request.name,
            description=request.description or f"Multi-EMA strategy with periods: {request.ema_periods}",
            indicators=indicators,
            crossover_rules=crossover_rules,
            threshold_rules=[]
        )
        
        ticker_request = TickerRequest(
            symbol=request.symbol,
            period=request.period,
            interval=request.interval
        )
        
        return strategy, ticker_request
    
    def create_rsi_strategy(self, request: RSIStrategyRequest) -> tuple[StrategyDefinition, TickerRequest]:
        """Create RSI-based strategy"""
        # Create RSI indicator
        rsi_indicator = IndicatorDefinition(
            name="rsi",
            type=IndicatorType.RSI,
            params=RSIConfig(window=request.rsi_period)
        )
        
        # Create threshold rules
        threshold_rules = [
            # Entry when RSI crosses above oversold threshold
            ThresholdRule(
                name="rsi_entry_oversold",
                indicator="rsi",
                threshold=request.oversold_threshold,
                condition=ThresholdCondition.ABOVE,
                signal_type=SignalType.ENTRY
            ),
            # Exit when RSI crosses above overbought threshold
            ThresholdRule(
                name="rsi_exit_overbought",
                indicator="rsi",
                threshold=request.overbought_threshold,
                condition=ThresholdCondition.ABOVE,
                signal_type=SignalType.EXIT
            )
        ]
        
        strategy = StrategyDefinition(
            name=request.name,
            description=request.description or f"RSI strategy (period: {request.rsi_period}, oversold: {request.oversold_threshold}, overbought: {request.overbought_threshold})",
            indicators=[rsi_indicator],
            crossover_rules=[],
            threshold_rules=threshold_rules
        )
        
        ticker_request = TickerRequest(
            symbol=request.symbol,
            period=request.period,
            interval=request.interval
        )
        
        return strategy, ticker_request
    
    def get_ticker_info(self, symbol: str) -> TickerInfo:
        """Get ticker information"""
        info = self.data_service.get_ticker_info(symbol)
        
        return TickerInfo(
            symbol=info["symbol"],
            name=info["name"],
            sector=info.get("sector"),
            industry=info.get("industry"),
            currency=info.get("currency", "USD"),
            exchange=info.get("exchange"),
            market_cap=info.get("market_cap"),
            description=info.get("description")
        ) 
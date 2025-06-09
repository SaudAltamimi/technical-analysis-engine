"""
Pydantic models for FastAPI application designed for iOS integration
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum

# Import existing models from technical analysis engine
from technical_analysis_engine import (
    IndicatorType, SignalType, CrossoverDirection, ThresholdCondition,
    IndicatorDefinition, StrategyDefinition,
    PeriodEnum, IntervalEnum, TickerRequest, DateRangeRequest
)
from technical_analysis_engine.config import (
    CrossoverRule, ThresholdRule, EMAConfig, SMAConfig, RSIConfig, MACDConfig, IndicatorParams
)
from technical_analysis_engine.data_service import DataFetchResult


class StatusEnum(str, Enum):
    """API response status"""
    SUCCESS = "success"
    ERROR = "error"


class DynamicIndicatorDefinition(BaseModel):
    """Indicator definition for API requests with flexible params"""
    name: str = Field(..., pattern=r'^[a-zA-Z][a-zA-Z0-9_]*$', description="Indicator name")
    type: IndicatorType = Field(..., description="Indicator type")
    params: Optional[Dict[str, Any]] = Field(None, description="Indicator parameters")
    
    # Allow direct parameter fields for convenience
    period: Optional[int] = Field(None, description="Period parameter (convenience field)")
    window: Optional[int] = Field(None, description="Window parameter (convenience field)")
    fast: Optional[int] = Field(None, description="Fast period for MACD")
    slow: Optional[int] = Field(None, description="Slow period for MACD")
    signal: Optional[int] = Field(None, description="Signal period for MACD")
    fast_period: Optional[int] = Field(None, description="Fast period (alternative)")
    slow_period: Optional[int] = Field(None, description="Slow period (alternative)")
    signal_period: Optional[int] = Field(None, description="Signal period (alternative)")
    
    def model_post_init(self, __context) -> None:
        """Auto-populate params from direct fields if params is empty"""
        if not self.params:
            self.params = {}
        
        # Collect all parameter fields
        param_fields = {}
        if self.period is not None:
            param_fields['period'] = self.period
        if self.window is not None:
            param_fields['window'] = self.window
        if self.fast is not None:
            param_fields['fast'] = self.fast
        if self.slow is not None:
            param_fields['slow'] = self.slow
        if self.signal is not None:
            param_fields['signal'] = self.signal
        if self.fast_period is not None:
            param_fields['fast_period'] = self.fast_period
        if self.slow_period is not None:
            param_fields['slow_period'] = self.slow_period
        if self.signal_period is not None:
            param_fields['signal_period'] = self.signal_period
        
        # Merge with existing params (params takes precedence)
        for key, value in param_fields.items():
            if key not in self.params:
                self.params[key] = value
    
    def to_typed_definition(self) -> IndicatorDefinition:
        """Convert to properly typed IndicatorDefinition"""
        if self.type == IndicatorType.EMA:
            # Support both 'window' and 'period' parameter names
            window = self.params.get('window') or self.params.get('period', 20)
            typed_params = EMAConfig(window=window)
        elif self.type == IndicatorType.SMA:
            # Support both 'window' and 'period' parameter names
            window = self.params.get('window') or self.params.get('period', 20)
            typed_params = SMAConfig(window=window)
        elif self.type == IndicatorType.RSI:
            # Support both 'window' and 'period' parameter names
            window = self.params.get('window') or self.params.get('period', 14)
            typed_params = RSIConfig(window=window)
        elif self.type == IndicatorType.MACD:
            typed_params = MACDConfig(
                fast=self.params.get('fast') or self.params.get('fast_period', 12),
                slow=self.params.get('slow') or self.params.get('slow_period', 26),
                signal=self.params.get('signal') or self.params.get('signal_period', 9)
            )
        else:
            # Fallback for unknown types
            typed_params = IndicatorParams()
        
        return IndicatorDefinition(
            name=self.name,
            type=self.type,
            params=typed_params
        )


class DynamicStrategyDefinition(BaseModel):
    """Strategy definition for API requests with flexible indicator params"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    indicators: List[DynamicIndicatorDefinition] = Field(..., min_items=1)
    crossover_rules: List[Dict[str, Any]] = Field(default_factory=list)
    threshold_rules: List[Dict[str, Any]] = Field(default_factory=list)
    
    def to_typed_definition(self) -> StrategyDefinition:
        """Convert to properly typed StrategyDefinition"""
        # Convert indicators
        typed_indicators = [ind.to_typed_definition() for ind in self.indicators]
        
        # Helper function to map trading signal types to framework signal types
        def map_signal_type(signal_type_str: str) -> SignalType:
            if signal_type_str.lower() in ['buy', 'long', 'entry']:
                return SignalType.ENTRY
            elif signal_type_str.lower() in ['sell', 'short', 'exit']:
                return SignalType.EXIT
            else:
                # Try direct enum conversion as fallback
                return SignalType(signal_type_str)
        
        # Convert crossover rules
        typed_crossover_rules = []
        for rule in self.crossover_rules:
            typed_crossover_rules.append(CrossoverRule(
                name=rule['name'],
                fast_indicator=rule['fast_indicator'],
                slow_indicator=rule['slow_indicator'],
                direction=CrossoverDirection(rule['direction']),
                signal_type=map_signal_type(rule['signal_type'])
            ))
        
        # Convert threshold rules
        typed_threshold_rules = []
        for rule in self.threshold_rules:
            typed_threshold_rules.append(ThresholdRule(
                name=rule['name'],
                indicator=rule['indicator'],
                threshold=rule['threshold'],
                condition=ThresholdCondition(rule['condition']),
                signal_type=map_signal_type(rule['signal_type'])
            ))
        
        return StrategyDefinition(
            name=self.name,
            description=self.description,
            indicators=typed_indicators,
            crossover_rules=typed_crossover_rules,
            threshold_rules=typed_threshold_rules
        )


class IndicatorValuePoint(BaseModel):
    """Single indicator value point for time series data"""
    timestamp: datetime = Field(..., description="Timestamp for the data point")
    value: float = Field(..., description="Indicator value")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class IndicatorResult(BaseModel):
    """Complete indicator calculation result"""
    name: str = Field(..., description="Indicator name")
    type: IndicatorType = Field(..., description="Indicator type")
    params: Dict[str, Any] = Field(..., description="Indicator parameters")
    values: List[IndicatorValuePoint] = Field(..., description="Time series values")


class SignalPoint(BaseModel):
    """Single signal point"""
    timestamp: datetime = Field(..., description="Signal timestamp")
    signal: bool = Field(..., description="Signal active/inactive")
    signal_type: SignalType = Field(..., description="Type of signal")
    rule_name: str = Field(..., description="Name of the rule that generated the signal")
    price: Optional[float] = Field(None, description="Price at which the signal was generated")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Keep the old PriceDataPoint for backward compatibility
class PriceDataPoint(BaseModel):
    """Single price data point"""
    timestamp: datetime = Field(..., description="Timestamp")
    price: float = Field(..., ge=0, description="Price value")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PricePoint(BaseModel):
    """OHLC price data point"""
    timestamp: datetime = Field(..., description="Timestamp")
    open: float = Field(..., ge=0, description="Opening price")
    high: float = Field(..., ge=0, description="High price")
    low: float = Field(..., ge=0, description="Low price")
    close: float = Field(..., ge=0, description="Closing price")
    volume: Optional[int] = Field(None, description="Trading volume")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AnalysisResult(BaseModel):
    """Complete analysis result"""
    strategy_name: str = Field(..., description="Name of the strategy")
    symbol: str = Field(..., description="Stock symbol analyzed")
    data_info: DataFetchResult = Field(..., description="Information about the fetched data")
    price_data: List[PricePoint] = Field(..., description="OHLC price data for charting")
    indicators: List[IndicatorResult] = Field(..., description="Calculated indicators")
    signals: List[SignalPoint] = Field(..., description="Generated signals")
    entry_signals: List[SignalPoint] = Field(..., description="Entry signals")
    exit_signals: List[SignalPoint] = Field(..., description="Exit signals")


# New ticker-based request models
class TickerAnalysisRequest(BaseModel):
    """Request model for ticker-based technical analysis"""
    strategy: DynamicStrategyDefinition = Field(..., description="Strategy definition")
    ticker: TickerRequest = Field(..., description="Ticker and period information")


class DateRangeAnalysisRequest(BaseModel):
    """Request model for date range-based technical analysis"""
    strategy: DynamicStrategyDefinition = Field(..., description="Strategy definition")
    ticker: DateRangeRequest = Field(..., description="Ticker and date range information")


# Legacy request model (for backward compatibility)
class AnalysisRequest(BaseModel):
    """Request model for technical analysis with raw price data"""
    strategy: DynamicStrategyDefinition = Field(..., description="Strategy definition")
    price_data: List[PriceDataPoint] = Field(
        ..., 
        min_items=1,
        description="Historical price data"
    )


class CreateIndicatorRequest(BaseModel):
    """Request to create a single indicator"""
    name: str = Field(..., pattern=r'^[a-zA-Z][a-zA-Z0-9_]*$', description="Indicator name")
    type: IndicatorType = Field(..., description="Indicator type")
    params: Union[EMAConfig, RSIConfig, MACDConfig] = Field(..., description="Indicator parameters")


class CreateRuleRequest(BaseModel):
    """Request to create a trading rule"""
    rule_type: str = Field(..., description="Type of rule: 'crossover' or 'threshold'")
    rule_data: Union[CrossoverRule, ThresholdRule] = Field(..., description="Rule configuration")


# Updated strategy request models using tickers
class QuickStrategyRequest(BaseModel):
    """Base request for creating common strategies quickly with ticker symbols"""
    name: str = Field(..., description="Strategy name")
    description: Optional[str] = Field(None, description="Strategy description")
    symbol: str = Field(..., description="Stock ticker symbol (e.g., AAPL, GOOGL)")
    period: PeriodEnum = Field(PeriodEnum.ONE_YEAR, description="Time period for analysis")
    interval: IntervalEnum = Field(IntervalEnum.ONE_DAY, description="Data interval")


class EMAStrategyRequest(QuickStrategyRequest):
    """Request for EMA crossover strategy"""
    fast_period: int = Field(12, ge=2, le=50, description="Fast EMA period")
    slow_period: int = Field(26, ge=10, le=200, description="Slow EMA period")


class MultiEMAStrategyRequest(QuickStrategyRequest):
    """Request for multiple EMA strategy"""
    ema_periods: List[int] = Field(..., min_items=2, max_items=5, description="EMA periods")


class RSIStrategyRequest(QuickStrategyRequest):
    """Request for RSI strategy"""
    rsi_period: int = Field(14, ge=2, le=100, description="RSI period")
    oversold_threshold: float = Field(30, ge=0, le=50, description="Oversold threshold")
    overbought_threshold: float = Field(70, ge=50, le=100, description="Overbought threshold")


class BacktestParams(BaseModel):
    """Backtesting parameters"""
    initial_cash: float = Field(10000, ge=1000, description="Initial cash amount")
    commission: float = Field(0.001, ge=0, le=0.1, description="Commission rate")


class TickerBacktestRequest(BaseModel):
    """Request for backtesting with ticker symbol"""
    strategy: DynamicStrategyDefinition = Field(..., description="Strategy to backtest")
    ticker: TickerRequest = Field(..., description="Ticker and period information")
    params: BacktestParams = Field(default_factory=BacktestParams, description="Backtest parameters")


class DateRangeBacktestRequest(BaseModel):
    """Request for backtesting with date range"""
    strategy: DynamicStrategyDefinition = Field(..., description="Strategy to backtest")
    ticker: DateRangeRequest = Field(..., description="Ticker and date range information")
    params: BacktestParams = Field(default_factory=BacktestParams, description="Backtest parameters")


# Legacy backtest request (for backward compatibility)
class BacktestRequest(BaseModel):
    """Request for backtesting with raw price data"""
    strategy: DynamicStrategyDefinition = Field(..., description="Strategy to backtest")
    price_data: List[PriceDataPoint] = Field(..., min_items=1, description="Price data")
    params: BacktestParams = Field(default_factory=BacktestParams, description="Backtest parameters")


class BacktestResult(BaseModel):
    """Backtesting results"""
    total_return: float = Field(..., description="Total return percentage")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    max_drawdown: float = Field(..., description="Maximum drawdown percentage")
    win_rate: float = Field(..., description="Win rate percentage")
    total_trades: int = Field(..., description="Total number of trades")
    final_value: float = Field(..., description="Final portfolio value")


class ComprehensiveBacktestResult(BaseModel):
    """Comprehensive backtesting results including analysis data"""
    # Performance metrics from VectorBT
    performance: BacktestResult = Field(..., description="Core performance metrics from VectorBT")
    
    # Full analysis data (indicators, signals, price data)
    analysis: AnalysisResult = Field(..., description="Complete strategy analysis including indicators and signals")
    
    # Additional VectorBT metadata
    backtest_metadata: Dict[str, Any] = Field(..., description="Additional metadata from VectorBT portfolio")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TickerInfo(BaseModel):
    """Stock ticker information"""
    symbol: str = Field(..., description="Stock symbol")
    name: str = Field(..., description="Company name")
    sector: Optional[str] = Field(None, description="Sector")
    industry: Optional[str] = Field(None, description="Industry")
    currency: str = Field("USD", description="Trading currency")
    exchange: Optional[str] = Field(None, description="Exchange")
    market_cap: Optional[int] = Field(None, description="Market capitalization")
    description: Optional[str] = Field(None, description="Company description")


class APIResponse(BaseModel):
    """Generic API response wrapper"""
    status: StatusEnum = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    status: StatusEnum = Field(StatusEnum.ERROR, description="Error status")
    message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field("healthy", description="Service status")
    version: str = Field("1.0.0", description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 
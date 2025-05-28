"""
FastAPI application for Technical Analysis Engine
Designed for easy integration with iOS apps using Swift
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import traceback
from typing import List, Dict, Any
import sys
import os

# Add the technical analysis engine to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'techincal-analysis-engine'))

from .models import (
    APIResponse, ErrorResponse, HealthResponse, StatusEnum,
    AnalysisRequest, AnalysisResult, BacktestRequest, BacktestResult,
    TickerAnalysisRequest, DateRangeAnalysisRequest,
    TickerBacktestRequest, DateRangeBacktestRequest,
    EMAStrategyRequest, MultiEMAStrategyRequest, RSIStrategyRequest,
    CreateIndicatorRequest, CreateRuleRequest, PriceDataPoint, TickerInfo,
    DynamicIndicatorDefinition, DynamicStrategyDefinition
)
from .services import TechnicalAnalysisService, StrategyBuilderService
from .data_service import YahooFinanceService, TickerRequest, DateRangeRequest, PeriodEnum, IntervalEnum
from config import StrategyDefinition, IndicatorDefinition
from ta_types import IndicatorType

# Create FastAPI app
app = FastAPI(
    title="Technical Analysis API",
    description="RESTful API for technical analysis and trading signal generation, optimized for iOS integration with Yahoo Finance data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for mobile app integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
analysis_service = TechnicalAnalysisService()
strategy_service = StrategyBuilderService()
data_service = YahooFinanceService()


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for consistent error responses"""
    error_response = ErrorResponse(
        message=f"Internal server error: {str(exc)}",
        error_code="INTERNAL_ERROR",
        details={"trace": traceback.format_exc()}
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.dict()
    )


@app.get("/", response_model=APIResponse)
async def root():
    """Root endpoint"""
    return APIResponse(
        status=StatusEnum.SUCCESS,
        message="Technical Analysis API is running with Yahoo Finance integration",
        data={"version": "1.0.0", "docs": "/docs", "features": ["ticker_analysis", "yahoo_finance", "ios_optimized"]}
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring"""
    return HealthResponse()


# New ticker-based endpoints (recommended)
@app.post("/analyze/ticker", response_model=APIResponse)
async def analyze_ticker_strategy(request: TickerAnalysisRequest):
    """
    Perform technical analysis using Yahoo Finance data
    
    Simply provide a ticker symbol and the API will fetch data automatically.
    This is the recommended way to use the API.
    """
    try:
        result = analysis_service.analyze_ticker_strategy(request.strategy, request.ticker)
        
        return APIResponse(
            status=StatusEnum.SUCCESS,
            message=f"Analysis completed for {request.ticker.symbol}",
            data=result.dict()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Analysis failed: {str(e)}"
        )


@app.post("/analyze/date-range", response_model=APIResponse)
async def analyze_date_range_strategy(request: DateRangeAnalysisRequest):
    """
    Perform technical analysis with custom date range
    
    Allows you to specify exact start and end dates for historical analysis.
    """
    try:
        result = analysis_service.analyze_ticker_date_range_strategy(request.strategy, request.ticker)
        
        return APIResponse(
            status=StatusEnum.SUCCESS,
            message=f"Analysis completed for {request.ticker.symbol} ({request.ticker.start_date.date()} to {request.ticker.end_date.date()})",
            data=result.dict()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Analysis failed: {str(e)}"
        )


@app.post("/backtest/ticker", response_model=APIResponse)
async def backtest_ticker_strategy(request: TickerBacktestRequest):
    """
    Backtest a strategy using Yahoo Finance data
    
    Returns performance metrics based on historical data.
    """
    try:
        result = analysis_service.backtest_ticker_strategy(
            request.strategy, 
            request.ticker, 
            request.params
        )
        
        return APIResponse(
            status=StatusEnum.SUCCESS,
            message=f"Backtest completed for {request.ticker.symbol}",
            data=result.dict()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Backtest failed: {str(e)}"
        )


@app.post("/backtest/date-range", response_model=APIResponse)
async def backtest_date_range_strategy(request: DateRangeBacktestRequest):
    """
    Backtest a strategy with custom date range
    """
    try:
        result = analysis_service.backtest_ticker_date_range_strategy(
            request.strategy, 
            request.ticker, 
            request.params
        )
        
        return APIResponse(
            status=StatusEnum.SUCCESS,
            message=f"Backtest completed for {request.ticker.symbol}",
            data=result.dict()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Backtest failed: {str(e)}"
        )


# Quick strategy endpoints (updated to use tickers)
@app.post("/strategies/ema-crossover", response_model=APIResponse)
async def create_ema_strategy(request: EMAStrategyRequest):
    """
    Create and analyze EMA crossover strategy using ticker symbol
    
    Quick way to create a simple fast/slow EMA crossover strategy with real market data.
    """
    try:
        # Create strategy and ticker request
        strategy, ticker_request = strategy_service.create_ema_crossover_strategy(request)
        
        # Fetch data from Yahoo Finance
        price_series, data_info = data_service.fetch_by_period(ticker_request)
        
        # Analyze strategy with the helper method
        result = analysis_service._analyze_with_price_series(strategy, price_series, request.symbol, data_info)
        
        return APIResponse(
            status=StatusEnum.SUCCESS,
            message=f"EMA crossover strategy created and analyzed for {request.symbol}",
            data={
                "strategy": strategy.dict(),
                "analysis": result.dict()
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"EMA strategy creation failed: {str(e)}"
        )


@app.post("/strategies/multi-ema", response_model=APIResponse)
async def create_multi_ema_strategy(request: MultiEMAStrategyRequest):
    """
    Create and analyze multiple EMA strategy using ticker symbol
    
    Dynamically creates multiple EMA indicators and crossover rules.
    Example: 3 EMAs with periods [5, 20, 50] creates crossover signals between consecutive pairs.
    """
    try:
        # Create strategy and ticker request
        strategy, ticker_request = strategy_service.create_multi_ema_strategy(request)
        
        # Fetch data from Yahoo Finance
        price_series, data_info = data_service.fetch_by_period(ticker_request)
        
        # Analyze strategy with the helper method
        result = analysis_service._analyze_with_price_series(strategy, price_series, request.symbol, data_info)
        
        return APIResponse(
            status=StatusEnum.SUCCESS,
            message=f"Multi-EMA strategy created with {len(request.ema_periods)} indicators for {request.symbol}",
            data={
                "strategy": strategy.dict(),
                "analysis": result.dict()
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Multi-EMA strategy creation failed: {str(e)}"
        )


@app.post("/strategies/rsi", response_model=APIResponse)
async def create_rsi_strategy(request: RSIStrategyRequest):
    """
    Create and analyze RSI-based strategy using ticker symbol
    
    Creates RSI indicator with overbought/oversold threshold rules.
    """
    try:
        # Create strategy and ticker request
        strategy, ticker_request = strategy_service.create_rsi_strategy(request)
        
        # Fetch data from Yahoo Finance
        price_series, data_info = data_service.fetch_by_period(ticker_request)
        
        # Analyze strategy with the helper method
        result = analysis_service._analyze_with_price_series(strategy, price_series, request.symbol, data_info)
        
        return APIResponse(
            status=StatusEnum.SUCCESS,
            message=f"RSI strategy created and analyzed for {request.symbol}",
            data={
                "strategy": strategy.dict(),
                "analysis": result.dict()
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"RSI strategy creation failed: {str(e)}"
        )


# Ticker information endpoints
@app.get("/tickers/{symbol}/info", response_model=APIResponse)
async def get_ticker_info(symbol: str):
    """
    Get information about a stock ticker
    
    Returns company name, sector, industry, and other basic information.
    """
    try:
        info = strategy_service.get_ticker_info(symbol)
        
        return APIResponse(
            status=StatusEnum.SUCCESS,
            message=f"Ticker information retrieved for {symbol}",
            data=info.dict()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get ticker info: {str(e)}"
        )


@app.get("/tickers/{symbol}/validate", response_model=APIResponse)
async def validate_ticker(symbol: str):
    """
    Validate if a ticker symbol exists and has data
    """
    try:
        is_valid = data_service.validate_symbol(symbol)
        
        return APIResponse(
            status=StatusEnum.SUCCESS,
            message=f"Ticker validation completed for {symbol}",
            data={
                "symbol": symbol.upper(),
                "is_valid": is_valid,
                "message": "Symbol is valid and has data" if is_valid else "Symbol is invalid or has no data"
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ticker validation failed: {str(e)}"
        )


# Utility endpoints
@app.get("/indicators/types", response_model=APIResponse)
async def get_indicator_types():
    """Get available indicator types"""
    return APIResponse(
        status=StatusEnum.SUCCESS,
        message="Available indicator types",
        data={
            "types": [indicator_type.value for indicator_type in IndicatorType],
            "descriptions": {
                "EMA": "Exponential Moving Average",
                "SMA": "Simple Moving Average", 
                "RSI": "Relative Strength Index",
                "MACD": "Moving Average Convergence Divergence"
            }
        }
    )


@app.get("/periods", response_model=APIResponse)
async def get_available_periods():
    """Get available time periods for analysis"""
    return APIResponse(
        status=StatusEnum.SUCCESS,
        message="Available time periods",
        data={
            "periods": [period.value for period in PeriodEnum],
            "intervals": [interval.value for interval in IntervalEnum],
            "descriptions": {
                "1d": "1 Day",
                "5d": "5 Days", 
                "1mo": "1 Month",
                "3mo": "3 Months",
                "6mo": "6 Months",
                "1y": "1 Year",
                "2y": "2 Years",
                "5y": "5 Years",
                "10y": "10 Years",
                "ytd": "Year to Date",
                "max": "Maximum Available"
            }
        }
    )


@app.post("/strategies/validate", response_model=APIResponse)
async def validate_strategy(strategy: StrategyDefinition):
    """
    Validate strategy definition without running analysis
    
    Useful for checking strategy configuration before analysis.
    """
    try:
        # The Pydantic model validation will catch most errors
        # Additional validation can be added here
        
        return APIResponse(
            status=StatusEnum.SUCCESS,
            message="Strategy definition is valid",
            data={
                "strategy": strategy.dict(),
                "indicators_count": len(strategy.indicators),
                "crossover_rules_count": len(strategy.crossover_rules),
                "threshold_rules_count": len(strategy.threshold_rules)
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Strategy validation failed: {str(e)}"
        )


# Legacy endpoints (for backward compatibility)
@app.post("/analyze", response_model=APIResponse)
async def analyze_strategy(request: AnalysisRequest):
    """
    [LEGACY] Perform technical analysis with custom price data
    
    ⚠️ This endpoint is deprecated. Use /analyze/ticker instead.
    """
    try:
        result = analysis_service.analyze_strategy(request.strategy, request.price_data)
        
        return APIResponse(
            status=StatusEnum.SUCCESS,
            message="Analysis completed successfully (legacy endpoint)",
            data=result.dict()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Analysis failed: {str(e)}"
        )


@app.post("/backtest", response_model=APIResponse)
async def backtest_strategy(request: BacktestRequest):
    """
    [LEGACY] Backtest a trading strategy with custom price data
    
    ⚠️ This endpoint is deprecated. Use /backtest/ticker instead.
    """
    try:
        result = analysis_service.backtest_strategy(
            request.strategy, 
            request.price_data, 
            request.params
        )
        
        return APIResponse(
            status=StatusEnum.SUCCESS,
            message="Backtest completed successfully (legacy endpoint)",
            data=result.dict()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Backtest failed: {str(e)}"
        )


@app.post("/strategies/custom", response_model=APIResponse)
async def create_custom_strategy(request: Dict[str, Any]):
    """
    Create a custom strategy with specified indicators and rules using ticker symbol
    
    Allows building complete strategies with indicators, crossover rules, and threshold rules.
    Example crossover rule: {"name": "EMA_Cross", "fast_indicator": "EMA_12", "slow_indicator": "EMA_26", "direction": "above", "signal_type": "buy"}
    Example threshold rule: {"name": "RSI_Oversold", "indicator": "RSI_14", "threshold": 30, "condition": "below", "signal_type": "buy"}
    """
    try:
        # Extract required fields
        name = request.get('name')
        symbol = request.get('symbol')
        description = request.get('description', '')
        indicators = request.get('indicators', [])
        crossover_rules = request.get('crossover_rules', [])
        threshold_rules = request.get('threshold_rules', [])
        period = request.get('period', 'ONE_YEAR')
        interval = request.get('interval', 'ONE_DAY')
        
        if not name:
            raise ValueError("Strategy name is required")
        if not symbol:
            raise ValueError("Symbol is required")
        if not indicators:
            raise ValueError("At least one indicator is required")
        
        # Convert string enums to proper enum values
        period_map = {
            '1d': PeriodEnum.ONE_DAY,
            '5d': PeriodEnum.FIVE_DAYS,
            '1mo': PeriodEnum.ONE_MONTH,
            '3mo': PeriodEnum.THREE_MONTHS,
            '6mo': PeriodEnum.SIX_MONTHS,
            '1y': PeriodEnum.ONE_YEAR,
            '2y': PeriodEnum.TWO_YEARS,
            '5y': PeriodEnum.FIVE_YEARS,
            '10y': PeriodEnum.TEN_YEARS,
            'ytd': PeriodEnum.YTD,
            'max': PeriodEnum.MAX
        }
        
        interval_map = {
            '1m': IntervalEnum.ONE_MINUTE,
            '2m': IntervalEnum.TWO_MINUTES,
            '5m': IntervalEnum.FIVE_MINUTES,
            '15m': IntervalEnum.FIFTEEN_MINUTES,
            '30m': IntervalEnum.THIRTY_MINUTES,
            '60m': IntervalEnum.SIXTY_MINUTES,
            '90m': IntervalEnum.NINETY_MINUTES,
            '1h': IntervalEnum.ONE_HOUR,
            '1d': IntervalEnum.ONE_DAY,
            '5d': IntervalEnum.FIVE_DAYS,
            '1wk': IntervalEnum.ONE_WEEK,
            '1mo': IntervalEnum.ONE_MONTH,
            '3mo': IntervalEnum.THREE_MONTHS
        }
        
        try:
            if isinstance(period, str):
                period_enum = period_map.get(period.lower(), PeriodEnum.ONE_YEAR)
            else:
                period_enum = period
        except:
            period_enum = PeriodEnum.ONE_YEAR
            
        try:
            if isinstance(interval, str):
                interval_enum = interval_map.get(interval.lower(), IntervalEnum.ONE_DAY)
            else:
                interval_enum = interval
        except:
            interval_enum = IntervalEnum.ONE_DAY
        
        # Convert indicators to proper format
        dynamic_indicators = []
        for ind in indicators:
            if isinstance(ind, dict):
                dynamic_indicators.append(DynamicIndicatorDefinition(**ind))
            else:
                dynamic_indicators.append(ind)
        
        # Create dynamic strategy with rules
        dynamic_strategy = DynamicStrategyDefinition(
            name=name,
            description=description,
            indicators=dynamic_indicators,
            crossover_rules=crossover_rules,
            threshold_rules=threshold_rules
        )
        
        # Create ticker request
        ticker_request = TickerRequest(
            symbol=symbol,
            period=period_enum,
            interval=interval_enum
        )
        
        # Analyze strategy
        result = analysis_service.analyze_ticker_strategy(dynamic_strategy, ticker_request)
        
        return APIResponse(
            status=StatusEnum.SUCCESS,
            message=f"Custom strategy '{name}' created and analyzed for {symbol}",
            data={
                "strategy": dynamic_strategy.dict(),
                "analysis": result.dict(),
                "rules_summary": {
                    "crossover_rules": len(crossover_rules),
                    "threshold_rules": len(threshold_rules),
                    "total_rules": len(crossover_rules) + len(threshold_rules)
                }
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Custom strategy creation failed: {str(e)}"
        )


@app.post("/strategies/create", response_model=APIResponse)
async def create_full_strategy(request: TickerAnalysisRequest):
    """
    Create and analyze a complete strategy with structured definition
    
    Accepts a full strategy definition with indicators, crossover rules, and threshold rules.
    This is the recommended way to create complex strategies programmatically.
    """
    try:
        # Validate that strategy has at least one indicator
        if not request.strategy.indicators:
            raise ValueError("Strategy must have at least one indicator")
        
        # Analyze strategy
        result = analysis_service.analyze_ticker_strategy(request.strategy, request.ticker)
        
        return APIResponse(
            status=StatusEnum.SUCCESS,
            message=f"Strategy '{request.strategy.name}' created and analyzed for {request.ticker.symbol}",
            data={
                "strategy": request.strategy.dict(),
                "analysis": result.dict(),
                "rules_summary": {
                    "indicators": len(request.strategy.indicators),
                    "crossover_rules": len(request.strategy.crossover_rules),
                    "threshold_rules": len(request.strategy.threshold_rules),
                    "total_rules": len(request.strategy.crossover_rules) + len(request.strategy.threshold_rules)
                }
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Strategy creation failed: {str(e)}"
        )


@app.post("/strategies/validate-full", response_model=APIResponse)
async def validate_full_strategy(strategy: DynamicStrategyDefinition):
    """
    Validate a complete strategy definition including indicators and rules
    
    Validates that all indicators exist, rules reference valid indicators, and parameters are correct.
    """
    try:
        # Basic validation
        if not strategy.indicators:
            raise ValueError("Strategy must have at least one indicator")
        
        # Get indicator names for rule validation
        indicator_names = {ind.name for ind in strategy.indicators}
        
        # Validate crossover rules
        for rule in strategy.crossover_rules:
            if 'fast_indicator' not in rule or 'slow_indicator' not in rule:
                raise ValueError(f"Crossover rule missing required fields: {rule}")
            
            if rule['fast_indicator'] not in indicator_names:
                raise ValueError(f"Crossover rule references unknown indicator: {rule['fast_indicator']}")
            
            if rule['slow_indicator'] not in indicator_names:
                raise ValueError(f"Crossover rule references unknown indicator: {rule['slow_indicator']}")
        
        # Validate threshold rules
        for rule in strategy.threshold_rules:
            if 'indicator' not in rule or 'threshold' not in rule:
                raise ValueError(f"Threshold rule missing required fields: {rule}")
            
            if rule['indicator'] not in indicator_names:
                raise ValueError(f"Threshold rule references unknown indicator: {rule['indicator']}")
        
        return APIResponse(
            status=StatusEnum.SUCCESS,
            message="Strategy definition is valid",
            data={
                "strategy": strategy.dict(),
                "validation_summary": {
                    "indicators_count": len(strategy.indicators),
                    "crossover_rules_count": len(strategy.crossover_rules),
                    "threshold_rules_count": len(strategy.threshold_rules),
                    "total_rules": len(strategy.crossover_rules) + len(strategy.threshold_rules),
                    "indicator_names": list(indicator_names)
                }
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Strategy validation failed: {str(e)}"
        )


# Error handlers for specific HTTP exceptions
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            message="Endpoint not found",
            error_code="NOT_FOUND"
        ).dict()
    )


@app.exception_handler(422)
async def validation_exception_handler(request, exc):
    """Handle validation errors"""
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            message="Validation error",
            error_code="VALIDATION_ERROR",
            details=exc.detail if hasattr(exc, 'detail') else None
        ).dict()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
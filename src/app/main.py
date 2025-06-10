"""
FastAPI application for Technical Analysis Engine
Focused on custom strategy creation and backtesting
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import traceback
from typing import List, Dict, Any
# Import from the technical analysis engine package
from technical_analysis_engine import (
    TechnicalAnalysisEngine,
    YahooFinanceService, TickerRequest, DateRangeRequest, PeriodEnum, IntervalEnum,
    IndicatorType, get_ticker_config
)

from models import (
    APIResponse, ErrorResponse, HealthResponse, StatusEnum,
    TickerBacktestRequest, DateRangeBacktestRequest,
    DynamicIndicatorDefinition, DynamicStrategyDefinition, TickerInfo
)
from services import TechnicalAnalysisService

# Create FastAPI app
app = FastAPI(
    title="Custom Strategy Analysis & Backtesting API",
    description="Focused API for custom strategy creation and backtesting with Yahoo Finance data",
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
data_service = YahooFinanceService()
ticker_config = get_ticker_config()


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
        message="Custom Strategy Analysis & Backtesting API",
        data={
            "version": "1.0.0", 
            "docs": "/docs", 
            "features": ["custom_strategies", "backtesting", "yahoo_finance", "ticker_management"],
            "main_endpoints": [
                "/strategies/custom", 
                "/backtest/custom/ticker", 
                "/backtest/custom/date-range",
                "/tickers/popular",
                "/tickers/{symbol}/validate",
                "/tickers/{symbol}/info",
                "/tickers/search",
                "/tickers/recommendations/{strategy_type}",
                "/tickers/config/stats"
            ]
        }
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring"""
    return HealthResponse()


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


@app.post("/backtest/custom/ticker", response_model=APIResponse)
async def backtest_custom_strategy_ticker(request: TickerBacktestRequest):
    """
    Backtest a custom strategy using Yahoo Finance data
    
    Specifically designed for custom strategies created via /strategies/custom.
    Returns detailed performance metrics and trading signals.
    """
    try:
        # Validate that it's a custom strategy (has indicators and rules)
        if not hasattr(request.strategy, 'indicators') or not request.strategy.indicators:
            raise ValueError("Strategy must be a custom strategy with indicators")
        
        result = analysis_service.comprehensive_backtest_ticker_strategy(
            request.strategy, 
            request.ticker, 
            request.params
        )
        
        return APIResponse(
            status=StatusEnum.SUCCESS,
            message=f"Custom strategy backtest completed for {request.ticker.symbol}",
            data={
                "backtest_results": result.dict(),
                "strategy_info": {
                    "name": request.strategy.name,
                    "indicators_count": len(request.strategy.indicators),
                    "rules_count": len(getattr(request.strategy, 'crossover_rules', [])) + len(getattr(request.strategy, 'threshold_rules', []))
                },
                "vectorbt_trusted": True,
                "dependency_chain": "Streamlit -> API -> TechnicalAnalysisEngine -> VectorBT"
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Custom strategy backtest failed: {str(e)}"
        )


@app.post("/backtest/custom/date-range", response_model=APIResponse)
async def backtest_custom_strategy_date_range(request: DateRangeBacktestRequest):
    """
    Backtest a custom strategy with specific date range
    
    Specifically designed for custom strategies with precise date control.
    Useful for testing strategies against specific market conditions or events.
    """
    try:
        # Validate that it's a custom strategy (has indicators and rules)
        if not hasattr(request.strategy, 'indicators') or not request.strategy.indicators:
            raise ValueError("Strategy must be a custom strategy with indicators")
        
        result = analysis_service.comprehensive_backtest_ticker_date_range_strategy(
            request.strategy, 
            request.ticker, 
            request.params
        )
        
        return APIResponse(
            status=StatusEnum.SUCCESS,
            message=f"Custom strategy backtest completed for {request.ticker.symbol} ({request.ticker.start_date.date()} to {request.ticker.end_date.date()})",
            data={
                "backtest_results": result.dict(),
                "strategy_info": {
                    "name": request.strategy.name,
                    "indicators_count": len(request.strategy.indicators),
                    "rules_count": len(getattr(request.strategy, 'crossover_rules', [])) + len(getattr(request.strategy, 'threshold_rules', []))
                },
                "date_range": {
                    "start_date": request.ticker.start_date.isoformat(),
                    "end_date": request.ticker.end_date.isoformat()
                },
                "vectorbt_trusted": True,
                "dependency_chain": "Streamlit -> API -> TechnicalAnalysisEngine -> VectorBT"
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Custom strategy backtest failed: {str(e)}"
        )


@app.get("/tickers/recommendations/{strategy_type}", response_model=APIResponse)
async def get_strategy_ticker_recommendations(strategy_type: str):
    """
    Get ticker recommendations for specific strategy types
    
    Returns recommended ticker categories and specific tickers based on strategy characteristics.
    Strategy types: trend_following, momentum, mean_reversion, volatility
    """
    try:
        # Get strategy recommendations from YAML config
        recommendations = ticker_config.get_strategy_recommendations()
        
        if strategy_type not in recommendations:
            available_types = list(recommendations.keys())
            raise ValueError(f"Strategy type '{strategy_type}' not found. Available: {available_types}")
        
        strategy_rec = recommendations[strategy_type]
        recommended_categories = strategy_rec.get('recommended_categories', [])
        
        # Get tickers for recommended categories
        recommended_tickers = {}
        total_tickers = 0
        
        for category in recommended_categories:
            try:
                category_data = ticker_config.get_category(category)
                tickers = category_data.get('tickers', [])
                recommended_tickers[category] = {
                    "description": category_data.get('description'),
                    "ticker_count": len(tickers),
                    "sample_tickers": [t.get('symbol') for t in tickers[:5]]  # First 5 as sample
                }
                total_tickers += len(tickers)
            except KeyError:
                continue  # Skip invalid categories
        
        return APIResponse(
            status=StatusEnum.SUCCESS,
            message=f"Ticker recommendations for {strategy_type} strategies",
            data={
                "strategy_type": strategy_type,
                "strategy_info": {
                    "description": strategy_rec.get('description'),
                    "note": strategy_rec.get('note'),
                    "avoid": strategy_rec.get('avoid')
                },
                "recommended_categories": recommended_tickers,
                "total_recommended_tickers": total_tickers,
                "usage_note": f"These tickers are specifically curated for {strategy_type} strategies",
                "next_steps": [
                    "Choose tickers from recommended categories",
                    "Use /tickers/{symbol}/validate to verify specific tickers", 
                    "Create custom strategy with /strategies/custom",
                    "Backtest with /backtest/custom/ticker"
                ]
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get strategy recommendations: {str(e)}"
        )


@app.get("/tickers/config/stats", response_model=APIResponse)
async def get_ticker_config_stats():
    """
    Get statistics about the ticker configuration
    
    Returns metadata about available tickers, categories, and configuration details.
    """
    try:
        stats = ticker_config.get_stats()
        metadata = ticker_config.get_metadata()
        strategy_recs = ticker_config.get_strategy_recommendations()
        
        return APIResponse(
            status=StatusEnum.SUCCESS,
            message="Ticker configuration statistics",
            data={
                "statistics": stats,
                "metadata": metadata,
                "available_strategy_types": list(strategy_recs.keys()),
                "configuration_health": {
                    "total_categories": stats['total_categories'],
                    "total_tickers": stats['total_unique_tickers'],
                    "avg_tickers_per_category": round(stats['total_unique_tickers'] / stats['total_categories'], 1),
                    "last_updated": metadata.get('last_updated'),
                    "version": metadata.get('version')
                }
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get config stats: {str(e)}"
        )


# Utility endpoints for metadata
@app.get("/indicators/types", response_model=APIResponse)
async def get_indicator_types():
    """Get available technical indicator types for custom strategies"""
    return APIResponse(
        status=StatusEnum.SUCCESS,
        message="Available indicator types for custom strategies",
        data={
            "types": [indicator_type.value for indicator_type in IndicatorType],
            "descriptions": {
                "EMA": "Exponential Moving Average - trend following indicator",
                "SMA": "Simple Moving Average - basic trend indicator", 
                "RSI": "Relative Strength Index - momentum oscillator (0-100)",
                "MACD": "Moving Average Convergence Divergence - trend and momentum"
            },
            "parameter_formats": {
                "note": "Parameters can be specified in two ways: nested in 'params' object or directly as fields",
                "nested_format": {
                    "EMA": {"name": "EMA_20", "type": "EMA", "params": {"period": 20}},
                    "SMA": {"name": "SMA_50", "type": "SMA", "params": {"window": 50}},
                    "RSI": {"name": "RSI_14", "type": "RSI", "params": {"period": 14}},
                    "MACD": {"name": "MACD_12_26_9", "type": "MACD", "params": {"fast": 12, "slow": 26, "signal": 9}}
                },
                "direct_format": {
                    "EMA": {"name": "EMA_20", "type": "EMA", "period": 20},
                    "SMA": {"name": "SMA_50", "type": "SMA", "window": 50},
                    "RSI": {"name": "RSI_14", "type": "RSI", "period": 14},
                    "MACD": {"name": "MACD_12_26_9", "type": "MACD", "fast": 12, "slow": 26, "signal": 9}
                }
            },
            "usage_examples": {
                "EMA": {"type": "EMA", "period": 20, "name": "EMA_20"},
                "SMA": {"type": "SMA", "period": 50, "name": "SMA_50"},
                "RSI": {"type": "RSI", "period": 14, "name": "RSI_14"},
                "MACD": {"type": "MACD", "fast": 12, "slow": 26, "signal": 9, "name": "MACD_12_26_9"}
            }
        }
    )


@app.get("/periods", response_model=APIResponse)
async def get_available_periods():
    """Get available time periods and intervals for backtesting"""
    return APIResponse(
        status=StatusEnum.SUCCESS,
        message="Available time periods and intervals for backtesting",
        data={
            "periods": [period.value for period in PeriodEnum],
            "intervals": [interval.value for interval in IntervalEnum],
            "descriptions": {
                "1d": "1 Day - very short-term analysis",
                "5d": "5 Days - short-term analysis", 
                "1mo": "1 Month - short-term strategy testing",
                "3mo": "3 Months - medium-term strategy testing",
                "6mo": "6 Months - medium-term analysis",
                "1y": "1 Year - standard backtesting period",
                "2y": "2 Years - longer-term validation",
                "5y": "5 Years - comprehensive long-term testing",
                "10y": "10 Years - extensive historical validation",
                "ytd": "Year to Date - current year performance",
                "max": "Maximum Available - full historical data"
            },
            "recommended_combinations": {
                "short_term": {"period": "3mo", "interval": "1d"},
                "medium_term": {"period": "1y", "interval": "1d"},
                "long_term": {"period": "5y", "interval": "1d"},
                "intraday": {"period": "1mo", "interval": "1h"}
            }
        }
    )


@app.post("/strategies/validate", response_model=APIResponse)
async def validate_custom_strategy(strategy: DynamicStrategyDefinition):
    """
    Validate custom strategy definition before backtesting
    
    Comprehensive validation for custom strategies including indicators, rules, and parameters.
    Use this before running expensive backtest operations.
    """
    try:
        # Basic validation
        if not strategy.indicators:
            raise ValueError("Custom strategy must have at least one indicator")
        
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
        
        # Check if strategy has any trading rules
        total_rules = len(strategy.crossover_rules) + len(strategy.threshold_rules)
        if total_rules == 0:
            raise ValueError("Custom strategy must have at least one trading rule (crossover or threshold)")
        
        return APIResponse(
            status=StatusEnum.SUCCESS,
            message="Custom strategy definition is valid and ready for backtesting",
            data={
                "strategy": strategy.dict(),
                "validation_summary": {
                    "indicators_count": len(strategy.indicators),
                    "crossover_rules_count": len(strategy.crossover_rules),
                    "threshold_rules_count": len(strategy.threshold_rules),
                    "total_rules": total_rules,
                    "indicator_names": list(indicator_names),
                    "is_ready_for_backtest": True
                }
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Custom strategy validation failed: {str(e)}"
        )


# Ticker management endpoints
@app.get("/tickers/{symbol}/validate", response_model=APIResponse)
async def validate_ticker(symbol: str):
    """
    Validate if a ticker symbol exists and has sufficient data for backtesting
    
    Essential for custom strategy creation - validates ticker before building strategies.
    """
    try:
        symbol = symbol.upper().strip()
        is_valid = data_service.validate_symbol(symbol)
        
        return APIResponse(
            status=StatusEnum.SUCCESS,
            message=f"Ticker validation completed for {symbol}",
            data={
                "symbol": symbol,
                "is_valid": is_valid,
                "status": "ready_for_backtesting" if is_valid else "invalid_or_insufficient_data",
                "message": f"'{symbol}' is valid and ready for custom strategy backtesting" if is_valid else f"'{symbol}' is invalid or lacks sufficient historical data"
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ticker validation failed: {str(e)}"
        )


@app.get("/tickers/{symbol}/info", response_model=APIResponse)
async def get_ticker_info(symbol: str):
    """
    Get detailed information about a stock ticker for custom strategy planning
    
    Returns company info, sector, industry, and market data to help with strategy selection.
    Combines YAML configuration data with live market data.
    """
    try:
        symbol = symbol.upper().strip()
        
        # Get basic info from data service (live data)
        info_dict = data_service.get_ticker_info(symbol)
        info = TickerInfo(
            symbol=info_dict["symbol"],
            name=info_dict["name"],
            sector=info_dict.get("sector"),
            industry=info_dict.get("industry"),
            currency=info_dict.get("currency", "USD"),
            exchange=info_dict.get("exchange"),
            market_cap=info_dict.get("market_cap"),
            description=info_dict.get("description")
        )
        
        # Get additional info from YAML configuration if available
        config_info = ticker_config.get_ticker_by_symbol(symbol)
        
        ticker_data = {
            "ticker_info": info.dict(),
            "backtesting_readiness": {
                "symbol": symbol,
                "suitable_for_custom_strategies": True,
                "recommended_periods": ["1y", "2y", "5y"],
                "data_availability": "Historical data available for backtesting"
            }
        }
        
        # Add configuration data if available
        if config_info:
            ticker_data["configuration_info"] = {
                "in_curated_list": True,
                "market_cap": config_info.get('market_cap'),
                "liquidity": config_info.get('liquidity'),
                "sector": config_info.get('sector'),
                "recommended_for": "Custom strategy backtesting"
            }
        else:
            ticker_data["configuration_info"] = {
                "in_curated_list": False,
                "note": "Ticker not in curated list but may still be valid for backtesting"
            }
        
        return APIResponse(
            status=StatusEnum.SUCCESS,
            message=f"Ticker information retrieved for {symbol}",
            data=ticker_data
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get ticker info for {symbol}: {str(e)}"
        )


@app.get("/tickers/popular", response_model=APIResponse)
async def get_popular_tickers():
    """
    Get a curated list of popular tickers suitable for custom strategy backtesting
    
    Returns commonly traded stocks with good liquidity and historical data coverage.
    Loads from YAML configuration file for easy maintenance.
    """
    try:
        # Get categories from YAML configuration
        categories = ticker_config.get_categories()
        
        # Transform to match previous API format but with richer data
        formatted_categories = {}
        for cat_name, cat_data in categories.items():
            tickers_list = []
            for ticker in cat_data.get('tickers', []):
                tickers_list.append({
                    "symbol": ticker.get('symbol'),
                    "name": ticker.get('name'),
                    "sector": ticker.get('sector'),
                    "market_cap": ticker.get('market_cap'),
                    "liquidity": ticker.get('liquidity')
                })
            
            formatted_categories[cat_name] = {
                "description": cat_data.get('description'),
                "tickers": tickers_list
            }
        
        # Get metadata and stats
        metadata = ticker_config.get_metadata()
        stats = ticker_config.get_stats()
        
        return APIResponse(
            status=StatusEnum.SUCCESS,
            message="Popular tickers for custom strategy backtesting (from YAML config)",
            data={
                "categories": formatted_categories,
                "total_tickers": stats['total_unique_tickers'],
                "total_categories": stats['total_categories'],
                "metadata": metadata,
                "usage_note": "All listed tickers have been verified for custom strategy backtesting",
                "recommendation": "Start with large cap stocks or ETFs for more stable backtesting results"
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get popular tickers: {str(e)}"
        )


@app.post("/tickers/search", response_model=APIResponse)
async def search_tickers(request: Dict[str, Any]):
    """
    Search for ticker symbols by company name or partial symbol match
    
    Helps users find the correct ticker symbol for their custom strategy backtesting.
    Searches through YAML configuration file.
    """
    try:
        query = request.get('query', '').strip()
        if not query:
            raise ValueError("Search query is required")
        
        if len(query) < 2:
            raise ValueError("Search query must be at least 2 characters")
        
        # Use ticker configuration to search
        matches = ticker_config.search_tickers(query)
        
        return APIResponse(
            status=StatusEnum.SUCCESS,
            message=f"Found {len(matches)} ticker matches for '{query}' (from YAML config)",
            data={
                "query": query,
                "matches": matches,
                "total_results": len(matches),
                "search_scope": f"{ticker_config.get_stats()['total_unique_tickers']} configured tickers",
                "note": "Use /tickers/{symbol}/validate to verify ticker before creating custom strategies"
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ticker search failed: {str(e)}"
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
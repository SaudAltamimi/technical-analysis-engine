"""
Data fetching service for the Technical Analysis API
Handles Yahoo Finance integration and data validation
"""

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum


class PeriodEnum(str, Enum):
    """Supported Yahoo Finance periods"""
    ONE_DAY = "1d"
    FIVE_DAYS = "5d"
    ONE_MONTH = "1mo"
    THREE_MONTHS = "3mo"
    SIX_MONTHS = "6mo"
    ONE_YEAR = "1y"
    TWO_YEARS = "2y"
    FIVE_YEARS = "5y"
    TEN_YEARS = "10y"
    YTD = "ytd"
    MAX = "max"


class IntervalEnum(str, Enum):
    """Supported Yahoo Finance intervals"""
    ONE_MINUTE = "1m"
    TWO_MINUTES = "2m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    SIXTY_MINUTES = "60m"
    NINETY_MINUTES = "90m"
    ONE_HOUR = "1h"
    ONE_DAY = "1d"
    FIVE_DAYS = "5d"
    ONE_WEEK = "1wk"
    ONE_MONTH = "1mo"
    THREE_MONTHS = "3mo"


class TickerRequest(BaseModel):
    """Request model for ticker-based data fetching"""
    symbol: str = Field(..., description="Stock ticker symbol (e.g., AAPL, GOOGL)")
    period: PeriodEnum = Field(PeriodEnum.ONE_YEAR, description="Time period")
    interval: IntervalEnum = Field(IntervalEnum.ONE_DAY, description="Data interval")
    
    @validator('symbol')
    def validate_symbol(cls, v):
        """Validate ticker symbol format"""
        if not v or not isinstance(v, str):
            raise ValueError("Symbol must be a non-empty string")
        
        # Clean and uppercase symbol
        symbol = v.strip().upper()
        
        # Basic validation - allow letters, numbers, dots, and hyphens
        if not all(c.isalnum() or c in '.-' for c in symbol):
            raise ValueError("Symbol contains invalid characters")
        
        return symbol


class DateRangeRequest(BaseModel):
    """Request model for custom date range data fetching"""
    symbol: str = Field(..., description="Stock ticker symbol")
    start_date: datetime = Field(..., description="Start date")
    end_date: datetime = Field(..., description="End date")
    interval: IntervalEnum = Field(IntervalEnum.ONE_DAY, description="Data interval")
    
    @validator('symbol')
    def validate_symbol(cls, v):
        return TickerRequest.validate_symbol(cls, v)
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        """Validate that end_date is after start_date"""
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError("End date must be after start date")
        return v


class DataFetchResult(BaseModel):
    """Result of data fetching operation"""
    symbol: str = Field(..., description="Stock symbol")
    data_points: int = Field(..., description="Number of data points fetched")
    start_date: datetime = Field(..., description="Actual start date of data")
    end_date: datetime = Field(..., description="Actual end date of data")
    price_range: tuple = Field(..., description="Min and max prices (min, max)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class YahooFinanceService:
    """Service for fetching stock data from Yahoo Finance"""
    
    @staticmethod
    def fetch_by_period(request: TickerRequest) -> tuple[pd.Series, pd.DataFrame, DataFetchResult]:
        """
        Fetch stock data for a specific period
        
        Returns:
            tuple: (price_series, ohlc_df, fetch_result)
        """
        try:
            # Create ticker object
            ticker = yf.Ticker(request.symbol)
            
            # Fetch historical data
            hist = ticker.history(
                period=request.period.value,
                interval=request.interval.value
            )
            
            if hist.empty:
                raise ValueError(f"No data found for symbol {request.symbol}")
            
            # Use closing prices for analysis
            price_series = hist['Close'].copy()
            price_series.name = 'price'
            
            # Keep full OHLC data for charting
            ohlc_df = hist[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
            
            # Create result metadata
            result = DataFetchResult(
                symbol=request.symbol,
                data_points=len(price_series),
                start_date=price_series.index[0].to_pydatetime(),
                end_date=price_series.index[-1].to_pydatetime(),
                price_range=(float(price_series.min()), float(price_series.max()))
            )
            
            return price_series, ohlc_df, result
            
        except Exception as e:
            raise ValueError(f"Failed to fetch data for {request.symbol}: {str(e)}")
    
    @staticmethod
    def fetch_by_date_range(request: DateRangeRequest) -> tuple[pd.Series, pd.DataFrame, DataFetchResult]:
        """
        Fetch stock data for a custom date range
        
        Returns:
            tuple: (price_series, ohlc_df, fetch_result)
        """
        try:
            # Create ticker object
            ticker = yf.Ticker(request.symbol)
            
            # Fetch historical data
            hist = ticker.history(
                start=request.start_date,
                end=request.end_date,
                interval=request.interval.value
            )
            
            if hist.empty:
                raise ValueError(f"No data found for symbol {request.symbol} in the specified date range")
            
            # Use closing prices for analysis
            price_series = hist['Close'].copy()
            price_series.name = 'price'
            
            # Keep full OHLC data for charting
            ohlc_df = hist[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
            
            # Create result metadata
            result = DataFetchResult(
                symbol=request.symbol,
                data_points=len(price_series),
                start_date=price_series.index[0].to_pydatetime(),
                end_date=price_series.index[-1].to_pydatetime(),
                price_range=(float(price_series.min()), float(price_series.max()))
            )
            
            return price_series, ohlc_df, result
            
        except Exception as e:
            raise ValueError(f"Failed to fetch data for {request.symbol}: {str(e)}")
    
    @staticmethod
    def get_ticker_info(symbol: str) -> dict:
        """
        Get basic information about a ticker symbol
        
        Returns:
            dict: Ticker information including name, sector, etc.
        """
        try:
            ticker = yf.Ticker(symbol.upper())
            info = ticker.info
            
            # Extract relevant information
            return {
                "symbol": symbol.upper(),
                "name": info.get("longName", "Unknown"),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "currency": info.get("currency", "USD"),
                "exchange": info.get("exchange", "Unknown"),
                "market_cap": info.get("marketCap"),
                "description": info.get("longBusinessSummary", "")[:200] + "..." if info.get("longBusinessSummary", "") else ""
            }
            
        except Exception as e:
            return {
                "symbol": symbol.upper(),
                "name": "Unknown",
                "error": str(e)
            }
    
    @staticmethod
    def validate_symbol(symbol: str) -> bool:
        """
        Validate if a ticker symbol exists and has data
        
        Returns:
            bool: True if symbol is valid and has data
        """
        try:
            ticker = yf.Ticker(symbol.upper())
            # Try to fetch recent data to validate
            hist = ticker.history(period="5d")
            return not hist.empty
        except:
            return False
    
    @staticmethod
    def suggest_period_for_analysis(analysis_type: str = "ema_crossover") -> PeriodEnum:
        """
        Suggest appropriate time period based on analysis type
        
        Args:
            analysis_type: Type of analysis being performed
            
        Returns:
            PeriodEnum: Recommended period
        """
        suggestions = {
            "ema_crossover": PeriodEnum.ONE_YEAR,
            "rsi": PeriodEnum.SIX_MONTHS,
            "macd": PeriodEnum.ONE_YEAR,
            "multi_ema": PeriodEnum.TWO_YEARS,
            "backtesting": PeriodEnum.TWO_YEARS,
            "short_term": PeriodEnum.THREE_MONTHS,
            "long_term": PeriodEnum.FIVE_YEARS
        }
        
        return suggestions.get(analysis_type, PeriodEnum.ONE_YEAR) 
"""
Unit tests for the core TechnicalAnalysisEngine
"""

import pytest
from technical_analysis_engine import TechnicalAnalysisEngine


class TestTechnicalAnalysisEngine:
    """Test cases for the main engine"""
    
    def test_engine_initialization(self):
        """Test that engine initializes properly"""
        engine = TechnicalAnalysisEngine()
        assert engine is not None
        assert hasattr(engine, 'data_service')
        assert hasattr(engine, 'ticker_config')
    
    def test_symbol_validation(self):
        """Test symbol validation functionality"""
        engine = TechnicalAnalysisEngine()
        
        # Test valid symbols
        assert engine.validate_symbol("AAPL") == True
        assert engine.validate_symbol("MSFT") == True
        
        # Test invalid symbols
        assert engine.validate_symbol("INVALID123") == False
        assert engine.validate_symbol("") == False
    
    def test_popular_tickers(self):
        """Test getting popular tickers"""
        engine = TechnicalAnalysisEngine()
        tickers = engine.get_popular_tickers()
        
        assert isinstance(tickers, list)
        assert len(tickers) > 0
        # Should contain common stocks
        assert any("AAPL" in ticker for ticker in tickers)
    
    def test_analyze_symbol(self, sample_strategy_config):
        """Test symbol analysis with strategy"""
        engine = TechnicalAnalysisEngine()
        
        result = engine.analyze_symbol(
            symbol="AAPL",
            strategy_config=sample_strategy_config,
            period="3mo"  # Use shorter period for faster testing
        )
        
        assert result is not None
        assert result.symbol == "AAPL"
        assert result.strategy_name == sample_strategy_config["name"]
        assert result.data_points > 0
        assert isinstance(result.indicators, dict)
        assert len(result.indicators) == 2  # EMA_12 and EMA_26
    
    def test_backtest_symbol(self, sample_strategy_config):
        """Test symbol backtesting"""
        engine = TechnicalAnalysisEngine()
        
        result = engine.backtest_symbol(
            symbol="AAPL",
            strategy_config=sample_strategy_config,
            period="3mo",  # Use shorter period for faster testing
            initial_cash=10000
        )
        
        assert result is not None
        assert result.backtest_performance is not None
        assert "total_return" in result.backtest_performance
        assert "sharpe_ratio" in result.backtest_performance
        assert "max_drawdown" in result.backtest_performance
        assert "final_value" in result.backtest_performance 
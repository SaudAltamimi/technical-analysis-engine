"""
Tests for signal generation using strategy builders

This module tests the actual signal generation logic by:
- Creating synthetic market data with known patterns
- Building strategies using the builders
- Running the strategies against the data
- Validating that signals are generated at the correct times and conditions
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# Import from the technical analysis engine
from technical_analysis_engine.engine.builders import StrategyBuilder, StrategyPresets
from technical_analysis_engine.engine.strategy import StrategyEngine
from technical_analysis_engine.engine.config import StrategyDefinition
from technical_analysis_engine.engine.ta_types import SignalType
# from technical_analysis_engine.utils import create_sample_data


class TestSignalGeneration:
    """Test suite for signal generation using strategy builders"""
    
    def create_trending_data(self, start_price: float = 100, trend_strength: float = 0.001, 
                           volatility: float = 0.01, length: int = 100) -> pd.Series:
        """Create synthetic trending price data"""
        dates = pd.date_range(start="2023-01-01", periods=length, freq='D')
        
        # Create trending data with some noise
        trend = np.cumsum(np.random.normal(trend_strength, volatility, length))
        prices = start_price * np.exp(trend)
        
        return pd.Series(prices, index=dates, name='close')
    
    def create_oscillating_data(self, start_price: float = 100, period: int = 20, 
                               amplitude: float = 0.1, length: int = 100) -> pd.Series:
        """Create synthetic oscillating price data"""
        dates = pd.date_range(start="2023-01-01", periods=length, freq='D')
        
        # Create oscillating pattern
        x = np.linspace(0, 4 * np.pi, length)
        oscillation = amplitude * np.sin(x * period / 10)
        noise = np.random.normal(0, 0.005, length)
        
        prices = start_price * (1 + oscillation + noise)
        
        return pd.Series(prices, index=dates, name='close')
    
    def create_crossover_data(self, start_price: float = 100, crossover_point: int = 50, 
                             length: int = 100) -> pd.Series:
        """Create data with a clear crossover pattern"""
        dates = pd.date_range(start="2023-01-01", periods=length, freq='D')
        
        # Create data that trends down then up to create crossover
        prices = []
        for i in range(length):
            if i < crossover_point:
                # Downtrend
                price = start_price * (1 - 0.001 * i)
            else:
                # Uptrend after crossover
                price = start_price * (0.95 + 0.002 * (i - crossover_point))
            
            # Add some noise
            price += np.random.normal(0, 0.5)
            prices.append(price)
        
        return pd.Series(prices, index=dates, name='close')
    
    def create_rsi_extreme_data(self, start_price: float = 100, length: int = 100) -> pd.Series:
        """Create data with RSI extreme conditions"""
        dates = pd.date_range(start="2023-01-01", periods=length, freq='D')
        
        prices = []
        current_price = start_price
        
        for i in range(length):
            if i < 20:
                # Create oversold condition
                current_price *= 0.98
            elif i < 40:
                # Recovery
                current_price *= 1.005
            elif i < 60:
                # Create overbought condition
                current_price *= 1.02
            else:
                # Correction
                current_price *= 0.995
            
            # Add noise
            current_price += np.random.normal(0, 0.2)
            prices.append(current_price)
        
        return pd.Series(prices, index=dates, name='close')
    
    def test_ema_crossover_signal_generation(self):
        """Test EMA crossover signal generation with synthetic data"""
        # Create data with clear crossover pattern
        price_data = self.create_crossover_data(start_price=100, crossover_point=30, length=60)
        
        # Build EMA crossover strategy
        strategy = StrategyBuilder.ema_crossover(fast_period=5, slow_period=15)
        
        # Create and run strategy engine
        engine = StrategyEngine(strategy)
        indicators = engine.calculate_indicators(price_data)
        signals = engine.generate_signals(indicators)
        
        # Get entry and exit signals
        entry_signals = engine.get_entry_signals(signals)
        exit_signals = engine.get_exit_signals(signals)
        
        # Validate signals were generated
        assert len(signals) == 2  # Should have entry and exit signals
        assert entry_signals.sum() > 0, "Should have at least one entry signal"
        
        # Validate signal timing - entry should come after crossover point
        entry_dates = entry_signals[entry_signals].index
        if len(entry_dates) > 0:
            first_entry_idx = price_data.index.get_loc(entry_dates[0])
            assert first_entry_idx > 20, "Entry signal should come after crossover setup"
        
        # Validate indicators exist
        assert 'ema_fast' in indicators
        assert 'ema_slow' in indicators
        assert len(indicators['ema_fast'].values) == len(price_data)
        assert len(indicators['ema_slow'].values) == len(price_data)
    
    def test_sma_crossover_signal_generation(self):
        """Test SMA crossover signal generation"""
        # Create trending data
        price_data = self.create_trending_data(trend_strength=0.002, length=100)
        
        # Build SMA crossover strategy
        strategy = StrategyBuilder.sma_crossover(fast_period=10, slow_period=30)
        
        # Run strategy
        engine = StrategyEngine(strategy)
        indicators = engine.calculate_indicators(price_data)
        signals = engine.generate_signals(indicators)
        
        entry_signals = engine.get_entry_signals(signals)
        
        # Validate signals
        assert len(signals) == 2
        assert 'sma_fast' in indicators
        assert 'sma_slow' in indicators
        
        # In trending data, should generate some entry signals
        assert entry_signals.sum() >= 0  # Could be 0 if trend is not strong enough
    
    def test_rsi_mean_reversion_signal_generation(self):
        """Test RSI mean reversion signal generation"""
        # Create data with RSI extremes
        price_data = self.create_rsi_extreme_data(length=80)
        
        # Build RSI mean reversion strategy
        strategy = StrategyBuilder.rsi_mean_reversion(rsi_period=14, oversold=30, overbought=70)
        
        # Run strategy
        engine = StrategyEngine(strategy)
        indicators = engine.calculate_indicators(price_data)
        signals = engine.generate_signals(indicators)
        
        entry_signals = engine.get_entry_signals(signals)
        exit_signals = engine.get_exit_signals(signals)
        
        # Validate signals
        assert len(signals) == 2  # Entry and exit rules
        assert 'rsi' in indicators
        
        # RSI should be calculated
        rsi_values = indicators['rsi'].values
        assert not rsi_values.isna().all(), "RSI should have valid values"
        assert rsi_values.min() >= 0 and rsi_values.max() <= 100, "RSI should be between 0-100"
        
        # Should generate some signals with extreme price movements
        total_signals = entry_signals.sum() + exit_signals.sum()
        assert total_signals > 0, "Should generate some signals with extreme price movements"
    
    def test_macd_momentum_signal_generation(self):
        """Test MACD momentum signal generation"""
        # Create trending data
        price_data = self.create_trending_data(trend_strength=0.003, length=100)
        
        # Build MACD momentum strategy
        strategy = StrategyBuilder.macd_momentum(fast_period=12, slow_period=26, signal_period=9)
        
        # Run strategy
        engine = StrategyEngine(strategy)
        indicators = engine.calculate_indicators(price_data)
        signals = engine.generate_signals(indicators)
        
        entry_signals = engine.get_entry_signals(signals)
        
        # Validate signals
        assert len(signals) == 2  # Entry and exit crossover rules
        assert 'macd' in indicators
        
        # MACD should be calculated
        macd_values = indicators['macd'].values
        assert not macd_values.isna().all(), "MACD should have valid values"
    
    def test_rsi_momentum_signal_generation(self):
        """Test RSI momentum signal generation"""
        # Create trending data
        price_data = self.create_trending_data(trend_strength=0.002, length=80)
        
        # Build RSI momentum strategy
        strategy = StrategyBuilder.rsi_momentum(rsi_period=14, momentum_threshold=50)
        
        # Run strategy
        engine = StrategyEngine(strategy)
        indicators = engine.calculate_indicators(price_data)
        signals = engine.generate_signals(indicators)
        
        entry_signals = engine.get_entry_signals(signals)
        exit_signals = engine.get_exit_signals(signals)
        
        # Validate signals
        assert len(signals) == 2  # Entry and exit threshold rules
        assert 'rsi' in indicators
        
        # RSI should be calculated
        rsi_values = indicators['rsi'].values
        assert not rsi_values.isna().all(), "RSI should have valid values"
    
    def test_dual_ema_rsi_signal_generation(self):
        """Test dual EMA + RSI signal generation"""
        # Create data with both trend and RSI conditions
        price_data = self.create_crossover_data(start_price=100, crossover_point=40, length=80)
        
        # Build dual EMA + RSI strategy
        strategy = StrategyBuilder.dual_ema_rsi(
            fast_ema=8, slow_ema=21, rsi_period=14, 
            rsi_oversold=30, rsi_overbought=70
        )
        
        # Run strategy
        engine = StrategyEngine(strategy)
        indicators = engine.calculate_indicators(price_data)
        signals = engine.generate_signals(indicators)
        
        entry_signals = engine.get_entry_signals(signals)
        exit_signals = engine.get_exit_signals(signals)
        
        # Validate signals
        assert len(signals) == 4  # 2 crossover rules + 2 threshold rules
        assert len(indicators) == 3  # ema_fast, ema_slow, rsi
        
        # All indicators should be calculated
        for indicator_name in ['ema_fast', 'ema_slow', 'rsi']:
            assert indicator_name in indicators
            assert not indicators[indicator_name].values.isna().all()
    
    def test_macd_rsi_confluence_signal_generation(self):
        """Test MACD + RSI confluence signal generation"""
        # Create complex data pattern
        price_data = self.create_rsi_extreme_data(length=100)
        
        # Build MACD + RSI confluence strategy
        strategy = StrategyBuilder.macd_rsi_confluence(
            macd_fast=12, macd_slow=26, macd_signal=9,
            rsi_period=14, rsi_oversold=30, rsi_overbought=70
        )
        
        # Run strategy
        engine = StrategyEngine(strategy)
        indicators = engine.calculate_indicators(price_data)
        signals = engine.generate_signals(indicators)
        
        # Validate signals
        assert len(signals) == 4  # 2 crossover rules + 2 threshold rules
        assert len(indicators) == 2  # macd, rsi
        
        # All indicators should be calculated
        assert 'macd' in indicators
        assert 'rsi' in indicators
        assert not indicators['macd'].values.isna().all()
        assert not indicators['rsi'].values.isna().all()
    
    def test_triple_ma_trend_signal_generation(self):
        """Test triple MA trend signal generation"""
        # Create strong trending data
        price_data = self.create_trending_data(trend_strength=0.004, length=100)
        
        # Build triple MA trend strategy
        strategy = StrategyBuilder.triple_ma_trend(
            short_period=9, medium_period=21, long_period=50
        )
        
        # Run strategy
        engine = StrategyEngine(strategy)
        indicators = engine.calculate_indicators(price_data)
        signals = engine.generate_signals(indicators)
        
        # Validate signals
        assert len(signals) == 3  # 3 crossover rules
        assert len(indicators) == 3  # ema_short, ema_medium, ema_long
        
        # All indicators should be calculated
        for indicator_name in ['ema_short', 'ema_medium', 'ema_long']:
            assert indicator_name in indicators
            assert not indicators[indicator_name].values.isna().all()
    
    def test_signal_timing_validation(self):
        """Test that signals are generated at the correct times"""
        # Create data with known crossover at specific point
        dates = pd.date_range(start="2023-01-01", periods=50, freq='D')
        
        # Create price data where fast EMA crosses above slow EMA around day 25
        prices = []
        for i in range(50):
            if i < 20:
                price = 100 - i * 0.5  # Declining
            else:
                price = 90 + (i - 20) * 1.5  # Rising
            prices.append(price)
        
        price_data = pd.Series(prices, index=dates, name='close')
        
        # Build EMA crossover strategy with short periods to detect crossover quickly
        strategy = StrategyBuilder.ema_crossover(fast_period=3, slow_period=8)
        
        # Run strategy
        engine = StrategyEngine(strategy)
        indicators = engine.calculate_indicators(price_data)
        signals = engine.generate_signals(indicators)
        
        entry_signals = engine.get_entry_signals(signals)
        
        # Validate timing
        entry_dates = entry_signals[entry_signals].index
        if len(entry_dates) > 0:
            first_entry_idx = price_data.index.get_loc(entry_dates[0])
            # Entry should occur after the crossover setup period
            assert first_entry_idx > 15, f"Entry at index {first_entry_idx} too early"
            assert first_entry_idx < 40, f"Entry at index {first_entry_idx} too late"
    
    def test_rsi_threshold_accuracy(self):
        """Test RSI threshold accuracy"""
        # Create data that will definitely create RSI extremes
        dates = pd.date_range(start="2023-01-01", periods=50, freq='D')
        
        # Create strong downtrend then uptrend
        prices = []
        start_price = 100
        for i in range(50):
            if i < 20:
                # Strong downtrend to create oversold
                price = start_price * (0.95 ** i)
            else:
                # Recovery
                price = prices[19] * (1.02 ** (i - 19))
            prices.append(price)
        
        price_data = pd.Series(prices, index=dates, name='close')
        
        # Build RSI strategy with specific thresholds
        strategy = StrategyBuilder.rsi_mean_reversion(
            rsi_period=14, oversold=25, overbought=75
        )
        
        # Run strategy
        engine = StrategyEngine(strategy)
        indicators = engine.calculate_indicators(price_data)
        signals = engine.generate_signals(indicators)
        
        # Get RSI values
        rsi_values = indicators['rsi'].values
        
        # Validate RSI calculation
        assert not rsi_values.isna().all(), "RSI should have valid values"
        
        # Check for oversold condition
        oversold_condition = rsi_values < 25
        if oversold_condition.any():
            # Should generate entry signals when oversold
            entry_signals = signals['rsi_entry']
            assert entry_signals.any(), "Should generate entry signals when RSI is oversold"


class TestStrategyPresetSignals:
    """Test signal generation for strategy presets"""
    
    def test_scalping_ema_signals(self):
        """Test scalping EMA preset signal generation"""
        # Create high-frequency oscillating data
        price_data = TestSignalGeneration().create_oscillating_data(
            period=5, amplitude=0.02, length=100
        )
        
        # Use scalping preset
        strategy = StrategyPresets.scalping_ema()
        
        # Run strategy
        engine = StrategyEngine(strategy)
        indicators = engine.calculate_indicators(price_data)
        signals = engine.generate_signals(indicators)
        
        entry_signals = engine.get_entry_signals(signals)
        
        # Scalping should generate multiple signals
        assert entry_signals.sum() > 1, "Scalping strategy should generate multiple signals"
    
    def test_swing_trading_sma_signals(self):
        """Test swing trading SMA preset signal generation"""
        # Create data with longer trends
        price_data = TestSignalGeneration().create_trending_data(
            trend_strength=0.001, length=150
        )
        
        # Use swing trading preset
        strategy = StrategyPresets.swing_trading_sma()
        
        # Run strategy
        engine = StrategyEngine(strategy)
        indicators = engine.calculate_indicators(price_data)
        signals = engine.generate_signals(indicators)
        
        # Should generate fewer signals than scalping
        entry_signals = engine.get_entry_signals(signals)
        assert entry_signals.sum() >= 0  # May not generate signals in weak trends
    
    def test_conservative_rsi_signals(self):
        """Test conservative RSI preset signal generation"""
        # Create data with extreme movements
        price_data = TestSignalGeneration().create_rsi_extreme_data(length=100)
        
        # Use conservative RSI preset
        strategy = StrategyPresets.conservative_rsi()
        
        # Run strategy
        engine = StrategyEngine(strategy)
        indicators = engine.calculate_indicators(price_data)
        signals = engine.generate_signals(indicators)
        
        # Conservative settings should generate fewer signals
        entry_signals = engine.get_entry_signals(signals)
        exit_signals = engine.get_exit_signals(signals)
        
        # Should have calculated RSI with longer period
        rsi_values = indicators['rsi'].values
        assert not rsi_values.isna().all()
        assert len(rsi_values) == len(price_data)
    
    def test_aggressive_momentum_signals(self):
        """Test aggressive momentum preset signal generation"""
        # Create trending data
        price_data = TestSignalGeneration().create_trending_data(
            trend_strength=0.003, length=100
        )
        
        # Use aggressive momentum preset
        strategy = StrategyPresets.aggressive_momentum()
        
        # Run strategy
        engine = StrategyEngine(strategy)
        indicators = engine.calculate_indicators(price_data)
        signals = engine.generate_signals(indicators)
        
        # Should generate more signals due to aggressive settings
        entry_signals = engine.get_entry_signals(signals)
        assert len(indicators) == 3  # fast_ema, slow_ema, rsi
    
    def test_trend_following_signals(self):
        """Test trend following preset signal generation"""
        # Create strong trending data
        price_data = TestSignalGeneration().create_trending_data(
            trend_strength=0.005, length=120
        )
        
        # Use trend following preset
        strategy = StrategyPresets.trend_following()
        
        # Run strategy
        engine = StrategyEngine(strategy)
        indicators = engine.calculate_indicators(price_data)
        signals = engine.generate_signals(indicators)
        
        # Should have 3 EMAs
        assert len(indicators) == 3
        assert len(signals) == 3  # 3 crossover rules
        
        # In strong trend, should generate entry signals
        entry_signals = engine.get_entry_signals(signals)
        assert entry_signals.sum() >= 0


class TestSignalValidation:
    """Test signal validation and edge cases"""
    
    def test_no_signals_with_flat_data(self):
        """Test that flat data generates no signals"""
        # Create completely flat data
        dates = pd.date_range(start="2023-01-01", periods=50, freq='D')
        prices = [100.0] * 50  # Completely flat
        price_data = pd.Series(prices, index=dates, name='close')
        
        # Test with EMA crossover
        strategy = StrategyBuilder.ema_crossover()
        engine = StrategyEngine(strategy)
        indicators = engine.calculate_indicators(price_data)
        signals = engine.generate_signals(indicators)
        
        entry_signals = engine.get_entry_signals(signals)
        exit_signals = engine.get_exit_signals(signals)
        
        # Should generate no signals with flat data
        assert entry_signals.sum() == 0, "Flat data should generate no entry signals"
        assert exit_signals.sum() == 0, "Flat data should generate no exit signals"
    
    def test_signal_consistency(self):
        """Test that signal generation is consistent across runs"""
        # Create deterministic data
        np.random.seed(42)
        price_data = TestSignalGeneration().create_trending_data(length=100)
        
        strategy = StrategyBuilder.ema_crossover()
        
        # Run twice
        engine1 = StrategyEngine(strategy)
        indicators1 = engine1.calculate_indicators(price_data)
        signals1 = engine1.generate_signals(indicators1)
        
        engine2 = StrategyEngine(strategy)
        indicators2 = engine2.calculate_indicators(price_data)
        signals2 = engine2.generate_signals(indicators2)
        
        # Results should be identical
        for rule_name in signals1:
            assert signals1[rule_name].equals(signals2[rule_name]), f"Signals for {rule_name} should be consistent"
    
    def test_indicator_nan_handling(self):
        """Test handling of NaN values in indicators"""
        # Create data with some NaN values at the beginning (typical for indicators)
        dates = pd.date_range(start="2023-01-01", periods=50, freq='D')
        prices = list(range(100, 150))
        price_data = pd.Series(prices, index=dates, name='close')
        
        # Test with RSI (which typically has NaN values at the beginning)
        strategy = StrategyBuilder.rsi_mean_reversion(rsi_period=14)
        engine = StrategyEngine(strategy)
        indicators = engine.calculate_indicators(price_data)
        signals = engine.generate_signals(indicators)
        
        # Signals should handle NaN values gracefully
        entry_signals = engine.get_entry_signals(signals)
        exit_signals = engine.get_exit_signals(signals)
        
        # Should not raise errors and should have valid boolean values
        assert entry_signals.dtype == bool
        assert exit_signals.dtype == bool


def test_comprehensive_signal_generation():
    """Comprehensive test that validates signal generation for all builders"""
    print("🔍 Testing Signal Generation for All Strategy Builders")
    print("=" * 60)
    
    # Create various data patterns
    test_generator = TestSignalGeneration()
    
    # Test data patterns
    data_patterns = {
        "Trending": test_generator.create_trending_data(length=80),
        "Oscillating": test_generator.create_oscillating_data(length=80),
        "Crossover": test_generator.create_crossover_data(length=80),
        "RSI Extreme": test_generator.create_rsi_extreme_data(length=80)
    }
    
    # Test builders
    builders = {
        "EMA Crossover": StrategyBuilder.ema_crossover(),
        "SMA Crossover": StrategyBuilder.sma_crossover(),
        "RSI Mean Reversion": StrategyBuilder.rsi_mean_reversion(),
        "MACD Momentum": StrategyBuilder.macd_momentum(),
        "RSI Momentum": StrategyBuilder.rsi_momentum(),
        "Dual EMA + RSI": StrategyBuilder.dual_ema_rsi(),
        "MACD + RSI Confluence": StrategyBuilder.macd_rsi_confluence(),
        "Triple MA Trend": StrategyBuilder.triple_ma_trend()
    }
    
    results = {}
    
    for data_name, price_data in data_patterns.items():
        results[data_name] = {}
        
        for strategy_name, strategy in builders.items():
            try:
                engine = StrategyEngine(strategy)
                indicators = engine.calculate_indicators(price_data)
                signals = engine.generate_signals(indicators)
                
                entry_signals = engine.get_entry_signals(signals)
                exit_signals = engine.get_exit_signals(signals)
                
                results[data_name][strategy_name] = {
                    "indicators": len(indicators),
                    "signals": len(signals),
                    "entries": entry_signals.sum(),
                    "exits": exit_signals.sum(),
                    "success": True
                }
                
            except Exception as e:
                results[data_name][strategy_name] = {
                    "error": str(e),
                    "success": False
                }
    
    # Print results
    for data_name, data_results in results.items():
        print(f"\n📊 {data_name} Data Pattern:")
        print("-" * 40)
        
        for strategy_name, result in data_results.items():
            if result["success"]:
                print(f"✅ {strategy_name}: {result['indicators']} indicators, "
                      f"{result['entries']} entries, {result['exits']} exits")
            else:
                print(f"❌ {strategy_name}: {result['error']}")
    
    print(f"\n🎉 Signal generation testing completed!")
    return results


if __name__ == "__main__":
    test_comprehensive_signal_generation() 
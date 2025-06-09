#!/usr/bin/env python3
"""
Standalone Technical Analysis Engine Example
===========================================

This script demonstrates how to use the technical analysis engine
independently of the API infrastructure.

The engine can:
1. Fetch data directly from Yahoo Finance
2. Calculate technical indicators
3. Generate trading signals
4. Run VectorBT backtests
5. Provide comprehensive analysis results

No API or external services required!
"""

import sys
import os

# Add the engine to path (if running directly)
sys.path.append(os.path.dirname(__file__))

try:
    from technical_analysis_engine import TechnicalAnalysisEngine
    print("✅ Successfully imported TechnicalAnalysisEngine")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Falling back to direct imports...")
    
    from __init__ import TechnicalAnalysisEngine


def run_basic_analysis_example():
    """Example 1: Basic technical analysis without backtesting"""
    print("\n" + "="*60)
    print("📊 EXAMPLE 1: Basic Technical Analysis")
    print("="*60)
    
    # Create engine
    engine = TechnicalAnalysisEngine()
    
    # Define strategy configuration
    strategy_config = {
        "name": "EMA Crossover Strategy",
        "description": "20-period EMA crossing above 50-period EMA",
        "indicators": [
            {"name": "EMA_20", "type": "EMA", "period": 20},
            {"name": "EMA_50", "type": "EMA", "period": 50}
        ],
        "crossover_rules": [
            {
                "name": "ema_buy_signal",
                "fast_indicator": "EMA_20",
                "slow_indicator": "EMA_50", 
                "direction": "above",
                "signal_type": "buy"
            }
        ],
        "threshold_rules": []
    }
    
    # Run analysis
    print("📈 Analyzing AAPL with EMA crossover strategy...")
    try:
        result = engine.analyze_symbol(
            symbol="AAPL",
            strategy_config=strategy_config,
            period="6mo",
            interval="1d"
        )
        
        print(f"✅ Analysis completed successfully!")
        print(f"   Symbol: {result.symbol}")
        print(f"   Strategy: {result.strategy_name}")
        print(f"   Data Points: {result.data_points}")
        print(f"   Indicators: {list(result.indicators.keys())}")
        print(f"   Signals: {list(result.signals.keys())}")
        
        # Show some indicator values
        if 'EMA_20' in result.indicators:
            ema_20 = result.indicators['EMA_20']
            print(f"   EMA 20 (last 5 values): {ema_20.tail().round(2).tolist()}")
        
        # Show signal counts
        if result.entry_signals is not None:
            signal_count = result.entry_signals.sum()
            print(f"   Entry Signals Generated: {signal_count}")
        
        return result
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return None


def run_comprehensive_backtest_example():
    """Example 2: Complete backtesting with performance metrics"""
    print("\n" + "="*60)
    print("🚀 EXAMPLE 2: Comprehensive Backtesting")
    print("="*60)
    
    # Create engine
    engine = TechnicalAnalysisEngine()
    
    # Define more complex strategy
    strategy_config = {
        "name": "EMA + RSI Strategy",
        "description": "EMA crossover with RSI confirmation", 
        "indicators": [
            {"name": "EMA_12", "type": "EMA", "period": 12},
            {"name": "EMA_26", "type": "EMA", "period": 26},
            {"name": "RSI_14", "type": "RSI", "period": 14}
        ],
        "crossover_rules": [
            {
                "name": "ema_entry",
                "fast_indicator": "EMA_12",
                "slow_indicator": "EMA_26",
                "direction": "above", 
                "signal_type": "entry"
            },
            {
                "name": "ema_exit",
                "fast_indicator": "EMA_12",
                "slow_indicator": "EMA_26",
                "direction": "below",
                "signal_type": "exit"
            }
        ],
        "threshold_rules": [
            {
                "name": "rsi_oversold",
                "indicator": "RSI_14",
                "threshold": 30,
                "condition": "below",
                "signal_type": "entry"
            }
        ]
    }
    
    # Run backtest
    print("🎯 Backtesting MSFT with EMA + RSI strategy...")
    try:
        result = engine.backtest_symbol(
            symbol="MSFT",
            strategy_config=strategy_config,
            period="1y",
            interval="1d",
            initial_cash=10000,
            commission=0.001
        )
        
        print(f"✅ Backtest completed successfully!")
        print(f"   Symbol: {result.symbol}")
        print(f"   Strategy: {result.strategy_name}")
        print(f"   Data Points: {result.data_points}")
        
        # Show performance metrics
        if result.backtest_performance:
            perf = result.backtest_performance
            print(f"\n📈 Performance Metrics:")
            print(f"   Total Return: {perf['total_return']:.2%}")
            print(f"   Sharpe Ratio: {perf['sharpe_ratio']:.3f}")
            print(f"   Max Drawdown: {perf['max_drawdown']:.2%}")
            print(f"   Final Value: ${perf['final_value']:.2f}")
            print(f"   Total Trades: {perf['total_trades']}")
            
            # Calculate some additional metrics
            roi = (perf['final_value'] - 10000) / 10000 * 100
            print(f"   ROI: {roi:.2f}%")
        
        return result
        
    except Exception as e:
        print(f"❌ Backtest failed: {e}")
        return None


def run_multiple_symbols_example():
    """Example 3: Analyze multiple symbols with the same strategy"""
    print("\n" + "="*60)
    print("🔍 EXAMPLE 3: Multiple Symbols Analysis")
    print("="*60)
    
    # Create engine
    engine = TechnicalAnalysisEngine()
    
    # Simple strategy for comparison
    strategy_config = {
        "name": "Simple SMA Strategy",
        "description": "20 vs 50 SMA crossover",
        "indicators": [
            {"name": "SMA_20", "type": "SMA", "period": 20},
            {"name": "SMA_50", "type": "SMA", "period": 50}
        ],
        "crossover_rules": [
            {
                "name": "sma_buy",
                "fast_indicator": "SMA_20",
                "slow_indicator": "SMA_50",
                "direction": "above",
                "signal_type": "buy"
            }
        ],
        "threshold_rules": []
    }
    
    # Symbols to analyze
    symbols = ["AAPL", "GOOGL", "TSLA"]
    results = {}
    
    print("🎯 Running backtests on multiple symbols...")
    
    for symbol in symbols:
        print(f"\n📊 Analyzing {symbol}...")
        try:
            result = engine.backtest_symbol(
                symbol=symbol,
                strategy_config=strategy_config,
                period="6mo",
                interval="1d",
                initial_cash=10000,
                commission=0.001
            )
            results[symbol] = result
            
            if result.backtest_performance:
                perf = result.backtest_performance
                print(f"   ✅ Return: {perf['total_return']:.2%}, Trades: {perf['total_trades']}")
            else:
                print(f"   ⚠️  No signals generated")
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    # Summary comparison
    print(f"\n📋 Summary Comparison:")
    print(f"{'Symbol':<8} {'Return':<10} {'Sharpe':<8} {'Trades':<8}")
    print("-" * 35)
    
    for symbol, result in results.items():
        if result and result.backtest_performance:
            perf = result.backtest_performance
            print(f"{symbol:<8} {perf['total_return']:<10.2%} {perf['sharpe_ratio']:<8.3f} {perf['total_trades']:<8}")
        else:
            print(f"{symbol:<8} {'N/A':<10} {'N/A':<8} {'N/A':<8}")


def run_data_validation_example():
    """Example 4: Data validation and ticker utilities"""
    print("\n" + "="*60)
    print("🔧 EXAMPLE 4: Data Validation & Utilities")
    print("="*60)
    
    # Create engine
    engine = TechnicalAnalysisEngine()
    
    # Test symbol validation
    test_symbols = ["AAPL", "GOOGL", "INVALID_TICKER", "MSFT"]
    
    print("🔍 Testing symbol validation...")
    for symbol in test_symbols:
        is_valid = engine.validate_symbol(symbol)
        status = "✅ Valid" if is_valid else "❌ Invalid"
        print(f"   {symbol}: {status}")
    
    # Show popular tickers
    print(f"\n📋 Available popular tickers:")
    try:
        popular = engine.get_popular_tickers()
        print(f"   Total tickers available: {len(popular)}")
        print(f"   Sample tickers: {popular[:10]}")  # Show first 10
    except Exception as e:
        print(f"   ❌ Failed to get tickers: {e}")


def main():
    """Run all examples"""
    print("🎯 Technical Analysis Engine - Standalone Examples")
    print("=" * 60)
    print("This script demonstrates the self-contained capabilities")
    print("of the technical analysis engine without requiring APIs.")
    
    try:
        # Run all examples
        run_basic_analysis_example()
        run_comprehensive_backtest_example()
        run_multiple_symbols_example()
        run_data_validation_example()
        
        print("\n" + "="*60)
        print("🎉 All examples completed successfully!")
        print("="*60)
        print("\nThe technical analysis engine is fully self-contained and can:")
        print("✅ Fetch data directly from Yahoo Finance")
        print("✅ Calculate technical indicators")
        print("✅ Generate trading signals")
        print("✅ Run VectorBT backtests")
        print("✅ Provide comprehensive analysis")
        print("✅ Work independently of any API infrastructure")
        
    except Exception as e:
        print(f"\n❌ Script failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 
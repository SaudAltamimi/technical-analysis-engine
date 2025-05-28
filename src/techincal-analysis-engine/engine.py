"""
Main entry point for the Technical Analysis Strategy Framework
Demonstrates usage of the modular framework
"""

try:
    # Try relative imports first (when used as module)
    from .strategy import StrategyEngine
    from .builders import StrategyBuilder
    from .utils import StrategySerializer, create_sample_data
except ImportError:
    # Fall back to direct imports (when run as script)
    from strategy import StrategyEngine
    from builders import StrategyBuilder
    from utils import StrategySerializer, create_sample_data


def main():
    """Demonstrate the framework"""
    print("🚀 Technical Analysis Strategy Framework Demo")
    print("=" * 50)
    
    # Create sample data
    price_data = create_sample_data()
    print(f"📊 Generated {len(price_data)} days of sample data")
    
    # Build EMA crossover strategy
    strategy_def = StrategyBuilder.ema_crossover(
        name="My EMA Strategy",
        fast_period=12,
        slow_period=26
    )
    
    print(f"📈 Created strategy: {strategy_def.name}")
    print(f"📝 Description: {strategy_def.description}")
    
    # Create and run strategy
    engine = StrategyEngine(strategy_def)
    portfolio = engine.backtest(price_data, init_cash=10000)
    
    # Display results
    print(f"\n💰 Backtest Results:")
    print(f"   Total Return: {portfolio.total_return():.2%}")
    print(f"   Sharpe Ratio: {portfolio.sharpe_ratio():.2f}")
    print(f"   Max Drawdown: {portfolio.max_drawdown():.2%}")
    print(f"   Win Rate: {portfolio.trades.win_rate():.2%}")
    
    # Save strategy
    StrategySerializer.save_strategy(strategy_def, "my_strategy.json")
    print(f"\n💾 Strategy saved to my_strategy.json")


if __name__ == "__main__":
    main()

# Technical Analysis Strategy Framework

A modular, extensible framework for building and backtesting trading strategies using VectorBT.

## 🏗️ Architecture

The framework is organized into the following modules:

### Core Modules

- **`types.py`** - Core enums and type definitions
- **`config.py`** - Pydantic configuration models and validation
- **`indicators.py`** - Technical indicator implementations and factory
- **`signals.py`** - Signal generation logic
- **`strategy.py`** - Main strategy execution engine
- **`builders.py`** - Pre-built strategy patterns
- **`utils.py`** - Utility functions and serialization
- **`__init__.py`** - Package exports and initialization
- **`engine.py`** - Main entry point and example usage

## 🚀 Quick Start

### Basic Usage

```python
from technical_analysis_engine import StrategyBuilder, StrategyEngine, create_sample_data

# Create sample data
price_data = create_sample_data()

# Build a strategy
strategy = StrategyBuilder.ema_crossover(fast_period=12, slow_period=26)

# Run backtest
engine = StrategyEngine(strategy)
portfolio = engine.backtest(price_data, init_cash=10000)

# View results
print(f"Total Return: {portfolio.total_return():.2%}")
print(f"Sharpe Ratio: {portfolio.sharpe_ratio():.2f}")
```

### Custom Strategy

```python
from technical_analysis_engine import (
    StrategyDefinition, IndicatorDefinition, CrossoverRule,
    IndicatorType, EMAConfig, CrossoverDirection, SignalType
)

strategy = StrategyDefinition(
    name="Custom EMA Strategy",
    indicators=[
        IndicatorDefinition(
            name="ema_fast",
            type=IndicatorType.EMA,
            params=EMAConfig(window=10)
        ),
        IndicatorDefinition(
            name="ema_slow",
            type=IndicatorType.EMA,
            params=EMAConfig(window=20)
        )
    ],
    crossover_rules=[
        CrossoverRule(
            name="buy_signal",
            fast_indicator="ema_fast",
            slow_indicator="ema_slow",
            direction=CrossoverDirection.ABOVE,
            signal_type=SignalType.ENTRY
        )
    ]
)
```

## 📦 Module Details

### Types (`types.py`)
Defines core enums:
- `IndicatorType` - Available indicators (EMA, RSI, MACD)
- `SignalType` - Entry/exit signals
- `CrossoverDirection` - Above/below crossovers
- `ThresholdCondition` - Above/below thresholds

### Configuration (`config.py`)
Pydantic models for type-safe configuration:
- `EMAConfig`, `RSIConfig`, `MACDConfig` - Indicator parameters
- `IndicatorDefinition` - Complete indicator specification
- `CrossoverRule`, `ThresholdRule` - Trading rules
- `StrategyDefinition` - Complete strategy specification

### Indicators (`indicators.py`)
- `IndicatorProtocol` - Interface for indicators
- `CalculatedIndicator` - Immutable calculation results
- `IndicatorFactory` - Creates indicators from configurations

### Signals (`signals.py`)
- `SignalGenerator` - Generates trading signals from indicator values

### Strategy (`strategy.py`)
- `StrategyEngine` - Main execution engine that orchestrates everything

### Builders (`builders.py`)
- `StrategyBuilder` - Factory for common strategy patterns
  - `ema_crossover()` - EMA crossover strategy
  - `rsi_mean_reversion()` - RSI mean reversion strategy

### Utils (`utils.py`)
- `StrategySerializer` - Save/load strategies to/from JSON
- `create_sample_data()` - Generate test data

## 🔧 Benefits of Modular Design

1. **Separation of Concerns** - Each module has a single responsibility
2. **Easy Testing** - Individual components can be tested in isolation
3. **Extensibility** - New indicators/strategies can be added easily
4. **Maintainability** - Smaller, focused files are easier to maintain
5. **Reusability** - Components can be imported and used independently
6. **Type Safety** - Strong typing with Pydantic validation

## 📝 Usage Examples

### Running the Demo
```bash
python -m technical_analysis_engine.engine
```

### Importing Specific Components
```python
# Import just what you need
from technical_analysis_engine.strategy import StrategyEngine
from technical_analysis_engine.builders import StrategyBuilder
from technical_analysis_engine.indicators import IndicatorFactory

# Or import everything
from technical_analysis_engine import *
```

### Saving and Loading Strategies
```python
from technical_analysis_engine import StrategySerializer, StrategyBuilder

# Create and save
strategy = StrategyBuilder.rsi_mean_reversion()
StrategySerializer.save_strategy(strategy, "my_strategy.json")

# Load later
loaded_strategy = StrategySerializer.load_strategy("my_strategy.json")
```

## 🎯 Next Steps

The modular design makes it easy to:
- Add new technical indicators
- Create custom signal generation logic
- Implement new strategy patterns
- Add additional data sources
- Integrate with other trading platforms 
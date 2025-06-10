# Technical Analysis API

A FastAPI server providing real-time technical analysis for stock market data. Build and analyze custom trading strategies dynamically through a flexible API.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- [UV](https://docs.astral.sh/uv/) (recommended) or pip

### Setup & Run
```bash
make setup              # Setup core engine + API
make api               # Start API server

# Optional: Streamlit web interface
make setup-streamlit   # Setup Streamlit app (separate environment)
make streamlit        # Start Streamlit interface

# Or run both together
make dev              # Start both API and Streamlit
```

Access API documentation at `http://localhost:8000/docs`  
Access Streamlit interface at `http://localhost:8501`

## 📊 Features

- **Real-Time Data**: Yahoo Finance integration
- **Technical Indicators**: EMA, RSI, MACD, SMA, Bollinger Bands
- **Custom Strategy Creation**: Dynamic strategy definition via API
- **Backtesting**: Portfolio performance analysis with VectorBT
- **REST API**: JSON responses optimized for mobile/web apps

## API Usage

### Basic Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Create custom strategy
curl -X POST http://localhost:8000/strategies/custom \
  -H "Content-Type: application/json" \
  -d '{
    "name": "EMA_Cross",
    "symbol": "AAPL",
    "indicators": [
      {"name": "EMA_12", "type": "EMA", "params": {"window": 12}},
      {"name": "EMA_26", "type": "EMA", "params": {"window": 26}}
    ],
    "crossover_rules": [
      {"name": "entry", "fast_indicator": "EMA_12", "slow_indicator": "EMA_26", "direction": "above", "signal_type": "entry"}
    ],
    "period": "6mo"
  }'

# Backtest strategy
curl -X POST http://localhost:8000/backtest/custom/ticker \
  -H "Content-Type: application/json" \
  -d '{
    "name": "EMA_Cross_Backtest",
    "symbol": "AAPL",
    "indicators": [
      {"name": "EMA_12", "type": "EMA", "params": {"window": 12}},
      {"name": "EMA_26", "type": "EMA", "params": {"window": 26}}
    ],
    "crossover_rules": [
      {"name": "entry", "fast_indicator": "EMA_12", "slow_indicator": "EMA_26", "direction": "above", "signal_type": "entry"},
      {"name": "exit", "fast_indicator": "EMA_12", "slow_indicator": "EMA_26", "direction": "below", "signal_type": "exit"}
    ],
    "period": "1y"
  }'
```

### Standalone Python Usage

Use the technical analysis engine directly without the API:

```python
# Install the package
# pip install -e .

from technical_analysis_engine import TechnicalAnalysisEngine
from technical_analysis_engine.engine.config import (
    StrategyDefinition, IndicatorDefinition, CrossoverRule, ThresholdRule,
    EMAConfig, RSIConfig, MACDConfig
)
from technical_analysis_engine.engine.ta_types import (
    IndicatorType, SignalType, CrossoverDirection, ThresholdCondition
)

# Initialize the engine
engine = TechnicalAnalysisEngine()

# Validate a ticker
is_valid = engine.validate_symbol("AAPL")
print(f"AAPL is valid: {is_valid}")

# Create a strategy configuration
strategy = StrategyDefinition(
    name="EMA_RSI_Strategy",
    description="EMA crossover with RSI filter",
    indicators=[
        IndicatorDefinition(
            name="EMA_12",
            type=IndicatorType.EMA,
            params=EMAConfig(window=12)
        ),
        IndicatorDefinition(
            name="EMA_26", 
            type=IndicatorType.EMA,
            params=EMAConfig(window=26)
        ),
        IndicatorDefinition(
            name="RSI_14",
            type=IndicatorType.RSI,
            params=RSIConfig(window=14)
        )
    ],
    crossover_rules=[
        CrossoverRule(
            name="EMA_Entry",
            fast_indicator="EMA_12",
            slow_indicator="EMA_26",
            direction=CrossoverDirection.ABOVE,
            signal_type=SignalType.ENTRY
        ),
        CrossoverRule(
            name="EMA_Exit",
            fast_indicator="EMA_12", 
            slow_indicator="EMA_26",
            direction=CrossoverDirection.BELOW,
            signal_type=SignalType.EXIT
        )
    ],
    threshold_rules=[
        ThresholdRule(
            name="RSI_Filter",
            indicator="RSI_14",
            threshold=70,
            condition=ThresholdCondition.BELOW,
            signal_type=SignalType.ENTRY
        )
    ]
)

# Run analysis
result = engine.analyze_symbol("AAPL", strategy, period="6mo")
print(f"Generated {len(result.signals)} signals")
print(f"Analysis summary: {result.summary}")

# Run backtest
backtest = engine.backtest_symbol("AAPL", strategy, period="1y")
print(f"Total return: {backtest.performance['total_return']:.2%}")
print(f"Sharpe ratio: {backtest.performance['sharpe_ratio']:.2f}")
print(f"Max drawdown: {backtest.performance['max_drawdown']:.2%}")
print(f"Total trades: {len(backtest.trades)}")
```

## 🔧 Development

```bash
make setup              # Install dependencies (UV environment)
make setup-streamlit   # Install Streamlit dependencies (pip environment)
make api               # Start API server
make streamlit        # Start Streamlit web interface
make dev              # Start both API and Streamlit
make test             # Run tests
make clean            # Clean temp files
make help             # Show all available commands
```

## 📂 Project Structure

```
technical-analysis-prod/
├── src/
│   ├── technical_analysis_engine/    # Core analysis engine (standalone package)
│   │   ├── engine/                   # Core engine components
│   │   │   ├── core.py              # Main TechnicalAnalysisEngine class
│   │   │   ├── strategy.py          # Strategy execution engine
│   │   │   ├── indicators.py        # Technical indicators (EMA, RSI, MACD, SMA)
│   │   │   ├── signals.py           # Signal generation logic
│   │   │   ├── config.py            # Strategy configuration models
│   │   │   ├── builders.py          # Strategy builders and factories
│   │   │   └── ta_types.py          # Type definitions and enums
│   │   ├── __init__.py              # Package exports
│   │   ├── data_service.py          # Yahoo Finance integration
│   │   ├── ticker_config.py         # Ticker management and validation
│   │   ├── tickers.yaml             # Curated ticker lists
│   │   └── utils.py                 # Utility functions
│   ├── app/                          # FastAPI REST API (optional)
│   │   ├── main.py                  # API endpoints and routing
│   │   ├── models.py                # API request/response models
│   │   └── services.py              # API business logic
│   └── streamlit_app/               # Streamlit web interface (optional)
│       ├── streamlit_app.py         # Main Streamlit application
│       └── pages/                   # Strategy builder and tester pages
├── docs/                            # Documentation
│   ├── README_API.md               # API reference guide
│   ├── README_iOS.md               # iOS developer integration guide
│   ├── ARCHITECTURE.md             # System architecture
│   └── DIRECTORY_STRUCTURE.md      # Detailed project structure
├── tests/                           # Test suite
├── pyproject.toml                   # Package configuration
├── Makefile                        # Development automation
└── README.md                       # This file
```

### Component Overview

- **Technical Analysis Engine**: Self-contained Python package for technical analysis
- **FastAPI Application**: REST API wrapper around the core engine
- **Streamlit Interface**: Web UI for interactive strategy building and testing
- **Documentation**: Comprehensive guides for different use cases
- **Tests**: Unit tests and integration examples

## 📖 Documentation

- **API Reference**: `/docs/README_API.md`
- **iOS Developer Guide**: `/docs/README_iOS.md`
- **Interactive Docs**: `http://localhost:8000/docs` (when server running)
- **Architecture**: `/docs/ARCHITECTURE.md`
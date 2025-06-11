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
# Strategy Structure Explanation:
# The API uses a two-step approach for maximum flexibility:
#
# 1. "indicators" section - Define which technical indicators to calculate
#    Each indicator gets a unique name (e.g., "EMA_12", "EMA_26") that you choose
#    
# 2. "crossover_rules" section - Define trading logic using the indicator names
#    Rules reference indicators by their names: "fast_indicator": "EMA_12", "slow_indicator": "EMA_26"
#    
# This design allows multiple rules to reuse the same indicators and makes strategies more readable

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

# Response:
{
  "status": "success",
  "message": "Custom strategy 'EMA_Cross' created and analyzed for AAPL",
  "data": {
    "strategy": {
      "name": "EMA_Cross",
      "description": "",
      "indicators": [
        {
          "name": "EMA_12",
          "type": "EMA",
          "params": {"window": 12}
        },
        {
          "name": "EMA_26", 
          "type": "EMA",
          "params": {"window": 26}
        }
      ],
      "crossover_rules": [
        {
          "name": "entry",
          "fast_indicator": "EMA_12",
          "slow_indicator": "EMA_26",
          "direction": "above",
          "signal_type": "entry"
        }
      ],
      "threshold_rules": []
    },
    "analysis": {
      "strategy_name": "EMA_Cross",
      "symbol": "AAPL",
      "data_info": {
        "symbol": "AAPL",
        "data_points": 130,
        "start_date": "2024-12-11T00:00:00-05:00",
        "end_date": "2025-06-10T00:00:00-04:00",
        "period": "6mo",
        "interval": "1d"
      },
      "price_data": [
        {
          "timestamp": "2024-12-27T00:00:00-05:00",
          "open": 263.0,
          "high": 263.54,
          "low": 262.11,
          "close": 263.0,
          "volume": 17296100
        }
        // ... additional OHLC data points for charting
      ],
      "indicators": [
        {
          "name": "EMA_12",
          "type": "EMA",
          "params": {"window": 12},
          "values": [
            {"timestamp": "2024-12-27T00:00:00-05:00", "value": 252.58},
            {"timestamp": "2024-12-30T00:00:00-05:00", "value": 252.42}
            // ... complete EMA_12 time series
          ]
        },
        {
          "name": "EMA_26",
          "type": "EMA", 
          "params": {"window": 26},
          "values": [
            {"timestamp": "2025-01-21T00:00:00-05:00", "value": 240.64},
            {"timestamp": "2025-01-22T00:00:00-05:00", "value": 239.36}
            // ... complete EMA_26 time series
          ]
        }
      ],
      "signals": [
        {
          "timestamp": "2025-02-18T00:00:00-05:00",
          "signal": true,
          "signal_type": "entry",
          "rule_name": "entry",
          "price": 244.15
        },
        {
          "timestamp": "2025-05-15T00:00:00-04:00",
          "signal": true,
          "signal_type": "entry",
          "rule_name": "entry",
          "price": 211.45
        }
      ],
      "entry_signals": [
        {
          "timestamp": "2025-02-18T00:00:00-05:00",
          "signal": true,
          "signal_type": "entry",
          "rule_name": "combined_entry",
          "price": 244.15
        },
        {
          "timestamp": "2025-05-15T00:00:00-04:00",
          "signal": true,
          "signal_type": "entry",
          "rule_name": "combined_entry", 
          "price": 211.45
        }
      ],
      "exit_signals": []
    },
    "rules_summary": {
      "crossover_rules": 1,
      "threshold_rules": 0,
      "total_rules": 1
    }
  },
  "timestamp": "2025-06-11T08:14:45.126328"
}

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
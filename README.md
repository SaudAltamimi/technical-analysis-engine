# Technical Analysis API

A professional-grade FastAPI server providing real-time technical analysis for stock market data. **Build and analyze custom trading strategies dynamically through a flexible API.** Perfect for iOS trading applications and financial analytics platforms.

## 🚀 Quick Start

```bash
# Complete setup and launch
make setup              # Setup core engine + API
make setup-streamlit    # Setup Streamlit app  
make dev               # Start both API and Streamlit

# Access applications
open http://localhost:8000/docs    # API documentation
open http://localhost:8501         # Streamlit interface
```

### 🏗️ Separated Architecture
This project has **clean separation of concerns**:
- **Core Engine + API**: Technical analysis engine with FastAPI (uv environment)
- **Streamlit Frontend**: Standalone web UI (pip environment, separate dependencies)

### 1. Setup Core Engine + API
```bash
# Install core engine with vectorbt + FastAPI dependencies
make setup

# Start API server
make api
```

### 2. Setup Streamlit Frontend (Optional, Separate)
```bash
# Install Streamlit app dependencies (separate pip environment)  
make setup-streamlit

# Start Streamlit frontend
make streamlit
```

### 3. Full Development Setup
```bash
# Setup both environments
make setup && make setup-streamlit

# Start both API + Streamlit
make dev

# Test API
open http://localhost:8000/docs
```

## 📊 Features

- ✅ **Real-Time Data**: Yahoo Finance integration
- ✅ **Technical Indicators**: EMA, RSI, MACD, Bollinger Bands
- ✅ **Trading Signals**: Entry/exit signal generation
- ✅ **Backtesting**: Portfolio performance analysis
- ✅ **Dynamic Strategy Definition & Rules**: Create custom strategies via API
- ✅ **iOS Ready**: JSON API optimized for mobile apps
- ✅ **Interactive Visualizations**: Plotly-based charts

## 🔧 Core Components

### API Server (`/src/`)
FastAPI application with:
- Real-time stock data endpoints
- **Dynamic strategy creation and analysis**
- Backtesting capabilities
- iOS-optimized JSON responses

### Documentation (`/docs/`)
Comprehensive documentation and examples:
- **Architecture** - System design and component relationships
- **API Documentation** - Complete endpoint reference and usage examples
- **Directory Structure** - Project organization guide
- **Examples** - Usage examples available through the Streamlit application

## 📱 iOS Integration

Perfect for iOS trading apps:

```swift
// Example iOS integration
let api = TechnicalAnalysisAPI(baseURL: "http://localhost:8000")

// Get EMA analysis
let analysis = try await api.createEMAStrategy(
    symbol: "AAPL",
    period: "1y",
    fastPeriod: 12,
    slowPeriod: 26
)

// Process indicators for charts
for indicator in analysis.indicators {
    plotChart(data: indicator.values)
}
```

## 📈 Example Usage

### API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Validate ticker
curl http://localhost:8000/tickers/AAPL/validate

# EMA crossover analysis (quick strategy)
curl -X POST http://localhost:8000/strategies/ema-crossover \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "period": "1y", "fast_period": 12, "slow_period": 26}'

# Create and analyze a CUSTOM dynamic strategy
curl -X POST http://localhost:8000/strategies/custom \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MyCustomStrategy",
    "symbol": "MSFT",
    "description": "EMA Cross + RSI Thresholds",
    "indicators": [
      {"name": "EMA_12", "type": "EMA", "params": {"window": 12}},
      {"name": "EMA_26", "type": "EMA", "params": {"window": 26}},
      {"name": "RSI_14", "type": "RSI", "params": {"window": 14}}
    ],
    "crossover_rules": [
      {"name": "EMA_Cross_Buy", "fast_indicator": "EMA_12", "slow_indicator": "EMA_26", "direction": "above", "signal_type": "buy"}
    ],
    "threshold_rules": [
      {"name": "RSI_Oversold", "indicator": "RSI_14", "threshold": 30, "condition": "below", "signal_type": "buy"}
    ],
    "period": "6mo",
    "interval": "1d"
  }'
```

### Python Integration
```python
import requests
import json

API_BASE_URL = "http://localhost:8000"

# Example: Create and analyze a CUSTOM dynamic strategy
custom_strategy_payload = {
    "name": "PythonDynamicStrategy",
    "symbol": "GOOGL",
    "description": "Example from README",
    "indicators": [
      {"name": "SMA_20", "type": "SMA", "params": {"window": 20}},
      {"name": "SMA_50", "type": "SMA", "params": {"window": 50}}
    ],
    "crossover_rules": [
      {"name": "SMA_Cross_Buy", "fast_indicator": "SMA_20", "slow_indicator": "SMA_50", "direction": "above", "signal_type": "buy"}
    ],
    "threshold_rules": [],
    "period": "1y",
    "interval": "1d"
}

try:
    print(f"\nCreating and analyzing custom strategy for {custom_strategy_payload['symbol']}...")
    response = requests.post(
        f"{API_BASE_URL}/strategies/custom",
        json=custom_strategy_payload,
        headers={'Content-Type': 'application/json'}
    )
    response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
    
    api_result = response.json()
    analysis_summary = api_result['data']['analysis']['summary'] # Assuming summary exists
    signals_count = len(api_result['data']['analysis'].get('signals', []))
    
    print("Custom strategy analysis successful!")
    print(f"  Generated {signals_count} signals.")
    # You can further process api_result['data']['analysis'] for detailed results
    
except requests.exceptions.RequestException as e:
    print(f"Error during API request: {e}")
except KeyError as e:
    print(f"Error processing API response structure: Missing key {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")


# Example: Using a quick strategy endpoint (EMA crossover)
ema_strategy_payload = {
    "symbol": "AAPL",
    "period": "1y",
    "fast_period": 12,
    "slow_period": 26
}

try:
    print(f"\nAnalyzing EMA crossover strategy for {ema_strategy_payload['symbol']}...")
    response = requests.post(
        f"{API_BASE_URL}/strategies/ema-crossover",
        json=ema_strategy_payload,
        headers={'Content-Type': 'application/json'}
    )
    response.raise_for_status()
    
    api_result = response.json()
    strategy_name = api_result['data']['strategy']['name']
    analysis_result = api_result['data']['analysis']
    ema_signals_count = len(analysis_result.get('signals', []))
    
    print(f"Quick strategy analysis successful! ('{strategy_name}')")
    print(f"  Generated {ema_signals_count} signals.")

except requests.exceptions.RequestException as e:
    print(f"Error during API request: {e}")
except KeyError as e:
    print(f"Error processing API response structure: Missing key {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
```

## 📊 Example Results

Recent GOOGL analysis (1 year):
- **Price Range**: $144.70 - $206.14
- **Entry Signals**: 4 buy opportunities
- **Exit Signals**: 4 sell opportunities  
- **Data Points**: 250 trading days
- **Indicators**: Fast EMA (12), Slow EMA (26)

**Dynamic Strategy Example (MSFT):**
- Strategy defined with EMA 12, EMA 26, and RSI 14 indicators.
- Includes a crossover rule for EMA 12 crossing above EMA 26 (Buy signal).
- Includes a threshold rule for RSI 14 being below 30 (Buy signal).
- Results include generated signals based on these dynamic rules.

## 🎯 Use Cases

### For iOS Developers
1. Review API documentation in `/docs/README_API.md`
2. Use the FastAPI interactive docs at `http://localhost:8000/docs`
3. Test with the Streamlit application to see examples in action

### For API Testing
1. Use the Streamlit application to create and test dynamic strategies interactively
2. View generated charts and analysis through the web interface
3. Check analysis summaries via the API endpoints

### For Technical Analysis
1. Use the core engine directly for standalone analysis
2. Explore usage patterns through unit tests in `/tests/`
3. Compare API vs direct integration approaches
4. **Leverage the API for flexible, on-the-fly strategy experimentation**

## 📂 Project Structure

```
technical-analysis-prod/
├── src/                        # Source code
│   ├── technical_analysis_engine/  # Core analysis engine (main package)
│   ├── app/                   # FastAPI application (optional)
│   └── streamlit_app/         # Streamlit interface (optional)
├── tests/                      # Test suite with examples
├── docs/                       # Documentation
├── pyproject.toml              # Package configuration  
├── Makefile                   # Development automation
└── README.md                  # This file
```

## 🔧 Development

### Setup and Run
```bash
# Setup core engine + API
make setup

# Setup Streamlit app (separate)
make setup-streamlit

# Start both API and Streamlit
make dev

# Or start individually
make api        # FastAPI server
make streamlit  # Streamlit app
```

### Run Tests
```bash
make test
# or
cd tests && python run_tests.py
```

### Project Commands
```bash
make help       # Show all available commands
make status     # Check service status
make clean      # Clean temporary files
```

## 📖 Documentation

- **API Reference**: `/docs/README_API.md`
- **Architecture**: `/docs/ARCHITECTURE.md`  
- **Directory Structure**: `/docs/DIRECTORY_STRUCTURE.md`
- **Interactive Docs**: `http://localhost:8000/docs` (when API server running)
- **Test Examples**: Available through the Streamlit application

## 🎉 Ready for Production

This project provides:
- Self-contained technical analysis engine
- Optional FastAPI backend for API integration
- Optional Streamlit frontend for interactive use
- Comprehensive test suite
- Clean dependency architecture
- Professional technical indicators

Perfect for building custom trading applications! 📱💹 
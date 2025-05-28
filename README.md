# Technical Analysis API

A professional-grade FastAPI server providing real-time technical analysis for stock market data. **Build and analyze custom trading strategies dynamically through a flexible API.** Perfect for iOS trading applications and financial analytics platforms.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
uv sync
```

### 2. Start API Server
```bash
python start_api.py
# or
uvicorn src.app.main:app --host 0.0.0.0 --port 8001
```

### 3. Test API
```bash
# Run comprehensive tests
python test_api.py

# Or visit interactive docs
open http://localhost:8001/docs
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

### Examples & Documentation (`/examples/`)
Comprehensive examples organized by use case:
- **API Integration** - Complete integration examples
- **iOS Development** - Swift templates and documentation  
- **Visualizations** - Interactive charts and analysis
- **Documentation** - API reference and guides

## 📱 iOS Integration

Perfect for iOS trading apps:

```swift
// Example iOS integration
let api = TechnicalAnalysisAPI(baseURL: "http://localhost:8001")

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
curl http://localhost:8001/health

# Validate ticker
curl http://localhost:8001/tickers/AAPL/validate

# EMA crossover analysis (quick strategy)
curl -X POST http://localhost:8001/strategies/ema-crossover \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "period": "1y", "fast_period": 12, "slow_period": 26}'

# Create and analyze a CUSTOM dynamic strategy
curl -X POST http://localhost:8001/strategies/custom \
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

API_BASE_URL = "http://localhost:8001"

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
1. Review `/examples/documentation/ios_api_documentation.md`
2. Use `/examples/ios_development/ios_integration.swift` template
3. Test with examples in `/examples/api_integration/` and `/examples/api_strategy_examples/`

### For API Testing
1. Run examples in `/examples/api_strategy_examples/` to see dynamic strategy creation and visualization.
2. View generated charts in `/examples/api_strategy_examples/`.
3. Check analysis summaries.

### For Technical Analysis
1. Study `/examples/engine_examples/real_data_example.py`.
2. Explore direct engine usage patterns.
3. Compare API vs direct integration approaches.
4. **Leverage the API for flexible, on-the-fly strategy experimentation.**

## 📂 Project Structure

```
technical-analysis-prod/
├── src/                        # FastAPI application
│   ├── app/                   # API endpoints and services
│   └── techincal-analysis-engine/  # Core analysis engine
├── examples/                   # Organized examples and documentation
│   ├── api_integration/       # General API usage examples
│   ├── api_strategy_examples/ # Examples demonstrating dynamic strategy creation via API
│   ├── ios_development/       # Swift templates
│   ├── visualizations/        # Generated charts (could consolidate into api_strategy_examples)
│   ├── documentation/         # API reference
│   ├── engine_examples/       # Direct engine usage
│   └── analysis_results/      # Example outputs
├── start_api.py               # Quick server start
├── test_api.py               # Comprehensive tests
└── README_API.md             # Detailed API documentation
```

## 🔧 Development

### Run Tests
```bash
python test_api.py
```

### Generate Visualizations
```bash
python examples/api_integration/enhanced_api_visualization.py
```

### iOS Development
```bash
# Start API server
python start_api.py

# Review iOS documentation
open examples/documentation/ios_api_documentation.md

# Use Swift template
open examples/ios_development/ios_integration.swift
```

## 📖 Documentation

- **API Reference**: `/examples/documentation/ios_api_documentation.md`
- **Examples Guide**: `/examples/README.md`
- **Detailed API Docs**: `README_API.md`
- **Interactive Docs**: `http://localhost:8001/docs` (when server running)
- **Dynamic Strategy Examples**: `/examples/api_strategy_examples/`

## 🎉 Ready for Production

This API is production-ready with:
- Real market data integration
- Professional technical indicators
- Comprehensive error handling
- iOS-optimized responses
- Interactive visualizations
- Complete documentation

Perfect for building professional trading applications! 📱💹 
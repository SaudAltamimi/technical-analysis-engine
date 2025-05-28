# Technical Analysis API - iOS Integration Guide

## Overview
This FastAPI server provides real-time technical analysis for stock market data. Perfect for iOS trading apps that need professional-grade technical indicators and backtesting.

**Base URL**: `http://localhost:8001`

## Quick Start Example
```python
# Python example from api_integration_example.py
# Shows the exact HTTP requests your iOS app needs to make

import requests

api_url = "http://localhost:8001"

# 1. Health Check
response = requests.get(f"{api_url}/health")
print(response.json())  # {"status": "healthy", "message": "API is running"}

# 2. Validate Ticker
response = requests.get(f"{api_url}/tickers/AAPL/validate")
print(response.json())  # {"status": "success", "data": {"is_valid": true, "message": "Symbol is valid"}}

# 3. Get Company Info
response = requests.get(f"{api_url}/tickers/AAPL/info")
print(response.json())  # Company details: name, sector, industry, market cap

# 4. Create EMA Strategy
request_data = {
    "name": "AAPL EMA Strategy", 
    "symbol": "AAPL",
    "period": "1y",
    "fast_period": 12,
    "slow_period": 26
}
response = requests.post(f"{api_url}/strategies/ema-crossover", json=request_data)
analysis = response.json()["data"]["analysis"]  # Full analysis with indicators and signals
```

## API Endpoints Reference

### 1. Health Check
**GET** `/health`

Check if the API server is running.

**Response:**
```json
{
  "status": "healthy",
  "message": "Technical Analysis API is running",
  "timestamp": "2024-12-19T..."
}
```

### 2. Available Periods
**GET** `/periods`

Get available time periods and intervals for data fetching.

**Response:**
```json
{
  "status": "success",
  "data": {
    "periods": ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
    "intervals": ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
  }
}
```

### 3. Ticker Validation
**GET** `/tickers/{symbol}/validate`

Validate if a ticker symbol exists and has data.

**Parameters:**
- `symbol` (path): Stock symbol (e.g., "AAPL", "GOOGL", "MSFT")

**Response:**
```json
{
  "status": "success",
  "data": {
    "is_valid": true,
    "message": "Symbol is valid and has data"
  }
}
```

### 4. Company Information
**GET** `/tickers/{symbol}/info`

Get detailed company information for a ticker.

**Response:**
```json
{
  "status": "success",
  "data": {
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "sector": "Technology",
    "industry": "Consumer Electronics",
    "currency": "USD",
    "exchange": "NASDAQ",
    "market_cap": 3500000000000,
    "description": "Apple Inc. designs, manufactures..."
  }
}
```

### 5. EMA Crossover Strategy
**POST** `/strategies/ema-crossover`

Create and analyze an EMA (Exponential Moving Average) crossover strategy.

**Request Body:**
```json
{
  "name": "AAPL EMA Strategy",
  "description": "Optional description",
  "symbol": "AAPL",
  "period": "1y",
  "interval": "1d",
  "fast_period": 12,
  "slow_period": 26
}
```

**Response:**
```json
{
  "status": "success",
  "message": "EMA crossover strategy analysis completed",
  "data": {
    "strategy": { /* Strategy definition */ },
    "analysis": {
      "strategy_name": "AAPL EMA Strategy",
      "symbol": "AAPL",
      "data_info": {
        "symbol": "AAPL",
        "data_points": 250,
        "start_date": "2024-05-28T00:00:00-04:00",
        "end_date": "2025-05-27T00:00:00-04:00",
        "price_range": [150.25, 195.89]
      },
      "indicators": [
        {
          "name": "ema_fast",
          "type": "EMA",
          "params": {"window": 12},
          "values": [
            {"timestamp": "2024-06-12T00:00:00-04:00", "value": 174.89},
            {"timestamp": "2024-06-13T00:00:00-04:00", "value": 175.23}
            /* ... more data points */
          ]
        },
        {
          "name": "ema_slow",
          "type": "EMA", 
          "params": {"window": 26},
          "values": [/* timestamp-value pairs */]
        }
      ],
      "entry_signals": [
        {
          "timestamp": "2024-09-27T00:00:00-04:00",
          "signal": true,
          "signal_type": "entry",
          "rule_name": "combined_entry"
        }
      ],
      "exit_signals": [
        {
          "timestamp": "2024-07-24T00:00:00-04:00", 
          "signal": true,
          "signal_type": "exit",
          "rule_name": "combined_exit"
        }
      ]
    }
  }
}
```

### 6. RSI Strategy
**POST** `/strategies/rsi`

Create and analyze an RSI (Relative Strength Index) strategy.

**Request Body:**
```json
{
  "name": "AAPL RSI Strategy",
  "symbol": "AAPL",
  "period": "6mo",
  "interval": "1d",
  "rsi_period": 14,
  "oversold_threshold": 30,
  "overbought_threshold": 70
}
```

**Response:** Similar structure to EMA strategy, but with RSI indicator data.

### 7. Multi-EMA Strategy
**POST** `/strategies/multi-ema`

Create a strategy with multiple EMA periods for complex crossover analysis.

**Request Body:**
```json
{
  "name": "AAPL Multi-EMA Strategy",
  "symbol": "AAPL", 
  "period": "1y",
  "ema_periods": [10, 20, 50]
}
```

### 8. Custom Strategy
**POST** `/strategies/custom?name=Strategy&symbol=AAPL&period=1y`

Create a custom strategy with multiple indicators.

**Query Parameters:**
- `name`: Strategy name
- `symbol`: Stock symbol
- `description`: Optional description
- `period`: Time period
- `interval`: Data interval (default: "1d")

**Request Body (JSON array of indicators):**
```json
[
  {
    "name": "ema_short",
    "type": "EMA",
    "params": {"window": 10}
  },
  {
    "name": "rsi_momentum", 
    "type": "RSI",
    "params": {"window": 14}
  }
]
```

### 9. Backtesting
**POST** `/backtest/ticker`

Run backtesting on a strategy with real market data.

**Request Body:**
```json
{
  "strategy": {
    "name": "Backtest Strategy",
    "description": "EMA crossover for backtesting",
    "indicators": [
      {"name": "ema_fast", "type": "EMA", "params": {"window": 12}},
      {"name": "ema_slow", "type": "EMA", "params": {"window": 26}}
    ],
    "crossover_rules": [
      {
        "name": "ema_cross_entry",
        "fast_indicator": "ema_fast",
        "slow_indicator": "ema_slow", 
        "direction": "above",
        "signal_type": "entry"
      }
    ],
    "threshold_rules": []
  },
  "ticker": {
    "symbol": "AAPL",
    "period": "1y",
    "interval": "1d"
  },
  "params": {
    "initial_cash": 10000,
    "commission": 0.001
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_return": 0.0682,
    "sharpe_ratio": 0.51,
    "max_drawdown": -0.1816,
    "win_rate": 0.75,
    "total_trades": 4,
    "final_value": 10682.46
  }
}
```

## iOS Integration Guide

### Recommended Workflow

1. **App Startup**: Check API health
2. **Ticker Input**: Validate symbols as user types
3. **Company Display**: Fetch and cache company info
4. **Strategy Selection**: Let user choose EMA, RSI, or Custom
5. **Analysis**: Call appropriate strategy endpoint  
6. **Chart Rendering**: Process indicators and signals for display
7. **Performance**: Optional backtesting for strategy evaluation

### iOS Code Structure

```swift
// Example iOS integration structure
class TechnicalAnalysisAPI {
    let baseURL = "http://localhost:8001"
    
    func healthCheck() async throws -> HealthResponse
    func validateTicker(_ symbol: String) async throws -> ValidationResponse  
    func getCompanyInfo(_ symbol: String) async throws -> CompanyInfo
    func createEMAStrategy(_ request: EMARequest) async throws -> AnalysisResponse
    func runBacktest(_ request: BacktestRequest) async throws -> BacktestResult
}

struct AnalysisResponse {
    let strategy: String
    let symbol: String
    let dataInfo: DataInfo
    let indicators: [Indicator]
    let entrySignals: [Signal]
    let exitSignals: [Signal]
}

struct Indicator {
    let name: String
    let type: String
    let params: [String: Any]
    let values: [DataPoint]
}

struct DataPoint {
    let timestamp: Date
    let value: Double
}
```

### Chart Integration Tips

1. **Indicator Data**: Extract `indicators` array from API response
2. **Time Series**: Each indicator has `values` array with timestamp-value pairs
3. **Signal Markers**: Use `entry_signals` and `exit_signals` for buy/sell markers
4. **Date Parsing**: All timestamps are ISO format with timezone info
5. **Performance**: Cache data and update incrementally when possible

### Error Handling

All endpoints return consistent error format:
```json
{
  "status": "error",
  "message": "Detailed error description",
  "timestamp": "2024-12-19T..."
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid parameters)
- `404`: Ticker not found
- `422`: Validation error
- `500`: Server error

### Performance Tips

1. **Caching**: Cache company info and frequently used analysis results
2. **Async Calls**: Use async/await for all API calls
3. **Batching**: Group related requests when possible
4. **Error Recovery**: Implement retry logic for network failures
5. **Data Validation**: Validate ticker symbols before API calls

## Testing

Run the complete API integration example:
```bash
python examples/api_integration_example.py
```

This demonstrates all endpoints and shows exactly what requests to make from iOS.

## Support

- **API Server**: Start with `uvicorn src.app.main:app --host 0.0.0.0 --port 8001`
- **Documentation**: Interactive docs at `http://localhost:8001/docs`
- **Health Check**: Always available at `http://localhost:8001/health` 
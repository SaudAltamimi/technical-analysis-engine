# Technical Analysis FastAPI Server

A RESTful API server that exposes the technical analysis engine with **automatic Yahoo Finance data fetching** for easy integration with mobile applications, particularly iOS apps using Swift.

## 🚀 New Ticker-Based Features

- **📊 Automatic Data Fetching**: Just provide a ticker symbol (e.g., AAPL, GOOGL) - the API fetches data automatically
- **🎯 Real Market Data**: Uses Yahoo Finance for up-to-date market data
- **📱 iOS-Optimized**: Perfect for mobile app integration with simple ticker requests
- **⚡ Fast & Easy**: No need to manage raw price data - just symbols and time periods

## Features

- 🚀 **Dynamic Indicator Creation**: Support for multiple EMA, RSI, and MACD indicators
- 📊 **Flexible Strategy Building**: Create crossover and threshold-based trading rules
- 📱 **iOS-Optimized**: API responses designed for easy Swift integration
- 🔄 **Real-time Analysis**: Calculate indicators and generate signals from Yahoo Finance data
- 📈 **Backtesting**: Test strategies with performance metrics on real market data
- ⚡ **Fast Performance**: Built with FastAPI for high-performance async operations
- 📚 **Auto-documentation**: Interactive API docs with Swagger UI
- 🎯 **Ticker Validation**: Validate ticker symbols before analysis

## Quick Start

### 1. Installation

Install the package with API dependencies:

```bash
# Install with API dependencies
pip install -e ".[api]"

# Or install all dependencies
pip install -e ".[all]"
```

### 2. Start the Server

```bash
# Using uvicorn directly
uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload

# Or using the startup script
python start_api.py
```

### 3. Access the API

- **API Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check

```http
GET /health
```

Check if the API is running and healthy.

### 🎯 Ticker-Based Analysis (Recommended)

#### Quick EMA Strategy

```http
POST /strategies/ema-crossover
```

Create and analyze an EMA crossover strategy with real market data.

**Example Request:**
```json
{
  "name": "Apple EMA Strategy",
  "description": "12/26 EMA crossover for AAPL",
  "symbol": "AAPL",
  "period": "1y",
  "interval": "1d",
  "fast_period": 12,
  "slow_period": 26
}
```

**Example Response:**
```json
{
  "status": "success",
  "message": "EMA crossover strategy created and analyzed for AAPL",
  "data": {
    "analysis": {
      "strategy_name": "Apple EMA Strategy",
      "symbol": "AAPL",
      "data_info": {
        "symbol": "AAPL",
        "data_points": 252,
        "start_date": "2023-01-01T00:00:00",
        "end_date": "2024-01-01T00:00:00",
        "price_range": [150.25, 198.75]
      },
      "indicators": [...],
      "entry_signals": [...],
      "exit_signals": [...]
    }
  }
}
```

#### Multiple EMA Strategy

```http
POST /strategies/multi-ema
```

Create a strategy with multiple EMA indicators and dynamic crossover rules.

**Example Request:**
```json
{
  "name": "Google Triple EMA",
  "description": "5/20/50 EMA multiple crossovers",
  "symbol": "GOOGL",
  "period": "2y",
  "interval": "1d",
  "ema_periods": [5, 20, 50]
}
```

#### RSI Strategy

```http
POST /strategies/rsi
```

Create an RSI-based strategy with overbought/oversold thresholds.

**Example Request:**
```json
{
  "name": "Tesla RSI Strategy",
  "description": "RSI 30/70 strategy",
  "symbol": "TSLA",
  "period": "6mo",
  "interval": "1d",
  "rsi_period": 14,
  "oversold_threshold": 30,
  "overbought_threshold": 70
}
```

### 📈 Advanced Ticker Analysis

#### Custom Analysis with Ticker

```http
POST /analyze/ticker
```

Perform custom technical analysis using ticker symbol.

**Example Request:**
```json
{
  "strategy": {
    "name": "Custom Strategy",
    "description": "Custom indicators with MSFT",
    "indicators": [
      {
        "name": "ema_fast",
        "type": "EMA",
        "params": {"window": 12}
      },
      {
        "name": "ema_slow",
        "type": "EMA",
        "params": {"window": 26}
      }
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
    "symbol": "MSFT",
    "period": "1y",
    "interval": "1d"
  }
}
```

#### Custom Date Range Analysis

```http
POST /analyze/date-range
```

Analyze with specific start and end dates.

**Example Request:**
```json
{
  "strategy": { /* strategy definition */ },
  "ticker": {
    "symbol": "NVDA",
    "start_date": "2023-01-01T00:00:00Z",
    "end_date": "2023-12-31T23:59:59Z",
    "interval": "1d"
  }
}
```

### 📊 Backtesting with Tickers

#### Ticker Backtesting

```http
POST /backtest/ticker
```

Backtest a strategy using real market data.

**Example Request:**
```json
{
  "strategy": { /* strategy definition */ },
  "ticker": {
    "symbol": "AMZN",
    "period": "2y",
    "interval": "1d"
  },
  "params": {
    "initial_cash": 10000,
    "commission": 0.001
  }
}
```

**Example Response:**
```json
{
  "status": "success",
  "message": "Backtest completed for AMZN",
  "data": {
    "total_return": 0.15,
    "sharpe_ratio": 1.2,
    "max_drawdown": -0.08,
    "win_rate": 0.65,
    "total_trades": 25,
    "final_value": 11500.0
  }
}
```

### 🎯 Ticker Information

#### Get Ticker Info

```http
GET /tickers/{symbol}/info
```

Get detailed information about a stock ticker.

**Example Response:**
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
    "market_cap": 3000000000000,
    "description": "Apple Inc. designs, manufactures, and markets smartphones..."
  }
}
```

#### Validate Ticker

```http
GET /tickers/{symbol}/validate
```

Check if a ticker symbol is valid and has data.

**Example Response:**
```json
{
  "status": "success",
  "data": {
    "symbol": "AAPL",
    "is_valid": true,
    "message": "Symbol is valid and has data"
  }
}
```

### 🛠️ Utility Endpoints

#### Available Periods

```http
GET /periods
```

Get available time periods and intervals.

**Example Response:**
```json
{
  "status": "success",
  "data": {
    "periods": ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
    "intervals": ["1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"],
    "descriptions": {
      "1y": "1 Year",
      "1d": "1 Day",
      "6mo": "6 Months"
    }
  }
}
```

#### Indicator Types

```http
GET /indicators/types
```

Get available indicator types.

## iOS Integration

### 🍎 Swift Models

The API is designed to work seamlessly with Swift's `Codable` protocol:

```swift
struct EMAStrategyRequest: Codable {
    let name: String
    let description: String?
    let symbol: String
    let period: Period
    let interval: Interval
    let fastPeriod: Int
    let slowPeriod: Int
    
    enum CodingKeys: String, CodingKey {
        case name, description, symbol, period, interval
        case fastPeriod = "fast_period"
        case slowPeriod = "slow_period"
    }
}

enum Period: String, Codable, CaseIterable {
    case oneDay = "1d"
    case oneMonth = "1mo"
    case sixMonths = "6mo"
    case oneYear = "1y"
    case twoYears = "2y"
    case fiveYears = "5y"
    case max = "max"
}

struct AnalysisResult: Codable {
    let strategyName: String
    let symbol: String
    let dataInfo: DataFetchResult
    let indicators: [IndicatorResult]
    let entrySignals: [SignalPoint]
    let exitSignals: [SignalPoint]
}
```

### 📱 Example iOS Usage

```swift
class TechnicalAnalysisAPI {
    private let baseURL = "http://localhost:8000"
    
    func analyzeStock(symbol: String, period: Period) async throws -> AnalysisResult {
        let request = EMAStrategyRequest(
            name: "iOS EMA Strategy",
            description: "EMA analysis from iOS app",
            symbol: symbol,
            period: period,
            interval: .oneDay,
            fastPeriod: 12,
            slowPeriod: 26
        )
        
        // Make API call and return analysis result
        return try await createEMAStrategy(request: request)
    }
}

// Usage in SwiftUI
@State private var selectedSymbol = "AAPL"
@State private var selectedPeriod = Period.oneYear

Button("Analyze Stock") {
    Task {
        let result = try await api.analyzeStock(
            symbol: selectedSymbol, 
            period: selectedPeriod
        )
        // Update UI with results
    }
}
```

### Complete iOS Integration

See `examples/ios_integration.swift` for a complete iOS app example with:
- Ticker validation
- Real-time data fetching
- Multiple strategy types
- SwiftUI interface
- Error handling

## Supported Time Periods

| Period | Description | Best For |
|--------|-------------|----------|
| `1d` | 1 Day | Intraday analysis |
| `5d` | 5 Days | Short-term patterns |
| `1mo` | 1 Month | Quick analysis |
| `3mo` | 3 Months | Quarterly analysis |
| `6mo` | 6 Months | Medium-term trends |
| `1y` | 1 Year | Annual analysis |
| `2y` | 2 Years | Long-term backtesting |
| `5y` | 5 Years | Historical analysis |
| `max` | All Available | Complete history |

## Supported Intervals

| Interval | Description | Use Case |
|----------|-------------|----------|
| `1m`, `5m`, `15m` | Minutes | Day trading |
| `1h` | 1 Hour | Intraday strategies |
| `1d` | 1 Day | Most common |
| `1wk` | 1 Week | Weekly analysis |
| `1mo` | 1 Month | Long-term trends |

## Popular Ticker Symbols

### US Stocks
- **AAPL** - Apple Inc.
- **GOOGL** - Alphabet Inc.
- **MSFT** - Microsoft Corporation
- **TSLA** - Tesla Inc.
- **NVDA** - NVIDIA Corporation
- **AMZN** - Amazon.com Inc.

### ETFs
- **SPY** - SPDR S&P 500 ETF
- **QQQ** - Invesco QQQ Trust
- **IWM** - iShares Russell 2000 ETF

### Crypto (when available)
- **BTC-USD** - Bitcoin
- **ETH-USD** - Ethereum

## Error Handling

The API provides consistent error responses:

```json
{
  "status": "error",
  "message": "Invalid ticker symbol: XYZ123",
  "error_code": "INVALID_TICKER",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

Common error scenarios:
- **Invalid Ticker**: Symbol doesn't exist or has no data
- **Network Error**: Yahoo Finance temporarily unavailable
- **Data Range Error**: Requested period has insufficient data
- **Validation Error**: Invalid request parameters

## Performance Considerations

- **Symbol Validation**: Always validate tickers before analysis
- **Period Selection**: Use appropriate periods for your analysis type
- **Rate Limiting**: Yahoo Finance has usage limits
- **Caching**: Consider caching results for repeated requests
- **Async Operations**: Use async/await patterns in mobile apps

## Development

### Running in Development Mode

```bash
# Install in development mode
pip install -e ".[dev,api]"

# Start with auto-reload
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the startup script
python start_api.py
```

### Testing

```bash
# Run comprehensive tests with real ticker data
python test_api.py

# Test specific endpoints
curl -X GET "http://localhost:8000/health"
curl -X GET "http://localhost:8000/tickers/AAPL/info"
curl -X GET "http://localhost:8000/tickers/AAPL/validate"
```

### Example Test Results

```
🧪 Starting Technical Analysis API Tests with Ticker Integration
======================================================================
🔍 Testing health check...
✅ Health check passed

🔍 Testing ticker validation...
✅ AAPL: Valid (as expected)
✅ GOOGL: Valid (as expected)
✅ INVALID: Invalid (as expected)

🔍 Testing EMA crossover strategy with ticker...
✅ EMA strategy test passed
📊 Symbol: AAPL
📈 Data points: 252
📅 Period: 2023-01-01 to 2024-01-01
💰 Price range: $150.25 - $198.75
🚦 Entry signals: 4
🛑 Exit signals: 3

======================================================================
📊 Test Results: 10/10 tests passed
🎉 All tests passed! Ticker-based API is working correctly.
```

## Legacy Endpoints

For backward compatibility, the original endpoints are still available:

- `POST /analyze` - Analysis with raw price data ⚠️ **Deprecated**
- `POST /backtest` - Backtesting with raw price data ⚠️ **Deprecated**

New applications should use the ticker-based endpoints instead.

## Production Deployment

### Environment Variables

```bash
export API_HOST=0.0.0.0
export API_PORT=8000
export API_WORKERS=4
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -e ".[api]"

EXPOSE 8000
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Security Considerations

1. **CORS**: Configure appropriate origins for production
2. **Rate Limiting**: Implement rate limiting for Yahoo Finance calls
3. **API Keys**: Consider adding authentication for production use
4. **HTTPS**: Always use HTTPS in production
5. **Input Validation**: All inputs validated via Pydantic models

## Troubleshooting

### Common Issues

1. **Invalid Ticker Errors**: 
   - Use the validation endpoint first: `GET /tickers/{symbol}/validate`
   - Check for correct symbol format (uppercase, no spaces)

2. **Yahoo Finance Connectivity**:
   ```bash
   # Test Yahoo Finance directly
   curl "https://query1.finance.yahoo.com/v8/finance/chart/AAPL"
   ```

3. **No Data Errors**:
   - Try different time periods (some symbols have limited history)
   - Use `max` period to get all available data

4. **iOS Connection Issues**:
   - Use `http://localhost:8000` for iOS Simulator
   - Use your computer's IP for physical devices
   - Check CORS settings in production

### Network Requirements

- **Internet Connection**: Required for Yahoo Finance data
- **Firewall**: Ensure outbound HTTPS access to Yahoo Finance
- **DNS**: Ensure DNS resolution for `finance.yahoo.com`

## Examples

### Quick Start Example

```bash
# Start the server
python start_api.py

# Test with a simple request
curl -X POST "http://localhost:8000/strategies/ema-crossover" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Apple EMA Test",
    "symbol": "AAPL",
    "period": "1y",
    "interval": "1d",
    "fast_period": 12,
    "slow_period": 26
  }'
```

### iOS App Integration

1. **Add the API client** (`ios_integration.swift`)
2. **Create request models** for your strategies
3. **Use async/await** for API calls
4. **Handle validation** and errors gracefully
5. **Cache results** for better performance

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Support

For issues and questions:
- Check the interactive API docs at `/docs`
- Review the example iOS integration code
- Test with the provided test script: `python test_api.py`
- Open an issue on the GitHub repository

---

**🎉 Ready to analyze real market data with just ticker symbols!** No more manual price data management - the API handles everything automatically with Yahoo Finance integration. 
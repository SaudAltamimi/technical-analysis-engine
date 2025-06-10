# Technical Analysis FastAPI Server

A RESTful API server that exposes the technical analysis engine with **automatic Yahoo Finance data fetching** for easy integration with mobile applications, particularly iOS apps using Swift.

## 🚀 Current API Features

- **📊 Automatic Data Fetching**: Just provide a ticker symbol (e.g., AAPL, GOOGL) - the API fetches data automatically
- **🎯 Real Market Data**: Uses Yahoo Finance for up-to-date market data
- **📱 iOS-Optimized**: Perfect for mobile app integration with simple ticker requests
- **⚡ Custom Strategies**: Build flexible strategies with multiple indicators and rules
- **🔄 Real-time Analysis**: Calculate indicators and generate signals from Yahoo Finance data
- **📈 Backtesting**: Test strategies with performance metrics on real market data
- **⚡ Fast Performance**: Built with FastAPI for high-performance async operations
- **📚 Auto-documentation**: Interactive API docs with Swagger UI
- **🎯 Ticker Tools**: Validation, search, and recommendation features

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

# Or using make command
make api
```

### 3. Access the API

- **API Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Core Endpoints

#### Health Check

```http
GET /health
```

Check if the API is running and healthy.

#### Root Endpoint

```http
GET /
```

Get API information and welcome message.

### 🎯 Strategy Creation and Analysis

#### Custom Strategy Creation

```http
POST /strategies/custom
```

Create and analyze a custom strategy with multiple indicators and rules.

**Example Request:**
```json
{
  "strategy": {
    "name": "EMA_RSI_Strategy",
    "description": "EMA crossover with RSI filter",
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
      },
      {
        "name": "RSI_14",
        "type": "RSI",
        "params": {"window": 14}
      }
    ],
    "crossover_rules": [
      {
        "name": "EMA_Entry",
        "fast_indicator": "EMA_12",
        "slow_indicator": "EMA_26",
        "direction": "above",
        "signal_type": "entry"
      }
    ],
    "threshold_rules": [
      {
        "name": "RSI_Filter",
        "indicator": "RSI_14",
        "threshold": 70,
        "condition": "below",
        "signal_type": "entry"
      }
    ]
  },
  "ticker_request": {
    "symbol": "AAPL",
    "period": "6mo"
  }
}
```

#### Strategy Validation

```http
POST /strategies/validate
```

Validate a strategy configuration without executing it.

**Example Request:**
```json
{
  "name": "Test Strategy",
  "indicators": [
    {
      "name": "EMA_12",
      "type": "EMA", 
      "params": {"window": 12}
    }
  ],
  "crossover_rules": [],
  "threshold_rules": []
}
```

### 📊 Backtesting

#### Ticker-Based Backtesting

```http
POST /backtest/custom/ticker
```

Backtest a strategy using ticker symbol and period.

**Example Request:**
```json
{
  "strategy": {
    "name": "EMA Crossover Strategy",
    "description": "12/26 EMA crossover backtest",
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
        "name": "EMA_Entry",
        "fast_indicator": "EMA_12",
        "slow_indicator": "EMA_26",
        "direction": "above",
        "signal_type": "entry"
      },
      {
        "name": "EMA_Exit",
        "fast_indicator": "EMA_12",
        "slow_indicator": "EMA_26", 
        "direction": "below",
        "signal_type": "exit"
      }
    ],
    "threshold_rules": []
  },
  "ticker_request": {
    "symbol": "AAPL",
    "period": "1y"
  }
}
```

#### Date Range Backtesting

```http
POST /backtest/custom/date-range
```

Backtest a strategy with specific start and end dates.

**Example Request:**
```json
{
  "strategy": {
    "name": "Custom Date Range Strategy",
    "indicators": [/* ... */],
    "crossover_rules": [/* ... */],
    "threshold_rules": [/* ... */]
  },
  "date_range_request": {
    "symbol": "MSFT",
    "start_date": "2023-01-01T00:00:00Z",
    "end_date": "2023-12-31T23:59:59Z",
    "interval": "1d"
  }
}
```

### 🎯 Ticker Management

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
    "symbol": "TSLA",
    "longName": "Tesla, Inc.",
    "sector": "Consumer Cyclical",
    "industry": "Auto Manufacturers", 
    "country": "United States",
    "currency": "USD",
    "exchange": "NASDAQ NMS - GLOBAL MARKET",
    "marketCap": 789000000000,
    "description": "Tesla, Inc. designs, develops, manufactures, leases, and sells electric vehicles..."
  }
}
```

#### Popular Tickers

```http
GET /tickers/popular
```

Get a curated list of popular stock tickers.

#### Search Tickers

```http
POST /tickers/search
```

Search for tickers by name or symbol.

**Example Request:**
```json
{
  "query": "apple",
  "limit": 10
}
```

#### Ticker Recommendations

```http
GET /tickers/recommendations/{strategy_type}
```

Get recommended tickers for specific strategy types.

**Strategy Types:**
- `trending` - Currently trending stocks
- `volume` - High volume stocks  
- `volatile` - Volatile stocks good for technical analysis
- `stable` - Stable blue-chip stocks

#### Ticker Configuration Stats

```http
GET /tickers/config/stats
```

Get statistics about the ticker configuration and available symbols.

### 🛠️ Utility Endpoints

#### Indicator Types

```http
GET /indicators/types
```

Get available indicator types and their parameters.

**Example Response:**
```json
{
  "status": "success",
  "data": {
    "indicators": [
      {
        "type": "EMA",
        "name": "Exponential Moving Average",
        "params": ["window"]
      },
      {
        "type": "RSI", 
        "name": "Relative Strength Index",
        "params": ["window"]
      },
      {
        "type": "MACD",
        "name": "Moving Average Convergence Divergence", 
        "params": ["fast_window", "slow_window", "signal_window"]
      },
      {
        "type": "SMA",
        "name": "Simple Moving Average",
        "params": ["window"]
      }
    ]
  }
}
```

#### Available Periods

```http
GET /periods
```

Get available time periods and intervals for Yahoo Finance data.

**Example Response:**
```json
{
  "status": "success",
  "data": {
    "periods": ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
    "intervals": ["1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"],
    "descriptions": {
      "1y": "1 Year of data",
      "6mo": "6 Months of data", 
      "1d": "1 Day of data",
      "max": "All available data"
    }
  }
}
```

## iOS Integration

### 🍎 Swift Models

The API is designed to work seamlessly with Swift's `Codable` protocol:

```swift
struct CustomStrategyRequest: Codable {
    let strategy: StrategyDefinition
    let tickerRequest: TickerRequest
    
    enum CodingKeys: String, CodingKey {
        case strategy
        case tickerRequest = "ticker_request"
    }
}

struct StrategyDefinition: Codable {
    let name: String
    let description: String?
    let indicators: [IndicatorDefinition]
    let crossoverRules: [CrossoverRule]
    let thresholdRules: [ThresholdRule]
    
    enum CodingKeys: String, CodingKey {
        case name, description, indicators
        case crossoverRules = "crossover_rules"
        case thresholdRules = "threshold_rules"
    }
}

struct IndicatorDefinition: Codable {
    let name: String
    let type: IndicatorType
    let params: [String: Int]
}

enum IndicatorType: String, Codable, CaseIterable {
    case EMA, RSI, MACD, SMA
}

struct TickerRequest: Codable {
    let symbol: String
    let period: Period
    let interval: Interval?
}

enum Period: String, Codable, CaseIterable {
    case oneDay = "1d"
    case fiveDays = "5d"
    case oneMonth = "1mo"
    case threeMonths = "3mo"
    case sixMonths = "6mo"
    case oneYear = "1y"
    case twoYears = "2y"
    case fiveYears = "5y"
    case tenYears = "10y"
    case ytd = "ytd"
    case max = "max"
}
```

### 📱 Example iOS Usage

```swift
class TechnicalAnalysisAPI {
    private let baseURL = "http://localhost:8000"
    
    func createCustomStrategy(symbol: String, period: Period) async throws -> APIResponse {
        let strategy = StrategyDefinition(
            name: "iOS EMA Strategy",
            description: "EMA crossover from iOS app",
            indicators: [
                IndicatorDefinition(name: "EMA_12", type: .EMA, params: ["window": 12]),
                IndicatorDefinition(name: "EMA_26", type: .EMA, params: ["window": 26])
            ],
            crossoverRules: [
                CrossoverRule(
                    name: "EMA_Entry",
                    fastIndicator: "EMA_12",
                    slowIndicator: "EMA_26", 
                    direction: "above",
                    signalType: "entry"
                )
            ],
            thresholdRules: []
        )
        
        let request = CustomStrategyRequest(
            strategy: strategy,
            tickerRequest: TickerRequest(symbol: symbol, period: period, interval: nil)
        )
        
        return try await postRequest(endpoint: "/strategies/custom", data: request)
    }
    
    func validateTicker(_ symbol: String) async throws -> Bool {
        let response = try await getRequest(endpoint: "/tickers/\(symbol)/validate")
        return response.data["is_valid"] as? Bool ?? false
    }
}

// Usage in SwiftUI
@State private var selectedSymbol = "AAPL"
@State private var selectedPeriod = Period.oneYear
@State private var isAnalyzing = false

Button("Create Strategy") {
    Task {
        isAnalyzing = true
        defer { isAnalyzing = false }
        
        do {
            // Validate ticker first
            let isValid = try await api.validateTicker(selectedSymbol)
            guard isValid else {
                // Show error
                return
            }
            
            // Create strategy
            let result = try await api.createCustomStrategy(
                symbol: selectedSymbol,
                period: selectedPeriod
            )
            
            // Update UI with results
        } catch {
            // Handle error
        }
    }
}
.disabled(isAnalyzing)
```

### Complete iOS Integration

See `/docs/README_iOS.md` for a complete iOS integration guide with:
- Complete Swift API client
- All data models with proper CodingKeys
- SwiftUI integration examples  
- Chart integration with Swift Charts
- Unit testing examples
- Production deployment considerations

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
# Install dependencies
make setup

# Start API server
make api

# Or start with custom settings
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing

```bash
# Test basic endpoints
curl -X GET "http://localhost:8000/health"
curl -X GET "http://localhost:8000/indicators/types"
curl -X GET "http://localhost:8000/tickers/AAPL/validate"
curl -X GET "http://localhost:8000/tickers/TSLA/info"

# Test strategy creation
curl -X POST "http://localhost:8000/strategies/custom" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": {
      "name": "Test Strategy",
      "indicators": [
        {"name": "EMA_12", "type": "EMA", "params": {"window": 12}}
      ],
      "crossover_rules": [],
      "threshold_rules": []
    },
    "ticker_request": {
      "symbol": "AAPL",
      "period": "6mo"
    }
  }'
```



## API Response Format

All API endpoints return responses in a consistent format:

**Success Response:**
```json
{
  "status": "success",
  "message": "Operation completed successfully",
  "data": {
    // Response data here
  }
}
```

**Error Response:**
```json
{
  "status": "error", 
  "message": "Error description",
  "error_code": "ERROR_TYPE",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

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
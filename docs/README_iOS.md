# iOS Developer Guide

Integration guide for iOS developers building trading applications with the Technical Analysis API.

## 📱 Overview

The Technical Analysis API provides JSON-based REST endpoints perfect for iOS applications. Build sophisticated trading apps with real-time technical analysis, custom strategies, and backtesting capabilities.

## 🚀 Quick Setup

### 1. Start the API Server
```bash
make setup && make api
```
API will be available at `http://localhost:8000`

### 2. iOS Project Setup
Add networking dependencies to your iOS project:
```swift
// Using URLSession (built-in) or Alamofire
import Foundation
// import Alamofire  // Optional: For advanced networking
```

## 📊 Core Integration

### Basic API Client
```swift
import Foundation

class TechnicalAnalysisAPI {
    private let baseURL: String
    private let session = URLSession.shared
    
    init(baseURL: String = "http://localhost:8000") {
        self.baseURL = baseURL
    }
    
    // MARK: - Health Check
    func healthCheck() async throws -> Bool {
        let url = URL(string: "\(baseURL)/health")!
        let (_, response) = try await session.data(from: url)
        return (response as? HTTPURLResponse)?.statusCode == 200
    }
    
    // MARK: - Ticker Validation
    func validateTicker(_ symbol: String) async throws -> Bool {
        let url = URL(string: "\(baseURL)/tickers/\(symbol)/validate")!
        let (_, response) = try await session.data(from: url)
        return (response as? HTTPURLResponse)?.statusCode == 200
    }
}
```

### Strategy Creation
```swift
// MARK: - Strategy Models
struct StrategyRequest: Codable {
    let name: String
    let symbol: String
    let description: String?
    let indicators: [IndicatorDefinition]
    let crossoverRules: [CrossoverRule]
    let thresholdRules: [ThresholdRule]
    let period: String
    
    enum CodingKeys: String, CodingKey {
        case name, symbol, description, indicators, period
        case crossoverRules = "crossover_rules"
        case thresholdRules = "threshold_rules"
    }
}

struct IndicatorDefinition: Codable {
    let name: String
    let type: String
    let params: [String: Int]
}

struct CrossoverRule: Codable {
    let name: String
    let fastIndicator: String
    let slowIndicator: String
    let direction: String
    let signalType: String
    
    enum CodingKeys: String, CodingKey {
        case name, direction
        case fastIndicator = "fast_indicator"
        case slowIndicator = "slow_indicator"
        case signalType = "signal_type"
    }
}

struct ThresholdRule: Codable {
    let name: String
    let indicator: String
    let threshold: Double
    let condition: String
    let signalType: String
    
    enum CodingKeys: String, CodingKey {
        case name, indicator, threshold, condition
        case signalType = "signal_type"
    }
}

// MARK: - API Response Models
struct StrategyResponse: Codable {
    let data: StrategyData
    let message: String
    let status: String
}

struct StrategyData: Codable {
    let strategy: Strategy
    let analysis: Analysis
}

struct Strategy: Codable {
    let name: String
    let symbol: String
    let indicators: [String]
}

struct Analysis: Codable {
    let indicators: [IndicatorResult]
    let signals: [Signal]
    let summary: AnalysisSummary
}

struct IndicatorResult: Codable {
    let name: String
    let type: String
    let values: [Double?]
}

struct Signal: Codable {
    let date: String
    let type: String
    let price: Double
    let rule: String
}

struct AnalysisSummary: Codable {
    let totalSignals: Int
    let entrySignals: Int
    let exitSignals: Int
    let priceRange: PriceRange
    
    enum CodingKeys: String, CodingKey {
        case priceRange = "price_range"
        case totalSignals = "total_signals"
        case entrySignals = "entry_signals"
        case exitSignals = "exit_signals"
    }
}

struct PriceRange: Codable {
    let min: Double
    let max: Double
}
```

### API Methods Extension
```swift
extension TechnicalAnalysisAPI {
    
    // MARK: - Create Custom Strategy
    func createStrategy(_ request: StrategyRequest) async throws -> StrategyResponse {
        let url = URL(string: "\(baseURL)/strategies/custom")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let encoder = JSONEncoder()
        urlRequest.httpBody = try encoder.encode(request)
        
        let (data, response) = try await session.data(for: urlRequest)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw APIError.invalidResponse
        }
        
        let decoder = JSONDecoder()
        return try decoder.decode(StrategyResponse.self, from: data)
    }
    
    // MARK: - Backtest Strategy
    func backtestStrategy(_ request: StrategyRequest) async throws -> BacktestResponse {
        let url = URL(string: "\(baseURL)/backtest/custom/ticker")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let encoder = JSONEncoder()
        urlRequest.httpBody = try encoder.encode(request)
        
        let (data, response) = try await session.data(for: urlRequest)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw APIError.invalidResponse
        }
        
        let decoder = JSONDecoder()
        return try decoder.decode(BacktestResponse.self, from: data)
    }
    
    // MARK: - Get Popular Tickers
    func getPopularTickers() async throws -> [String] {
        let url = URL(string: "\(baseURL)/tickers/popular")!
        let (data, _) = try await session.data(from: url)
        
        let decoder = JSONDecoder()
        let response = try decoder.decode(TickersResponse.self, from: data)
        return response.data.tickers
    }
}

// MARK: - Additional Models
struct BacktestResponse: Codable {
    let data: BacktestData
    let message: String
    let status: String
}

struct BacktestData: Codable {
    let strategy: Strategy
    let backtest: BacktestResults
}

struct BacktestResults: Codable {
    let performance: BacktestPerformance
    let trades: [Trade]
    let portfolio: PortfolioStats
}

struct BacktestPerformance: Codable {
    let totalReturn: Double
    let sharpeRatio: Double
    let maxDrawdown: Double
    
    enum CodingKeys: String, CodingKey {
        case totalReturn = "total_return"
        case sharpeRatio = "sharpe_ratio"
        case maxDrawdown = "max_drawdown"
    }
}

struct Trade: Codable {
    let entryDate: String
    let exitDate: String?
    let entryPrice: Double
    let exitPrice: Double?
    let size: Double
    let pnl: Double?
    
    enum CodingKeys: String, CodingKey {
        case entryDate = "entry_date"
        case exitDate = "exit_date"
        case entryPrice = "entry_price"
        case exitPrice = "exit_price"
        case size, pnl
    }
}

struct PortfolioStats: Codable {
    let startValue: Double
    let endValue: Double
    let totalTrades: Int
    
    enum CodingKeys: String, CodingKey {
        case startValue = "start_value"
        case endValue = "end_value"
        case totalTrades = "total_trades"
    }
}

struct TickersResponse: Codable {
    let data: TickersData
}

struct TickersData: Codable {
    let tickers: [String]
}

// MARK: - Error Handling
enum APIError: Error {
    case invalidURL
    case invalidResponse
    case noData
    case decodingError(Error)
    case networkError(Error)
}
```

## 📈 Usage Examples

### SwiftUI Integration
```swift
import SwiftUI

struct TradingView: View {
    @StateObject private var viewModel = TradingViewModel()
    
    var body: some View {
        NavigationView {
            VStack {
                // Strategy Creation Form
                StrategyForm(onCreateStrategy: viewModel.createStrategy)
                
                // Results Display
                if let analysis = viewModel.analysis {
                    AnalysisResultsView(analysis: analysis)
                }
                
                // Backtest Results
                if let backtest = viewModel.backtest {
                    BacktestResultsView(backtest: backtest)
                }
            }
            .navigationTitle("Technical Analysis")
        }
        .task {
            await viewModel.loadPopularTickers()
        }
    }
}

@MainActor
class TradingViewModel: ObservableObject {
    @Published var analysis: Analysis?
    @Published var backtest: BacktestResults?
    @Published var popularTickers: [String] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let api = TechnicalAnalysisAPI()
    
    func loadPopularTickers() async {
        do {
            popularTickers = try await api.getPopularTickers()
        } catch {
            errorMessage = "Failed to load tickers: \(error.localizedDescription)"
        }
    }
    
    func createStrategy(_ request: StrategyRequest) async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            let response = try await api.createStrategy(request)
            analysis = response.data.analysis
        } catch {
            errorMessage = "Strategy creation failed: \(error.localizedDescription)"
        }
    }
    
    func runBacktest(_ request: StrategyRequest) async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            let response = try await api.backtestStrategy(request)
            backtest = response.data.backtest
        } catch {
            errorMessage = "Backtest failed: \(error.localizedDescription)"
        }
    }
}
```

### Chart Integration (with Charts framework)
```swift
import Charts
import SwiftUI

struct IndicatorChart: View {
    let indicator: IndicatorResult
    let prices: [Double]
    
    var body: some View {
        Chart {
            // Price line
            ForEach(Array(prices.enumerated()), id: \.offset) { index, price in
                LineMark(
                    x: .value("Index", index),
                    y: .value("Price", price)
                )
                .foregroundStyle(.blue)
            }
            
            // Indicator line
            ForEach(Array(indicator.values.enumerated()), id: \.offset) { index, value in
                if let value = value {
                    LineMark(
                        x: .value("Index", index),
                        y: .value("Indicator", value)
                    )
                    .foregroundStyle(.red)
                }
            }
        }
        .chartYScale(domain: .automatic)
        .frame(height: 200)
    }
}
```

## 🔄 Real-Time Updates

### WebSocket Integration (Future Enhancement)
```swift
// For real-time price updates when WebSocket support is added
class RealTimeDataManager: ObservableObject {
    @Published var currentPrice: Double = 0.0
    @Published var latestSignals: [Signal] = []
    
    // WebSocket implementation would go here
    // This is a placeholder for future real-time functionality
}
```

## 🧪 Testing

### Unit Tests
```swift
import XCTest
@testable import YourTradingApp

class TechnicalAnalysisAPITests: XCTestCase {
    
    func testHealthCheck() async throws {
        let api = TechnicalAnalysisAPI(baseURL: "http://localhost:8000")
        let isHealthy = try await api.healthCheck()
        XCTAssertTrue(isHealthy)
    }
    
    func testTickerValidation() async throws {
        let api = TechnicalAnalysisAPI(baseURL: "http://localhost:8000")
        let isValid = try await api.validateTicker("AAPL")
        XCTAssertTrue(isValid)
    }
    
    func testStrategyCreation() async throws {
        let api = TechnicalAnalysisAPI(baseURL: "http://localhost:8000")
        
        let strategy = StrategyRequest(
            name: "Test_EMA_Strategy",
            symbol: "AAPL",
            description: "Test strategy",
            indicators: [
                IndicatorDefinition(name: "EMA_12", type: "EMA", params: ["window": 12]),
                IndicatorDefinition(name: "EMA_26", type: "EMA", params: ["window": 26])
            ],
            crossoverRules: [
                CrossoverRule(
                    name: "entry",
                    fastIndicator: "EMA_12",
                    slowIndicator: "EMA_26",
                    direction: "above",
                    signalType: "entry"
                )
            ],
            thresholdRules: [],
            period: "6mo"
        )
        
        let response = try await api.createStrategy(strategy)
        XCTAssertEqual(response.status, "success")
        XCTAssertFalse(response.data.analysis.indicators.isEmpty)
    }
}
```

## 🚀 Deployment Considerations

### Production Setup
1. **API URL Configuration**: Use environment-specific URLs
   ```swift
   #if DEBUG
   let apiURL = "http://localhost:8000"
   #else
   let apiURL = "https://your-production-api.com"
   #endif
   ```

2. **Error Handling**: Implement comprehensive error handling
3. **Caching**: Cache frequently accessed data like popular tickers
4. **Security**: Use HTTPS in production, implement API key authentication if required

### Performance Optimization
- Use background queues for API calls
- Implement result caching where appropriate
- Consider pagination for large datasets
- Use compression for large payloads

## 📚 Additional Resources

- **API Documentation**: `http://localhost:8000/docs`
- **Strategy Examples**: See main README for curl examples
- **Charts Integration**: Consider using Swift Charts or third-party charting libraries
- **Real-time Data**: Plan for WebSocket integration for live updates

## 🤝 Support

For iOS-specific questions or issues:
1. Check the main API documentation at `/docs/README_API.md`
2. Test endpoints using the interactive docs at `http://localhost:8000/docs`
3. Use the Streamlit interface for visual validation of strategies

Happy coding! 📱💹 
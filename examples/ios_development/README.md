# iOS Development Templates

Ready-to-use Swift code and templates for iOS trading app development.

## 📁 Files

### `ios_integration.swift`
**Complete Swift integration template**
- Full API client implementation
- All endpoint integrations
- Swift 5.7+ with async/await
- Proper error handling
- Chart data structures
- Production-ready code

## 🎯 Features

### ✅ Complete API Coverage
- Health checks
- Ticker validation
- Company information
- EMA crossover strategies
- RSI analysis
- Custom indicators
- Backtesting

### ✅ Modern Swift Patterns
- async/await for network calls
- Structured concurrency
- Proper error handling
- Codable models
- Type-safe endpoints

### ✅ Chart Integration Ready
- Parsed indicator data
- Signal structures
- Time series data
- Ready for Core Plot or Charts framework

## 🚀 Quick Setup

### 1. Copy Template
```swift
// Copy ios_integration.swift to your Xcode project
```

### 2. Add Dependencies
```swift
// Package.swift or Xcode Package Manager
dependencies: [
    .package(url: "https://github.com/Alamofire/Alamofire.git", from: "5.0.0")
]
```

### 3. Configure API
```swift
let api = TechnicalAnalysisAPI(baseURL: "http://localhost:8001")
```

### 4. Use in Your App
```swift
// Example usage
Task {
    do {
        let analysis = try await api.createEMAStrategy(
            symbol: "AAPL",
            period: "1y"
        )
        
        // Process for charts
        updateChart(with: analysis.indicators)
        showSignals(analysis.entrySignals, analysis.exitSignals)
        
    } catch {
        print("Error: \(error)")
    }
}
```

## 📊 Data Structures

### Analysis Response
```swift
struct AnalysisResponse: Codable {
    let symbol: String
    let indicators: [Indicator]
    let entrySignals: [Signal]
    let exitSignals: [Signal]
    let dataInfo: DataInfo
}
```

### Indicator Data
```swift
struct Indicator: Codable {
    let name: String
    let type: String
    let params: [String: AnyCodable]
    let values: [IndicatorValue]
}

struct IndicatorValue: Codable {
    let timestamp: String
    let value: Double
}
```

### Trading Signals
```swift
struct Signal: Codable {
    let timestamp: String
    let signalType: String
    let ruleName: String
    let strength: Double?
}
```

## 📱 UI Integration

### SwiftUI Charts
```swift
import Charts

Chart(indicators.first?.values ?? []) { value in
    LineMark(
        x: .value("Date", parseDate(value.timestamp)),
        y: .value("Price", value.value)
    )
}
```

### UIKit Integration
```swift
// Use with Core Plot or custom drawing
func plotIndicator(_ indicator: Indicator) {
    let dataPoints = indicator.values.map { value in
        CPTScatterPlotField.Y: value.value,
        CPTScatterPlotField.X: parseDate(value.timestamp).timeIntervalSince1970
    }
    // Add to plot...
}
```

## 🎯 Best Practices

### Error Handling
```swift
enum APIError: Error {
    case invalidURL
    case noData
    case decodingError
    case networkError(Error)
}
```

### Caching
```swift
// Cache company info to reduce API calls
class DataCache {
    private var companyCache: [String: CompanyInfo] = [:]
    
    func getCachedCompanyInfo(for symbol: String) -> CompanyInfo? {
        return companyCache[symbol]
    }
}
```

### Background Processing
```swift
// Process data on background queue
func processAnalysis(_ analysis: AnalysisResponse) async {
    await withTaskGroup(of: Void.self) { group in
        group.addTask {
            await self.updateCharts(analysis.indicators)
        }
        group.addTask {
            await self.processSignals(analysis.entrySignals, analysis.exitSignals)
        }
    }
}
```

## 📖 Documentation Reference

- **API Documentation**: `../documentation/ios_api_documentation.md`
- **Integration Examples**: `../api_integration/`
- **Visualization Examples**: `../visualizations/`

Perfect foundation for professional iOS trading apps! 📱💹 
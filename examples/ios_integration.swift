import Foundation

// MARK: - API Models (matching the Python Pydantic models)

// Data models
struct IndicatorValuePoint: Codable {
    let timestamp: String
    let value: Double
}

struct IndicatorResult: Codable {
    let name: String
    let type: String
    let params: [String: AnyCodable]
    let values: [IndicatorValuePoint]
}

struct SignalPoint: Codable {
    let timestamp: String
    let signal: Bool
    let signalType: String
    let ruleName: String
    
    enum CodingKeys: String, CodingKey {
        case timestamp, signal, ruleName
        case signalType = "signal_type"
    }
}

struct DataFetchResult: Codable {
    let symbol: String
    let dataPoints: Int
    let startDate: String
    let endDate: String
    let priceRange: [Double] // [min, max]
    
    enum CodingKeys: String, CodingKey {
        case symbol, startDate, endDate, priceRange
        case dataPoints = "data_points"
        case startDate = "start_date"
        case endDate = "end_date"
        case priceRange = "price_range"
    }
}

struct AnalysisResult: Codable {
    let strategyName: String
    let symbol: String
    let dataInfo: DataFetchResult
    let indicators: [IndicatorResult]
    let signals: [SignalPoint]
    let entrySignals: [SignalPoint]
    let exitSignals: [SignalPoint]
    
    enum CodingKeys: String, CodingKey {
        case indicators, signals, symbol
        case strategyName = "strategy_name"
        case dataInfo = "data_info"
        case entrySignals = "entry_signals"
        case exitSignals = "exit_signals"
    }
}

struct APIResponse: Codable {
    let status: String
    let message: String
    let data: AnyCodable?
    let timestamp: String
}

struct BacktestResult: Codable {
    let totalReturn: Double
    let sharpeRatio: Double
    let maxDrawdown: Double
    let winRate: Double
    let totalTrades: Int
    let finalValue: Double
    
    enum CodingKeys: String, CodingKey {
        case totalReturn = "total_return"
        case sharpeRatio = "sharpe_ratio"
        case maxDrawdown = "max_drawdown"
        case winRate = "win_rate"
        case totalTrades = "total_trades"
        case finalValue = "final_value"
    }
}

struct TickerInfo: Codable {
    let symbol: String
    let name: String
    let sector: String?
    let industry: String?
    let currency: String
    let exchange: String?
    let marketCap: Int?
    let description: String?
    
    enum CodingKeys: String, CodingKey {
        case symbol, name, sector, industry, currency, exchange, description
        case marketCap = "market_cap"
    }
}

// Request models
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
    
    var displayName: String {
        switch self {
        case .oneDay: return "1 Day"
        case .fiveDays: return "5 Days"
        case .oneMonth: return "1 Month"
        case .threeMonths: return "3 Months"
        case .sixMonths: return "6 Months"
        case .oneYear: return "1 Year"
        case .twoYears: return "2 Years"
        case .fiveYears: return "5 Years"
        case .tenYears: return "10 Years"
        case .ytd: return "Year to Date"
        case .max: return "All Available"
        }
    }
}

enum Interval: String, Codable, CaseIterable {
    case oneMinute = "1m"
    case fiveMinutes = "5m"
    case fifteenMinutes = "15m"
    case thirtyMinutes = "30m"
    case oneHour = "1h"
    case oneDay = "1d"
    case oneWeek = "1wk"
    case oneMonth = "1mo"
    
    var displayName: String {
        switch self {
        case .oneMinute: return "1 Minute"
        case .fiveMinutes: return "5 Minutes"
        case .fifteenMinutes: return "15 Minutes"
        case .thirtyMinutes: return "30 Minutes"
        case .oneHour: return "1 Hour"
        case .oneDay: return "1 Day"
        case .oneWeek: return "1 Week"
        case .oneMonth: return "1 Month"
        }
    }
}

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

struct MultiEMAStrategyRequest: Codable {
    let name: String
    let description: String?
    let symbol: String
    let period: Period
    let interval: Interval
    let emaPeriods: [Int]
    
    enum CodingKeys: String, CodingKey {
        case name, description, symbol, period, interval
        case emaPeriods = "ema_periods"
    }
}

struct RSIStrategyRequest: Codable {
    let name: String
    let description: String?
    let symbol: String
    let period: Period
    let interval: Interval
    let rsiPeriod: Int
    let oversoldThreshold: Double
    let overboughtThreshold: Double
    
    enum CodingKeys: String, CodingKey {
        case name, description, symbol, period, interval
        case rsiPeriod = "rsi_period"
        case oversoldThreshold = "oversold_threshold"
        case overboughtThreshold = "overbought_threshold"
    }
}

// MARK: - Helper for handling dynamic JSON
struct AnyCodable: Codable {
    let value: Any
    
    init<T>(_ value: T?) {
        self.value = value ?? ()
    }
}

extension AnyCodable {
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        
        if let intValue = try? container.decode(Int.self) {
            value = intValue
        } else if let doubleValue = try? container.decode(Double.self) {
            value = doubleValue
        } else if let stringValue = try? container.decode(String.self) {
            value = stringValue
        } else if let boolValue = try? container.decode(Bool.self) {
            value = boolValue
        } else if let arrayValue = try? container.decode([AnyCodable].self) {
            value = arrayValue.map { $0.value }
        } else if let dictValue = try? container.decode([String: AnyCodable].self) {
            value = dictValue.mapValues { $0.value }
        } else {
            value = ()
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        
        switch value {
        case let intValue as Int:
            try container.encode(intValue)
        case let doubleValue as Double:
            try container.encode(doubleValue)
        case let stringValue as String:
            try container.encode(stringValue)
        case let boolValue as Bool:
            try container.encode(boolValue)
        case let arrayValue as [Any]:
            let codableArray = arrayValue.map { AnyCodable($0) }
            try container.encode(codableArray)
        case let dictValue as [String: Any]:
            let codableDict = dictValue.mapValues { AnyCodable($0) }
            try container.encode(codableDict)
        default:
            try container.encodeNil()
        }
    }
}

// MARK: - Technical Analysis API Client
class TechnicalAnalysisAPI {
    private let baseURL: String
    private let session: URLSession
    
    init(baseURL: String = "http://localhost:8000") {
        self.baseURL = baseURL
        self.session = URLSession.shared
    }
    
    // MARK: - Helper Methods
    private func makeRequest<T: Codable>(
        endpoint: String,
        method: String = "GET",
        body: Data? = nil,
        responseType: T.Type
    ) async throws -> T {
        guard let url = URL(string: "\(baseURL)\(endpoint)") else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        if let body = body {
            request.httpBody = body
        }
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        guard 200...299 ~= httpResponse.statusCode else {
            throw APIError.httpError(httpResponse.statusCode)
        }
        
        do {
            let decoder = JSONDecoder()
            return try decoder.decode(responseType, from: data)
        } catch {
            throw APIError.decodingError(error)
        }
    }
    
    // MARK: - API Methods
    
    /// Check API health
    func healthCheck() async throws -> APIResponse {
        return try await makeRequest(
            endpoint: "/health",
            responseType: APIResponse.self
        )
    }
    
    /// Get ticker information
    func getTickerInfo(symbol: String) async throws -> TickerInfo {
        let response = try await makeRequest(
            endpoint: "/tickers/\(symbol.uppercased())/info",
            responseType: APIResponse.self
        )
        
        guard let data = response.data else {
            throw APIError.noData
        }
        
        let jsonData = try JSONSerialization.data(withJSONObject: data.value)
        let decoder = JSONDecoder()
        return try decoder.decode(TickerInfo.self, from: jsonData)
    }
    
    /// Validate ticker symbol
    func validateTicker(symbol: String) async throws -> Bool {
        let response = try await makeRequest(
            endpoint: "/tickers/\(symbol.uppercased())/validate",
            responseType: APIResponse.self
        )
        
        guard let data = response.data,
              let dataDict = data.value as? [String: Any],
              let isValid = dataDict["is_valid"] as? Bool else {
            throw APIError.invalidResponse
        }
        
        return isValid
    }
    
    /// Create and analyze EMA crossover strategy
    func createEMAStrategy(request: EMAStrategyRequest) async throws -> AnalysisResult {
        let encoder = JSONEncoder()
        let body = try encoder.encode(request)
        
        let response = try await makeRequest(
            endpoint: "/strategies/ema-crossover",
            method: "POST",
            body: body,
            responseType: APIResponse.self
        )
        
        return try extractAnalysisResult(from: response)
    }
    
    /// Create and analyze multiple EMA strategy
    func createMultiEMAStrategy(request: MultiEMAStrategyRequest) async throws -> AnalysisResult {
        let encoder = JSONEncoder()
        let body = try encoder.encode(request)
        
        let response = try await makeRequest(
            endpoint: "/strategies/multi-ema",
            method: "POST",
            body: body,
            responseType: APIResponse.self
        )
        
        return try extractAnalysisResult(from: response)
    }
    
    /// Create and analyze RSI strategy
    func createRSIStrategy(request: RSIStrategyRequest) async throws -> AnalysisResult {
        let encoder = JSONEncoder()
        let body = try encoder.encode(request)
        
        let response = try await makeRequest(
            endpoint: "/strategies/rsi",
            method: "POST",
            body: body,
            responseType: APIResponse.self
        )
        
        return try extractAnalysisResult(from: response)
    }
    
    /// Get available time periods
    func getAvailablePeriods() async throws -> [String] {
        let response = try await makeRequest(
            endpoint: "/periods",
            responseType: APIResponse.self
        )
        
        guard let data = response.data,
              let dataDict = data.value as? [String: Any],
              let periods = dataDict["periods"] as? [String] else {
            throw APIError.invalidResponse
        }
        
        return periods
    }
    
    /// Get available indicator types
    func getIndicatorTypes() async throws -> [String: Any] {
        let response = try await makeRequest(
            endpoint: "/indicators/types",
            responseType: APIResponse.self
        )
        
        guard let data = response.data else {
            throw APIError.noData
        }
        
        return data.value as? [String: Any] ?? [:]
    }
    
    // MARK: - Helper Methods
    
    private func extractAnalysisResult(from response: APIResponse) throws -> AnalysisResult {
        guard let data = response.data else {
            throw APIError.noData
        }
        
        // Extract analysis result from nested response
        let jsonData = try JSONSerialization.data(withJSONObject: data.value)
        let decoder = JSONDecoder()
        let analysisData = try decoder.decode([String: AnyCodable].self, from: jsonData)
        
        guard let analysisValue = analysisData["analysis"] else {
            throw APIError.missingAnalysisData
        }
        
        let analysisJson = try JSONSerialization.data(withJSONObject: analysisValue.value)
        return try decoder.decode(AnalysisResult.self, from: analysisJson)
    }
}

// MARK: - API Errors
enum APIError: Error, LocalizedError {
    case invalidURL
    case invalidResponse
    case httpError(Int)
    case decodingError(Error)
    case noData
    case missingAnalysisData
    case invalidTicker
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid URL"
        case .invalidResponse:
            return "Invalid response"
        case .httpError(let code):
            return "HTTP error: \(code)"
        case .decodingError(let error):
            return "Decoding error: \(error.localizedDescription)"
        case .noData:
            return "No data in response"
        case .missingAnalysisData:
            return "Missing analysis data in response"
        case .invalidTicker:
            return "Invalid ticker symbol"
        }
    }
}

// MARK: - Usage Example
class TradingViewController {
    private let api = TechnicalAnalysisAPI()
    
    func analyzeStock(symbol: String) async {
        do {
            // First validate the ticker
            let isValid = try await api.validateTicker(symbol: symbol)
            guard isValid else {
                print("❌ Invalid ticker symbol: \(symbol)")
                return
            }
            
            // Get ticker information
            let tickerInfo = try await api.getTickerInfo(symbol: symbol)
            print("📊 Analyzing \(tickerInfo.name) (\(tickerInfo.symbol))")
            print("🏢 Sector: \(tickerInfo.sector ?? "Unknown")")
            
            // Create EMA crossover strategy
            let emaRequest = EMAStrategyRequest(
                name: "iOS EMA Strategy",
                description: "12/26 EMA crossover from iOS app",
                symbol: symbol,
                period: .oneYear,
                interval: .oneDay,
                fastPeriod: 12,
                slowPeriod: 26
            )
            
            let emaResult = try await api.createEMAStrategy(request: emaRequest)
            
            print("\n📈 EMA Strategy Results for \(emaResult.symbol):")
            print("📊 Data Points: \(emaResult.dataInfo.dataPoints)")
            print("📅 Period: \(emaResult.dataInfo.startDate) to \(emaResult.dataInfo.endDate)")
            print("💰 Price Range: $\(emaResult.dataInfo.priceRange[0]) - $\(emaResult.dataInfo.priceRange[1])")
            print("📈 Indicators: \(emaResult.indicators.count)")
            print("🚦 Entry Signals: \(emaResult.entrySignals.count)")
            print("🛑 Exit Signals: \(emaResult.exitSignals.count)")
            
            // Create Multi-EMA strategy
            let multiEMARequest = MultiEMAStrategyRequest(
                name: "Triple EMA Strategy",
                description: "5/20/50 EMA multiple crossovers",
                symbol: symbol,
                period: .twoYears,
                interval: .oneDay,
                emaPeriods: [5, 20, 50]
            )
            
            let multiEMAResult = try await api.createMultiEMAStrategy(request: multiEMARequest)
            
            print("\n📊 Multi-EMA Strategy Results:")
            print("📈 Indicators: \(multiEMAResult.indicators.count)")
            print("🚦 Total Signals: \(multiEMAResult.signals.count)")
            
            // Create RSI strategy
            let rsiRequest = RSIStrategyRequest(
                name: "RSI Strategy",
                description: "14-period RSI with 30/70 thresholds",
                symbol: symbol,
                period: .sixMonths,
                interval: .oneDay,
                rsiPeriod: 14,
                oversoldThreshold: 30,
                overboughtThreshold: 70
            )
            
            let rsiResult = try await api.createRSIStrategy(request: rsiRequest)
            
            print("\n📊 RSI Strategy Results:")
            print("📈 RSI Indicator: \(rsiResult.indicators.first?.name ?? "Unknown")")
            print("🚦 Entry Signals: \(rsiResult.entrySignals.count)")
            print("🛑 Exit Signals: \(rsiResult.exitSignals.count)")
            
            // Update UI with results
            DispatchQueue.main.async {
                self.updateChartWithAnalysis(emaResult)
                self.updateTickerInfo(tickerInfo)
                self.updateSignalsList(multiEMAResult.entrySignals + multiEMAResult.exitSignals)
            }
            
        } catch {
            print("❌ API Error: \(error.localizedDescription)")
            // Handle error appropriately in UI
        }
    }
    
    private func updateChartWithAnalysis(_ result: AnalysisResult) {
        // Update trading chart with indicator lines
        for indicator in result.indicators {
            print("📊 Adding \(indicator.name) (\(indicator.type)) to chart with \(indicator.values.count) points")
            // Implement chart update logic here
        }
    }
    
    private func updateTickerInfo(_ info: TickerInfo) {
        // Update ticker information display
        print("🏢 Company: \(info.name)")
        print("🏭 Industry: \(info.industry ?? "Unknown")")
        print("💱 Currency: \(info.currency)")
    }
    
    private func updateSignalsList(_ signals: [SignalPoint]) {
        // Update signals list in UI
        let sortedSignals = signals.sorted { signal1, signal2 in
            let formatter = ISO8601DateFormatter()
            let date1 = formatter.date(from: signal1.timestamp) ?? Date.distantPast
            let date2 = formatter.date(from: signal2.timestamp) ?? Date.distantPast
            return date1 > date2
        }
        
        print("\n🚦 Recent signals:")
        for signal in sortedSignals.prefix(5) {
            let formatter = ISO8601DateFormatter()
            if let date = formatter.date(from: signal.timestamp) {
                let dateFormatter = DateFormatter()
                dateFormatter.dateStyle = .short
                print("📅 \(dateFormatter.string(from: date)): \(signal.signalType) (\(signal.ruleName))")
            }
        }
    }
}

// MARK: - Example Usage in SwiftUI
import SwiftUI

struct TradingView: View {
    @StateObject private var viewModel = TradingViewModel()
    @State private var selectedSymbol = "AAPL"
    @State private var selectedPeriod = Period.oneYear
    @State private var selectedStrategy = StrategyType.ema
    
    enum StrategyType: String, CaseIterable {
        case ema = "EMA Crossover"
        case multiEMA = "Multi-EMA"
        case rsi = "RSI"
    }
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                // Header
                Text("Technical Analysis")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .padding()
                
                // Input Section
                VStack(alignment: .leading, spacing: 16) {
                    Text("Stock Analysis")
                        .font(.headline)
                    
                    // Symbol input
                    HStack {
                        Text("Symbol:")
                            .font(.subheadline)
                            .frame(width: 80, alignment: .leading)
                        
                        TextField("AAPL", text: $selectedSymbol)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .autocapitalization(.allCharacters)
                    }
                    
                    // Period picker
                    HStack {
                        Text("Period:")
                            .font(.subheadline)
                            .frame(width: 80, alignment: .leading)
                        
                        Picker("Period", selection: $selectedPeriod) {
                            ForEach(Period.allCases, id: \.self) { period in
                                Text(period.displayName).tag(period)
                            }
                        }
                        .pickerStyle(MenuPickerStyle())
                    }
                    
                    // Strategy picker
                    HStack {
                        Text("Strategy:")
                            .font(.subheadline)
                            .frame(width: 80, alignment: .leading)
                        
                        Picker("Strategy", selection: $selectedStrategy) {
                            ForEach(StrategyType.allCases, id: \.self) { strategy in
                                Text(strategy.rawValue).tag(strategy)
                            }
                        }
                        .pickerStyle(SegmentedPickerStyle())
                    }
                }
                .padding(.horizontal)
                
                // Action Button
                Button(action: {
                    Task {
                        await viewModel.runAnalysis(
                            symbol: selectedSymbol,
                            period: selectedPeriod,
                            strategy: selectedStrategy
                        )
                    }
                }) {
                    HStack {
                        if viewModel.isLoading {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                .scaleEffect(0.8)
                        }
                        Text(viewModel.isLoading ? "Analyzing..." : "Analyze Stock")
                    }
                    .font(.headline)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(viewModel.isLoading ? Color.gray : Color.blue)
                    .cornerRadius(12)
                }
                .disabled(viewModel.isLoading || selectedSymbol.isEmpty)
                .padding(.horizontal)
                
                // Results Section
                if let result = viewModel.analysisResult {
                    ScrollView {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Analysis Results")
                                .font(.headline)
                                .padding(.bottom, 4)
                            
                            // Stock Info
                            if let tickerInfo = viewModel.tickerInfo {
                                VStack(alignment: .leading, spacing: 8) {
                                    Text("\(tickerInfo.name) (\(tickerInfo.symbol))")
                                        .font(.title2)
                                        .fontWeight(.semibold)
                                    
                                    if let sector = tickerInfo.sector {
                                        Text("Sector: \(sector)")
                                            .font(.subheadline)
                                            .foregroundColor(.secondary)
                                    }
                                }
                                .padding()
                                .background(Color(.systemGray6))
                                .cornerRadius(8)
                            }
                            
                            // Data Info
                            VStack(alignment: .leading, spacing: 4) {
                                Text("Data: \(result.dataInfo.dataPoints) points")
                                Text("Period: \(formatDate(result.dataInfo.startDate)) - \(formatDate(result.dataInfo.endDate))")
                                Text("Price Range: $\(String(format: "%.2f", result.dataInfo.priceRange[0])) - $\(String(format: "%.2f", result.dataInfo.priceRange[1]))")
                            }
                            .font(.caption)
                            .padding()
                            .background(Color(.systemGray6))
                            .cornerRadius(8)
                            
                            // Indicators
                            VStack(alignment: .leading, spacing: 4) {
                                Text("Indicators: \(result.indicators.count)")
                                ForEach(result.indicators, id: \.name) { indicator in
                                    Text("• \(indicator.name) (\(indicator.type)): \(indicator.values.count) values")
                                        .font(.caption)
                                }
                            }
                            .padding()
                            .background(Color.green.opacity(0.1))
                            .cornerRadius(8)
                            
                            // Signals
                            HStack(spacing: 16) {
                                VStack {
                                    Text("\(result.entrySignals.count)")
                                        .font(.title2)
                                        .fontWeight(.bold)
                                        .foregroundColor(.green)
                                    Text("Entry Signals")
                                        .font(.caption)
                                }
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.green.opacity(0.1))
                                .cornerRadius(8)
                                
                                VStack {
                                    Text("\(result.exitSignals.count)")
                                        .font(.title2)
                                        .fontWeight(.bold)
                                        .foregroundColor(.red)
                                    Text("Exit Signals")
                                        .font(.caption)
                                }
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.red.opacity(0.1))
                                .cornerRadius(8)
                            }
                        }
                        .padding(.horizontal)
                    }
                }
                
                Spacer()
            }
            .navigationTitle("TA Analysis")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
    
    private func formatDate(_ dateString: String) -> String {
        let formatter = ISO8601DateFormatter()
        guard let date = formatter.date(from: dateString) else { return dateString }
        
        let displayFormatter = DateFormatter()
        displayFormatter.dateStyle = .short
        return displayFormatter.string(from: date)
    }
}

@MainActor
class TradingViewModel: ObservableObject {
    @Published var isLoading = false
    @Published var analysisResult: AnalysisResult?
    @Published var tickerInfo: TickerInfo?
    @Published var errorMessage: String?
    
    private let api = TechnicalAnalysisAPI()
    
    func runAnalysis(symbol: String, period: Period, strategy: TradingView.StrategyType) async {
        isLoading = true
        errorMessage = nil
        
        do {
            // Validate ticker first
            let isValid = try await api.validateTicker(symbol: symbol)
            guard isValid else {
                errorMessage = "Invalid ticker symbol: \(symbol)"
                isLoading = false
                return
            }
            
            // Get ticker info
            tickerInfo = try await api.getTickerInfo(symbol: symbol)
            
            // Run analysis based on strategy type
            let result: AnalysisResult
            
            switch strategy {
            case .ema:
                let request = EMAStrategyRequest(
                    name: "iOS EMA Strategy",
                    description: "EMA crossover from iOS app",
                    symbol: symbol,
                    period: period,
                    interval: .oneDay,
                    fastPeriod: 12,
                    slowPeriod: 26
                )
                result = try await api.createEMAStrategy(request: request)
                
            case .multiEMA:
                let request = MultiEMAStrategyRequest(
                    name: "Multi-EMA Strategy",
                    description: "Multiple EMA crossovers",
                    symbol: symbol,
                    period: period,
                    interval: .oneDay,
                    emaPeriods: [5, 20, 50]
                )
                result = try await api.createMultiEMAStrategy(request: request)
                
            case .rsi:
                let request = RSIStrategyRequest(
                    name: "RSI Strategy",
                    description: "RSI overbought/oversold",
                    symbol: symbol,
                    period: period,
                    interval: .oneDay,
                    rsiPeriod: 14,
                    oversoldThreshold: 30,
                    overboughtThreshold: 70
                )
                result = try await api.createRSIStrategy(request: request)
            }
            
            analysisResult = result
            
        } catch {
            errorMessage = error.localizedDescription
        }
        
        isLoading = false
    }
} 
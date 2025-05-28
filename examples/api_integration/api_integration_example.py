"""
API Integration Example - Google (GOOGL) Analysis
This example shows how to use the Technical Analysis FastAPI for real stock analysis.
Perfect reference for iOS developers to understand API integration.
"""

import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import json
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8001"

class TechnicalAnalysisAPI:
    """
    API client for Technical Analysis endpoints
    This shows exactly how to integrate with the FastAPI from iOS
    """
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check if the API is running
        iOS equivalent: GET request to /health
        """
        print("🔍 Checking API health...")
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        result = response.json()
        print(f"   ✅ API Status: {result['status']}")
        return result
    
    def get_available_periods(self) -> Dict[str, Any]:
        """
        Get available time periods and intervals
        iOS equivalent: GET request to /periods
        """
        print("📅 Fetching available periods...")
        response = self.session.get(f"{self.base_url}/periods")
        response.raise_for_status()
        result = response.json()
        periods = result['data']['periods']
        intervals = result['data']['intervals']
        print(f"   📊 Available periods: {periods[:5]}...")  # Show first 5
        print(f"   ⏰ Available intervals: {intervals[:5]}...")
        return result
    
    def validate_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        Validate if a ticker symbol exists
        iOS equivalent: GET request to /tickers/{symbol}/validate
        """
        print(f"🔍 Validating ticker symbol: {symbol}")
        response = self.session.get(f"{self.base_url}/tickers/{symbol}/validate")
        response.raise_for_status()
        result = response.json()
        is_valid = result['data']['is_valid']
        print(f"   {'✅' if is_valid else '❌'} {symbol}: {result['data']['message']}")
        return result
    
    def get_ticker_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get company information for a ticker
        iOS equivalent: GET request to /tickers/{symbol}/info
        """
        print(f"📊 Fetching company info for {symbol}...")
        response = self.session.get(f"{self.base_url}/tickers/{symbol}/info")
        response.raise_for_status()
        result = response.json()
        info = result['data']
        print(f"   🏢 Company: {info['name']}")
        print(f"   🏭 Sector: {info.get('sector', 'Unknown')}")
        print(f"   🔧 Industry: {info.get('industry', 'Unknown')}")
        return result
    
    def create_ema_strategy(self, symbol: str, period: str = "1y", interval: str = "1d", 
                          fast_period: int = 12, slow_period: int = 26) -> Dict[str, Any]:
        """
        Create and analyze EMA crossover strategy
        iOS equivalent: POST request to /strategies/ema-crossover
        """
        print(f"📈 Creating EMA crossover strategy for {symbol}...")
        
        request_data = {
            "name": f"{symbol} EMA Crossover Strategy",
            "description": f"EMA crossover analysis for {symbol} stock",
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "fast_period": fast_period,
            "slow_period": slow_period
        }
        
        print(f"   📤 Request: {json.dumps(request_data, indent=2)}")
        
        response = self.session.post(
            f"{self.base_url}/strategies/ema-crossover",
            json=request_data
        )
        response.raise_for_status()
        result = response.json()
        
        analysis = result['data']['analysis']
        print(f"   ✅ Strategy created successfully")
        print(f"   📊 Data points analyzed: {analysis['data_info']['data_points']}")
        print(f"   📈 Indicators calculated: {len(analysis['indicators'])}")
        print(f"   🎯 Entry signals: {len(analysis['entry_signals'])}")
        print(f"   🛑 Exit signals: {len(analysis['exit_signals'])}")
        
        return result
    
    def create_rsi_strategy(self, symbol: str, period: str = "6mo", interval: str = "1d",
                           rsi_period: int = 14, oversold: float = 30, overbought: float = 70) -> Dict[str, Any]:
        """
        Create and analyze RSI strategy
        iOS equivalent: POST request to /strategies/rsi
        """
        print(f"📊 Creating RSI strategy for {symbol}...")
        
        request_data = {
            "name": f"{symbol} RSI Strategy",
            "description": f"RSI overbought/oversold analysis for {symbol}",
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "rsi_period": rsi_period,
            "oversold_threshold": oversold,
            "overbought_threshold": overbought
        }
        
        print(f"   📤 Request: {json.dumps(request_data, indent=2)}")
        
        response = self.session.post(
            f"{self.base_url}/strategies/rsi",
            json=request_data
        )
        response.raise_for_status()
        result = response.json()
        
        analysis = result['data']['analysis']
        print(f"   ✅ RSI strategy created successfully")
        print(f"   📊 RSI signals: Entry({len(analysis['entry_signals'])}), Exit({len(analysis['exit_signals'])})")
        
        return result
    
    def backtest_strategy(self, symbol: str, period: str = "1y", initial_cash: float = 10000,
                         commission: float = 0.001) -> Dict[str, Any]:
        """
        Backtest an EMA strategy
        iOS equivalent: POST request to /backtest/ticker
        """
        print(f"💰 Running backtest for {symbol}...")
        
        # Create a simple EMA strategy for backtesting
        strategy = {
            "name": f"{symbol} Backtest Strategy",
            "description": "EMA crossover strategy for backtesting",
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
                },
                {
                    "name": "ema_cross_exit",
                    "fast_indicator": "ema_fast",
                    "slow_indicator": "ema_slow",
                    "direction": "below",
                    "signal_type": "exit"
                }
            ],
            "threshold_rules": []
        }
        
        request_data = {
            "strategy": strategy,
            "ticker": {
                "symbol": symbol,
                "period": period,
                "interval": "1d"
            },
            "params": {
                "initial_cash": initial_cash,
                "commission": commission
            }
        }
        
        response = self.session.post(
            f"{self.base_url}/backtest/ticker",
            json=request_data
        )
        response.raise_for_status()
        result = response.json()
        
        backtest = result['data']
        print(f"   ✅ Backtest completed")
        print(f"   💰 Total return: {backtest['total_return']:.2%}")
        print(f"   📊 Sharpe ratio: {backtest['sharpe_ratio']:.2f}")
        print(f"   📉 Max drawdown: {backtest['max_drawdown']:.2%}")
        print(f"   🎯 Win rate: {backtest['win_rate']:.2%}")
        print(f"   🔄 Total trades: {backtest['total_trades']}")
        print(f"   💵 Final value: ${backtest['final_value']:,.2f}")
        
        return result
    
    def create_custom_strategy(self, symbol: str, indicators: list, period: str = "6mo") -> Dict[str, Any]:
        """
        Create a custom strategy with specified indicators
        iOS equivalent: POST request to /strategies/custom with query params and JSON body
        """
        print(f"🛠️ Creating custom strategy for {symbol}...")
        
        # Query parameters
        params = {
            "name": f"{symbol} Custom Strategy",
            "symbol": symbol,
            "description": f"Custom multi-indicator analysis for {symbol}",
            "period": period,
            "interval": "1d"
        }
        
        print(f"   📤 Params: {params}")
        print(f"   📤 Indicators: {json.dumps(indicators, indent=2)}")
        
        response = self.session.post(
            f"{self.base_url}/strategies/custom",
            params=params,
            json=indicators
        )
        response.raise_for_status()
        result = response.json()
        
        analysis = result['data']['analysis']
        print(f"   ✅ Custom strategy created")
        print(f"   📊 Indicators: {len(analysis['indicators'])}")
        for indicator in analysis['indicators']:
            print(f"      • {indicator['name']}: {indicator['type']}")
        
        return result


def main():
    """
    Complete API integration example for iOS developers
    Shows the exact sequence of API calls needed for technical analysis
    """
    print("🚀 Technical Analysis API Integration Example")
    print("📱 Perfect reference for iOS development")
    print("=" * 60)
    
    # Initialize API client
    api = TechnicalAnalysisAPI()
    
    # STEP 1: Health Check (Always do this first)
    print("\n" + "="*50)
    print("STEP 1: API Health Check")
    print("="*50)
    try:
        health = api.health_check()
    except requests.exceptions.ConnectionError:
        print("❌ API server is not running!")
        print("💡 Start the server with: python -c \"import uvicorn; uvicorn.run('src.app.main:app', host='0.0.0.0', port=8001)\"")
        return
    
    # STEP 2: Get Available Options
    print("\n" + "="*50)
    print("STEP 2: Fetch Available Periods & Intervals")
    print("="*50)
    periods_info = api.get_available_periods()
    
    # STEP 3: Validate and Get Company Info
    print("\n" + "="*50)
    print("STEP 3: Ticker Validation & Company Information")
    print("="*50)
    symbol = "GOOGL"  # Google stock
    validation = api.validate_ticker(symbol)
    
    if validation['data']['is_valid']:
        company_info = api.get_ticker_info(symbol)
    else:
        print(f"❌ {symbol} is not a valid ticker symbol")
        return
    
    # STEP 4: EMA Crossover Analysis
    print("\n" + "="*50)
    print("STEP 4: EMA Crossover Strategy Analysis")
    print("="*50)
    ema_result = api.create_ema_strategy(
        symbol=symbol,
        period="1y",  # 1 year of data
        interval="1d",  # Daily data
        fast_period=12,  # 12-day EMA
        slow_period=26   # 26-day EMA
    )
    
    # STEP 5: RSI Analysis
    print("\n" + "="*50)
    print("STEP 5: RSI Strategy Analysis")
    print("="*50)
    rsi_result = api.create_rsi_strategy(
        symbol=symbol,
        period="6mo",  # 6 months of data
        rsi_period=14,
        oversold=30,
        overbought=70
    )
    
    # STEP 6: Custom Multi-Indicator Strategy
    print("\n" + "="*50)
    print("STEP 6: Custom Multi-Indicator Strategy")
    print("="*50)
    custom_indicators = [
        {
            "name": "ema_short",
            "type": "EMA",
            "params": {"window": 10}
        },
        {
            "name": "ema_long",
            "type": "EMA",
            "params": {"window": 50}
        },
        {
            "name": "rsi_momentum",
            "type": "RSI",
            "params": {"window": 14}
        }
    ]
    
    custom_result = api.create_custom_strategy(
        symbol=symbol,
        indicators=custom_indicators,
        period="1y"
    )
    
    # STEP 7: Backtesting
    print("\n" + "="*50)
    print("STEP 7: Strategy Backtesting")
    print("="*50)
    backtest_result = api.backtest_strategy(
        symbol=symbol,
        period="1y",
        initial_cash=10000,
        commission=0.001  # 0.1% commission
    )
    
    # STEP 8: Create Visualization from API Data
    print("\n" + "="*50)
    print("STEP 8: Data Visualization")
    print("="*50)
    create_api_visualization(ema_result, symbol)
    
    # STEP 9: Summary for iOS Developer
    print("\n" + "="*60)
    print("📱 iOS INTEGRATION SUMMARY")
    print("="*60)
    print_ios_integration_guide(ema_result, backtest_result)
    
    return ema_result, rsi_result, custom_result, backtest_result


def create_api_visualization(ema_result: Dict[str, Any], symbol: str):
    """
    Create visualization from API response data
    Shows how to process API responses for charts
    """
    print("📊 Creating visualization from API response...")
    
    # Extract data from API response
    analysis = ema_result['data']['analysis']
    indicators = analysis['indicators']
    entry_signals = analysis['entry_signals']
    exit_signals = analysis['exit_signals']
    data_info = analysis['data_info']
    
    print(f"   ✅ API Response Processing Complete")
    print(f"   📊 Data period: {data_info['start_date']} to {data_info['end_date']}")
    print(f"   📈 Data points: {data_info['data_points']}")
    print(f"   📊 Indicators available: {len(indicators)}")
    
    # Show indicator details
    for indicator in indicators:
        print(f"      • {indicator['name']}: {indicator['type']} ({len(indicator['values'])} data points)")
    
    print(f"   🎯 Entry signals: {len(entry_signals)} signals")
    if entry_signals:
        print(f"      • First signal: {entry_signals[0]['timestamp']}")
        print(f"      • Signal type: {entry_signals[0]['signal_type']}")
        print(f"      • Rule name: {entry_signals[0]['rule_name']}")
    
    print(f"   🛑 Exit signals: {len(exit_signals)} signals")
    if exit_signals:
        print(f"      • First signal: {exit_signals[0]['timestamp']}")
    
    # Create a simple summary plot showing indicator data structure
    # This is what iOS developers need to understand for chart integration
    print("\n📱 iOS Chart Integration Guide:")
    print("   1. Extract 'indicators' array from API response")
    print("   2. Each indicator has 'values' array with timestamp-value pairs")
    print("   3. Extract 'entry_signals' and 'exit_signals' arrays")
    print("   4. Each signal has timestamp, signal_type, and rule_name")
    print("   5. Use Core Plot or similar iOS framework to render charts")
    
    # Show example data structure for iOS
    if indicators:
        first_indicator = indicators[0]
        print(f"\n💡 Example Indicator Data Structure:")
        print(f"   Name: {first_indicator['name']}")
        print(f"   Type: {first_indicator['type']}")
        print(f"   Parameters: {first_indicator['params']}")
        if first_indicator['values']:
            sample_value = first_indicator['values'][0]
            print(f"   Sample Value: {sample_value}")
    
    # Save a simple text summary instead of complex plot
    filename = f"{symbol}_api_analysis_summary.txt"
    with open(filename, 'w') as f:
        f.write(f"API Analysis Summary for {symbol}\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Data Period: {data_info['start_date']} to {data_info['end_date']}\n")
        f.write(f"Data Points: {data_info['data_points']}\n")
        f.write(f"Indicators: {len(indicators)}\n")
        f.write(f"Entry Signals: {len(entry_signals)}\n")
        f.write(f"Exit Signals: {len(exit_signals)}\n\n")
        
        f.write("Indicators:\n")
        for indicator in indicators:
            f.write(f"  - {indicator['name']}: {indicator['type']}\n")
            f.write(f"    Parameters: {indicator['params']}\n")
            f.write(f"    Data Points: {len(indicator['values'])}\n\n")
    
    print(f"   ✅ Analysis summary saved: {filename}")
    print(f"   📊 This shows the data structure for iOS chart integration")


def print_ios_integration_guide(ema_result: Dict[str, Any], backtest_result: Dict[str, Any]):
    """
    Print integration guide for iOS developers
    """
    print("📱 KEY API ENDPOINTS FOR iOS:")
    print("   • GET  /health - Check API status")
    print("   • GET  /periods - Get available time periods")
    print("   • GET  /tickers/{symbol}/validate - Validate ticker")
    print("   • GET  /tickers/{symbol}/info - Get company info")
    print("   • POST /strategies/ema-crossover - EMA analysis")
    print("   • POST /strategies/rsi - RSI analysis")
    print("   • POST /strategies/custom - Custom indicators")
    print("   • POST /backtest/ticker - Strategy backtesting")
    
    print("\n📊 TYPICAL API RESPONSE STRUCTURE:")
    print("   {")
    print("     'status': 'success',")
    print("     'message': 'Analysis completed...',")
    print("     'data': {")
    print("       'analysis': {")
    print("         'symbol': 'GOOGL',")
    print("         'indicators': [...],")
    print("         'entry_signals': [...],")
    print("         'exit_signals': [...],")
    print("         'data_info': {...}")
    print("       }")
    print("     },")
    print("     'timestamp': '2024-...'")
    print("   }")
    
    print("\n🚀 RECOMMENDED iOS WORKFLOW:")
    print("   1. Health check on app startup")
    print("   2. Validate ticker symbol as user types")
    print("   3. Fetch company info for display")
    print("   4. Choose strategy type (EMA, RSI, Custom)")
    print("   5. Call appropriate strategy endpoint")
    print("   6. Process indicators and signals for charts")
    print("   7. Optional: Run backtesting for performance")
    
    print("\n💡 iOS TIPS:")
    analysis = ema_result['data']['analysis']
    print(f"   • API returns {len(analysis['indicators'])} indicators with time series data")
    print(f"   • Each signal has timestamp, type, and rule name")
    print(f"   • Data info includes {analysis['data_info']['data_points']} data points")
    print("   • All timestamps are ISO format for easy parsing")
    print("   • Use async/await for API calls")
    print("   • Handle 400/500 errors gracefully")
    print("   • Cache company info to reduce API calls")


if __name__ == "__main__":
    try:
        print("🌐 Make sure the API server is running on http://localhost:8001")
        print("💡 Start with: python -c \"import uvicorn; uvicorn.run('src.app.main:app', host='0.0.0.0', port=8001)\"")
        print()
        
        results = main()
        
        print("\n🎉 API Integration Example Completed Successfully!")
        print("📱 This example shows exactly how to integrate with the API from iOS")
        print("🌐 Open the generated HTML file to see the visualization")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc() 
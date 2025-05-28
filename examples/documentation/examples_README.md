# Technical Analysis Strategy Examples

This folder contains a professional example demonstrating real market data analysis using the Technical Analysis Strategy Framework.

## Real Market Data Analysis

### `real_data_example.py` ⭐ **PROFESSIONAL MARKET ANALYSIS**
**Google Stock Analysis** - Professional example using real Yahoo Finance data:
- Fetches real Google (GOOGL) stock data from Yahoo Finance
- Uses last 1 year of actual market data
- Enhanced Plotly visualizations with professional styling
- Real backtest results on live market data
- Detailed performance analysis with profit/loss calculations

**Usage:**
```bash
cd examples
python real_data_example.py
```

**Output:**
- `google_comprehensive_analysis.html` - **Complete 3-panel analysis with cumulative returns**
- `google_signal_timeline.html` - Trading signal timeline for Google stock
- Real performance metrics (recent results: +7.52% return, 0.55 Sharpe ratio)

## Real Market Results

The example recently analyzed Google (GOOGL) stock and achieved:
- **📊 Total Return**: +7.52% over 1 year
- **⚖️ Sharpe Ratio**: 0.55 (risk-adjusted performance)
- **📉 Max Drawdown**: -17.84% (worst decline)
- **💰 Profit**: $752 on $10,000 investment
- **🎯 Signals**: 4 buy signals, 4 sell signals over 250 trading days

## Understanding the Analysis

The comprehensive interactive plot shows three panels:

**Panel 1: Stock Price & Indicators**
- **Price data** (black line) - Actual stock prices from Yahoo Finance
- **EMA indicators** (blue = fast 12-day, red = slow 26-day)
- **Buy signals** (green triangles ↗️) - When fast EMA crosses above slow EMA
- **Sell signals** (red triangles ↘️) - When fast EMA crosses below slow EMA

**Panel 2: Signal Timeline**
- Visual representation of when buy/sell signals occur over time

**Panel 3: Cumulative Strategy Returns**
- **Portfolio performance** over time showing cumulative returns (%)
- **Break-even line** (0%) for reference
- Shows how the strategy performs compared to buy-and-hold

## Strategy Logic

The EMA crossover strategy works as follows:
- **Buy Signal**: When fast EMA crosses above slow EMA (bullish trend)
- **Sell Signal**: When fast EMA crosses below slow EMA (bearish trend)

This is a classic technical analysis strategy used by professional traders.

## Customizing for Different Stocks

### Change the stock symbol:
```python
# In real_data_example.py, modify the fetch function:
ticker = yf.Ticker("AAPL")  # Apple
ticker = yf.Ticker("TSLA")  # Tesla
ticker = yf.Ticker("MSFT")  # Microsoft
ticker = yf.Ticker("NVDA")  # NVIDIA
ticker = yf.Ticker("SPY")   # S&P 500 ETF
```

### Change time period:
```python
price_data = fetch_google_data(period="2y")  # 2 years
price_data = fetch_google_data(period="6mo") # 6 months
price_data = fetch_google_data(period="5y")  # 5 years
price_data = fetch_google_data(period="max") # All available data
```

### Adjust EMA periods for different strategies:
```python
# More sensitive (more signals)
strategy = StrategyBuilder.ema_crossover(
    name="Fast EMA Strategy",
    fast_period=5,   # Very fast
    slow_period=15   # Moderately slow
)

# Less sensitive (fewer, higher confidence signals)
strategy = StrategyBuilder.ema_crossover(
    name="Conservative EMA Strategy", 
    fast_period=20,  # Slower
    slow_period=50   # Much slower
)
```

## Professional Features

- **Real-time data fetching** from Yahoo Finance API
- **Fallback mechanism** if data is unavailable
- **Professional visualizations** with hover details
- **Risk metrics calculation** (Sharpe ratio, max drawdown)
- **Profit/loss analysis** with exact dollar amounts
- **Signal analysis** with dates and prices

## Requirements

```bash
# Install the package with all dependencies
pip install -e .[backtesting]
```

This includes:
- `yfinance` for real market data
- `plotly` for interactive visualizations
- `vectorbt` for professional backtesting
- `pandas` and `numpy` for data analysis

## Troubleshooting

**Import errors**: Make sure you're in the examples directory and the package is installed  
**No internet/Yahoo Finance issues**: The script will automatically fall back to sample data  
**No plots showing**: Open the generated HTML files in any web browser  
**Poor performance**: Try different EMA periods or analyze different stocks

## Advanced Usage

### Analyze Multiple Stocks
Run the analysis on different stocks to compare performance:
```bash
# Modify the script for different stocks and run multiple times
python real_data_example.py  # GOOGL
# Change to AAPL and run again
# Change to TSLA and run again
```

### Different Time Horizons
- **Short-term**: 6 months, fast EMAs (5,15)
- **Medium-term**: 1 year, standard EMAs (12,26) 
- **Long-term**: 2-5 years, slow EMAs (20,50)

### Performance Comparison
Compare the strategy performance across:
- Different stocks (tech vs financials vs energy)
- Different time periods (bull vs bear markets)
- Different EMA parameters (fast vs slow strategies)

## Next Steps

1. **Run the analysis**: `python real_data_example.py`
2. **Analyze different stocks**: Modify ticker symbols
3. **Experiment with parameters**: Try different EMA periods
4. **Compare time periods**: Test on different date ranges
5. **Build custom strategies**: Use this as a foundation for more complex analysis

This example provides a solid foundation for professional technical analysis using real market data. 
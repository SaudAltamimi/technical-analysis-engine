"""
Enhanced API Visualization - Shows Stock Prices + Technical Analysis
This creates a comprehensive visualization showing actual prices with EMA indicators and signals
"""

import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

API_BASE_URL = "http://localhost:8001"

def fetch_api_data_with_prices(symbol="GOOGL"):
    """Fetch both API analysis data and raw price data"""
    print(f"📊 Fetching API analysis for {symbol}...")
    
    # Get analysis from API
    request_data = {
        "name": f"{symbol} EMA Strategy",
        "symbol": symbol,
        "period": "1y",
        "interval": "1d",
        "fast_period": 12,
        "slow_period": 26
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/strategies/ema-crossover",
            json=request_data
        )
        response.raise_for_status()
        api_result = response.json()
        
        # Also fetch raw price data for the same period
        print(f"📈 Fetching raw price data for {symbol}...")
        ticker = yf.Ticker(symbol)
        price_data = ticker.history(period="1y")
        
        return api_result, price_data
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def create_enhanced_visualization(api_result, price_data, symbol):
    """Create comprehensive visualization with prices, EMAs, and signals"""
    print("📊 Creating enhanced visualization with prices...")
    
    analysis = api_result['data']['analysis']
    indicators = analysis['indicators']
    entry_signals = analysis['entry_signals']
    exit_signals = analysis['exit_signals']
    data_info = analysis['data_info']
    
    # Find EMA indicators
    ema_fast = None
    ema_slow = None
    
    for indicator in indicators:
        if 'fast' in indicator['name']:
            ema_fast = indicator
        elif 'slow' in indicator['name']:
            ema_slow = indicator
    
    if not ema_fast or not ema_slow:
        print("❌ Could not find EMA indicators")
        return
    
    # Convert EMA data to DataFrames
    fast_data = pd.DataFrame(ema_fast['values'])
    slow_data = pd.DataFrame(ema_slow['values'])
    
    # Convert timestamps
    fast_data['timestamp'] = pd.to_datetime(fast_data['timestamp'], utc=True)
    slow_data['timestamp'] = pd.to_datetime(slow_data['timestamp'], utc=True)
    
    # Prepare price data
    price_data = price_data.reset_index()
    price_data['Date'] = pd.to_datetime(price_data['Date'], utc=True)
    
    # Create the plot with 3 subplots
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        subplot_titles=[
            f'{symbol} Stock Price with EMA Analysis',
            'Volume',
            'Trading Signals Timeline'
        ],
        vertical_spacing=0.05,
        row_heights=[0.6, 0.2, 0.2],
        specs=[[{"secondary_y": False}],
               [{"secondary_y": False}],
               [{"secondary_y": False}]]
    )
    
    # 1. Add stock price (candlestick or line)
    fig.add_trace(
        go.Scatter(
            x=price_data['Date'],
            y=price_data['Close'],
            name=f'{symbol} Stock Price',
            line=dict(color='black', width=2),
            hovertemplate='<b>Stock Price</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # 2. Add EMA lines
    fig.add_trace(
        go.Scatter(
            x=fast_data['timestamp'],
            y=fast_data['value'],
            name=f'Fast EMA ({ema_fast["params"]["window"]})',
            line=dict(color='blue', width=1.5),
            hovertemplate='<b>Fast EMA</b><br>Date: %{x}<br>Value: $%{y:.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=slow_data['timestamp'],
            y=slow_data['value'],
            name=f'Slow EMA ({ema_slow["params"]["window"]})',
            line=dict(color='red', width=1.5),
            hovertemplate='<b>Slow EMA</b><br>Date: %{x}<br>Value: $%{y:.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # 3. Add trading signals on the price chart
    if entry_signals:
        entry_times = [pd.to_datetime(signal['timestamp'], utc=True) for signal in entry_signals]
        # Find actual prices at signal times
        signal_prices = []
        for entry_time in entry_times:
            # Find closest price data
            time_diff = abs(price_data['Date'] - entry_time)
            closest_idx = time_diff.idxmin()
            signal_prices.append(price_data.loc[closest_idx, 'Close'])
        
        fig.add_trace(
            go.Scatter(
                x=entry_times,
                y=signal_prices,
                mode='markers',
                name='📈 Buy Signals',
                marker=dict(
                    color='green',
                    size=15,
                    symbol='triangle-up',
                    line=dict(color='darkgreen', width=2)
                ),
                hovertemplate='<b>BUY SIGNAL</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'
            ),
            row=1, col=1
        )
    
    if exit_signals:
        exit_times = [pd.to_datetime(signal['timestamp'], utc=True) for signal in exit_signals]
        signal_prices = []
        for exit_time in exit_times:
            time_diff = abs(price_data['Date'] - exit_time)
            closest_idx = time_diff.idxmin()
            signal_prices.append(price_data.loc[closest_idx, 'Close'])
        
        fig.add_trace(
            go.Scatter(
                x=exit_times,
                y=signal_prices,
                mode='markers',
                name='📉 Sell Signals',
                marker=dict(
                    color='red',
                    size=15,
                    symbol='triangle-down',
                    line=dict(color='darkred', width=2)
                ),
                hovertemplate='<b>SELL SIGNAL</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'
            ),
            row=1, col=1
        )
    
    # 4. Add volume chart
    fig.add_trace(
        go.Bar(
            x=price_data['Date'],
            y=price_data['Volume'],
            name='Volume',
            marker_color='lightblue',
            opacity=0.7
        ),
        row=2, col=1
    )
    
    # 5. Add signal timeline
    # Create signal intensity over time
    signal_timeline = pd.DataFrame({
        'date': price_data['Date'],
        'entry_activity': 0,
        'exit_activity': 0
    })
    
    # Mark actual signal dates
    for signal in entry_signals:
        signal_date = pd.to_datetime(signal['timestamp'], utc=True)
        # Find closest date in timeline
        time_diff = abs(signal_timeline['date'] - signal_date)
        closest_idx = time_diff.idxmin()
        signal_timeline.loc[closest_idx, 'entry_activity'] = 1
    
    for signal in exit_signals:
        signal_date = pd.to_datetime(signal['timestamp'], utc=True)
        time_diff = abs(signal_timeline['date'] - signal_date)
        closest_idx = time_diff.idxmin()
        signal_timeline.loc[closest_idx, 'exit_activity'] = -1
    
    fig.add_trace(
        go.Scatter(
            x=signal_timeline['date'],
            y=signal_timeline['entry_activity'],
            fill='tonexty',
            name='Buy Activity',
            line=dict(color='green', width=1),
            fillcolor='rgba(0,255,0,0.3)'
        ),
        row=3, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=signal_timeline['date'],
            y=signal_timeline['exit_activity'],
            fill='tonexty',
            name='Sell Activity',
            line=dict(color='red', width=1),
            fillcolor='rgba(255,0,0,0.3)'
        ),
        row=3, col=1
    )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=f"{symbol} Complete Technical Analysis - Price, EMAs & Signals",
            font=dict(size=18)
        ),
        height=900,
        template="plotly_white",
        showlegend=True,
        hovermode='x unified'
    )
    
    # Update axes
    fig.update_xaxes(title_text="Date", row=3, col=1)
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_yaxes(title_text="Signal Activity", row=3, col=1, range=[-1.2, 1.2])
    
    # Save the enhanced chart
    filename = f"{symbol}_complete_analysis.html"
    fig.write_html(filename)
    
    print(f"   ✅ Enhanced chart saved: {filename}")
    print(f"   📊 Period: {data_info['start_date'][:10]} to {data_info['end_date'][:10]}")
    print(f"   📈 Data points: {data_info['data_points']}")
    print(f"   💰 Price range: ${data_info['price_range'][0]:.2f} - ${data_info['price_range'][1]:.2f}")
    print(f"   🎯 Entry signals: {len(entry_signals)}")
    print(f"   🛑 Exit signals: {len(exit_signals)}")
    
    return filename

def print_enhanced_summary(api_result, price_data, symbol):
    """Print comprehensive analysis summary"""
    analysis = api_result['data']['analysis']
    data_info = analysis['data_info']
    
    print("\n" + "="*70)
    print(f"📊 COMPLETE TECHNICAL ANALYSIS SUMMARY FOR {symbol}")
    print("="*70)
    
    # Price analysis
    current_price = price_data['Close'].iloc[-1]
    price_change = current_price - price_data['Close'].iloc[0]
    price_change_pct = (price_change / price_data['Close'].iloc[0]) * 100
    
    print(f"💰 PRICE ANALYSIS:")
    print(f"   Current Price: ${current_price:.2f}")
    print(f"   Period Change: ${price_change:.2f} ({price_change_pct:+.2f}%)")
    print(f"   52-Week High: ${price_data['High'].max():.2f}")
    print(f"   52-Week Low: ${price_data['Low'].min():.2f}")
    print(f"   Average Volume: {price_data['Volume'].mean():,.0f}")
    
    print(f"\n📊 TECHNICAL INDICATORS:")
    for indicator in analysis['indicators']:
        current_value = indicator['values'][-1]['value']
        print(f"   • {indicator['name']}: ${current_value:.2f}")
        print(f"     Type: {indicator['type']}")
        print(f"     Parameters: {indicator['params']}")
    
    print(f"\n🎯 TRADING SIGNALS ANALYSIS:")
    print(f"   📈 Buy Signals: {len(analysis['entry_signals'])}")
    if analysis['entry_signals']:
        latest_entry = analysis['entry_signals'][-1]
        print(f"      Latest: {latest_entry['timestamp'][:10]} ({latest_entry['rule_name']})")
    
    print(f"   📉 Sell Signals: {len(analysis['exit_signals'])}")
    if analysis['exit_signals']:
        latest_exit = analysis['exit_signals'][-1]
        print(f"      Latest: {latest_exit['timestamp'][:10]} ({latest_exit['rule_name']})")
    
    # Signal performance analysis
    if analysis['entry_signals'] and analysis['exit_signals']:
        print(f"\n📈 SIGNAL PERFORMANCE:")
        entry_dates = [pd.to_datetime(s['timestamp']) for s in analysis['entry_signals']]
        exit_dates = [pd.to_datetime(s['timestamp']) for s in analysis['exit_signals']]
        
        print(f"   Total Trading Opportunities: {min(len(entry_dates), len(exit_dates))}")
        print(f"   Signal Frequency: {len(entry_dates + exit_dates)} signals over 1 year")

def main():
    """Main function"""
    symbol = "GOOGL"
    
    print("🚀 Enhanced API Visualization with Stock Prices")
    print("=" * 60)
    
    # Fetch both API data and price data
    api_result, price_data = fetch_api_data_with_prices(symbol)
    if not api_result or price_data is None:
        print("❌ Could not fetch required data")
        return
    
    # Create enhanced visualization
    chart_file = create_enhanced_visualization(api_result, price_data, symbol)
    
    # Print comprehensive summary
    print_enhanced_summary(api_result, price_data, symbol)
    
    print(f"\n🎉 Enhanced Visualization Complete!")
    print(f"📂 Open {chart_file} in your browser")
    print(f"💡 Now shows actual stock prices with EMA indicators and signals")
    print(f"📱 Perfect for demonstrating to iOS developer")

if __name__ == "__main__":
    main() 
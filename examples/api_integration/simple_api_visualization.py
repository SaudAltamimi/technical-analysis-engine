"""
Simple API Visualization - Shows API Response Data
This creates a clean visualization from the Technical Analysis API
"""

import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

API_BASE_URL = "http://localhost:8001"

def fetch_api_data(symbol="GOOGL"):
    """Fetch data from the API"""
    print(f"📊 Fetching API data for {symbol}...")
    
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
        return response.json()
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def create_visualization(api_result, symbol):
    """Create visualization from API data"""
    print("📊 Creating visualization...")
    
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
    
    # Convert to DataFrames
    fast_data = pd.DataFrame(ema_fast['values'])
    slow_data = pd.DataFrame(ema_slow['values'])
    
    # Convert timestamps with UTC handling
    fast_data['timestamp'] = pd.to_datetime(fast_data['timestamp'], utc=True)
    slow_data['timestamp'] = pd.to_datetime(slow_data['timestamp'], utc=True)
    
    # Create the plot
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        subplot_titles=[
            f'{symbol} EMA Analysis from API',
            'Signal Summary'
        ],
        vertical_spacing=0.1,
        row_heights=[0.8, 0.2]
    )
    
    # Add EMA lines
    fig.add_trace(
        go.Scatter(
            x=fast_data['timestamp'],
            y=fast_data['value'],
            name=f'Fast EMA ({ema_fast["params"]["window"]})',
            line=dict(color='blue', width=2)
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=slow_data['timestamp'],
            y=slow_data['value'],
            name=f'Slow EMA ({ema_slow["params"]["window"]})',
            line=dict(color='red', width=2)
        ),
        row=1, col=1
    )
    
    # Add signal markers (simplified approach)
    if entry_signals:
        entry_times = [pd.to_datetime(signal['timestamp'], utc=True) for signal in entry_signals]
        # Use the first few EMA values as approximate signal levels
        signal_levels = [fast_data['value'].iloc[i*50] if i*50 < len(fast_data) else fast_data['value'].iloc[-1] 
                        for i in range(len(entry_times))]
        
        fig.add_trace(
            go.Scatter(
                x=entry_times,
                y=signal_levels,
                mode='markers',
                name='📈 Buy Signals',
                marker=dict(color='green', size=12, symbol='triangle-up')
            ),
            row=1, col=1
        )
    
    if exit_signals:
        exit_times = [pd.to_datetime(signal['timestamp'], utc=True) for signal in exit_signals]
        signal_levels = [fast_data['value'].iloc[i*50] if i*50 < len(fast_data) else fast_data['value'].iloc[-1] 
                        for i in range(len(exit_times))]
        
        fig.add_trace(
            go.Scatter(
                x=exit_times,
                y=signal_levels,
                mode='markers',
                name='📉 Sell Signals',
                marker=dict(color='red', size=12, symbol='triangle-down')
            ),
            row=1, col=1
        )
    
    # Signal count over time (simplified)
    signal_summary = pd.DataFrame({
        'date': fast_data['timestamp'],
        'entry_count': 0,
        'exit_count': 0
    })
    
    # Mark signal periods
    for i, signal in enumerate(entry_signals):
        if i < len(signal_summary):
            signal_summary.iloc[i*60 if i*60 < len(signal_summary) else -1, 1] = 1
    
    for i, signal in enumerate(exit_signals):
        if i < len(signal_summary):
            signal_summary.iloc[i*60 if i*60 < len(signal_summary) else -1, 2] = -1
    
    fig.add_trace(
        go.Scatter(
            x=signal_summary['date'],
            y=signal_summary['entry_count'],
            fill='tonexty',
            name='Entry Activity',
            line=dict(color='green', width=1)
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=signal_summary['date'],
            y=signal_summary['exit_count'],
            fill='tonexty',
            name='Exit Activity',
            line=dict(color='red', width=1)
        ),
        row=2, col=1
    )
    
    # Update layout
    fig.update_layout(
        title=f"{symbol} Technical Analysis - API Integration Results",
        height=700,
        template="plotly_white",
        showlegend=True
    )
    
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="EMA Value", row=1, col=1)
    fig.update_yaxes(title_text="Signal Activity", row=2, col=1)
    
    # Save the chart
    filename = f"{symbol}_api_chart.html"
    fig.write_html(filename)
    
    print(f"   ✅ Chart saved: {filename}")
    print(f"   📊 Period: {data_info['start_date'][:10]} to {data_info['end_date'][:10]}")
    print(f"   📈 Data points: {data_info['data_points']}")
    print(f"   🎯 Entry signals: {len(entry_signals)}")
    print(f"   🛑 Exit signals: {len(exit_signals)}")
    
    return filename

def print_api_summary(api_result, symbol):
    """Print detailed API response summary"""
    analysis = api_result['data']['analysis']
    data_info = analysis['data_info']
    
    print("\n" + "="*60)
    print(f"📊 API RESPONSE SUMMARY FOR {symbol}")
    print("="*60)
    
    print(f"🏢 Symbol: {data_info['symbol']}")
    print(f"📅 Period: {data_info['start_date'][:10]} to {data_info['end_date'][:10]}")
    print(f"📈 Data Points: {data_info['data_points']}")
    print(f"💰 Price Range: ${data_info['price_range'][0]:.2f} - ${data_info['price_range'][1]:.2f}")
    
    print(f"\n📊 INDICATORS FROM API:")
    for indicator in analysis['indicators']:
        print(f"   • {indicator['name']}: {indicator['type']}")
        print(f"     Parameters: {indicator['params']}")
        print(f"     Data Points: {len(indicator['values'])}")
        if indicator['values']:
            first_value = indicator['values'][0]
            last_value = indicator['values'][-1]
            print(f"     First Value: {first_value['value']:.2f} on {first_value['timestamp'][:10]}")
            print(f"     Last Value: {last_value['value']:.2f} on {last_value['timestamp'][:10]}")
        print()
    
    print(f"🎯 TRADING SIGNALS FROM API:")
    print(f"   📈 Entry Signals: {len(analysis['entry_signals'])}")
    for i, signal in enumerate(analysis['entry_signals']):
        print(f"      {i+1}. {signal['timestamp'][:10]} - {signal['rule_name']}")
    
    print(f"   📉 Exit Signals: {len(analysis['exit_signals'])}")
    for i, signal in enumerate(analysis['exit_signals']):
        print(f"      {i+1}. {signal['timestamp'][:10]} - {signal['rule_name']}")

def main():
    """Main function"""
    symbol = "GOOGL"
    
    print("🚀 API Visualization Generator")
    print("=" * 50)
    
    # Fetch API data
    api_result = fetch_api_data(symbol)
    if not api_result:
        print("❌ Could not fetch API data")
        return
    
    # Create visualization
    chart_file = create_visualization(api_result, symbol)
    
    # Print summary
    print_api_summary(api_result, symbol)
    
    print(f"\n🎉 Visualization Complete!")
    print(f"📂 Open {chart_file} in your browser to see the interactive chart")
    print(f"💡 This shows real API data perfect for iOS integration")

if __name__ == "__main__":
    main() 
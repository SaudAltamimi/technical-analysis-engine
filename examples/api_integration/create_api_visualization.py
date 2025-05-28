"""
Create Visualization from API Data
This script calls the Technical Analysis API and creates interactive charts
"""

import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime

API_BASE_URL = "http://localhost:8001"

def fetch_api_analysis(symbol="GOOGL"):
    """Fetch analysis data from the API"""
    print(f"📊 Fetching API analysis for {symbol}...")
    
    # Create EMA strategy request
    request_data = {
        "name": f"{symbol} EMA Crossover Strategy",
        "description": f"EMA crossover analysis for {symbol} stock",
        "symbol": symbol,
        "period": "1y",
        "interval": "1d",
        "fast_period": 12,
        "slow_period": 26
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/strategies/ema-crossover",
            json=request_data,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        result = response.json()
        
        analysis = result['data']['analysis']
        print(f"   ✅ Successfully fetched analysis data")
        print(f"   📈 Data points: {analysis['data_info']['data_points']}")
        print(f"   📊 Indicators: {len(analysis['indicators'])}")
        print(f"   🎯 Entry signals: {len(analysis['entry_signals'])}")
        print(f"   🛑 Exit signals: {len(analysis['exit_signals'])}")
        
        return result
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server!")
        print("💡 Make sure the server is running: uvicorn src.app.main:app --host 0.0.0.0 --port 8001")
        return None
    except Exception as e:
        print(f"❌ Error fetching API data: {e}")
        return None

def create_interactive_chart(api_result, symbol):
    """Create interactive charts from API response data"""
    print("📊 Creating interactive visualization...")
    
    analysis = api_result['data']['analysis']
    indicators = analysis['indicators']
    entry_signals = analysis['entry_signals']
    exit_signals = analysis['exit_signals']
    data_info = analysis['data_info']
    
    # Extract indicator data
    ema_fast_data = None
    ema_slow_data = None
    
    for indicator in indicators:
        if 'fast' in indicator['name'].lower():
            ema_fast_data = indicator
        elif 'slow' in indicator['name'].lower():
            ema_slow_data = indicator
    
    if not ema_fast_data or not ema_slow_data:
        print("❌ Could not find EMA indicator data")
        return
    
    # Convert to DataFrame for easier handling
    fast_df = pd.DataFrame(ema_fast_data['values'])
    slow_df = pd.DataFrame(ema_slow_data['values'])
    
    # Convert timestamps
    fast_df['timestamp'] = pd.to_datetime(fast_df['timestamp'])
    slow_df['timestamp'] = pd.to_datetime(slow_df['timestamp'])
    
    # Create signal DataFrames
    entry_df = pd.DataFrame(entry_signals) if entry_signals else pd.DataFrame()
    exit_df = pd.DataFrame(exit_signals) if exit_signals else pd.DataFrame()
    
    if not entry_df.empty:
        entry_df['timestamp'] = pd.to_datetime(entry_df['timestamp'])
    if not exit_df.empty:
        exit_df['timestamp'] = pd.to_datetime(exit_df['timestamp'])
    
    # Create subplots
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        subplot_titles=[
            f'{symbol} EMA Crossover Analysis (API Data)',
            'Signal Intensity',
            'Trading Activity Timeline'
        ],
        vertical_spacing=0.08,
        row_heights=[0.6, 0.2, 0.2]
    )
    
    # Add EMA lines
    fig.add_trace(
        go.Scatter(
            x=fast_df['timestamp'], 
            y=fast_df['value'],
            name=f'Fast EMA ({ema_fast_data["params"]["window"]})',
            line=dict(color='#1f77b4', width=2),
            hovertemplate='<b>Fast EMA</b><br>Date: %{x}<br>Value: %{y:.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=slow_df['timestamp'], 
            y=slow_df['value'],
            name=f'Slow EMA ({ema_slow_data["params"]["window"]})',
            line=dict(color='#ff7f0e', width=2),
            hovertemplate='<b>Slow EMA</b><br>Date: %{x}<br>Value: %{y:.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Add entry signals
    if not entry_df.empty:
        # Find corresponding EMA values for signal points
        signal_values = []
        for _, signal in entry_df.iterrows():
            # Find closest fast EMA value
            time_diff = abs(fast_df['timestamp'] - signal['timestamp'])
            closest_idx = time_diff.idxmin()
            signal_values.append(fast_df.loc[closest_idx, 'value'])
        
        fig.add_trace(
            go.Scatter(
                x=entry_df['timestamp'],
                y=signal_values,
                mode='markers',
                name='📈 Buy Signals',
                marker=dict(
                    color='green',
                    size=12,
                    symbol='triangle-up',
                    line=dict(color='darkgreen', width=2)
                ),
                hovertemplate='<b>BUY SIGNAL</b><br>Date: %{x}<br>Price: %{y:.2f}<extra></extra>'
            ),
            row=1, col=1
        )
    
    # Add exit signals
    if not exit_df.empty:
        signal_values = []
        for _, signal in exit_df.iterrows():
            time_diff = abs(fast_df['timestamp'] - signal['timestamp'])
            closest_idx = time_diff.idxmin()
            signal_values.append(fast_df.loc[closest_idx, 'value'])
        
        fig.add_trace(
            go.Scatter(
                x=exit_df['timestamp'],
                y=signal_values,
                mode='markers',
                name='📉 Sell Signals',
                marker=dict(
                    color='red',
                    size=12,
                    symbol='triangle-down',
                    line=dict(color='darkred', width=2)
                ),
                hovertemplate='<b>SELL SIGNAL</b><br>Date: %{x}<br>Price: %{y:.2f}<extra></extra>'
            ),
            row=1, col=1
        )
    
    # Signal intensity plot (EMA difference)
    ema_diff = fast_df.set_index('timestamp')['value'] - slow_df.set_index('timestamp')['value']
    ema_diff = ema_diff.dropna()
    
    fig.add_trace(
        go.Scatter(
            x=ema_diff.index,
            y=ema_diff.values,
            fill='tonexty',
            name='EMA Momentum',
            line=dict(color='purple', width=1),
            fillcolor='rgba(128,0,128,0.2)',
            hovertemplate='<b>EMA Momentum</b><br>Date: %{x}<br>Difference: %{y:.2f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)
    
    # Trading activity timeline
    # Create binary signals for visualization
    all_dates = pd.date_range(start=fast_df['timestamp'].min(), end=fast_df['timestamp'].max(), freq='D')
    activity_timeline = pd.DataFrame({'date': all_dates, 'entry': 0, 'exit': 0})
    
    # Mark signal dates
    for _, signal in entry_df.iterrows():
        closest_date = activity_timeline['date'].sub(signal['timestamp']).abs().idxmin()
        activity_timeline.loc[closest_date, 'entry'] = 1
    
    for _, signal in exit_df.iterrows():
        closest_date = activity_timeline['date'].sub(signal['timestamp']).abs().idxmin()
        activity_timeline.loc[closest_date, 'exit'] = -1
    
    fig.add_trace(
        go.Scatter(
            x=activity_timeline['date'],
            y=activity_timeline['entry'],
            fill='tonexty',
            name='Buy Activity',
            line=dict(color='green', width=1),
            fillcolor='rgba(0,255,0,0.3)'
        ),
        row=3, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=activity_timeline['date'],
            y=activity_timeline['exit'],
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
            text=f"{symbol} Technical Analysis - API Integration Results",
            font=dict(size=18)
        ),
        height=900,
        template="plotly_white",
        showlegend=True,
        hovermode='x unified'
    )
    
    # Update axes
    fig.update_xaxes(title_text="Date", row=3, col=1)
    fig.update_yaxes(title_text="EMA Value", row=1, col=1)
    fig.update_yaxes(title_text="Momentum", row=2, col=1)
    fig.update_yaxes(title_text="Activity", row=3, col=1, range=[-1.2, 1.2])
    
    # Save the chart
    filename = f"{symbol}_api_visualization.html"
    fig.write_html(filename)
    
    print(f"   ✅ Interactive chart saved: {filename}")
    print(f"   📊 Data period: {data_info['start_date']} to {data_info['end_date']}")
    print(f"   📈 Total data points: {data_info['data_points']}")
    
    return fig

def create_summary_table(api_result, symbol):
    """Create a summary table of the analysis"""
    analysis = api_result['data']['analysis']
    data_info = analysis['data_info']
    
    print("\n" + "="*60)
    print(f"📊 {symbol} ANALYSIS SUMMARY FROM API")
    print("="*60)
    print(f"🏢 Symbol: {data_info['symbol']}")
    print(f"📅 Period: {data_info['start_date'][:10]} to {data_info['end_date'][:10]}")
    print(f"📈 Data Points: {data_info['data_points']}")
    print(f"💰 Price Range: ${data_info['price_range'][0]:.2f} - ${data_info['price_range'][1]:.2f}")
    
    print(f"\n📊 INDICATORS:")
    for indicator in analysis['indicators']:
        print(f"   • {indicator['name']}: {indicator['type']}")
        print(f"     Parameters: {indicator['params']}")
        print(f"     Data Points: {len(indicator['values'])}")
    
    print(f"\n🎯 TRADING SIGNALS:")
    print(f"   📈 Entry Signals: {len(analysis['entry_signals'])}")
    if analysis['entry_signals']:
        print(f"      First: {analysis['entry_signals'][0]['timestamp'][:10]}")
        print(f"      Last:  {analysis['entry_signals'][-1]['timestamp'][:10]}")
    
    print(f"   📉 Exit Signals: {len(analysis['exit_signals'])}")
    if analysis['exit_signals']:
        print(f"      First: {analysis['exit_signals'][0]['timestamp'][:10]}")
        print(f"      Last:  {analysis['exit_signals'][-1]['timestamp'][:10]}")

def main():
    """Main function to create API visualization"""
    symbol = "GOOGL"
    
    print("🚀 Creating Visualization from Technical Analysis API")
    print("=" * 60)
    
    # Fetch API data
    api_result = fetch_api_analysis(symbol)
    if not api_result:
        return
    
    # Create interactive chart
    fig = create_interactive_chart(api_result, symbol)
    
    # Create summary
    create_summary_table(api_result, symbol)
    
    print(f"\n🎉 Visualization Complete!")
    print(f"📂 Open {symbol}_api_visualization.html in your browser")
    print(f"💡 This shows real API data visualization for iOS integration")

if __name__ == "__main__":
    main() 
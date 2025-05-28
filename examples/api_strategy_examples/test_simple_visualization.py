"""
Simple visualization test with working API data
"""

import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

API_BASE_URL = "http://localhost:8001"

def create_and_visualize_aapl():
    """Create AAPL custom strategy and visualize"""
    print("🚀 Creating AAPL Custom Strategy Visualization")
    print("=" * 60)
    
    # Test the endpoint with simpler request
    payload = {
        "name": "AAPL_Test_Chart",
        "symbol": "AAPL",
        "description": "Simple test for chart",
        "indicators": [
            {"name": "EMA_12", "type": "EMA", "params": {"window": 12}},
            {"name": "EMA_26", "type": "EMA", "params": {"window": 26}},
            {"name": "RSI_14", "type": "RSI", "params": {"window": 14}}
        ],
        "crossover_rules": [
            {
                "name": "EMA_Cross_Buy",
                "fast_indicator": "EMA_12",
                "slow_indicator": "EMA_26",
                "direction": "above",
                "signal_type": "buy"
            }
        ],
        "threshold_rules": [
            {
                "name": "RSI_Oversold",
                "indicator": "RSI_14",
                "threshold": 30,
                "condition": "below",
                "signal_type": "buy"
            }
        ],
        "period": "3mo",
        "interval": "1d"
    }
    
    print("📤 Making API request...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/strategies/custom",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return None
            
        data = response.json()
        print("✅ API request successful!")
        
        # Create visualization
        chart_filename = create_chart(data, "AAPL")
        
        # Print summary
        print_results(data)
        
        print(f"\n🎉 Success!")
        print(f"📂 Chart saved: {chart_filename}")
        print(f"💡 Open the HTML file in your browser to see the interactive chart")
        
        return chart_filename
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def create_chart(api_data, symbol):
    """Create simple chart from API data"""
    print("📊 Creating chart...")
    
    analysis = api_data['data']['analysis']
    indicators = analysis['indicators']
    signals = analysis.get('signals', [])
    
    # Find indicators
    ema_12 = next((ind for ind in indicators if ind['name'] == 'EMA_12'), None)
    ema_26 = next((ind for ind in indicators if ind['name'] == 'EMA_26'), None)
    rsi_14 = next((ind for ind in indicators if ind['name'] == 'RSI_14'), None)
    
    if not all([ema_12, ema_26, rsi_14]):
        print("❌ Missing indicators")
        return None
    
    # Convert to DataFrames
    ema_12_df = pd.DataFrame(ema_12['values'])
    ema_26_df = pd.DataFrame(ema_26['values'])
    rsi_df = pd.DataFrame(rsi_14['values'])
    
    # Handle timestamps
    ema_12_df['timestamp'] = pd.to_datetime(ema_12_df['timestamp'], utc=True)
    ema_26_df['timestamp'] = pd.to_datetime(ema_26_df['timestamp'], utc=True)
    rsi_df['timestamp'] = pd.to_datetime(rsi_df['timestamp'], utc=True)
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        subplot_titles=[
            f'{symbol} EMA Crossover Strategy',
            'RSI Overbought/Oversold'
        ],
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3]
    )
    
    # Add EMA lines
    fig.add_trace(
        go.Scatter(
            x=ema_12_df['timestamp'],
            y=ema_12_df['value'],
            name='EMA 12',
            line=dict(color='blue', width=2)
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=ema_26_df['timestamp'],
            y=ema_26_df['value'],
            name='EMA 26',
            line=dict(color='red', width=2)
        ),
        row=1, col=1
    )
    
    # Add RSI
    fig.add_trace(
        go.Scatter(
            x=rsi_df['timestamp'],
            y=rsi_df['value'],
            name='RSI',
            line=dict(color='purple', width=2)
        ),
        row=2, col=1
    )
    
    # Add RSI thresholds
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    
    # Add signals as markers
    if signals:
        buy_signals = [s for s in signals if s.get('signal_type') == 'entry']
        sell_signals = [s for s in signals if s.get('signal_type') == 'exit']
        
        if buy_signals:
            buy_times = [pd.to_datetime(s['timestamp'], utc=True) for s in buy_signals]
            buy_levels = []
            for signal_time in buy_times:
                # Find closest EMA value for marker positioning
                time_diffs = (ema_12_df['timestamp'] - signal_time).abs()
                closest_idx = time_diffs.idxmin()
                buy_levels.append(ema_12_df['value'].iloc[closest_idx])
            
            fig.add_trace(
                go.Scatter(
                    x=buy_times,
                    y=buy_levels,
                    mode='markers',
                    name='📈 Buy Signals',
                    marker=dict(color='green', size=12, symbol='triangle-up'),
                    showlegend=True
                ),
                row=1, col=1
            )
        
        if sell_signals:
            sell_times = [pd.to_datetime(s['timestamp'], utc=True) for s in sell_signals]
            sell_levels = []
            for signal_time in sell_times:
                time_diffs = (ema_12_df['timestamp'] - signal_time).abs()
                closest_idx = time_diffs.idxmin()
                sell_levels.append(ema_12_df['value'].iloc[closest_idx])
            
            fig.add_trace(
                go.Scatter(
                    x=sell_times,
                    y=sell_levels,
                    mode='markers',
                    name='📉 Sell Signals',
                    marker=dict(color='red', size=12, symbol='triangle-down'),
                    showlegend=True
                ),
                row=1, col=1
            )
    
    # Update layout
    fig.update_layout(
        title=f"{symbol} Custom Strategy - Dynamic Rules Visualization",
        height=700,
        template="plotly_white"
    )
    
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
    
    # Save chart
    filename = f"{symbol}_custom_strategy_working.html"
    fig.write_html(filename)
    print(f"   ✅ Chart saved: {filename}")
    
    return filename

def print_results(api_data):
    """Print analysis results"""
    analysis = api_data['data']['analysis']
    strategy = api_data['data']['strategy']
    data_info = analysis['data_info']
    
    print("\n📊 STRATEGY RESULTS:")
    print(f"   Symbol: {data_info['symbol']}")
    print(f"   Data Points: {data_info['data_points']}")
    print(f"   Period: {data_info['start_date'][:10]} to {data_info['end_date'][:10]}")
    print(f"   Price Range: ${data_info['price_range'][0]:.2f} - ${data_info['price_range'][1]:.2f}")
    
    print(f"\n🔧 STRATEGY CONFIG:")
    print(f"   Name: {strategy['name']}")
    print(f"   Indicators: {len(strategy['indicators'])}")
    print(f"   Rules: {len(strategy['crossover_rules']) + len(strategy['threshold_rules'])}")
    
    all_signals = analysis.get('signals', [])
    entry_signals = [s for s in all_signals if s.get('signal_type') == 'entry']
    exit_signals = [s for s in all_signals if s.get('signal_type') == 'exit']
    
    print(f"\n🎯 SIGNALS:")
    print(f"   Entry Signals: {len(entry_signals)}")
    print(f"   Exit Signals: {len(exit_signals)}")
    print(f"   Total Signals: {len(all_signals)}")

if __name__ == "__main__":
    create_and_visualize_aapl() 
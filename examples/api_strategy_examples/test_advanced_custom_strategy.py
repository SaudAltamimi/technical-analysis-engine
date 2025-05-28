"""
Advanced Custom Strategy Test - Multiple Symbols and Complex Rules
Demonstrates the full power of dynamic strategy creation
"""

import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

API_BASE_URL = "http://localhost:8001"

def test_complex_strategies():
    """Test multiple complex strategies"""
    print("🚀 Advanced Custom Strategy Testing")
    print("=" * 70)
    
    # Strategy 1: TSLA with SMA and MACD
    print("\n1️⃣ Testing TSLA with SMA + MACD Strategy...")
    tsla_result = create_sma_macd_strategy("TSLA")
    if tsla_result:
        create_advanced_chart(tsla_result, "TSLA", "SMA_MACD")
    
    # Strategy 2: NVDA with Multiple EMAs
    print("\n2️⃣ Testing NVDA with Triple EMA Strategy...")
    nvda_result = create_triple_ema_strategy("NVDA")
    if nvda_result:
        create_advanced_chart(nvda_result, "NVDA", "Triple_EMA")
    
    # Strategy 3: MSFT with RSI + Bollinger-like strategy using EMAs
    print("\n3️⃣ Testing MSFT with RSI + EMA Bollinger Strategy...")
    msft_result = create_rsi_ema_strategy("MSFT")
    if msft_result:
        create_advanced_chart(msft_result, "MSFT", "RSI_EMA")

def create_sma_macd_strategy(symbol):
    """Create strategy with SMA and MACD indicators"""
    payload = {
        "name": f"{symbol}_SMA_MACD_Strategy",
        "symbol": symbol,
        "description": "SMA trend with MACD momentum",
        "indicators": [
            {"name": "SMA_20", "type": "SMA", "params": {"window": 20}},
            {"name": "SMA_50", "type": "SMA", "params": {"window": 50}},
            {"name": "MACD_12_26_9", "type": "MACD", "params": {"fast": 12, "slow": 26, "signal": 9}}
        ],
        "crossover_rules": [
            {
                "name": "SMA_Bullish_Cross",
                "fast_indicator": "SMA_20",
                "slow_indicator": "SMA_50", 
                "direction": "above",
                "signal_type": "buy"
            },
            {
                "name": "SMA_Bearish_Cross",
                "fast_indicator": "SMA_20",
                "slow_indicator": "SMA_50",
                "direction": "below", 
                "signal_type": "sell"
            }
        ],
        "threshold_rules": [
            {
                "name": "MACD_Positive",
                "indicator": "MACD_12_26_9",
                "threshold": 0,
                "condition": "above",
                "signal_type": "buy"
            },
            {
                "name": "MACD_Negative", 
                "indicator": "MACD_12_26_9",
                "threshold": 0,
                "condition": "below",
                "signal_type": "sell"
            }
        ],
        "period": "6mo",
        "interval": "1d"
    }
    
    return make_api_request(payload)

def create_triple_ema_strategy(symbol):
    """Create strategy with 3 EMAs for trend analysis"""
    payload = {
        "name": f"{symbol}_Triple_EMA_Strategy",
        "symbol": symbol,
        "description": "Triple EMA trend following",
        "indicators": [
            {"name": "EMA_9", "type": "EMA", "params": {"window": 9}},
            {"name": "EMA_21", "type": "EMA", "params": {"window": 21}}, 
            {"name": "EMA_55", "type": "EMA", "params": {"window": 55}}
        ],
        "crossover_rules": [
            {
                "name": "Fast_Over_Medium",
                "fast_indicator": "EMA_9",
                "slow_indicator": "EMA_21",
                "direction": "above", 
                "signal_type": "buy"
            },
            {
                "name": "Medium_Over_Slow",
                "fast_indicator": "EMA_21", 
                "slow_indicator": "EMA_55",
                "direction": "above",
                "signal_type": "buy"
            },
            {
                "name": "Fast_Under_Medium",
                "fast_indicator": "EMA_9",
                "slow_indicator": "EMA_21",
                "direction": "below",
                "signal_type": "sell"
            }
        ],
        "threshold_rules": [],
        "period": "1y",
        "interval": "1d"
    }
    
    return make_api_request(payload)

def create_rsi_ema_strategy(symbol):
    """Create strategy with RSI and EMA channels"""
    payload = {
        "name": f"{symbol}_RSI_EMA_Strategy", 
        "symbol": symbol,
        "description": "RSI oversold/overbought with EMA channels",
        "indicators": [
            {"name": "EMA_10", "type": "EMA", "params": {"window": 10}},
            {"name": "EMA_30", "type": "EMA", "params": {"window": 30}},
            {"name": "RSI_7", "type": "RSI", "params": {"window": 7}},
            {"name": "RSI_21", "type": "RSI", "params": {"window": 21}}
        ],
        "crossover_rules": [
            {
                "name": "Fast_EMA_Bullish",
                "fast_indicator": "EMA_10",
                "slow_indicator": "EMA_30",
                "direction": "above",
                "signal_type": "buy" 
            },
            {
                "name": "RSI_Cross_Up",
                "fast_indicator": "RSI_7",
                "slow_indicator": "RSI_21", 
                "direction": "above",
                "signal_type": "buy"
            }
        ],
        "threshold_rules": [
            {
                "name": "RSI7_Oversold",
                "indicator": "RSI_7",
                "threshold": 25,
                "condition": "below",
                "signal_type": "buy"
            },
            {
                "name": "RSI7_Overbought",
                "indicator": "RSI_7", 
                "threshold": 75,
                "condition": "above",
                "signal_type": "sell"
            },
            {
                "name": "RSI21_Overbought",
                "indicator": "RSI_21",
                "threshold": 70,
                "condition": "above", 
                "signal_type": "sell"
            }
        ],
        "period": "3mo",
        "interval": "1d"
    }
    
    return make_api_request(payload)

def make_api_request(payload):
    """Make API request and handle response"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/strategies/custom",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Strategy '{payload['name']}' created successfully")
            
            # Print quick stats
            analysis = result['data']['analysis']
            signals = analysis.get('signals', [])
            entry_signals = [s for s in signals if s.get('signal_type') == 'entry']
            exit_signals = [s for s in signals if s.get('signal_type') == 'exit']
            
            print(f"   📈 Signals: {len(entry_signals)} entry, {len(exit_signals)} exit")
            print(f"   📊 Data points: {analysis['data_info']['data_points']}")
            
            return result
        else:
            print(f"   ❌ API Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return None

def create_advanced_chart(api_data, symbol, strategy_type):
    """Create advanced visualization"""
    print(f"   📊 Creating {strategy_type} chart for {symbol}...")
    
    analysis = api_data['data']['analysis']
    indicators = analysis['indicators']
    signals = analysis.get('signals', [])
    
    # Create chart with appropriate number of subplots based on indicators
    num_indicators = len(indicators)
    rsi_indicators = [ind for ind in indicators if 'RSI' in ind['name']]
    macd_indicators = [ind for ind in indicators if 'MACD' in ind['name']]
    price_indicators = [ind for ind in indicators if ind['type'] in ['EMA', 'SMA']]
    
    # Determine subplot structure
    if rsi_indicators and macd_indicators:
        rows = 3
        subplot_titles = [f'{symbol} Price & Moving Averages', 'RSI Indicators', 'MACD']
    elif rsi_indicators:
        rows = 2  
        subplot_titles = [f'{symbol} Price & Moving Averages', 'RSI Indicators']
    elif macd_indicators:
        rows = 2
        subplot_titles = [f'{symbol} Price & Moving Averages', 'MACD']
    else:
        rows = 1
        subplot_titles = [f'{symbol} Price & Moving Averages']
    
    fig = make_subplots(
        rows=rows, cols=1,
        shared_xaxes=True,
        subplot_titles=subplot_titles,
        vertical_spacing=0.08
    )
    
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
    
    # Add price indicators (EMA, SMA) to first subplot
    for i, indicator in enumerate(price_indicators):
        data_df = pd.DataFrame(indicator['values'])
        data_df['timestamp'] = pd.to_datetime(data_df['timestamp'], utc=True)
        
        fig.add_trace(
            go.Scatter(
                x=data_df['timestamp'],
                y=data_df['value'],
                name=indicator['name'],
                line=dict(color=colors[i % len(colors)], width=2)
            ),
            row=1, col=1
        )
    
    # Add RSI indicators to second subplot if they exist
    if rsi_indicators:
        rsi_row = 2
        for i, indicator in enumerate(rsi_indicators):
            data_df = pd.DataFrame(indicator['values']) 
            data_df['timestamp'] = pd.to_datetime(data_df['timestamp'], utc=True)
            
            fig.add_trace(
                go.Scatter(
                    x=data_df['timestamp'],
                    y=data_df['value'],
                    name=indicator['name'],
                    line=dict(color=colors[(i+len(price_indicators)) % len(colors)], width=2)
                ),
                row=rsi_row, col=1
            )
        
        # Add RSI thresholds
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=rsi_row, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=rsi_row, col=1)
        fig.update_yaxes(range=[0, 100], row=rsi_row, col=1)
    
    # Add MACD indicators
    if macd_indicators:
        macd_row = 3 if rsi_indicators else 2
        for i, indicator in enumerate(macd_indicators):
            data_df = pd.DataFrame(indicator['values'])
            data_df['timestamp'] = pd.to_datetime(data_df['timestamp'], utc=True)
            
            fig.add_trace(
                go.Scatter(
                    x=data_df['timestamp'],
                    y=data_df['value'], 
                    name=indicator['name'],
                    line=dict(color=colors[(i+len(price_indicators)+len(rsi_indicators)) % len(colors)], width=2)
                ),
                row=macd_row, col=1
            )
        
        # Add MACD zero line
        fig.add_hline(y=0, line_dash="dash", line_color="gray", row=macd_row, col=1)
    
    # Add signal markers to price chart
    if signals and price_indicators:
        entry_signals = [s for s in signals if s.get('signal_type') == 'entry'] 
        exit_signals = [s for s in signals if s.get('signal_type') == 'exit']
        
        if entry_signals:
            entry_times = [pd.to_datetime(s['timestamp'], utc=True) for s in entry_signals]
            # Use first price indicator for positioning
            price_df = pd.DataFrame(price_indicators[0]['values'])
            price_df['timestamp'] = pd.to_datetime(price_df['timestamp'], utc=True)
            
            entry_levels = []
            for signal_time in entry_times:
                time_diffs = (price_df['timestamp'] - signal_time).abs()
                closest_idx = time_diffs.idxmin()
                entry_levels.append(price_df['value'].iloc[closest_idx])
            
            fig.add_trace(
                go.Scatter(
                    x=entry_times,
                    y=entry_levels,
                    mode='markers',
                    name='📈 Entry Signals',
                    marker=dict(color='green', size=10, symbol='triangle-up')
                ),
                row=1, col=1
            )
        
        if exit_signals:
            exit_times = [pd.to_datetime(s['timestamp'], utc=True) for s in exit_signals]
            price_df = pd.DataFrame(price_indicators[0]['values'])
            price_df['timestamp'] = pd.to_datetime(price_df['timestamp'], utc=True)
            
            exit_levels = []
            for signal_time in exit_times:
                time_diffs = (price_df['timestamp'] - signal_time).abs()
                closest_idx = time_diffs.idxmin()
                exit_levels.append(price_df['value'].iloc[closest_idx])
            
            fig.add_trace(
                go.Scatter(
                    x=exit_times,
                    y=exit_levels,
                    mode='markers',
                    name='📉 Exit Signals',
                    marker=dict(color='red', size=10, symbol='triangle-down')
                ),
                row=1, col=1
            )
    
    # Update layout
    fig.update_layout(
        title=f"{symbol} {strategy_type} Strategy - Advanced Dynamic Rules",
        height=200 + (rows * 250),
        template="plotly_white"
    )
    
    # Update axis labels
    fig.update_xaxes(title_text="Date", row=rows, col=1)
    fig.update_yaxes(title_text="Price", row=1, col=1)
    
    if rsi_indicators:
        fig.update_yaxes(title_text="RSI", row=2 if not macd_indicators else 2, col=1)
    if macd_indicators:
        fig.update_yaxes(title_text="MACD", row=rows, col=1)
    
    # Save chart
    filename = f"{symbol}_{strategy_type}_advanced.html"
    fig.write_html(filename)
    print(f"   ✅ Chart saved: {filename}")
    
    return filename

if __name__ == "__main__":
    test_complex_strategies()
    
    print(f"\n🎉 Advanced Strategy Testing Complete!")
    print(f"📂 Check the generated HTML files for interactive charts")
    print(f"💡 These demonstrate the full power of dynamic custom strategies!") 
"""
Strategy Builder Page - Create custom trading strategies
Uses FastAPI endpoints only for all operations
"""

import streamlit as st
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from typing import Dict, List, Any

# API Configuration
API_BASE_URL = "http://localhost:8000"

def make_api_request(endpoint: str, method: str = "GET", data: Dict = None):
    """Make API request with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.Timeout:
        st.error("API request timed out. Please try again.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to API. Please ensure the FastAPI server is running.")
        return None
    except Exception as e:
        st.error(f"Request failed: {str(e)}")
        return None

# Page Header
st.title("🔧 Custom Strategy Builder")
st.markdown("Create and configure custom trading strategies with indicators and rules")

# Check API status
if not st.session_state.get('api_status', False):
    st.error("❌ API not available. Please start the FastAPI server first.")
    st.stop()

# Helper functions
def get_indicator_types():
    """Get available indicator types from API"""
    result = make_api_request("/indicators/types")
    if result and result['status'] == 'success':
        return result['data']
    return {}

def get_available_periods():
    """Get available periods from API"""
    result = make_api_request("/periods")
    if result and result['status'] == 'success':
        return result['data']
    return {}

def get_popular_tickers():
    """Get popular tickers from API"""
    result = make_api_request("/tickers/popular")
    if result and result['status'] == 'success':
        return result['data']
    return {}

def search_tickers(query: str):
    """Search tickers via API"""
    if len(query) < 2:
        return []
    
    result = make_api_request("/tickers/search", "POST", {"query": query})
    if result and result['status'] == 'success':
        return result['data']['matches']
    return []

def validate_ticker(symbol: str):
    """Validate ticker via API"""
    result = make_api_request(f"/tickers/{symbol}/validate")
    if result and result['status'] == 'success':
        return result['data']
    return None

def get_strategy_recommendations(strategy_type: str):
    """Get strategy recommendations from API"""
    result = make_api_request(f"/tickers/recommendations/{strategy_type}")
    if result and result['status'] == 'success':
        return result['data']
    return None

# Load data
with st.spinner("Loading configuration data..."):
    indicator_types = get_indicator_types()
    periods_data = get_available_periods()
    tickers_data = get_popular_tickers()

# Strategy Configuration Form
st.header("Strategy Configuration")

col1, col2 = st.columns([2, 1])

with col1:
    # Basic Strategy Info
    st.subheader("Basic Information")
    strategy_name = st.text_input("Strategy Name", placeholder="e.g., My EMA RSI Strategy")
    strategy_description = st.text_area("Description", placeholder="Brief description of your strategy...")

    # Ticker Selection
    st.subheader("Ticker Selection")
    
    # Strategy type selection for recommendations
    strategy_type = st.selectbox(
        "Strategy Type (for ticker recommendations)",
        ["", "trend_following", "momentum", "mean_reversion", "volatility"],
        help="Select strategy type to get recommended tickers"
    )
    
    if strategy_type:
        with st.expander("📊 Recommended Tickers for This Strategy", expanded=True):
            recommendations = get_strategy_recommendations(strategy_type)
            if recommendations:
                st.info(f"**{recommendations['strategy_info']['description']}**")
                if 'note' in recommendations['strategy_info']:
                    st.markdown(f"💡 **Tip**: {recommendations['strategy_info']['note']}")
                
                for category, info in recommendations['recommended_categories'].items():
                    st.markdown(f"**{category.title()}**: {info['description']}")
                    st.markdown(f"Sample tickers: {', '.join(info['sample_tickers'])}")
    
    # Ticker input methods
    ticker_method = st.radio(
        "How would you like to select a ticker?",
        ["Search by name/symbol", "Browse popular tickers"],
        horizontal=True
    )
    
    selected_ticker = None
    
    if ticker_method == "Search by name/symbol":
        search_query = st.text_input("Search for ticker", placeholder="e.g., Apple, AAPL, Tesla")
        if search_query:
            with st.spinner("Searching..."):
                search_results = search_tickers(search_query)
            
            if search_results:
                ticker_options = [f"{t['symbol']} - {t['name']}" for t in search_results]
                selected_option = st.selectbox("Select ticker:", [""] + ticker_options)
                if selected_option:
                    selected_ticker = selected_option.split(" - ")[0]
    
    else:  # Browse popular tickers
        if tickers_data.get('categories'):
            category = st.selectbox(
                "Select category:",
                [""] + list(tickers_data['categories'].keys())
            )
            
            if category:
                category_tickers = tickers_data['categories'][category]['tickers']
                ticker_options = [f"{t['symbol']} - {t['name']}" for t in category_tickers]
                selected_option = st.selectbox("Select ticker:", [""] + ticker_options)
                if selected_option:
                    selected_ticker = selected_option.split(" - ")[0]

    # Validate selected ticker
    if selected_ticker:
        with st.spinner(f"Validating {selected_ticker}..."):
            validation = validate_ticker(selected_ticker)
        
        if validation and validation['is_valid']:
            st.success(f"✅ {selected_ticker} is valid and ready for backtesting")
        else:
            st.error(f"❌ {selected_ticker} is invalid or has insufficient data")
            selected_ticker = None

with col2:
    # Quick Info Panel
    st.subheader("Quick Info")
    
    if indicator_types:
        st.markdown("**Available Indicators:**")
        for ind_type, desc in indicator_types.get('descriptions', {}).items():
            st.markdown(f"• **{ind_type}**: {desc}")
    
    if periods_data.get('recommended_combinations'):
        st.markdown("**Recommended Periods:**")
        for combo_name, combo in periods_data['recommended_combinations'].items():
            st.markdown(f"• **{combo_name.title()}**: {combo['period']}, {combo['interval']}")

# Indicators Configuration
st.header("Indicators Configuration")

if 'indicators' not in st.session_state:
    st.session_state.indicators = []

# Add indicator button
if st.button("➕ Add Indicator"):
    st.session_state.indicators.append({
        'name': '',
        'type': '',
        'params': {}
    })

# Display and configure indicators
for i, indicator in enumerate(st.session_state.indicators):
    with st.expander(f"Indicator {i+1}: {indicator.get('name', 'Unnamed')}", expanded=True):
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            ind_name = st.text_input(f"Name", value=indicator.get('name', ''), key=f"ind_name_{i}")
            indicator['name'] = ind_name
        
        with col2:
            ind_type = st.selectbox(
                "Type", 
                [""] + list(indicator_types.get('types', [])),
                index=0 if not indicator.get('type') else list(indicator_types.get('types', [])).index(indicator['type']) + 1,
                key=f"ind_type_{i}"
            )
            indicator['type'] = ind_type
        
        with col3:
            if st.button(f"🗑️", key=f"del_ind_{i}", help="Delete indicator"):
                st.session_state.indicators.pop(i)
                st.rerun()
        
        # Indicator parameters based on type
        if ind_type:
            st.markdown("**Parameters:**")
            params = {}
            
            if ind_type in ['EMA', 'SMA', 'RSI']:
                period = st.number_input(
                    "Period", 
                    min_value=2, 
                    max_value=200, 
                    value=indicator.get('params', {}).get('period', 20),
                    key=f"period_{i}"
                )
                params['period'] = period
            
            elif ind_type == 'MACD':
                fast = st.number_input(
                    "Fast Period", 
                    min_value=2, 
                    max_value=50, 
                    value=indicator.get('params', {}).get('fast_period', 12),
                    key=f"fast_{i}"
                )
                slow = st.number_input(
                    "Slow Period", 
                    min_value=2, 
                    max_value=100, 
                    value=indicator.get('params', {}).get('slow_period', 26),
                    key=f"slow_{i}"
                )
                signal = st.number_input(
                    "Signal Period", 
                    min_value=2, 
                    max_value=50, 
                    value=indicator.get('params', {}).get('signal_period', 9),
                    key=f"signal_{i}"
                )
                params.update({'fast_period': fast, 'slow_period': slow, 'signal_period': signal})
            
            indicator['params'] = params

# Trading Rules Configuration
st.header("Trading Rules Configuration")

# Crossover Rules
st.subheader("Crossover Rules")

if 'crossover_rules' not in st.session_state:
    st.session_state.crossover_rules = []

if st.button("➕ Add Crossover Rule"):
    st.session_state.crossover_rules.append({
        'name': '',
        'fast_indicator': '',
        'slow_indicator': '',
        'direction': 'above',
        'signal_type': 'buy'
    })

for i, rule in enumerate(st.session_state.crossover_rules):
    with st.expander(f"Crossover Rule {i+1}: {rule.get('name', 'Unnamed')}", expanded=True):
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        
        with col1:
            rule_name = st.text_input(f"Rule Name", value=rule.get('name', ''), key=f"cross_name_{i}")
            rule['name'] = rule_name
        
        with col2:
            indicator_names = [ind['name'] for ind in st.session_state.indicators if ind['name']]
            
            fast_ind = st.selectbox(
                "Fast Indicator",
                [""] + indicator_names,
                index=0 if not rule.get('fast_indicator') or rule['fast_indicator'] not in indicator_names else indicator_names.index(rule['fast_indicator']) + 1,
                key=f"fast_ind_{i}"
            )
            rule['fast_indicator'] = fast_ind
            
            slow_ind = st.selectbox(
                "Slow Indicator", 
                [""] + indicator_names,
                index=0 if not rule.get('slow_indicator') or rule['slow_indicator'] not in indicator_names else indicator_names.index(rule['slow_indicator']) + 1,
                key=f"slow_ind_{i}"
            )
            rule['slow_indicator'] = slow_ind
        
        with col3:
            direction = st.selectbox("Direction", ["above", "below"], 
                                   index=0 if rule.get('direction', 'above') == 'above' else 1,
                                   key=f"direction_{i}")
            rule['direction'] = direction
            
            signal_type = st.selectbox("Signal", ["buy", "sell"],
                                     index=0 if rule.get('signal_type', 'buy') == 'buy' else 1,
                                     key=f"signal_{i}")
            rule['signal_type'] = signal_type
        
        with col4:
            if st.button(f"🗑️", key=f"del_cross_{i}", help="Delete rule"):
                st.session_state.crossover_rules.pop(i)
                st.rerun()

# Threshold Rules
st.subheader("Threshold Rules")

if 'threshold_rules' not in st.session_state:
    st.session_state.threshold_rules = []

if st.button("➕ Add Threshold Rule"):
    st.session_state.threshold_rules.append({
        'name': '',
        'indicator': '',
        'threshold': 0.0,
        'condition': 'above',
        'signal_type': 'buy'
    })

for i, rule in enumerate(st.session_state.threshold_rules):
    with st.expander(f"Threshold Rule {i+1}: {rule.get('name', 'Unnamed')}", expanded=True):
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            rule_name = st.text_input(f"Rule Name", value=rule.get('name', ''), key=f"thresh_name_{i}")
            rule['name'] = rule_name
            
            indicator_names = [ind['name'] for ind in st.session_state.indicators if ind['name']]
            indicator = st.selectbox(
                "Indicator",
                [""] + indicator_names,
                index=0 if not rule.get('indicator') or rule['indicator'] not in indicator_names else indicator_names.index(rule['indicator']) + 1,
                key=f"thresh_ind_{i}"
            )
            rule['indicator'] = indicator
        
        with col2:
            threshold = st.number_input(
                "Threshold",
                value=rule.get('threshold', 0.0),
                key=f"threshold_{i}"
            )
            rule['threshold'] = threshold
        
        with col3:
            condition = st.selectbox("Condition", ["above", "below"],
                                   index=0 if rule.get('condition', 'above') == 'above' else 1,
                                   key=f"condition_{i}")
            rule['condition'] = condition
            
            signal_type = st.selectbox("Signal", ["buy", "sell"],
                                     index=0 if rule.get('signal_type', 'buy') == 'buy' else 1,
                                     key=f"thresh_signal_{i}")
            rule['signal_type'] = signal_type
        
        with col4:
            if st.button(f"🗑️", key=f"del_thresh_{i}", help="Delete rule"):
                st.session_state.threshold_rules.pop(i)
                st.rerun()

# Period Selection
st.header("Analysis Period")
col1, col2 = st.columns(2)

with col1:
    period = st.selectbox(
        "Period",
        periods_data.get('periods', ['1y']),
        index=periods_data.get('periods', ['1y']).index('1y') if '1y' in periods_data.get('periods', []) else 0
    )

with col2:
    interval = st.selectbox(
        "Interval", 
        periods_data.get('intervals', ['1d']),
        index=periods_data.get('intervals', ['1d']).index('1d') if '1d' in periods_data.get('intervals', []) else 0
    )

# Strategy Summary
st.header("Strategy Summary")

if strategy_name and selected_ticker and st.session_state.indicators:
    st.success("✅ Strategy is ready to create!")
    
    # Display summary
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Strategy Details:**")
        st.markdown(f"• **Name**: {strategy_name}")
        st.markdown(f"• **Ticker**: {selected_ticker}")
        st.markdown(f"• **Period**: {period} ({interval})")
        st.markdown(f"• **Indicators**: {len(st.session_state.indicators)}")
        st.markdown(f"• **Crossover Rules**: {len(st.session_state.crossover_rules)}")
        st.markdown(f"• **Threshold Rules**: {len(st.session_state.threshold_rules)}")
    
    with col2:
        st.markdown("**Indicators:**")
        for ind in st.session_state.indicators:
            if ind['name'] and ind['type']:
                st.markdown(f"• {ind['name']} ({ind['type']})")
        
        if st.session_state.crossover_rules:
            st.markdown("**Crossover Rules:**")
            for rule in st.session_state.crossover_rules:
                if rule['name']:
                    st.markdown(f"• {rule['name']}")
        
        if st.session_state.threshold_rules:
            st.markdown("**Threshold Rules:**")
            for rule in st.session_state.threshold_rules:
                if rule['name']:
                    st.markdown(f"• {rule['name']}")

    # Create Strategy Button
    if st.button("🚀 Create Strategy", type="primary", use_container_width=True):
        # Prepare strategy data
        strategy_data = {
            "name": strategy_name,
            "symbol": selected_ticker,
            "description": strategy_description,
            "indicators": [
                {
                    "name": ind['name'],
                    "type": ind['type'],
                    **ind['params']
                }
                for ind in st.session_state.indicators 
                if ind['name'] and ind['type']
            ],
            "crossover_rules": [
                {
                    "name": rule['name'],
                    "fast_indicator": rule['fast_indicator'],
                    "slow_indicator": rule['slow_indicator'],
                    "direction": rule['direction'],
                    "signal_type": rule['signal_type']
                }
                for rule in st.session_state.crossover_rules
                if rule['name'] and rule['fast_indicator'] and rule['slow_indicator']
            ],
            "threshold_rules": [
                {
                    "name": rule['name'],
                    "indicator": rule['indicator'],
                    "threshold": rule['threshold'],
                    "condition": rule['condition'],
                    "signal_type": rule['signal_type']
                }
                for rule in st.session_state.threshold_rules
                if rule['name'] and rule['indicator']
            ],
            "period": period,
            "interval": interval
        }
        
        # Validate and create strategy
        with st.spinner("Creating strategy..."):
            result = make_api_request("/strategies/custom", "POST", strategy_data)
        
        if result and result['status'] == 'success':
            st.success("🎉 Strategy created successfully!")
            st.session_state.selected_strategy = {
                'data': strategy_data,
                'result': result['data']
            }
            
            # Show results
            with st.expander("Strategy Analysis Results", expanded=True):
                analysis_data = result['data']['analysis']
                
                # Display price chart with indicators and signals using subplots
                if 'price_data' in analysis_data and analysis_data['price_data']:
                    st.subheader("📈 Price Chart with Indicators & Signals")
                    
                    # Separate indicators by type
                    price_indicators = []  # EMA, SMA
                    oscillator_indicators = []  # RSI, MACD
                    
                    if 'indicators' in analysis_data and analysis_data['indicators']:
                        for indicator_obj in analysis_data['indicators']:
                            if indicator_obj and 'values' in indicator_obj and len(indicator_obj['values']) > 0:
                                indicator_type = indicator_obj.get('type', '').upper()
                                if indicator_type in ['RSI', 'MACD']:
                                    oscillator_indicators.append(indicator_obj)
                                else:
                                    price_indicators.append(indicator_obj)
                    
                    # Create subplots: price chart on top, oscillators below
                    has_oscillators = len(oscillator_indicators) > 0
                    if has_oscillators:
                        fig = make_subplots(
                            rows=2, cols=1,
                            shared_xaxes=True,
                            vertical_spacing=0.1,
                            row_heights=[0.7, 0.3],
                            subplot_titles=[f"{selected_ticker} Price & Moving Averages", "Oscillators (RSI, MACD)"]
                        )
                    else:
                        fig = make_subplots(rows=1, cols=1)
                    
                    # Add OHLC price data
                    price_data = analysis_data['price_data']
                    if len(price_data) > 0:
                        dates = [point['timestamp'] for point in price_data]
                        closes = [point['close'] for point in price_data]
                        highs = [point['high'] for point in price_data]
                        lows = [point['low'] for point in price_data]
                        opens = [point['open'] for point in price_data]
                        
                        # Add candlestick chart to top subplot
                        fig.add_trace(go.Candlestick(
                            x=dates,
                            open=opens,
                            high=highs,
                            low=lows,
                            close=closes,
                            name=f"{selected_ticker} Price",
                            showlegend=False
                        ), row=1, col=1)
                        
                        # Add close price line
                        fig.add_trace(go.Scatter(
                            x=dates,
                            y=closes,
                            mode='lines',
                            name=f"{selected_ticker} Close",
                            line=dict(color='blue', width=1.5),
                            showlegend=True
                        ), row=1, col=1)
                    
                    # Add price-based indicators (EMA, SMA) to top subplot
                    for indicator_obj in price_indicators:
                        ind_dates = [point['timestamp'] for point in indicator_obj['values']]
                        ind_values = [point['value'] for point in indicator_obj['values']]
                        indicator_name = indicator_obj.get('name', 'Unknown Indicator')
                        
                        fig.add_trace(go.Scatter(
                            x=ind_dates,
                            y=ind_values,
                            mode='lines',
                            name=indicator_name,
                            line=dict(width=2)
                        ), row=1, col=1)
                    
                    # Add buy/sell signals to top subplot
                    if 'signals' in analysis_data and analysis_data['signals']:
                        buy_signals = []
                        sell_signals = []
                        
                        for signal in analysis_data['signals']:
                            if signal['signal_type'] in ['buy', 'entry']:
                                buy_signals.append(signal)
                            elif signal['signal_type'] in ['sell', 'exit']:
                                sell_signals.append(signal)
                        
                        # Add buy signals
                        if buy_signals:
                            buy_dates = [signal['timestamp'] for signal in buy_signals]
                            buy_prices = [signal['price'] for signal in buy_signals]
                            
                            fig.add_trace(go.Scatter(
                                x=buy_dates,
                                y=buy_prices,
                                mode='markers',
                                marker=dict(
                                    symbol='triangle-up',
                                    size=15,
                                    color='green'
                                ),
                                name='Buy Signals'
                            ), row=1, col=1)
                        
                        # Add sell signals
                        if sell_signals:
                            sell_dates = [signal['timestamp'] for signal in sell_signals]
                            sell_prices = [signal['price'] for signal in sell_signals]
                            
                            fig.add_trace(go.Scatter(
                                x=sell_dates,
                                y=sell_prices,
                                mode='markers',
                                marker=dict(
                                    symbol='triangle-down',
                                    size=15,
                                    color='red'
                                ),
                                name='Sell Signals'
                            ), row=1, col=1)
                    
                    # Add oscillators to bottom subplot
                    if has_oscillators:
                        for indicator_obj in oscillator_indicators:
                            ind_dates = [point['timestamp'] for point in indicator_obj['values']]
                            ind_values = [point['value'] for point in indicator_obj['values']]
                            indicator_name = indicator_obj.get('name', 'Unknown Indicator')
                            indicator_type = indicator_obj.get('type', '').upper()
                            
                            line_style = dict(width=2, dash='dash' if indicator_type == 'MACD' else 'solid')
                            
                            fig.add_trace(go.Scatter(
                                x=ind_dates,
                                y=ind_values,
                                mode='lines',
                                name=indicator_name,
                                line=line_style
                            ), row=2, col=1)
                            
                            # Add RSI reference lines
                            if indicator_type == 'RSI':
                                # Oversold line (30)
                                fig.add_hline(y=30, line_dash="dot", line_color="red", 
                                            annotation_text="Oversold (30)", 
                                            annotation_position="right", row=2, col=1)
                                # Overbought line (70)
                                fig.add_hline(y=70, line_dash="dot", line_color="red", 
                                            annotation_text="Overbought (70)", 
                                            annotation_position="right", row=2, col=1)
                                # Middle line (50)
                                fig.add_hline(y=50, line_dash="dot", line_color="gray", 
                                            annotation_text="Neutral (50)", 
                                            annotation_position="right", row=2, col=1)
                    
                    # Update layout
                    fig.update_layout(
                        title=f"{selected_ticker} - Strategy Analysis",
                        height=800 if has_oscillators else 500,
                        showlegend=True,
                        xaxis_rangeslider_visible=False
                    )
                    
                    # Update y-axis labels
                    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
                    if has_oscillators:
                        fig.update_yaxes(title_text="Oscillator Value", row=2, col=1)
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display signals summary
                    if 'signals' in analysis_data and analysis_data['signals']:
                        col1, col2, col3 = st.columns(3)
                        
                        total_signals = len(analysis_data['signals'])
                        buy_count = len([s for s in analysis_data['signals'] if s['signal_type'] in ['buy', 'entry']])
                        sell_count = len([s for s in analysis_data['signals'] if s['signal_type'] in ['sell', 'exit']])
                        
                        with col1:
                            st.metric("Total Signals", total_signals)
                        with col2:
                            st.metric("Buy Signals", buy_count)
                        with col3:
                            st.metric("Sell Signals", sell_count)
                
            
            st.info("💡 **Next Step**: Go to the Strategy Tester page to backtest your strategy!")
            
            # Raw data in separate expander (outside the main expander to avoid nesting)
            with st.expander("Raw Analysis Data", expanded=False):
                st.json(analysis_data)
        else:
            st.error("Failed to create strategy. Please check your configuration.")

else:
    missing = []
    if not strategy_name:
        missing.append("Strategy Name")
    if not selected_ticker:
        missing.append("Valid Ticker")
    if not st.session_state.indicators:
        missing.append("At least one Indicator")
    
    st.warning(f"⚠️ Please provide: {', '.join(missing)}")

# Clear form button
if st.button("🗑️ Clear All", help="Clear all form data"):
    for key in ['indicators', 'crossover_rules', 'threshold_rules']:
        if key in st.session_state:
            st.session_state[key] = []
    st.rerun() 
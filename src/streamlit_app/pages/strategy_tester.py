"""
Strategy Tester Page - Backtest custom trading strategies
Uses FastAPI endpoints only for all operations
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
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
st.title("🧪 Strategy Tester")
st.markdown("Backtest your custom strategies against historical market data")

# Check API status
if not st.session_state.get('api_status', False):
    st.error("❌ API not available. Please start the FastAPI server first.")
    st.stop()

# Helper functions
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

def get_ticker_info(symbol: str):
    """Get ticker info from API"""
    result = make_api_request(f"/tickers/{symbol}/info")
    if result and result['status'] == 'success':
        return result['data']
    return None

def backtest_strategy(strategy_data: Dict, backtest_params: Dict):
    """Run backtest via API"""
    request_data = {
        "strategy": strategy_data,
        "ticker": {
            "symbol": strategy_data['symbol'],
            "period": strategy_data['period'],
            "interval": strategy_data['interval']
        },
        "params": backtest_params
    }
    
    result = make_api_request("/backtest/custom/ticker", "POST", request_data)
    if result and result['status'] == 'success':
        return result['data']
    return None

def backtest_strategy_date_range(strategy_data: Dict, start_date: str, end_date: str, backtest_params: Dict):
    """Run backtest with date range via API"""
    request_data = {
        "strategy": strategy_data,
        "ticker": {
            "symbol": strategy_data['symbol'],
            "start_date": start_date,
            "end_date": end_date,
            "interval": strategy_data['interval']
        },
        "params": backtest_params
    }
    
    result = make_api_request("/backtest/custom/date-range", "POST", request_data)
    if result and result['status'] == 'success':
        return result['data']
    return None

# Load data
periods_data = get_available_periods()
tickers_data = get_popular_tickers()

# Strategy Selection
st.header("Strategy Selection")

# Check if we have a strategy from the builder
if st.session_state.get('selected_strategy'):
    strategy = st.session_state.selected_strategy
    st.success(f"✅ Using strategy: **{strategy['data']['name']}** ({strategy['data']['symbol']})")
    
    with st.expander("View Strategy Details", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Strategy Information:**")
            st.markdown(f"• **Name**: {strategy['data']['name']}")
            st.markdown(f"• **Symbol**: {strategy['data']['symbol']}")
            st.markdown(f"• **Description**: {strategy['data'].get('description', 'No description')}")
            st.markdown(f"• **Indicators**: {len(strategy['data']['indicators'])}")
            st.markdown(f"• **Rules**: {len(strategy['data']['crossover_rules']) + len(strategy['data']['threshold_rules'])}")
        
        with col2:
            st.markdown("**Indicators:**")
            for ind in strategy['data']['indicators']:
                st.markdown(f"• {ind['name']} ({ind['type']})")
            
            if strategy['data']['crossover_rules']:
                st.markdown("**Crossover Rules:**")
                for rule in strategy['data']['crossover_rules']:
                    st.markdown(f"• {rule['name']}")
            
            if strategy['data']['threshold_rules']:
                st.markdown("**Threshold Rules:**")
                for rule in strategy['data']['threshold_rules']:
                    st.markdown(f"• {rule['name']}")
    
    use_existing = st.checkbox("Use this strategy for backtesting", value=True)
    
    if use_existing:
        selected_strategy_data = strategy['data']
    else:
        selected_strategy_data = None
else:
    st.info("💡 **No strategy selected.** Please go to the Strategy Builder page to create a strategy first.")
    selected_strategy_data = None

# Manual Strategy Input (if no strategy selected)
if not selected_strategy_data:
    st.subheader("Manual Strategy Input")
    st.markdown("You can also manually input a strategy JSON or create one in the Strategy Builder.")
    
    manual_strategy = st.text_area(
        "Strategy JSON",
        placeholder='{\n  "name": "My Strategy",\n  "symbol": "AAPL",\n  "indicators": [...],\n  "crossover_rules": [...],\n  "threshold_rules": [...]\n}',
        height=200
    )
    
    if manual_strategy:
        try:
            selected_strategy_data = json.loads(manual_strategy)
            st.success("✅ Strategy JSON parsed successfully!")
        except json.JSONDecodeError as e:
            st.error(f"❌ Invalid JSON: {str(e)}")
            selected_strategy_data = None

# Backtesting Configuration
if selected_strategy_data:
    st.header("Backtesting Configuration")
    
    # Backtest method selection
    backtest_method = st.radio(
        "Backtesting Method",
        ["Use Strategy Period", "Custom Date Range"],
        horizontal=True,
        help="Use the period defined in the strategy or specify custom dates"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Backtest Parameters")
        
        initial_capital = st.number_input(
            "Initial Capital ($)",
            min_value=1000,
            max_value=10000000,
            value=100000,
            step=1000,
            help="Starting capital for backtesting"
        )
        
        commission = st.number_input(
            "Commission Rate (%)",
            min_value=0.0,
            max_value=10.0,
            value=0.1,
            step=0.01,
            help="Commission rate as percentage (0.1% = 0.1)"
        ) / 100  # Convert percentage to decimal
        
        position_size = st.selectbox(
            "Position Sizing",
            ["fixed_amount", "percentage", "all_in"],
            index=1,
            help="How to size positions"
        )
        
        if position_size == "fixed_amount":
            position_value = st.number_input(
                "Position Amount ($)",
                min_value=100,
                max_value=initial_capital,
                value=10000,
                step=100
            )
        elif position_size == "percentage":
            position_value = st.slider(
                "Position Percentage (%)",
                min_value=1,
                max_value=100,
                value=25,
                step=1
            )
        else:  # all_in
            position_value = 100
    
    with col2:
        st.subheader("Time Period")
        
        if backtest_method == "Use Strategy Period":
            # Use the period from strategy
            st.info(f"Using strategy period: **{selected_strategy_data.get('period', 'N/A')}** ({selected_strategy_data.get('interval', 'N/A')})")
            
            # Show ticker info
            symbol = selected_strategy_data['symbol']
            ticker_info = get_ticker_info(symbol)
            
            if ticker_info:
                with st.expander("Ticker Information", expanded=False):
                    st.json(ticker_info)
        
        else:  # Custom Date Range
            st.markdown("**Custom Date Range:**")
            
            # Date range selection
            col_start, col_end = st.columns(2)
            
            with col_start:
                start_date = st.date_input(
                    "Start Date",
                    value=datetime.now() - timedelta(days=365),
                    max_value=datetime.now() - timedelta(days=1)
                )
            
            with col_end:
                end_date = st.date_input(
                    "End Date",
                    value=datetime.now() - timedelta(days=1),
                    min_value=start_date,
                    max_value=datetime.now()
                )
            
            # Interval selection
            interval = st.selectbox(
                "Data Interval",
                periods_data.get('intervals', ['1d']),
                index=periods_data.get('intervals', ['1d']).index('1d') if '1d' in periods_data.get('intervals', []) else 0
            )
            
            # Update strategy data with custom settings
            selected_strategy_data = selected_strategy_data.copy()
            selected_strategy_data['interval'] = interval
    
    # Run Backtest Button
    st.header("Run Backtest")
    
    # Prepare backtest parameters
    backtest_params = {
        "initial_capital": initial_capital,
        "commission": commission,
        "position_sizing": {
            "method": position_size,
            "value": position_value
        }
    }
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("🚀 Run Backtest", type="primary", use_container_width=True):
            with st.spinner("Running backtest... This may take a moment."):
                
                if backtest_method == "Use Strategy Period":
                    # Use ticker-based backtest
                    backtest_result = backtest_strategy(selected_strategy_data, backtest_params)
                else:
                    # Use date range backtest
                    start_date_str = start_date.isoformat()
                    end_date_str = end_date.isoformat()
                    backtest_result = backtest_strategy_date_range(
                        selected_strategy_data, 
                        start_date_str, 
                        end_date_str, 
                        backtest_params
                    )
                
                if backtest_result:
                    st.session_state.backtest_results = backtest_result
                    st.success("🎉 Backtest completed successfully!")
                else:
                    st.error("❌ Backtest failed. Please check your configuration and try again.")
    
    with col2:
        if st.button("🗑️ Clear Results"):
            st.session_state.backtest_results = None
            st.rerun()

# Display Results
if st.session_state.get('backtest_results'):
    st.header("📊 Backtest Results")
    
    results = st.session_state.backtest_results
    
    # Summary Metrics
    st.subheader("Performance Summary")
    
    # Extract key metrics from VectorBT comprehensive backtest results
    backtest_data = results.get('backtest_results', {})
    
    # Handle comprehensive format (performance + analysis) or legacy format
    performance_data = backtest_data.get('performance', backtest_data)
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Display VectorBT-powered performance metrics
    with col1:
        total_return = performance_data.get('total_return', 0)
        st.metric("Total Return", f"{total_return:.2%}" if isinstance(total_return, (int, float)) else "N/A")
    
    with col2:
        win_rate = performance_data.get('win_rate', 0)
        st.metric("Win Rate", f"{win_rate:.2%}" if isinstance(win_rate, (int, float)) else "N/A")
    
    with col3:
        max_drawdown = performance_data.get('max_drawdown', 0)
        st.metric("Max Drawdown", f"{max_drawdown:.2%}" if isinstance(max_drawdown, (int, float)) else "N/A")
    
    with col4:
        sharpe_ratio = performance_data.get('sharpe_ratio', 0)
        st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}" if isinstance(sharpe_ratio, (int, float)) else "N/A")
    
    # Display VectorBT and dependency chain info
    if results.get('vectorbt_trusted'):
        st.success("🔒 **Trusted VectorBT Backtest** - Full dependency chain: " + results.get('dependency_chain', 'N/A'))
    
    # Detailed Results
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Strategy Information")
        if results.get('strategy_info'):
            strategy_info = results['strategy_info']
            st.markdown(f"**Strategy Name**: {strategy_info.get('name', 'N/A')}")
            st.markdown(f"**Indicators**: {strategy_info.get('indicators_count', 'N/A')}")
            st.markdown(f"**Rules**: {strategy_info.get('rules_count', 'N/A')}")
    
    with col2:
        st.subheader("Backtest Parameters")
        st.markdown(f"**Initial Capital**: ${backtest_params['initial_capital']:,}")
        st.markdown(f"**Commission**: {backtest_params['commission']*100:.3f}%")
        st.markdown(f"**Position Sizing**: {backtest_params['position_sizing']['method']}")
        if backtest_method == "Custom Date Range":
            st.markdown(f"**Period**: {start_date} to {end_date}")
    
    # Raw Results
    with st.expander("Raw Backtest Results", expanded=False):
        st.json(results)
    
    # Charts (if data is available)
    st.subheader("Performance Charts")
    
    # Check if we have analysis data from the comprehensive backtest
    # New format has analysis data nested under 'analysis'
    analysis_data = backtest_data.get('analysis', backtest_data)
    
    # Display price chart with indicators and signals using subplots
    if 'price_data' in analysis_data and analysis_data['price_data']:
        st.subheader("📈 Price Chart with Trading Signals")
        
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
                subplot_titles=[f"{selected_strategy_data['symbol']} Price & Moving Averages", "Oscillators (RSI, MACD)"]
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
                name=f"{selected_strategy_data['symbol']} Price",
                showlegend=False
            ), row=1, col=1)
            
            # Add close price line
            fig.add_trace(go.Scatter(
                x=dates,
                y=closes,
                mode='lines',
                name=f"{selected_strategy_data['symbol']} Close",
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
            title=f"{selected_strategy_data['symbol']} - Backtest Results",
            height=800 if has_oscillators else 500,
            showlegend=True,
            xaxis_rangeslider_visible=False
        )
        
        # Update y-axis labels
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        if has_oscillators:
            fig.update_yaxes(title_text="Oscillator Value", row=2, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display signals and trade summary
        if 'signals' in analysis_data and analysis_data['signals']:
            col1, col2, col3, col4 = st.columns(4)
            
            total_signals = len(analysis_data['signals'])
            buy_count = len([s for s in analysis_data['signals'] if s['signal_type'] in ['buy', 'entry']])
            sell_count = len([s for s in analysis_data['signals'] if s['signal_type'] in ['sell', 'exit']])
            
            with col1:
                st.metric("Total Signals", total_signals)
            with col2:
                st.metric("Buy Signals", buy_count)
            with col3:
                st.metric("Sell Signals", sell_count)
            with col4:
                trades_count = min(buy_count, sell_count)
                st.metric("Completed Trades", trades_count)
        
        # Performance comparison chart (if available)
        if len(price_data) > 0 and 'signals' in analysis_data:
            st.subheader("📊 Strategy Performance vs Buy & Hold")
            
            # Calculate simple buy & hold performance
            initial_price = price_data[0]['close']
            final_price = price_data[-1]['close']
            buy_hold_return = (final_price - initial_price) / initial_price * 100
            
            # Display comparison
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Buy & Hold Return", 
                    f"{buy_hold_return:.2f}%",
                    delta=None
                )
            with col2:
                if isinstance(total_return, (int, float)):
                    strategy_return = total_return * 100
                    outperformance = strategy_return - buy_hold_return
                    st.metric(
                        "Strategy Return", 
                        f"{strategy_return:.2f}%",
                        delta=f"{outperformance:+.2f}% vs B&H"
                    )
    
    elif 'equity_curve' in backtest_data:
        st.subheader("📈 Equity Curve")
        # Handle equity curve if available in a different format
        df = pd.DataFrame(backtest_data['equity_curve'])
        fig = px.line(df, x='date', y='equity', title='Portfolio Equity Curve')
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("📊 No chart data available in the backtest results. The API response may be in a different format.")
        st.markdown("**Available data keys:**")
        st.write(list(backtest_data.keys()) if isinstance(backtest_data, dict) else "No data structure")
    
    # Export Results
    st.subheader("Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Download Results as JSON"):
            json_str = json.dumps(results, indent=2, default=str)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("📋 Copy Results to Clipboard"):
            json_str = json.dumps(results, indent=2, default=str)
            st.code(json_str, language="json")

else:
    # No results to show
    st.info("👆 Configure and run a backtest to see results here")
    
    # Quick start tips
    with st.expander("💡 Quick Start Tips", expanded=True):
        st.markdown("""
        **Getting Started with Backtesting:**
        
        1. **Create a Strategy**: Go to Strategy Builder to create a custom strategy
        2. **Select Parameters**: Choose your initial capital, commission rate (%), and position sizing
        3. **Choose Time Period**: Use the strategy's default period or set a custom date range
        4. **Run Backtest**: Click "Run Backtest" and wait for results
        5. **Analyze Results**: Review performance metrics and charts
        
        **Tips for Better Results:**
        - Start with longer time periods (1+ years) for more reliable results
        - Consider transaction costs and slippage in real trading
        - Test multiple market conditions (bull, bear, sideways markets)
        - Compare your strategy against buy-and-hold benchmarks
        """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "💡 **Tip**: Backtest results are for educational purposes only and don't guarantee future performance"
    "</div>",
    unsafe_allow_html=True
) 
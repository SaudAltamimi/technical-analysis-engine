"""
Real Stock Data Analysis - Google (GOOGL)
Enhanced example using real market data from Yahoo Finance
"""

import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta

# Add the src directory to the path for imports
sys.path.append(str(Path(__file__).parent.parent / "src" / "techincal-analysis-engine"))

from strategy import StrategyEngine
from builders import StrategyBuilder


def fetch_google_data(period="1y"):
    """Fetch real Google stock data from Yahoo Finance"""
    print(f"📊 Fetching Google (GOOGL) stock data for the last {period}...")
    
    try:
        # Fetch Google stock data
        ticker = yf.Ticker("GOOGL")
        data = ticker.history(period=period)
        
        if data.empty:
            raise ValueError("No data received from Yahoo Finance")
        
        # Use closing prices for analysis
        price_data = data['Close']
        price_data.name = 'price'
        
        print(f"   ✅ Successfully fetched {len(price_data)} days of data")
        print(f"   📅 Date range: {price_data.index[0].date()} to {price_data.index[-1].date()}")
        print(f"   💰 Price range: ${price_data.min():.2f} - ${price_data.max():.2f}")
        
        return price_data
        
    except Exception as e:
        print(f"   ❌ Error fetching data: {e}")
        print("   🔄 Falling back to sample data...")
        
        # Fallback to sample data if Yahoo Finance fails
        from utils import create_sample_data
        return create_sample_data(
            start_date="2023-01-01",
            end_date="2024-01-01",
            initial_price=150.0,  # Google-like price
            volatility=0.02
        )


def main():
    """Real stock data analysis with Google stock"""
    print("🚀 Real Stock Data Analysis - Google (GOOGL)")
    print("=" * 50)
    
    # 1. Fetch real Google stock data
    price_data = fetch_google_data(period="1y")  # Last 1 year
    
    # 2. Create EMA crossover strategy
    print("\n📈 Building EMA crossover strategy...")
    strategy = StrategyBuilder.ema_crossover(
        name="Google EMA Crossover Strategy",
        fast_period=12,  # 12-day EMA
        slow_period=26   # 26-day EMA
    )
    print(f"   Strategy: {strategy.name}")
    
    # 3. Run strategy analysis
    print("\n⚙️  Running strategy analysis...")
    engine = StrategyEngine(strategy)
    indicators = engine.calculate_indicators(price_data)
    entry_signals = engine.get_entry_signals(engine.generate_signals(indicators))
    exit_signals = engine.get_exit_signals(engine.generate_signals(indicators))
    
    print(f"   📊 Indicators calculated: {list(indicators.keys())}")
    print(f"   🎯 Entry signals generated: {entry_signals.sum()}")
    print(f"   🎯 Exit signals generated: {exit_signals.sum()}")
    
    # 4. Prepare data for plotting
    df = pd.DataFrame({
        'Date': price_data.index,
        'Price': price_data.values,
        'Fast_EMA_12': indicators['ema_fast'].values.values,
        'Slow_EMA_26': indicators['ema_slow'].values.values,
    })
    
    # Add signal markers
    df['Buy_Signal'] = entry_signals.values
    df['Sell_Signal'] = exit_signals.values
    
    # Mark signal points for plotting
    buy_points = df[df['Buy_Signal'] == True].copy()
    sell_points = df[df['Sell_Signal'] == True].copy()
    
    # 5. Create enhanced plots with cumulative returns
    print("\n📊 Creating interactive plots with cumulative returns...")
    
    # Run backtest first to get portfolio data for plotting
    portfolio = engine.backtest(price_data, init_cash=10000, freq='D')
    portfolio_value = portfolio.value()
    cumulative_returns = (portfolio_value / 10000 - 1) * 100  # Convert to percentage
    
    # Create comprehensive subplot layout
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        subplot_titles=[
            'Google (GOOGL) Stock Price & EMA Indicators',
            'Trading Signals Timeline', 
            'Cumulative Strategy Returns (%)'
        ],
        vertical_spacing=0.05,
        row_heights=[0.5, 0.2, 0.3],
        specs=[[{"secondary_y": False}],
               [{"secondary_y": False}],
               [{"secondary_y": False}]]
    )
    
    # Panel 1: Price and indicators with signals
    fig.add_trace(
        go.Scatter(x=df['Date'], y=df['Price'], name='Stock Price', 
                  line=dict(color='black', width=2)),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df['Date'], y=df['Fast_EMA_12'], name='Fast EMA (12)', 
                  line=dict(color='blue', width=1.5)),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df['Date'], y=df['Slow_EMA_26'], name='Slow EMA (26)', 
                  line=dict(color='red', width=1.5)),
        row=1, col=1
    )
    
    # Add buy signals
    if not buy_points.empty:
        fig.add_trace(
            go.Scatter(x=buy_points['Date'], y=buy_points['Price'],
                      mode='markers', name='📈 Buy Signal',
                      marker=dict(color='green', size=12, symbol='triangle-up'),
                      hovertemplate='<b>BUY SIGNAL</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'),
            row=1, col=1
        )
    
    # Add sell signals  
    if not sell_points.empty:
        fig.add_trace(
            go.Scatter(x=sell_points['Date'], y=sell_points['Price'],
                      mode='markers', name='📉 Sell Signal',
                      marker=dict(color='red', size=12, symbol='triangle-down'),
                      hovertemplate='<b>SELL SIGNAL</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'),
            row=1, col=1
        )
    
    # Panel 2: Signal timeline
    fig.add_trace(
        go.Scatter(x=df['Date'], y=df['Buy_Signal'].astype(int),
                  fill='tonexty', name='Buy Signals',
                  line=dict(color='green', width=1),
                  fillcolor='rgba(0,255,0,0.3)'),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df['Date'], y=-df['Sell_Signal'].astype(int),
                  fill='tonexty', name='Sell Signals',
                  line=dict(color='red', width=1),
                  fillcolor='rgba(255,0,0,0.3)'),
        row=2, col=1
    )
    
    # Panel 3: Cumulative returns
    fig.add_trace(
        go.Scatter(x=portfolio_value.index, y=cumulative_returns.values,
                  name='Strategy Returns', 
                  line=dict(color='blue', width=3),
                  fill='tonexty',
                  fillcolor='rgba(0,100,255,0.1)',
                  hovertemplate='<b>Portfolio Performance</b><br>Date: %{x}<br>Return: %{y:.2f}%<extra></extra>'),
        row=3, col=1
    )
    
    # Add zero line for reference
    fig.add_hline(y=0, line_dash="dash", line_color="gray", 
                  annotation_text="Break-even", row=3, col=1)
    
    # Enhanced styling
    fig.update_layout(
        title=dict(
            text="Google (GOOGL) Stock Analysis - EMA Crossover Strategy with Returns",
            font=dict(size=16)
        ),
        height=900,
        hovermode='x unified',
        showlegend=True,
        template="plotly_white",
        font=dict(size=12)
    )
    
    # Update axes labels
    fig.update_xaxes(title_text="Date", row=3, col=1)
    fig.update_yaxes(title_text="Stock Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="Signal", row=2, col=1, range=[-1.2, 1.2])
    fig.update_yaxes(title_text="Cumulative Returns (%)", row=3, col=1)
    
    # Save comprehensive plot
    fig.write_html("google_comprehensive_analysis.html")
    
    print("✅ Enhanced comprehensive plot saved:")
    print("   📈 google_comprehensive_analysis.html - Complete analysis with cumulative returns")
    
    # Also create a simple signal timeline (keeping the original)
    signal_df = pd.DataFrame({
        'Date': df['Date'],
        'Buy Signals': df['Buy_Signal'].astype(int),
        'Sell Signals': -df['Sell_Signal'].astype(int)
    })
    
    fig2 = px.area(signal_df, x='Date', y=['Buy Signals', 'Sell Signals'],
                   title='Trading Signal Timeline - Google (GOOGL)',
                   color_discrete_map={'Buy Signals': 'green', 'Sell Signals': 'red'},
                   labels={'value': 'Signal Strength', 'Date': 'Date'})
    
    fig2.update_layout(height=300, template="plotly_white", yaxis=dict(range=[-1.2, 1.2]))
    fig2.write_html("google_signal_timeline.html")
    
    print("   📊 google_signal_timeline.html - Trading signal timeline")
    
    # 6. Run backtest analysis (portfolio already calculated above)
    print("\n💰 Backtest Results on Real Google Data:")
    total_return = portfolio.total_return()
    sharpe_ratio = portfolio.sharpe_ratio()
    max_drawdown = portfolio.max_drawdown()
    
    print(f"   💵 Initial Investment: $10,000")
    print(f"   📊 Total Return: {total_return:.2%}")
    print(f"   ⚖️  Sharpe Ratio: {sharpe_ratio:.2f}")
    print(f"   📉 Max Drawdown: {max_drawdown:.2%}")
    
    # Calculate final portfolio value
    final_value = 10000 * (1 + total_return)
    profit_loss = final_value - 10000
    print(f"   💰 Final Portfolio Value: ${final_value:,.2f}")
    print(f"   {'📈' if profit_loss > 0 else '📉'} Profit/Loss: ${profit_loss:,.2f}")
    
    # Show signal statistics
    if not buy_points.empty:
        print(f"\n🎯 Signal Analysis:")
        print(f"   📅 First Buy Signal: {buy_points.iloc[0]['Date'].date()}")
        print(f"   💰 Price at First Buy: ${buy_points.iloc[0]['Price']:.2f}")
        
        if not sell_points.empty:
            print(f"   📅 First Sell Signal: {sell_points.iloc[0]['Date'].date()}")
            print(f"   💰 Price at First Sell: ${sell_points.iloc[0]['Price']:.2f}")
    
    return fig, fig2, portfolio, price_data


if __name__ == "__main__":
    try:
        fig, fig2, portfolio, price_data = main()
        print(f"\n🎉 Real data analysis completed successfully!")
        print(f"   📊 Analyzed {len(price_data)} days of Google stock data")
        print(f"   🌐 Open the HTML files in your browser to see interactive plots")
        print(f"   💡 The strategy {'performed well' if portfolio.total_return() > 0 else 'underperformed'} on real market data")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
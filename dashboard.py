import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Function to fetch stock data
def get_stock_data(ticker, period="1y", interval="1d"):
    df = yf.download(ticker, period=period, interval=interval)
    return df

# Function to calculate technical indicators
def add_technical_indicators(df):
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['RSI_14'] = compute_rsi(df['Close'])
    df['MACD'], df['MACD_signal'] = compute_macd(df['Close'])
    return df

# Function to compute RSI
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# Function to compute MACD
def compute_macd(series, short=12, long=26, signal=9):
    short_ema = series.ewm(span=short, adjust=False).mean()
    long_ema = series.ewm(span=long, adjust=False).mean()
    macd = short_ema - long_ema
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    return macd, macd_signal

# Streamlit UI
st.title("📊 AI-Powered Technical Analyst Dashboard")

# Sidebar user input
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., AAPL, MSFT, GOOGL)", "AAPL")
period = st.sidebar.selectbox("Select Time Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
if st.sidebar.button("Analyze"):
    df = get_stock_data(ticker, period=period)
    df = add_technical_indicators(df)
    
    # Plot Candlestick Chart
    st.subheader(f"Stock Price & Technical Indicators - {ticker}")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], line=dict(color='orange', width=1), name='50-day SMA'))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_200'], line=dict(color='blue', width=1), name='200-day SMA'))
    st.plotly_chart(fig, use_container_width=True)
    
    # Display latest technical indicator values
    latest = df.iloc[-1]
    st.write(f"**Latest Close Price:** {latest['Close']:.2f}")
    st.write(f"**RSI(14):** {latest['RSI_14']:.1f}")
    st.write(f"**50-day SMA:** {latest['SMA_50']:.2f}")
    st.write(f"**200-day SMA:** {latest['SMA_200']:.2f}")
    
    # Trading Signals
    signals = []
    if latest['RSI_14'] < 30:
        signals.append("BUY: RSI is oversold (<30)")
    if latest['RSI_14'] > 70:
        signals.append("SELL: RSI is overbought (>70)")
    if latest['SMA_50'] > latest['SMA_200']:
        signals.append("BUY: Golden Cross (50-day SMA above 200-day SMA)")
    if latest['SMA_50'] < latest['SMA_200']:
        signals.append("SELL: Death Cross (50-day SMA below 200-day SMA)")
    
    st.subheader("Trading Signals")
    if signals:
        for signal in signals:
            st.write(f"✅ {signal}")
    else:
        st.write("No strong buy/sell signals detected.")

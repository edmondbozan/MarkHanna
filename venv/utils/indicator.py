# utils/indicator.py

import pandas_ta as ta

def calculate_indicators(df):
    df['MA20'] = ta.sma(df['Close'], length=20)
    df['MA50'] = ta.sma(df['Close'], length=50)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])

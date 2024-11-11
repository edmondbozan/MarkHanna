# strategies/day_trading.py

import time
import pandas as pd
import logging
from ibapi.contract import Contract
from utils.indicator import calculate_indicators
from utils.order import place_bracket_order

class DayTradingStrategy:
    def __init__(self, app):
        self.app = app
        self.data_received = False

    def execute(self):
        self.app.connect_app()
        self.request_data()
        # Wait until data is received
        while not self.data_received:
            time.sleep(1)
        df = self.app.df
        calculate_indicators(df)
        signal = self.check_day_trade_signal(df)
        if signal == 'BUY':
            self.execute_trade(df)
        else:
            logging.info('No trading signal generated.')
        self.app.disconnect_app()

    def request_data(self):
        # Define the contract
        self.app.contract = Contract()
        self.app.contract.symbol = "AAPL"
        self.app.contract.secType = "STK"
        self.app.contract.exchange = "SMART"
        self.app.contract.currency = "USD"

        # Request historical data
        self.app.reqHistoricalData(
            reqId=1,
            contract=self.app.contract,
            endDateTime='',
            durationStr='4 D',
            barSizeSetting='5 mins',
            whatToShow='TRADES',
            useRTH=1,
            formatDate=1,
            keepUpToDate=False,
            chartOptions=[]
        )

    # These methods override the EWrapper methods in IBApp
    def historicalData(self, reqId, bar):
        self.app.data.append([bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume])

    def historicalDataEnd(self, reqId, start, end):
        # Convert data to DataFrame
        self.app.df = pd.DataFrame(self.app.data, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        self.app.df['Date'] = pd.to_datetime(self.app.df['Date'])
        self.app.df.set_index('Date', inplace=True)
        self.data_received = True

    def check_day_trade_signal(self, df):
        latest = df.iloc[-1]
        previous = df.iloc[-2]

        # Identify recent resistance level
        resistance = df['High'].rolling(window=20).max().shift(1).iloc[-1]
        price_breakout = latest['Close'] > resistance

        # Volume spike condition
        avg_volume = df['Volume'].rolling(window=10).mean().shift(1).iloc[-1]
        volume_spike = latest['Volume'] > avg_volume * 1.5

        # Price above VWAP
        price_above_vwap = latest['Close'] > latest['VWAP']

        if price_breakout and volume_spike and price_above_vwap:
            logging.info("Day trading BUY signal generated.")
            return 'BUY'
        else:
            return 'HOLD'

    def execute_trade(self, df):
        entry_price = df['Close'].iloc[-1]
        quantity = 10  # Adjust as needed
        stop_loss_price = entry_price * 0.99
        take_profit_price = entry_price * 1.02

        place_bracket_order(self.app, self.app.contract, 'BUY', quantity, take_profit_price, stop_loss_price)
        logging.info(f"Placed day trade for {quantity} shares at {entry_price}")

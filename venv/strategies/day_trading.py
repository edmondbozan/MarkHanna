import time
import pandas as pd
import logging
from ibapi.contract import Contract
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import threading
from utils.indicator import calculate_indicators
from utils.order import place_bracket_order

class IBApp(EWrapper, EClient):
    def __init__(self):
        EWrapper.__init__(self)
        EClient.__init__(self, self)
        self.data = []  # To hold historical data
        self.data_received = False  # Flag to indicate data reception

    def connect_app(self):
        # Connect to IB Gateway or TWS
        self.connect("127.0.0.1", 7497, clientId=1)
        # Start the IB event loop in a separate thread
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
    
    def disconnect_app(self):
        self.disconnect()

    # Historical data callback
    def historicalData(self, reqId, bar):
        print(f"Received data: {bar.date}, {bar.close}")
        self.data.append([bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume])

    def historicalDataEnd(self, reqId, start, end):
        print("Historical data download complete.")
        self.df = pd.DataFrame(self.data, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.df.set_index('Date', inplace=True)
        self.data_received = True  # Set the flag to indicate data has been received

class DayTradingStrategy:
    def __init__(self, app):
        self.app = app

    def execute(self):
        try:
            self.app.connect_app()
            self.request_data()
            
            # Wait until data is received or timeout occurs
            start_time = time.time()
            timeout = 20  # 60 seconds timeout

            while not self.app.data_received:
                if time.time() - start_time > timeout:
                    logging.error("Timeout: Data was not received within the expected time frame.")
                    return  # Exit if data is not received in time
                time.sleep(1)
                print("Waiting for data...")

            # Proceed with data processing
            df = self.app.df
            calculate_indicators(df)
            signal = self.check_day_trade_signal(df)
            if signal == 'BUY':
                self.execute_trade(df)
            else:
                logging.info('No trading signal generated.')
        finally:
            self.app.disconnect_app()
            print("Disconnected from TWS")

    def request_data(self):
        # Define the contract for the stock
        self.app.contract = Contract()
        self.app.contract.symbol = "MSFT"
        self.app.contract.secType = "STK"
        self.app.contract.exchange = "SMART"
        self.app.contract.currency = "USD"

        # Request historical data
        self.app.reqHistoricalData(
            reqId=1,
            contract=self.app.contract,
            endDateTime='',
            durationStr='900 S',
            barSizeSetting='1 min',
            whatToShow='TRADES',
            useRTH=1,
            formatDate=1,
            keepUpToDate=False,
            chartOptions=[]
        )

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

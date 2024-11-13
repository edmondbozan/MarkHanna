from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time
import pandas as pd

class IBApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = []  # List to store historical data
        self.df = None  # DataFrame to store the final data
        self.data_received = False

    def error(self, reqId, errorCode, errorString):
        print(f"Error {errorCode}, ReqId {reqId}: {errorString}")

    def historicalData(self, reqId, bar):
        print(f"HistoricalData. ReqId: {reqId}, Date: {bar.date}, Close: {bar.close}")
        self.data.append([bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume])

    def historicalDataEnd(self, reqId, start, end):
        print(f"HistoricalDataEnd. ReqId: {reqId}")
        self.data_received = True
        # Convert data to DataFrame
        self.df = pd.DataFrame(self.data, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.df.set_index('Date', inplace=True)

    def nextValidId(self, orderId):
        print(f"NextValidId received. OrderId: {orderId}")
        self.nextOrderId = orderId

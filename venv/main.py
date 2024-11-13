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
        if errorCode in [2104, 2106, 2107]:
            print(f"Info {errorCode}: {errorString}")
        else:
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

def run_app():
    # Create an instance of the IBApp class
    app = IBApp()
    
    # Connect to the IB API
    app.connect('127.0.0.1', 7497, clientId=1)
    
    # Start the socket in a thread
    api_thread = threading.Thread(target=app.run, daemon=True)
    api_thread.start()
    
    # Give the connection time to establish
    time.sleep(1)
    
    # Define the contract for the instrument you want to request data for
    contract = Contract()
    contract.symbol = "AAPL"            # Symbol of the stock
    contract.secType = "STK"            # Security type
    contract.exchange = "SMART"         # Exchange
    contract.currency = "USD"           # Currency
    
    # Request historical data
    app.reqHistoricalData(
        reqId=1,
        contract=contract,
        endDateTime='',
        durationStr='2 D',               # Duration of data to request (e.g., '2 D' for 2 days)
        barSizeSetting='10 mins',         # Size of each bar (e.g., '5 mins')
        whatToShow='TRADES',             # Type of data to show (e.g., 'TRADES')
        useRTH=0,                        # Use regular trading hours (1) or all available data (0)
        formatDate=1,                    # Format date as a string
        keepUpToDate=False,
        chartOptions=[]
    )
    
    # Wait until data is received or timeout occurs
    timeout = 10  # seconds
    start_time = time.time()
    while not app.data_received and time.time() - start_time < timeout:
        time.sleep(1)
    
    # Check if data was received
    if app.data_received:
        print("Data received successfully.")
        print(app.df)
    else:
        print("Failed to receive data.")
    
    # Disconnect from the IB API
    app.disconnect()
    api_thread.join()

if __name__ == "__main__":
    run_app()

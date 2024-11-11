# ib_connection/ib_connection.py

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import threading
import logging

class IBApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.data_received = False
        self.data = []
        self.nextOrderId = None
        self.contract = None
        self.df = None
        self.connected = False

    def connect_app(self):
        if not self.connected:
            self.connect("127.0.0.1", 7497, clientId=1)
            self.connected = True
            # Start the socket in a thread
            thread = threading.Thread(target=self.run, daemon=True)
            thread.start()
            logging.info("IB API connection started.")

    def disconnect_app(self):
        print('disconnect')
        if self.connected:
            self.disconnect()
            self.connected = False
            logging.info("IB API connection closed.")

    def nextValidId(self, orderId):
        super().nextValidId(orderId)
        self.nextOrderId = orderId
        logging.info(f"Next valid order ID: {orderId}")

    def error(self, reqId, errorCode, errorString):
        logging.error(f"Error {errorCode}: {errorString}")

    # Additional methods will be added by the strategy

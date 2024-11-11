import time
import schedule
from ib_connection.ib_connection import IBApp
from strategies.day_trading import DayTradingStrategy
from utils.logger import setup_logger

def run_bot():
    setup_logger()
    app = IBApp()
    strategy = DayTradingStrategy(app)
    strategy.execute()
    app.disconnect_app()

if __name__ == "__main__":
    run_bot()

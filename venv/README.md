# Trading Bot

This is a Python-based trading bot that implements a day trading strategy using the Interactive Brokers API.

## Project Structure

- `main.py`: Entry point of the application.
- `ibapi/ib_connection.py`: Manages the IB API connection.
- `strategies/day_trading.py`: Contains the day trading strategy logic.
- `utils/indicators.py`: Functions to calculate technical indicators.
- `utils/order.py`: Functions related to order creation and management.
- `utils/logger.py`: Sets up logging configurations.
- `data/`: Stores logs and any data files.
- `requirements.txt`: Lists Python dependencies.

## Setup Instructions

1. **Clone the Repository**

   ```bash
   git clone <repository_url>
   cd trading_bot

# utils/logger.py

import logging

def setup_logger():
    logging.basicConfig(
        filename='data/trading_bot.log',
        level=logging.INFO,
        format='%(asctime)s %(levelname)s:%(message)s'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s:%(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

import logging
import os
import asyncio
import pandas as pd
import json
import time

from logging.handlers import RotatingFileHandler
from services.downloader import Downloader
from services.manager import Manager
from strategies.doubleST.main import DoubleST

logger = logging.getLogger(__name__)


def prepare_logs() -> None:
    """Prepare logging system for the bot.

    This function does the following:
        - Ensure "logs/" directory exists in the current working directory.
        - Set up basic configuration for the logging module.
        - Configure a rotating file handler which logs to robot.log in the logs/ directory.
    """
    # Ensure "logs/" directory exists in the current working directory
    if not os.path.exists("logs/"):
        # Create "logs/" directory
        os.makedirs("logs/")

    # Set up basic configuration for the logging module
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
        handlers=[
            RotatingFileHandler(
                "logs/robot.log", maxBytes=100000000, backupCount=10, encoding="utf-8"
            )
        ],
        encoding="utf-8",
    )


def prepare_tickers() -> None:
    for ticker in tickers:
        # Check ticker directory
        if not os.path.exists('tickers/'+ticker+"/"):
            # Create ticker directory
            os.makedirs('tickers/'+ticker+"/")

        # Check config file
        if not os.path.exists('tickers/'+ticker+"/config.json"):
            # Create default config
            default = {
                'var_profit': 1.5, 'period': [10, 20], 'multiplier': [3, 5]
            }
            # Create config file
            with open('tickers/'+ticker+"/config.json", 'w') as f:
                json.dump(default, f)


if __name__ == "__main__":

    prepare_logs()  # Prepare logging system
    logger.info("Program start")

    tickers = ['ALRS', 'BANE', 'BSPB', 'CBOM', 'CHMF', 'FLOT', 'GCHE', 'HEAD', 'LENT', 'MAGN', 'MOEX', 'ROSN', 'SBER', 'YDEX']  # Add your tickers here
    prepare_tickers()  # Prepare directories for tickers (if they don't exist)

    try:
        message = '''Choose mode:
    1 - download historical data;
    2 - show;
    3 - optimize;
    0 - exit;
                         
Please, enter mode:'''

        # Choose mode
        mode = int(input(message))
        if mode == 1:
            loader = Downloader(tickers)
            asyncio.run(loader.run())

        elif mode == 2:
            print('Start reading quotes...')
            start_time = time.time()
            manager = Manager('SBER')
            quotes = manager.get_quotes()

            quotes['date'] = pd.to_datetime(quotes['date'], format='%Y%m%d %H:%M:%S')
            end_time = time.time()
            print('Quotes completed...'+str(round(end_time-start_time,3))+'s')
            print('Start prepare data...')
            start_time = time.time()
            double_st = DoubleST(manager.get_directory())

            data = double_st.run(quotes)
            end_time = time.time()
            print('Data completed...'+str(round(end_time-start_time,3))+'s')
            print('Start calculate...')
            start_time = time.time()
            data = double_st.calculate(data)['data']
            end_time = time.time()
            print('Calculate completed...'+str(round(end_time-start_time,3))+'s')
            print('Start show...')
            double_st.show(data)

        elif mode == 3:
            manager = Manager('SBER')

            data = pd.read_csv(manager.get_doubleST_path(), header=0)

            double_st = DoubleST(manager.get_directory())
            double_st.optimize(data, {'start': 1.0, 'step': 0.1, 'end': 5.0})

        elif mode == 0:
            print("Program exit")
        else:
            print("Invalid mode. Stopping the program. Exiting...")

    except Exception as ex:
        logger.critical("Something went wrong: %s", repr(ex))

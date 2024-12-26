import logging
import os
import asyncio
import pandas as pd
import json
import time

from logging.handlers import RotatingFileHandler
from services.downloader import Downloader
from services.manager import Manager
from terminals.main import DoubleST
from accounts.alor import AlorAccount
from configurations.alor import AlorConfiguration

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
    config = AlorConfiguration()

    for ticker in config.tickers:
        # Check ticker directory
        if not os.path.exists('tickers/'+ticker+"/"):
            # Create ticker directory
            os.makedirs('tickers/'+ticker+"/")

        # Check config file
        if not os.path.exists('tickers/'+ticker+"/config.json"):
            # Create default config
            default = {
                'var_take': 1.5, 'period': [10, 20], 'multiplier': [3, 5]
            }
            # Create config file
            with open('tickers/'+ticker+"/config.json", 'w') as f:
                json.dump(default, f)


if __name__ == "__main__":

    prepare_logs()  # Prepare logging system
    logger.info("Program start")

    prepare_tickers()  # Prepare directories for tickers (if they don't exist)

    try:
        message = '''Choose mode:
    1 - download historical data;
    2 - show;
    3 - optimize;
    4 - run;
    0 - exit;
                         
Please, enter mode:'''

        # Choose mode
        mode = int(input(message))
        # Download historical data
        if mode == 1:
            loader = Downloader()
            asyncio.run(loader.run())
        # Show
        elif mode == 2:
            start_time = time.time()
            manager = Manager('SBER')
            quotes = manager.get_quotes()
            quotes['date'] = pd.to_datetime(quotes['date'], format='%Y%m%d %H:%M:%S')
            quotes_completed = time.time()
            print('Quotes completed...'+str(round(quotes_completed-start_time, 3))+'s')

            dir = manager.get_directory()
            double_st = DoubleST(dir)

            # Check if file with data exists
            if os.path.exists(os.path.join(dir, 'explore.csv')):
                # Read data from file
                dobleST = pd.read_csv(os.path.join(dir, 'explore.csv'), header=0)
            else:
                # Create empty DataFrame with columns
                dobleST = pd.DataFrame(columns=['ticker', 'date', 'open', 'high', 'low', 'close'])
                # Write DataFrame to file
                dobleST.to_csv(os.path.join(dir, 'explore.csv'), index=False)
                # Calculate data
                dobleST = double_st.run(quotes)

            # If the data and quotes have the same last dates, then there is no point in recalculating
            data = dobleST if (dobleST['date'].iloc[-1] == str(quotes['date'].iloc[-1])) else double_st.run(quotes)
            data.to_csv(os.path.join(dir, 'explore.csv'), index=False)  # write data to file
            data_completed = time.time()
            print('Data completed...'+str(round(data_completed-quotes_completed, 3))+'s')

            data = double_st.calculate(data)
            calculate_completed = time.time()
            print('Calculate completed...'+str(round(calculate_completed-data_completed, 3))+'s')

            print('Start show...')
            double_st.show(data)
        # Optimize
        elif mode == 3:
            manager = Manager('SBER')

            data = pd.read_csv(manager.get_doubleST_path(), header=0)

            double_st = DoubleST(manager.get_directory())
            double_st.optimize(data, {'start': 1.0, 'step': 0.1, 'end': 3.0})
        # Run
        elif mode == 4:
            print("Start running...")
            alor = AlorAccount()
            alor.run()
        # Exit
        elif mode == 0:
            print("Program exit")
        else:
            print("Invalid mode. Stopping the program. Exiting...")

    except Exception as ex:
        logger.critical("Something went wrong: %s", repr(ex))

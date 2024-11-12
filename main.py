import logging
import os
import asyncio
import pandas as pd

from logging.handlers import RotatingFileHandler
from services.downloader import Downloader
from services.manager import Manager
from strategies.doubleST import DoubleST

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
        if not os.path.exists('tickers/'+ticker+"/"):
            # Create ticker directory
            os.makedirs('tickers/'+ticker+"/")
        if not os.path.exists('tickers/'+ticker+"/config.py"):
            # Create config file
            open('tickers/'+ticker+"/config.py", 'w').close()

if __name__ == "__main__":
    
    prepare_logs() # Prepare logging system
    logger.info("Program start")

    tickers = ['ALRS', 'SBER']  # Add your tickers here
    prepare_tickers() # Prepare directories for tickers (if they don't exist)

    try:
        message = '''Choose mode:
    1 - download historical data;
    2 - show;
    3 - optimize;
    0 - exit;
                         
Please, enter mode:'''

        # Choose mode
        mode = int(input(message ))
        if mode == 1:
            loader = Downloader(tickers)
            asyncio.run(loader.run())

        elif mode == 2:
            manager = Manager('SBER')
            quotes = manager.get_quotes()

            quotes['date'] = pd.to_datetime(quotes['date'], format='%Y%m%d %H:%M:%S')

            double_st = DoubleST(manager.get_directory(), 1.6)

            data = double_st.run(quotes)

            data = double_st.calculate(data)['data']
            double_st.show(data)

        elif mode ==3:
            manager = Manager('SBER')
            
            data =pd.read_csv(manager.get_doubleST_path(), header=0)

            double_st = DoubleST(manager.get_directory(), 1.6)
            double_st.optimize(data, {'start': 1.0, 'step': 0.1, 'end': 5.0})

        elif mode == 0:
            print("Program exit")
        else:
            print("Invalid mode. Stopping the program. Exiting...")

    except Exception as ex:
        logger.critical("Something went wrong: %s", repr(ex))

import logging
import os
import pandas as pd

from services.file import FileService
from api.services.client import AlorClientService

__all__ = "Downloader"

logger = logging.getLogger(__name__)


class Downloader:
    def __init__(self, tickers: list[str]) -> None:
        self.tickers = tickers  # list of tickers
        self.indexes =['IMOEX']

    async def run(self) -> pd.DataFrame:
        file = FileService()
        client = AlorClientService()

        async def update_quotes(file_path: str, ticker: str) -> None:
            if not os.path.exists(file_path):  # if file with quotes doesn't exist
                file.create_data_file(file_path)  # create date file in directory

            quotes = pd.read_csv(file_path, header=0)  # read quotes from file data.csv

            # get last date from file, if there is no data then it will be firs minute of first day of previous month
            last_date = file.get_last_date(quotes)            

            data = await client.ws_history_date(ticker, last_date)  # get data from last date to now

            if len(data) > 1:
                file.update_file(ticker, quotes, data,)  # update file
                quotes.to_csv(file_path, index=False)  # write quotes to file

        percent_step = 100/(len(self.tickers) + len(self.indexes))  # initial percentage
        percentage = 0.0

        logger.info("Start downloading...")
        print("Start downloading...")

        for ticker in self.tickers:

            file_path = os.path.join(os.path.dirname(os.path.dirname(__file__))+'\\tickers\\', ticker, 'data.csv')  # file path for ticker

            await update_quotes(file_path, ticker)

            percentage += percent_step

            logger.info(f"Downloaded {ticker} quotes, {percentage:.2f}% completed")
            print(f"Downloaded {ticker} quotes, {percentage:.2f}% completed")
            
        for index in self.indexes:
            file_path = os.path.join(os.path.dirname(os.path.dirname(__file__))+'\\indexes\\', index, 'data.csv')  # file path for index

            await update_quotes(file_path, index)

            percentage += percent_step

            logger.info(f"Downloaded {index} quotes, {percentage:.2f}% completed")
            print(f"Downloaded {index} quotes, {percentage:.2f}% completed")

        logger.info("Downloading completed")
        print("Downloading completed")
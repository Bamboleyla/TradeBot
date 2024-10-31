import logging
import os
import pandas as pd

from services.file import FileService
from api.services.client import AlorClientService

__all__ = "IMOEX_Manager"

logger = logging.getLogger(__name__)


class IMOEX_Manager:
    def __init__(self):
        self.ticker = 'IMOEX'
        self.__directory = os.path.dirname(__file__)  # get current directory
        self.__data_path = os.path.join(self.__directory, 'data.csv')

    async def __prepare(self) -> pd.DataFrame:
        file = FileService()

        if not os.path.exists(self.__data_path):  # if file doesn't exist
            file.create_data_file(self.__data_path)  # create date file in directory
            logger.info("Date file created")

        quotes = pd.read_csv(self.__data_path, header=0)

        # get last date from file, if there is no data then it will be firs minute of first day of current month
        last_date = file.get_last_date(quotes)

        client = AlorClientService()

        data = await client.ws_history_date(self.ticker, last_date)  # get data from last date to now

        if len(data) == 1:  # if data is empty
            return quotes
        else:
            file.update_file(self.ticker, quotes, data,)  # update file
            quotes.to_csv(self.__data_path, index=False)  # write quotes to file
            return quotes

    async def run(self):
        quotes = await self.__prepare()

        print(quotes)

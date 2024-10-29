import logging
import os
import pandas as pd

from services.file import FileService
from api.services.client import AlorClientService
from strategies.doubleST import DoubleST

__all__ = "SBER_Manager"

logger = logging.getLogger(__name__)


class SBER_Manager:
    def __init__(self):
        self.ticker = 'SBER'
        self.__directory = os.path.dirname(__file__)  # get current directory
        self.__data_path = os.path.join(self.__directory, 'data.csv')

    async def __prepare(self) -> pd.DataFrame:
        """
        Prepare and update the quotes DataFrame with historical data.

        This asynchronous method performs the following steps:
        - Checks if the data file exists. If not, creates it and logs the event.
        - Reads the quotes from the data file into a DataFrame.
        - Retrieves the last date from the quotes file or defaults to the first minute
        of the first day of the current month if the file is empty.
        - Fetches historical data from the AlorClientService starting from the last date.
        - Updates the file with new data if available and returns the updated DataFrame.

        :return: A pandas DataFrame containing the updated quotes data.
        """
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
        logger.info("Start %s manager", self.ticker)

        quotes = await self.__prepare()

        logger.info(" %s manager prepared", self.ticker)

        quotes['date'] = pd.to_datetime(quotes['date'], format='%Y%m%d %H:%M:%S')
        quotes['ticker'] = quotes['ticker'].astype('category')

        double_st = DoubleST(self.__directory, quotes)

        double_st.run(quotes)
        double_st.show(quotes)

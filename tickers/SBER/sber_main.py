import logging
import os

from services.file import FileService
from api.services.client import AlorClientService
from strategies.doubleST import DoubleST

__all__ = "SBER_Manager"

logger = logging.getLogger(__name__)


class SBER_Manager:
    def __init__(self):
        self.ticker = 'SBER'
        self.__directory = os.path.dirname(__file__)  # get current directory

    async def __prepare(self):
        file = FileService()

        file_path = os.path.join(self.__directory, 'data.txt')  # get path to file, where data will be stored

        if not os.path.exists(file_path):  # if file doesn't exist
            file.create_file(file_path)  # create date file in directory
            logger.info("Date file created")

        # get last date from file, if there is no data then it will be firs minute of first day of current month
        last_date = file.last_line_date(file_path)

        client = AlorClientService()

        data = await client.ws_history_date(self.ticker, last_date)  # get data from last date to now

        if len(data) == 1:  # if data is empty
            logger.info(f"No new data from {self.ticker}")
            return
        else:
            file.update_file(self.ticker, data, file_path)  # update file
            logger.info(f"Data from {self.ticker} updated")

    async def run(self):
        logger.info("Start %s manager", self.ticker)
        await self.__prepare()
        logger.info(" %s manager prepared", self.ticker)

        double_st = DoubleST(self.__directory)
        is_buy = double_st.buy()
        is_sell = double_st.sell()

        if is_buy:
            logger.info(f"{self.ticker} buy")

        elif is_sell:
            logger.info(f"{self.ticker} sell")

        else:
            logger.info(f"{self.ticker} nothing")

import logging
import os

from services.history import HistoryService
from services.file import FileService
from api.services.client import AlorClientService

__all__ = "SBER_Manager"

logger = logging.getLogger(__name__)


class SBER_Manager:
    def __init__(self):
        self.ticker = 'SBER'

    async def __prepare(self):
        directory = os.path.dirname(__file__)  # get current directory

        hs = HistoryService()
        is_there_date_file = hs.check_date_file(directory)  # is there date file in directory?

        client = AlorClientService()
        file = FileService()

        if not is_there_date_file:
            file.create_file(directory)  # create date file in directory
            logger.info("Date file created")

        last_date = file.last_line_date(directory)  # get last date from file, if there is no data then it will be firs minute of first day of current month
        data = await client.ws_history_date(self.ticker, last_date)  # get data from last date to now

        if len(data) == 1:  # if data is empty
            logger.info(f"No new data from {self.ticker}")
            return
        else:
            file.update_file(self.ticker, directory, data)  # update file
            logger.info(f"Data from {self.ticker} updated")

    async def run(self):
        logger.info("Start %s manager", self.ticker)
        await self.__prepare()
        logger.info(" %s manager prepared", self.ticker)

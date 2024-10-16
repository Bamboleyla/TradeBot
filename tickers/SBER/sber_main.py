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
        file = FileService()

        if not os.path.exists(self.__data_path):  # if file doesn't exist
            file.create_data_file(self.__data_path)  # create date file in directory
            logger.info("Date file created")

        df = pd.read_csv(self.__data_path, header=0)

        # get last date from file, if there is no data then it will be firs minute of first day of current month
        last_date = file.get_last_date(df)
        df.info()

        client = AlorClientService()

        data = await client.ws_history_date(self.ticker, last_date)  # get data from last date to now

        if len(data) == 1:  # if data is empty
            return df
        else:
            file.update_file(self.ticker, df, data,)  # update file
            df.to_csv(self.__data_path, index=False)  # write df to file
            return df

    async def run(self):
        logger.info("Start %s manager", self.ticker)
        df = await self.__prepare()
        logger.info(" %s manager prepared", self.ticker)

        df['date'] = pd.to_datetime(df['date'], format='%Y%m%d %H:%M:%S')
        df['ticker'] = df['ticker'].astype('category')

        df.info()

        df.set_index('date')
        print(df)

        double_st = DoubleST(self.__directory,)
        is_buy = double_st.buy()
        is_sell = double_st.sell()

        if is_buy:
            logger.info(f"{self.ticker} buy")

        elif is_sell:
            logger.info(f"{self.ticker} sell")

        else:
            logger.info(f"{self.ticker} nothing")

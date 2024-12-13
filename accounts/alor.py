import asyncio
import pandas as pd
import os

from datetime import datetime, timezone, timedelta
from api.client import AlorClientService
from configurations.alor import AlorConfiguration
from services.downloader import Downloader
from services.manager import Manager
from terminals.main import DoubleST


class AlorAccount:
    def __init__(self):
        self.__client = AlorClientService()
        self.__config = AlorConfiguration()
        self.__balance = asyncio.run(self.__client.get_balance())
        self.__positions = asyncio.run(self.__client.get_positions())
        self.__orders = asyncio.run(self.__client.get_orders())

    def run(self):
        loader = Downloader()
        asyncio.run(loader.run(tickers=['SBER', 'BSPB'], indexes=[]))
        manager = Manager('SBER')
        quotes = manager.get_quotes()
        quotes['date'] = pd.to_datetime(quotes['date'], format='%Y%m%d %H:%M:%S')

        dir = manager.get_directory()
        double_st = DoubleST(dir)

        dobleST = pd.read_csv(os.path.join(dir, 'dobleST.csv'), header=0)
        # If the data and quotes have the same last dates, then there is no point in recalculating
        data = dobleST if (dobleST['date'].iloc[-1] == str(quotes['date'].iloc[-1])) else double_st.run(quotes)
        data.to_csv(os.path.join(dir, 'dobleST.csv'), index=False)  # write data to file

        data['date'] = pd.to_datetime(data['date'])  # Convert 'date' column to datetime type
        two_days_quotes = data[data['date'] >= data['date'].dt.strftime('%Y%m%d').unique()[-2] + ' 10:00:00']  # get last 2 days

        double_st.show(two_days_quotes)

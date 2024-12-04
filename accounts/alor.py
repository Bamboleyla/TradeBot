import asyncio
import pandas as pd

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
        asyncio.run(loader.run())
        for ticker in ['SBER', 'BSPB']:
            manager = Manager(ticker)
            chart = manager.get_chart()
            if chart is None:
                quotes = manager.get_quotes()  # get quotes
                quotes['date'] = pd.to_datetime(quotes['date'])  # Convert 'date' column to datetime type
                two_days_quotes = quotes[quotes['date'] >= quotes['date'].dt.strftime('%Y%m%d').unique()[-2] + ' 10:00:00']  # get last 2 days
                dir = manager.get_directory()
                double_st = DoubleST(dir)
                chart = double_st.run(two_days_quotes)
                print(chart)
            else:
                pass

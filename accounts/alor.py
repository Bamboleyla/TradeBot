import asyncio
import pandas as pd
import os
import time

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
        if self.__config.is_work == True:
            last_load_time = None
            time_until_next_update = None

            while self.__config.is_work:
                if last_load_time is None or (time_until_next_update and time_until_next_update < timedelta(seconds=0)):
                    asyncio.run(loader.run(tickers=['SBER'], indexes=[]))
                    manager = Manager('SBER')
                    quotes = manager.get_quotes()
                    quotes['date'] = pd.to_datetime(quotes['date'], format='%Y%m%d %H:%M:%S')

                    dir = manager.get_directory()
                    double_st = DoubleST(dir)

                    dobleST = pd.read_csv(os.path.join(dir, 'dobleST.csv'), header=0)
                    # If the data and quotes have the same last dates, then there is no point in recalculating
                    data = dobleST if (dobleST['date'].iloc[-1] == str(quotes['date'].iloc[-1])) else double_st.run(quotes)
                    data.to_csv(os.path.join(dir, 'dobleST.csv'), index=False)  # write data to file

                    last_load_time = pd.to_datetime(data['date'].iloc[-1]).tz_localize('Etc/GMT-3')
                    time.sleep(10)

                else:
                    time_now = datetime.now(timezone(timedelta(hours=3)))
                    print(f"Current time (UTC+3): {time_now}")
                    print(f"Last load time (UTC+3): {last_load_time}")
                    time_until_next_update = ((last_load_time + timedelta(minutes=5)) - time_now)
                    print(f"Time until next update: {time_until_next_update} seconds")
                    time.sleep(10)

        # data['date'] = pd.to_datetime(data['date'])  # Convert 'date' column to datetime type
        # two_days_quotes = data[data['date'] >= data['date'].dt.strftime('%Y%m%d').unique()[-2] + ' 10:00:00']  # get last 2 days
        # double_st.show(two_days_quotes)

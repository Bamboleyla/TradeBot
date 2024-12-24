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
        if self.__config.is_work:

            manager = Manager('SBER')
            dir = manager.get_directory()

            double_st = DoubleST(dir)

            data = pd.read_csv(os.path.join(dir, 'dobleST.csv'), header=0)

            last_load_time = pd.to_datetime(data['date'].iloc[-1]).tz_localize('Etc/GMT-3')
            time_until_next_update = None

            while self.__config.is_work:
                time_now = datetime.now(timezone(timedelta(hours=3))).replace(microsecond=0)

                if (last_load_time + timedelta(minutes=5)) < time_now:
                    asyncio.run(loader.run(tickers=['SBER'], indexes=[]))

                    quotes = manager.get_quotes()
                    quotes['date'] = pd.to_datetime(quotes['date'], format='%Y%m%d %H:%M:%S')

                    if data['date'].iloc[-1] != str(quotes['date'].iloc[-1]):
                        data = double_st.run(quotes)
                        data.to_csv(os.path.join(dir, 'dobleST.csv'), index=False)  # write data to file

                        last_load_time = pd.to_datetime(data['date'].iloc[-1]).tz_localize('Etc/GMT-3').replace(microsecond=0)
                        time_until_next_update = None

                    time.sleep(10)

                else:
                    time_until_next_update = ((last_load_time + timedelta(minutes=5)) - time_now)
                    info = pd.DataFrame(columns=['time_now', 'last_load_time', 'time_until_next_update'])
                    info.loc[len(info)] = [time_now, last_load_time, time_until_next_update]
                    print(info)
                    time.sleep(10)

        # data['date'] = pd.to_datetime(data['date'])  # Convert 'date' column to datetime type
        # two_days_quotes = data[data['date'] >= data['date'].dt.strftime('%Y%m%d').unique()[-2] + ' 10:00:00']  # get last 2 days
        # double_st.show(two_days_quotes)

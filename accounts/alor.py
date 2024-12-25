import asyncio
import pandas as pd
import os
import finplot as fplt
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
        if self.__config.is_work:
            manager = Manager('SBER')
            dir = manager.get_directory()

            data = pd.read_csv(os.path.join(dir, 'dobleST.csv'), header=0)

            def update():
                loader = Downloader()
                manager = Manager('SBER')
                dir = manager.get_directory()
                double_st = DoubleST(dir)

                data = pd.read_csv(os.path.join(dir, 'dobleST.csv'), header=0)
                last_load_time = pd.to_datetime(data['date'].iloc[-1]).tz_localize('Etc/GMT-3')
                time_until_next_update = None

                if self.__config.is_work:
                    time_now = datetime.now(timezone(timedelta(hours=3))).replace(microsecond=0)

                    if (last_load_time + timedelta(minutes=5, seconds=20)) < time_now:
                        asyncio.run(loader.run(tickers=['SBER'], indexes=[]))

                        quotes = manager.get_quotes()
                        quotes['date'] = pd.to_datetime(quotes['date'], format='%Y%m%d %H:%M:%S')

                        if data['date'].iloc[-1] != str(quotes['date'].iloc[-1]):
                            data = double_st.run(quotes)
                            data.to_csv(os.path.join(dir, 'dobleST.csv'), index=False)  # write data to file

                            last_load_time = pd.to_datetime(data['date'].iloc[-1]).tz_localize('Etc/GMT-3').replace(microsecond=0)
                            time_until_next_update = None

                            # Update the live plot
                            self.update_plot(data)

                    else:
                        time_until_next_update = ((last_load_time + timedelta(minutes=5, seconds=20)) - time_now)
                        info = pd.DataFrame(columns=['time_now', 'last_load_time', 'time_until_next_update'])
                        info.loc[len(info)] = [time_now, last_load_time, time_until_next_update]
                        print(info)

            fplt.foreground = '#FFFFFF'
            fplt.background = '#000000'
            fplt.cross_hair_color = '#FFFFFF'

            data.set_index('date', inplace=True)
            data.index = pd.to_datetime(data.index).tz_localize('Etc/GMT-5')

            fplt.candlestick_ochl(data[['open', 'close', 'high', 'low']].tail(100))
            fplt.add_legend("SBER")
            fplt.timer_callback(update, 10)  # start update timer
            fplt.show()

    def update_plot(self, data: pd.DataFrame):
        data.set_index('date', inplace=True)
        data.index = pd.to_datetime(data.index).tz_localize('Etc/GMT-5')

        fplt.candlestick_ochl(data[['open', 'close', 'high', 'low']].tail(100))
        fplt.refresh()

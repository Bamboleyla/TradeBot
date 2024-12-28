import asyncio
import pandas as pd
import os
import finplot as fplt
import json

from datetime import datetime, timezone, timedelta
from api.client import AlorClientService
from configurations.alor import AlorConfiguration
from services.downloader import Downloader
from services.manager import Manager
from terminals.main import DoubleST
from services.file import FileService


class AlorAccount:
    def __init__(self):
        self.__client = AlorClientService()
        self.__config = AlorConfiguration()
        self.__balance = asyncio.run(self.__client.get_balance())
        self.__positions = asyncio.run(self.__client.get_positions())
        self.__orders = asyncio.run(self.__client.get_orders())

    def run(self):
        # if self.__config.is_work:
        manager = Manager('SBER')

        terminal = manager.get_terminal_data()
        updated_terminal = asyncio.run(self.update_terminal(terminal))

        def update():
            loader = Downloader()
            manager = Manager('SBER')
            dir = manager.get_directory()
            double_st = DoubleST(dir)

            terminal = manager.get_terminal()
            last_load_time = pd.to_datetime(terminal['date'].iloc[-1]).tz_localize('Etc/GMT-3')
            time_until_next_update = None

            if self.__config.is_work:
                time_now = datetime.now(timezone(timedelta(hours=3))).replace(microsecond=0)

                if (last_load_time + timedelta(minutes=5, seconds=20)) < time_now:
                    asyncio.run(loader.run(tickers=['SBER'], indexes=[]))

                    quotes = manager.get_quotes()
                    quotes['date'] = pd.to_datetime(quotes['date'], format='%Y%m%d %H:%M:%S')

                    if terminal['date'].iloc[-1] != str(quotes['date'].iloc[-1]):
                        terminal = double_st.run(quotes)
                        terminal.to_csv(os.path.join(dir, 'explore.csv'), index=False)  # write data to file

                        last_load_time = pd.to_datetime(terminal['date'].iloc[-1]).tz_localize('Etc/GMT-3').replace(microsecond=0)
                        time_until_next_update = None

                        # Update the live plot
                        self.update_plot(terminal)

                else:
                    time_until_next_update = ((last_load_time + timedelta(minutes=5, seconds=20)) - time_now)
                    info = pd.DataFrame(columns=['time_now', 'last_load_time', 'time_until_next_update'])
                    info.loc[len(info)] = [time_now, last_load_time, time_until_next_update]
                    print(info)

        fplt.foreground = '#FFFFFF'
        fplt.background = '#000000'
        fplt.cross_hair_color = '#FFFFFF'

        terminal.set_index('date', inplace=True)
        terminal.index = pd.to_datetime(terminal.index).tz_localize('Etc/GMT-5')

        fplt.candlestick_ochl(terminal[['open', 'close', 'high', 'low']].tail(100))
        fplt.add_legend("SBER")
        fplt.timer_callback(update, 10)  # start update timer
        fplt.show()

    def update_plot(self, data: pd.DataFrame):
        data.set_index('date', inplace=True)
        data.index = pd.to_datetime(data.index).tz_localize('Etc/GMT-5')

        fplt.candlestick_ochl(data[['open', 'close', 'high', 'low']].tail(100))
        fplt.refresh()

    async def update_terminal(self, data: pd.DataFrame):
        last_date = datetime.strptime(data.iloc[-1]["date"], "%Y%m%d %H:%M:%S").replace(tzinfo=timezone(timedelta(hours=3)))
        ticker = data.iloc[-1]["ticker"]
        quotes = await self.__client.ws_history_date(ticker, last_date)  # get data from last date to now

        if len(quotes) > 0:
            for i, item in enumerate(quotes):  # for each item in data
                json_item = json.loads(item)['data']  # convert item to json
                date = datetime.fromtimestamp(json_item['time'], timezone.utc).astimezone(
                    timezone(offset=timedelta(hours=3))).strftime('%Y%m%d %H:%M:%S')  # convert timestamp to datetime, then to local time (UTC+3)

                if i == 0:
                    data.iloc[-1] = [
                        ticker, date, json_item["open"], json_item["high"], json_item["low"],
                        json_item["close"], json_item["volume"], None, None, None, None, None
                    ]
                    print(data.tail(1))
                    continue

                data.loc[len(data), ['ticker', 'date', 'open', 'high', 'low', 'close', 'volume']] = [
                    ticker, date, json_item["open"], json_item["high"], json_item["low"],
                    json_item["close"], json_item["volume"]
                ]  # add row to df

                manager = Manager('SBER')
                dir = manager.get_directory()
            data.to_csv(os.path.join(dir, 'test.csv'), index=False)  # write data to file

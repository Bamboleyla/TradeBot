import asyncio
import pandas as pd
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
        loader = Downloader()
        asyncio.run(loader.run(tickers=['SBER', 'BSPB'], indexes=[]))

        def download_two_days_quotes():
            quotes = manager.get_quotes()  # get quotes
            quotes['date'] = pd.to_datetime(quotes['date'])  # Convert 'date' column to datetime type
            two_days_quotes = quotes[quotes['date'] >= quotes['date'].dt.strftime('%Y%m%d').unique()[-2] + ' 10:00:00']  # get last 2 days
            dir = manager.get_directory()
            double_st = DoubleST(dir)
            chart = double_st.run(two_days_quotes)
            chart.to_csv(dir+'/chart.csv', index=False)  # write quotes to file
            return chart

        for ticker in ['SBER', 'BSPB']:
            manager = Manager(ticker)
            chart = manager.get_chart()
            if chart is None:
                chart = download_two_days_quotes()

            else:
                last_time = datetime.strptime(chart.iloc[-1]["date"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone(timedelta(hours=3)))
                now = datetime.now(timezone(timedelta(hours=3)))
                if (((now - last_time).total_seconds() / 60) > 10):
                    chart = download_two_days_quotes()

                else:
                    data = asyncio.run(self.__client.ws_history_date(ticker, last_time))
                    print(data)

            # self.show(chart, ticker)

    def show(self, data: pd.DataFrame, ticker: str) -> None:

        # candlestick
        data.set_index('date', inplace=True)
        data.index = pd.to_datetime(data.index).tz_localize('Etc/GMT-5')

        fplt.candlestick_ochl(data[['open', 'close', 'high', 'low']])
        fplt.plot(data['ST_FAST_UP'], legend='ST_FAST_UP', color='#FF0000', width=2)
        fplt.plot(data['ST_FAST_LOW'], legend='ST_FAST_LOW', color='#228B22', width=2)
        fplt.plot(data['ST_SLOW_UP'], legend='ST_SLOW_UP', color='#B22222', width=3)
        fplt.plot(data['ST_SLOW_LOW'], legend='ST_SLOW_LOW', color='#006400', width=3)
        fplt.plot(data['EMA'], legend='EMA')

        fplt.add_legend(ticker)
        fplt.show()

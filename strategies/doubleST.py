import logging
import os
import pandas as pd
# import matplotlib.pyplot as plt
import finplot as fplt

from indicators.ema import EMA
from indicators.super_trend import super_trend

__all__ = "DoubleST_Strategy"

logger = logging.getLogger(__name__)


class DoubleST:
    def __init__(self, directory: str, quotes: pd.DataFrame):
        self.__export_path = os.path.join(directory, 'doubleST_data.csv')

        if not os.path.exists(self.__export_path):
            with open(self.__export_path, 'w') as f:
                f.write('ticker,date,ST3,ST5,EMA\n')
            quotes[['ticker', 'date']].to_csv(self.__export_path, mode='a', header=False, index=False)

    def run(self, quotes: pd.DataFrame) -> None:

        date = pd.read_csv(self.__export_path, header=0)

        date = EMA(5, quotes, date)  # calculate EMA
        date = super_trend(10, 3, quotes, date, 'ST3')  # calculate SuperTrend
        date = super_trend(20, 5, quotes, date, 'ST5')  # calculate SuperTrend

        date.to_csv(self.__export_path, index=False)  # write date to file

    def buy(self, close: float, st3: float, st5: float) -> bool:
        return close > st3 and close < st5

    def sell(self) -> bool:
        pass

    def show(self, quotes: pd.DataFrame) -> None:
        indicators = pd.read_csv(self.__export_path, header=0)
        quotes[['ST3', 'ST5', 'EMA']] = indicators[['ST3', 'ST5', 'EMA']]
        quotes.set_index('date', inplace=True)
        quotes.index = pd.to_datetime(quotes.index).tz_localize('Etc/GMT-5')

        fplt.candlestick_ochl(quotes[['open', 'close', 'high', 'low']])
        fplt.plot(quotes['ST3'], legend='ST3', width=2)
        fplt.plot(quotes['ST5'], legend='ST5', width=2)
        fplt.plot(quotes['EMA'], legend='EMA')

        fplt.add_legend('Double SuperTrend')
        fplt.show()

    def analyze(self, quotes: pd.DataFrame) -> None:
        date = pd.read_csv(self.__export_path, header=0)
        date[['close']] = quotes[['close']]
        date['BUY'] = date.apply(lambda row: self.buy(row['close'], row['ST3'], row['ST5']), axis=1)
        pass

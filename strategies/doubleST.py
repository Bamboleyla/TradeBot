import logging
import os
import pandas as pd
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

        date = pd.read_csv(self.__export_path, header=0)  # read date from file

        date = EMA(5, quotes, date)  # calculate EMA
        date = super_trend(10, 3, quotes, date, 'ST3')  # calculate SuperTrend
        date = super_trend(20, 5, quotes, date, 'ST5')  # calculate SuperTrend

        date.to_csv(self.__export_path, index=False)  # write date to file

    def long_buy(self, close: float, st3: float, st5: float) -> bool:
        return close < st3 and close > st5

    def long_sell(self, open: float, close: float, st3: float, st5: float) -> bool:
        if close < st3 and close < st5:
            return True
        elif open > st3 and close < st3:
            return True
        else:
            return False

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
        date[['open', 'close', 'high', 'low']] = quotes[['open', 'close', 'high', 'low']]
        date['BUY'] = date.apply(lambda row: self.long_buy(row['close'], row['ST3'], row['ST5']), axis=1)
        date['SELL'] = date.apply(lambda row: self.long_sell(row['open'], row['close'], row['ST3'], row['ST5']), axis=1)
        date['Marker_Buy', 'Marker_Sell'] = pd.Series(dtype='float64')

        account = 3000
        stocks = 0
        action = None
        for index, row in date.iterrows():
            if action == 'BUY' and stocks == 0:
                account -= row['open']*10
                stocks = 10
                date.loc[index, 'Marker_Buy'] = row['open']
                action = None
            elif action == 'SELL' and stocks > 0:
                account += row['open']*10
                stocks = 0
                date.loc[index, 'Marker_Sell'] = row['open']
                action = None
            elif row['BUY']:
                action = 'BUY'
            elif row['SELL'] and stocks > 0:
                action = 'SELL'
            else:
                pass

        print(f'Final account: {account}')
        print(f'Stocks: {stocks}')

        date.set_index('date', inplace=True)
        date.index = pd.to_datetime(quotes.index).tz_localize('Etc/GMT-5')

        fplt.candlestick_ochl(date[['open', 'close', 'high', 'low']])
        fplt.plot(date['ST3'], legend='ST3', width=2)
        fplt.plot(date['ST5'], legend='ST5', width=2)
        fplt.plot(date['EMA'], legend='EMA')

        fplt.plot(date['Marker_Buy'], color='b', style='x', width=2)
        fplt.plot(date['Marker_Buy']-1, color='#4a5', style='^', legend='buy', width=2)
        fplt.plot(date['Marker_Sell'], color='b', style='x', width=2)
        fplt.plot(date['Marker_Sell']+1, color='r', style='v', legend='sell', width=2)

        fplt.add_legend('Double SuperTrend')
        fplt.show()

import logging
import os
import pandas as pd
import finplot as fplt

from indicators.ema import EMA
from indicators.super_trend import super_trend
from indicators.dmoex import dmoex
from indexes.IMOEX.imoex_main import IMOEX_Manager

__all__ = "DoubleST_Strategy"

logger = logging.getLogger(__name__)


class DoubleST:
    def __init__(self, directory: str, quotes: pd.DataFrame):
        self.__directory = directory
        self.__export_data = os.path.join(directory, 'doubleST\\data.csv')

        if not os.path.exists(self.__export_data):
            with open(self.__export_data, 'w') as f:
                f.write('ticker,date,ST3,ST5,EMA\n')
            quotes[['ticker', 'date']].to_csv(self.__export_data, mode='a', header=False, index=False)

    def run(self, quotes: pd.DataFrame) -> None:
        imoex = IMOEX_Manager()
        index_quotes = imoex.get_quotes()

        date = pd.read_csv(self.__export_data, header=0)  # read date from file

        # if data length less than quotes length then add new data
        if len(date) < len(quotes):
            new_data = quotes[len(date):]
            date = pd.concat([date, new_data], ignore_index=True)

        date = EMA(5, quotes, date)  # calculate EMA
        date = super_trend(10, 3, quotes, date, 'ST3')  # calculate SuperTrend
        date = super_trend(20, 5, quotes, date, 'ST5')  # calculate SuperTrend
        date = dmoex(index_quotes)  # calculate DMOEX

        date.to_csv(self.__export_data, index=False)  # write date to file

    def long_buy(self, close: float, st3: float, st5: float) -> bool:
        if close < st3 and close > st5:
            deep = (st3 - st5)/3
            if close < st5 + deep:
                return True
            else:
                return False

    def long_sell(self, open: float, close: float, st3: float, st5: float) -> bool:
        if close < st3 and close < st5:
            return True

        elif open > st3 and close < st3:
            return True
        elif open > st3 + 1.5 or close > st3 + 1.5:
            return True
        else:
            return False

    def show(self, quotes: pd.DataFrame) -> None:
        date = pd.read_csv(self.__export_data, header=0)
        date[['open', 'close', 'high', 'low']] = quotes[['open', 'close', 'high', 'low']]
        date['BUY'] = date.apply(lambda row: self.long_buy(row['close'], row['ST3'], row['ST5']), axis=1)
        date['SELL'] = date.apply(lambda row: self.long_sell(row['open'], row['close'], row['ST3'], row['ST5']), axis=1)
        date['Marker_Buy', 'Marker_Sell', 'Account', 'P/L'] = pd.Series(dtype='float64')

        account = 3000
        stocks = 0
        action = None
        last_buy = 0
        for index, row in date.iterrows():
            if index == 0:
                date.loc[index, 'Account'] = account
            if action == 'BUY' and stocks == 0 and row['BUY']:
                account -= row['open']*10
                date.loc[index, 'Account'] = account
                stocks = 10
                date.loc[index, 'Marker_Buy'] = row['open']
                last_buy = row['open']
                action = None
            elif action == 'SELL' and stocks > 0:
                account += row['open']*10
                date.loc[index, 'Account'] = account
                date.loc[index, 'P/L'] = (row['open'] - last_buy) * 10
                stocks = 0
                date.loc[index, 'Marker_Sell'] = row['open']
                last_buy = 0
                action = None
            elif row['BUY']:
                action = 'BUY'
            elif row['SELL'] and stocks > 0:
                action = 'SELL'
            else:
                pass

        print(f'Final account: {account}')
        print(f'Stocks: {stocks}')

        # list of deals
        deals = pd.DataFrame()
        deals[['ticker', 'date',  'Marker_Buy', 'Marker_Sell', 'P/L', 'Account']] = date[['ticker', 'date', 'Marker_Buy', 'Marker_Sell', 'P/L', 'Account']]
        deals = deals[deals['Account'].notnull()]
        deals.to_excel(os.path.join(self.__directory, 'doubleST/deals.xlsx'), index=False)

        # candlestick
        date.set_index('date', inplace=True)
        date.index = pd.to_datetime(date.index).tz_localize('Etc/GMT-5')

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

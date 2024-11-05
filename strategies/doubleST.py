import logging
import os
import pandas as pd
import finplot as fplt
import talib

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
                f.write('ticker,data,ST3,ST5,EMA\n')
            quotes[['ticker', 'date']].to_csv(self.__export_data, mode='a', header=False, index=False)

    def run(self, quotes: pd.DataFrame) -> None:
        imoex = IMOEX_Manager()
        index_quotes = imoex.get_quotes()

        data = quotes[['ticker', 'date', 'open', 'high', 'low', 'close']].copy()

        data['EMA'] = talib.EMA(data['close'].values, timeperiod=5)
        data = super_trend(10, 3, data)  # calculate SuperTrend
        data = super_trend(20, 5, data)  # calculate SuperTrend
        data = dmoex(index_quotes, data)  # calculate DMOEX

        data.to_csv(self.__export_data, index=False)  # write data to file

    def long_buy(self, close: float, st3: float, st5: float) -> bool:
        if close < st3 and close > st5:

            if close < st5 + 0.35:
                return True
            else:
                return False
        else:
            return False

    def long_sell(self, open: float, close: float, st3: float, st5: float) -> bool:
        if close < st3 and close < st5:
            return True
        elif open > st3 and close < st5:
            return True
        else:
            return False

    def long_take_profit(self, open: float, close: float, st3: float) -> bool:
        return True if open > st3 + 1.5 or close > st3 + 1.5 else False

    def show(self) -> None:
        data = pd.read_csv(self.__export_data, header=0)
        data['LONG_BUY'] = data.apply(lambda row: self.long_buy(row['close'], row['ST3'], row['ST5']), axis=1)
        data['LONG_SELL'] = data.apply(lambda row: self.long_sell(row['open'], row['close'], row['ST3'], row['ST5']), axis=1)
        data['LONG_TAKE_PROFIT'] = data.apply(lambda row: self.long_take_profit(row['open'], row['close'], row['ST3']), axis=1)
        data['BUY_PRISE', 'SELL_PRISE', 'Account', 'P/L', 'SIGNAL'] = pd.Series(dtype='float64')

        account = 3000  # amount of money
        stocks = 0  # amount of stocks
        action = None  # 'BUY' or 'SELL'
        last_buy = 0  # last price of buy
        commission = 0.0005  # broker commission is 0,05%

        for index, row in data.iterrows():
            if index == 0:
                data.loc[index, 'Account'] = account
            elif index == len(data) - 1 and stocks > 0:
                action = 'LONG_SELL'

            if action == 'LONG_BUY' and stocks == 0 and row['LONG_BUY']:
                data.loc[index, 'SIGNAL'] = action
                prise = (data.loc[index-1, 'ST5']+0.35)
                account -= prise*10
                account -= prise * commission
                data.loc[index, 'Account'] = account
                stocks = 10
                data.loc[index, 'BUY_PRISE'] = prise
                last_buy = prise
                action = None
            elif action == 'LONG_SELL' or action == 'LONG_TAKE_PROFIT' and stocks > 0:
                data.loc[index, 'SIGNAL'] = action
                account += row['open']*10
                account -= row['open']*10 * commission
                data.loc[index, 'Account'] = account
                data.loc[index, 'P/L'] = (row['open'] - last_buy) * 10
                stocks = 0
                data.loc[index, 'SELL_PRISE'] = row['open']
                last_buy = 0
                action = None

            if row['LONG_BUY']:
                action = 'LONG_BUY'
            elif row['LONG_SELL'] and stocks > 0:
                action = 'LONG_SELL'
            elif row['LONG_TAKE_PROFIT'] and stocks > 0:
                action = 'LONG_TAKE_PROFIT'

        print(f'Final account: {account}')
        print(f'Stocks: {stocks}')

        data.to_excel('show.xlsx', index=False)

        # list of deals
        deals = pd.DataFrame()
        deals[['ticker', 'date', 'SIGNAL',  'BUY_PRISE', 'SELL_PRISE', 'P/L', 'Account']
              ] = data[['ticker', 'date', 'SIGNAL', 'BUY_PRISE', 'SELL_PRISE', 'P/L', 'Account']]
        deals = deals[deals['Account'].notnull()]
        deals.to_excel(os.path.join(self.__directory, 'doubleST/deals.xlsx'), index=False)

        # candlestick
        data.set_index('date', inplace=True)
        data.index = pd.to_datetime(data.index).tz_localize('Etc/GMT-5')

        fplt.candlestick_ochl(data[['open', 'close', 'high', 'low']])
        fplt.plot(data['ST3'], legend='ST3', width=2)
        fplt.plot(data['ST5'], legend='ST5', width=2)
        fplt.plot(data['EMA'], legend='EMA')

        fplt.plot(data['BUY_PRISE'], color='b', style='x', width=2)
        fplt.plot(data.loc[data['SIGNAL'] == 'LONG_BUY', 'BUY_PRISE']-1, color='#4a5', style='^', legend='buy', width=2)

        fplt.plot(data['SELL_PRISE'], color='b', style='x', width=2)
        fplt.plot(data.loc[data['SIGNAL'] == 'LONG_SELL', 'SELL_PRISE']+1, color='r', style='v', legend='long sell', width=2)
        fplt.plot(data.loc[data['SIGNAL'] == 'LONG_TAKE_PROFIT', 'SELL_PRISE']+1, color='#4a5', style='p', legend='take profit', width=2)

        fplt.add_legend('Double SuperTrend')
        fplt.show()

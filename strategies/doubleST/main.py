import logging
import os
import pandas as pd
import finplot as fplt
import talib
import json

from indicators.super_trend import super_trend
from strategies.doubleST.signals.long_open import long_buy
from strategies.doubleST.signals.long_close import long_sell
from strategies.doubleST.signals.short_open import short_buy

__all__ = "DoubleST_Strategy"

logger = logging.getLogger(__name__)


class DoubleST:
    def __init__(self, directory: str):
        self.__directory = directory

        with open(os.path.join(self.__directory, 'config.json'), 'r') as f:
            config = json.load(f)
            self.__var_profit = config['var_profit']
            self.__period = config['period']
            self.__multiplier = config['multiplier']

    def run(self, quotes: pd.DataFrame) -> pd.DataFrame:
        if os.path.exists(os.path.join(self.__directory, 'dobleST.csv')):  # if file with data exist
            data = pd.read_csv(os.path.join(self.__directory, 'dobleST.csv'), header=0)

            # If the data and quotes have the same last dates, then there is no point in recalculating
            if (data['date'].iloc[-1] == str(quotes['date'].iloc[-1])):
                return data

        data = quotes[['ticker', 'date', 'open', 'high', 'low', 'close']].copy()

        data['EMA'] = talib.EMA(data['close'].values, timeperiod=50)

        config = pd.DataFrame({'period': self.__period, 'multiplier': self.__multiplier})
        data = super_trend(config, data)  # calculate SuperTrends

        data.to_csv(os.path.join(self.__directory, 'dobleST.csv'), index=False)  # write data to file
        return data

    def calculate(self, data: pd.DataFrame, var_profit: float = None) -> None:
        if var_profit is None:
            var_profit = self.__var_profit

        stocks = 0  # amount of stocks
        buy_limit = []
        sell_limit = []

        for index, row in data.iterrows():
            # config
            if pd.isnull(row['ST_FAST']) or pd.isnull(row['ST_SLOW']):
                continue
            elif index == len(data) - 1 and stocks > 0:
                signal = 'LONG_SELL'
            elif index == len(data) - 1 and stocks < 0:
                signal = 'SHORT_SELL'

            # if len(buy_limit) > 0:

                # signals
            if stocks == 0:
                price = long_buy(data.loc[index - 1], row)
                if price is not None:
                    buy_limit.append(price)
                    if len(sell_limit) > 0:
                        sell_limit.pop(0)

                price = short_buy(data.loc[index - 1], row)
                if price is not None:
                    sell_limit.append(price)
            elif stocks > 0:
                price = long_sell(row)
                if price is not None:
                    sell_limit.append(price)

        # print(f'var_profit: {round(var_profit, 2)}, Final account: {round(account, 3)}')

    def show(self, data: pd.DataFrame) -> None:
        # list of deals
        deals = pd.DataFrame()
        deals[['ticker', 'date', 'SIGNAL_OPEN', 'SIGNAL_CLOSE',  'BUY_PRISE', 'SELL_PRISE']
              ] = data[['ticker', 'date', 'SIGNAL_OPEN', 'SIGNAL_CLOSE', 'BUY_PRISE', 'SELL_PRISE']]
        # deals = deals[deals['P/L'].notnull()]
        deals.to_excel(os.path.join(self.__directory, 'deals.xlsx'), index=False)

        # report
        print('|SIGNAL|COUNT|SUM P/L|VIN RATE|')

        # candlestick
        data.set_index('date', inplace=True)
        data.index = pd.to_datetime(data.index).tz_localize('Etc/GMT-5')

        fplt.candlestick_ochl(data[['open', 'close', 'high', 'low']])
        fplt.plot(data['ST_FAST'], legend='ST_FAST', width=2)
        fplt.plot(data['ST_SLOW'], legend='ST_SLOW', width=2)
        fplt.plot(data['EMA'], legend='EMA')

        fplt.plot(data['BUY_PRISE'], color='b', style='x', width=2)

        long_buy = data.loc[data['SIGNAL_OPEN'] == 'LONG_BUY', 'BUY_PRISE']
        if not long_buy.empty:
            fplt.plot(long_buy-1, color='#4a5', style='^', legend='buy', width=2)

        fplt.plot(data['SELL_PRISE'], color='b', style='x', width=2)

        long_sell = data.loc[data['SIGNAL_CLOSE'] == 'LONG_SELL', 'SELL_PRISE']
        if not long_sell.empty:
            fplt.plot(long_sell+1, color='#4a6', style='o', legend='sell', width=2)

        long_take_profit = data.loc[data['SIGNAL_CLOSE'] == 'LONG_TAKE_PROFIT', 'SELL_PRISE']
        if not long_take_profit.empty:
            fplt.plot(long_take_profit+1, color='#4a5', style='p', legend='take profit', width=2)

        short_buy = data.loc[data['SIGNAL_OPEN'] == 'SHORT_BUY', 'BUY_PRISE']
        if not short_buy.empty:
            fplt.plot(short_buy-1, color='r', style='^', legend='short buy', width=2)

        short_sell = data.loc[data['SIGNAL_CLOSE'] == 'SHORT_SELL', 'SELL_PRISE']
        if not short_sell.empty:
            fplt.plot(short_sell+1, color='r', style='o', legend='short sell', width=2)

        short_take_profit = data.loc[data['SIGNAL_CLOSE'] == 'SHORT_TAKE_PROFIT', 'SELL_PRISE']
        if not short_take_profit.empty:
            fplt.plot(short_take_profit-1, color='r', style='p', legend='short take profit', width=2)

        fplt.add_legend('Double SuperTrend')
        fplt.show()

    def optimize(self, data: pd.DataFrame, var_profit: dict) -> None:
        results = pd.DataFrame(columns=['var_profit', 'account', 'long_buy_count', 'long_sell_count',
                               'long_take_profit_count', 'short_buy_count', 'short_sell_count', 'short_take_profit_count'])

        start = var_profit['start']

        while start <= var_profit['end']:
            result = self.calculate(data, start)
            results.loc[len(results)] = {'var_profit': round(start, 3), 'account': round(result['account'], 3), 'long_buy_count': result['long_buy_count'],
                                         'long_sell_count': result['long_sell_count'], 'long_take_profit_count': result['long_take_profit_count'],
                                         'short_buy_count': result['short_buy_count'], 'short_sell_count': result['short_sell_count'],
                                         'short_take_profit_count': result['short_take_profit_count']}

            start += var_profit['step']

        results.to_excel(os.path.join(self.__directory, 'optimize.xlsx'), index=False)

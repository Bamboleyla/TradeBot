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
    def __init__(self, directory: str, var_profit: float):
        self.__directory = directory
        self.__export_data = os.path.join(directory, 'dobleST.csv')
        self.__var_profit = var_profit

    def run(self, quotes: pd.DataFrame) -> pd.DataFrame:

        data = quotes[['ticker', 'date', 'open', 'high', 'low', 'close']].copy()

        data['EMA'] = talib.EMA(data['close'].values, timeperiod=50)

        config = pd.DataFrame({'period': [10, 20], 'multiplier': [3, 5]})
        data = super_trend(config, data)  # calculate SuperTrends

        data.to_csv(self.__export_data, index=False)  # write data to file
        return data

    def long_buy(self, previous: pd.DataFrame, current: pd.DataFrame) -> bool:
        if previous['close'] <= previous['ST_FAST'] and previous['close'] > previous['ST_SLOW']:
            if current['open'] > current['ST_FAST'] and current['open'] > current['ST_SLOW']:
                return True
        return False

    def long_sell(self, open: float, close: float, st3: float) -> bool:
        if close < st3 or open < st3:
            return True
        return False

    def short_buy(self, open: float, close: float, hight: float, st3: float, st5: float) -> bool:
        if st3 < st5:
            if open < st3 and close < st3 and hight > st3:
                return True
        return False

    def short_sell(self, open: float, close: float, st3: float) -> bool:
        return True if open > st3 or close > st3 else False

    def short_take_profit(self, short_prise: float, open: float, close: float, low: float) -> bool:
        return True if open < short_prise - 20 or close < short_prise - 20 or low < short_prise - 20 else False

    def calculate(self, data: pd.DataFrame, var_profit: float = None) -> None:
        if var_profit is None:
            var_profit = self.__var_profit

        account = 0  # amount of money
        stocks = 0  # amount of stocks
        action = None  # 'BUY' or 'SELL'
        last_buy = 0  # last price of buy
        commission = 0.0005  # broker commission is 0,05%

        for index, row in data.iterrows():
            # config
            if index == 0:
                data.loc[index, 'Account'] = account
                continue
            elif pd.isnull(row['ST_FAST']) or pd.isnull(row['ST_SLOW']):
                continue
            elif index == len(data) - 1 and stocks > 0:
                action = 'LONG_SELL'
            elif index == len(data) - 1 and stocks < 0:
                action = 'SHORT_SELL'

            # take profit
            if stocks > 0:  # long sell
                take_profit = last_buy + var_profit
                if take_profit <= row['open'] or take_profit <= row['close'] or take_profit <= row['high']:
                    data.loc[index, 'SIGNAL'] = 'LONG_TAKE_PROFIT'
                    account += take_profit*10
                    account -= take_profit*10 * commission
                    data.loc[index, 'Account'] = account
                    data.loc[index, 'P/L'] = (var_profit) * 10
                    stocks = 0
                    data.loc[index, 'SELL_PRISE'] = take_profit
                    last_buy = 0
                    action = None

            # actions
            if action == 'LONG_BUY' and stocks == 0:
                data.loc[index, 'SIGNAL'] = action
                prise = (data.loc[index - 2, 'ST_FAST'])
                account -= prise*10
                account -= prise * commission
                data.loc[index, 'Account'] = account
                stocks = 10
                data.loc[index, 'BUY_PRISE'] = prise
                last_buy = prise
                action = None
            elif action == 'LONG_SELL' and stocks > 0:
                data.loc[index, 'SIGNAL'] = action
                account += row['open']*10
                account -= row['open']*10 * commission
                data.loc[index, 'Account'] = account
                data.loc[index, 'P/L'] = (row['open'] - last_buy) * 10
                stocks = 0
                data.loc[index, 'SELL_PRISE'] = row['open']
                last_buy = 0
                action = None
            elif action == 'SHORT_BUY' and stocks == 0:
                if row['open'] < row['ST_FAST']:
                    data.loc[index, 'SIGNAL'] = action
                    account += row['open']*10
                    account -= row['open']*10 * commission
                    data.loc[index, 'Account'] = account
                    stocks = -10
                    data.loc[index, 'BUY_PRISE'] = row['open']
                    last_buy = row['open']
                    action = None
                else:
                    action = None
            elif action == 'SHORT_SELL' or action == 'SHORT_TAKE_PROFIT' and stocks < 0:
                data.loc[index, 'SIGNAL'] = action
                account -= row['open']*10
                account -= row['open']*10 * commission
                data.loc[index, 'Account'] = account
                data.loc[index, 'P/L'] = (row['close'] - last_buy) * 10
                stocks = 0
                data.loc[index, 'SELL_PRISE'] = row['open']
                last_buy = 0
                action = None

            # signals
            if stocks == 0:
                if self.long_buy(data.loc[index - 1], row):
                    action = 'LONG_BUY'
                elif self.short_buy(row['open'], row['close'], row['high'], row['ST_FAST'], row['ST_SLOW']):
                    action = 'SHORT_BUY'
            elif stocks > 0:
                if self.long_sell(row['open'], row['close'], row['ST_FAST']):
                    action = 'LONG_SELL'
            elif stocks < 0:
                if self.short_sell(row['open'], row['close'], row['ST_FAST']):
                    action = 'SHORT_SELL'
                elif self.short_take_profit(last_buy, row['open'], row['close'], row['low']):
                    action = 'SHORT_TAKE_PROFIT'

        print(f'var_profit: {round(var_profit, 2)}, Final account: {round(account, 3)}')

        long_buy_count = data['SIGNAL'].value_counts().get('LONG_BUY', 0)
        long_sell_count = data['SIGNAL'].value_counts().get('LONG_SELL', 0)
        long_take_profit_count = data['SIGNAL'].value_counts().get('LONG_TAKE_PROFIT', 0)
        short_buy_count = data['SIGNAL'].value_counts().get('SHORT_BUY', 0)
        short_sell_count = data['SIGNAL'].value_counts().get('SHORT_SELL', 0)
        short_take_profit_count = data['SIGNAL'].value_counts().get('SHORT_TAKE_PROFIT', 0)

        return {'data': data, 'account': account, 'long_buy_count': long_buy_count,
                'long_sell_count': long_sell_count, 'long_take_profit_count': long_take_profit_count,
                'short_buy_count': short_buy_count, 'short_sell_count': short_sell_count,
                'short_take_profit_count': short_take_profit_count}

    def show(self, data: pd.DataFrame) -> None:
        # list of deals
        deals = pd.DataFrame()
        deals[['ticker', 'date', 'SIGNAL',  'BUY_PRISE', 'SELL_PRISE', 'P/L', 'Account']
              ] = data[['ticker', 'date', 'SIGNAL', 'BUY_PRISE', 'SELL_PRISE', 'P/L', 'Account']]
        deals = deals[deals['Account'].notnull()]
        deals.to_excel(os.path.join(self.__directory, 'deals.xlsx'), index=False)

        # candlestick
        data.set_index('date', inplace=True)
        data.index = pd.to_datetime(data.index).tz_localize('Etc/GMT-5')

        fplt.candlestick_ochl(data[['open', 'close', 'high', 'low']])
        fplt.plot(data['ST_FAST'], legend='ST_FAST', width=2)
        fplt.plot(data['ST_SLOW'], legend='ST_SLOW', width=2)
        fplt.plot(data['EMA'], legend='EMA')

        fplt.plot(data['BUY_PRISE'], color='b', style='x', width=2)

        long_buy = data.loc[data['SIGNAL'] == 'LONG_BUY', 'BUY_PRISE']
        if not long_buy.empty:
            fplt.plot(long_buy-1, color='#4a5', style='^', legend='buy', width=2)

        fplt.plot(data['SELL_PRISE'], color='b', style='x', width=2)

        long_sell = data.loc[data['SIGNAL'] == 'LONG_SELL', 'SELL_PRISE']
        if not long_sell.empty:
            fplt.plot(long_sell+1, color='r', style='v', legend='sell', width=2)

        long_take_profit = data.loc[data['SIGNAL'] == 'LONG_TAKE_PROFIT', 'SELL_PRISE']
        if not long_take_profit.empty:
            fplt.plot(long_take_profit+1, color='#4a5', style='p', legend='take profit', width=2)

        short_buy = data.loc[data['SIGNAL'] == 'SHORT_BUY', 'BUY_PRISE']
        if not short_buy.empty:
            fplt.plot(short_buy-1, color='#4a6', style='o', legend='short buy', width=2)

        short_sell = data.loc[data['SIGNAL'] == 'SHORT_SELL', 'SELL_PRISE']
        if not short_sell.empty:
            fplt.plot(short_sell+1, color='r', style='o', legend='short sell', width=2)

        short_take_profit = data.loc[data['SIGNAL'] == 'SHORT_TAKE_PROFIT', 'SELL_PRISE']
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

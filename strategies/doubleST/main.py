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

    def calculate(self, data: pd.DataFrame, var_profit: float = None) -> pd.DataFrame:
        if var_profit is None:
            var_profit = self.__var_profit

        stocks = 0  # amount of stocks
        orders = []  # list of orders

        for index, row in data.iterrows():
            # config
            if pd.isnull(row['ST_FAST']) or pd.isnull(row['ST_SLOW']):
                continue
            elif index == len(data) - 1 and stocks > 0:
                orders.append({'order': 'SELL_LIMIT', 'signal': 'LONG_SELL', 'price': row['open']})
            elif 'TAKE_PROFIT' in data.columns and data.loc[index - 1, 'TAKE_PROFIT'] is not None:
                data.loc[index, 'TAKE_PROFIT'] = data.loc[index - 1, 'TAKE_PROFIT']

                # signals
            if stocks == 0:
                price = long_buy(data.loc[index - 1], row)
                if price is not None:
                    orders.clear()
                    orders.append(price)
            elif stocks > 0:
                price = long_sell(row)
                if price is not None:
                    orders.clear()
                    orders.append(price)

                # orders
            if len(orders) > 0:
                for order in orders:
                    if order['order'] == 'BUY_LIMIT':
                        if order['price'] <= row['high'] and order['price'] >= row['low']:
                            stocks += 10
                            data.loc[index, 'SIGNAL'] = order['signal']
                            data.loc[index, 'BUY_PRICE'] = order['price']
                            data.loc[index, 'TAKE_PROFIT'] = round(order['price'] + var_profit, 2)
                            orders.clear()
                    elif order['order'] == 'SELL_LIMIT':
                        if order['price'] <= row['high'] and order['price'] >= row['low']:
                            stocks -= 10
                            data.loc[index, 'SIGNAL'] = order['signal']
                            data.loc[index, 'SELL_PRICE'] = order['price']
                            orders.clear()
                            data.loc[index, 'TAKE_PROFIT'] = None

            if 'TAKE_PROFIT' in data.columns and data.loc[index, 'TAKE_PROFIT'] is not None:
                if data.loc[index, 'TAKE_PROFIT'] <= row['high'] and data.loc[index, 'TAKE_PROFIT'] >= row['low']:
                    stocks -= 10
                    data.loc[index, 'SIGNAL'] = 'TAKE_PROFIT'
                    data.loc[index, 'SELL_PRICE'] = data.loc[index, 'TAKE_PROFIT']
                    data.loc[index, 'TAKE_PROFIT'] = None
        return data

    def report(self, data: pd.DataFrame) -> None:
        # list of deals
        deals = pd.DataFrame()  # create empty DataFrame
        # add columns
        deals[['ticker', 'date', 'SIGNAL', 'BUY_PRICE', 'SELL_PRICE']
              ] = data[['ticker', 'date', 'SIGNAL', 'BUY_PRICE', 'SELL_PRICE']]
        deals = deals[deals['SIGNAL'].notnull()]
        deals = deals.assign(COMMISSION=None, **{'P/L': None}, ACCOUNT=None)  # add columns

        init = 3000  # initial capital
        account = init  # current capital
        commission = 0.00005  # commission
        last_buy_price = 0  # last buy price
        trades = 0  # number of trades

        for index, row in deals.iterrows():
            if not pd.isnull(row['BUY_PRICE']):
                deals.loc[index, 'COMMISSION'] = round(10 * row['BUY_PRICE'] * commission, 2)
                account -= round((10 * row['BUY_PRICE'])+deals.loc[index, 'COMMISSION'], 2)
                deals.loc[index, 'ACCOUNT'] = account
                last_buy_price = row['BUY_PRICE']

            elif not pd.isnull(row['SELL_PRICE']):
                deals.loc[index, 'COMMISSION'] = round(10 * row['SELL_PRICE'] * commission, 2)
                account += round((10 * row['SELL_PRICE'])-deals.loc[index, 'COMMISSION'], 2)
                deals.loc[index, 'ACCOUNT'] = account
                deals.loc[index, 'P/L'] = (row['SELL_PRICE']-last_buy_price) * 10
                last_buy_price = 0
                trades += 1

        deals.to_excel(os.path.join(self.__directory, 'deals.xlsx'), index=False)

        loss = len(deals[deals['P/L'] < 0])  # number of losses
        profit = len(deals[deals['P/L'] > 0])  # number of profits
        win_rate = str(round((profit / (loss + profit)) * 100, 2))+'%'  # win rate
        result = (account - init)/init*100  # result in %

        # report
        report = pd.DataFrame(columns=['trades', 'loss', 'profit', 'win_rate', 'account_start', 'account_end', 'result'])
        report.loc[len(report)] = [trades, loss, profit, win_rate, init, round(account, 2), str(round(result, 2))+'%']
        print(report)

    def show(self, data: pd.DataFrame) -> None:
        self.report(data)

        # candlestick
        data.set_index('date', inplace=True)
        data.index = pd.to_datetime(data.index).tz_localize('Etc/GMT-5')

        fplt.candlestick_ochl(data[['open', 'close', 'high', 'low']])
        fplt.plot(data['ST_FAST'], legend='ST_FAST', width=2)
        fplt.plot(data['ST_SLOW'], legend='ST_SLOW', width=2)
        fplt.plot(data['EMA'], legend='EMA')
        fplt.plot(data['TAKE_PROFIT'], legend='TAKE_PROFIT', width=1, color='g')

        fplt.plot(data['BUY_PRICE'], color='b', style='x', width=2)

        long_buy = data.loc[data['SIGNAL'] == 'LONG_BUY', 'BUY_PRICE']
        if not long_buy.empty:
            fplt.plot(long_buy-1, color='#4a5', style='^', legend='buy', width=2)

        fplt.plot(data['SELL_PRICE'], color='b', style='x', width=2)

        long_sell = data.loc[data['SIGNAL'] == 'LONG_SELL', 'SELL_PRICE']
        if not long_sell.empty:
            fplt.plot(long_sell+1, color='#4a6', style='o', legend='sell', width=2)

        long_take_profit = data.loc[data['SIGNAL'] == 'LONG_TAKE_PROFIT', 'SELL_PRICE']
        if not long_take_profit.empty:
            fplt.plot(long_take_profit+1, color='#4a5', style='p', legend='take profit', width=2)

        short_buy = data.loc[data['SIGNAL'] == 'SHORT_BUY', 'BUY_PRICE']
        if not short_buy.empty:
            fplt.plot(short_buy-1, color='r', style='^', legend='short buy', width=2)

        short_sell = data.loc[data['SIGNAL'] == 'SHORT_SELL', 'SELL_PRICE']
        if not short_sell.empty:
            fplt.plot(short_sell+1, color='r', style='o', legend='short sell', width=2)

        short_take_profit = data.loc[data['SIGNAL'] == 'SHORT_TAKE_PROFIT', 'SELL_PRICE']
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

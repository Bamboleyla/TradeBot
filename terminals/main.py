import logging
import os
import pandas as pd
import finplot as fplt
import talib
import json

from indicators.super_trend import super_trend
from strategies.withDoubleTrend import WithDoubleTrend
from services.position import Position
from services.orders import Orders

__all__ = "DoubleST_Strategy"

logger = logging.getLogger(__name__)


class DoubleST:
    def __init__(self, directory: str):
        self.__directory = directory
        self.__indicators_aleases = {
            'fast_up': 'ST 10 3 UP',
            'fast_down': 'ST 10 3 LOW',
            'slow_up': 'ST 20 5 UP',
            'slow_down': 'ST 20 5 LOW'
        }

        with open(os.path.join(self.__directory, 'config.json'), 'r') as f:
            config = json.load(f)
            self.__var_take = config['var_take']
            self.__super_trends = config['indicators']['super_trends']

    def run(self, quotes: pd.DataFrame) -> pd.DataFrame:
        """
        Read data from 'explore.csv' file, calculate SuperTrend indicators if they are not already in the data and return the result.

        If the SuperTrend indicators are already in the data, read the data from the file and return it. Otherwise, calculate the SuperTrend indicators
        and save the result to the 'explore.csv' file.
        """
        with open(os.path.join(self.__directory, 'explore.csv'), 'r') as f:
            data = pd.read_csv(f, header=0)
            max_period = 0
            for indicator in self.__super_trends:
                # check if the SuperTrend indicators not are already in the data
                if f'ST {indicator["period"]} {indicator["multiplier"]} UP' not in data.columns or f'ST {indicator["period"]} {indicator["multiplier"]} LOW' not in data.columns:
                    # calculate the SuperTrend indicators
                    copy = quotes[['ticker', 'date', 'open', 'high', 'low', 'close']].copy()
                    copy['EMA 50'] = talib.EMA(quotes['close'].values, timeperiod=50)
                    copy['EMA 50'] = copy['EMA 50'].round(2)

                    # return the calculated SuperTrend indicators
                    return super_trend(self.__super_trends, copy)

                # Update max_period with the maximum period from the indicators
                max_period = max(max_period, indicator['period'])

            # Calculate 50-period EMA for the closing prices
            quotes['EMA 50'] = talib.EMA(quotes['close'].values, timeperiod=50)
            quotes['EMA 50'] = quotes['EMA 50'].round(2)

            # Extract the data corresponding to the last max_period entries
            empty_data = quotes.iloc[len(data) - max_period:]

            # Get the last max_period data from existing data
            last_data = data.iloc[-max_period:]

            # Calculate new SuperTrend indicators
            new_data = super_trend(self.__super_trends, empty_data, last_data)

            # Remove the 'volume' column from the new data
            new_data = new_data.drop(columns=['volume'])

            # Concatenate the existing data with the newly calculated data, excluding the initial max_period entries
            return pd.concat([data, new_data.iloc[max_period:]], ignore_index=True)

    def calculate(self, data: pd.DataFrame, var_take: float = None) -> pd.DataFrame:
        if var_take is None:
            var_take = self.__var_take

        params = {
            'var_take': var_take,
            'indicators': self.__indicators_aleases
        }

        position = Position()
        orders = Orders(position)
        widthDT = WithDoubleTrend(params, orders, position)

        for index, row in data.iterrows():
            # config
            if index == 0:
                continue
            elif index == len(data) - 1 and position.get_size(widthDT.name) > 0:
                orders.create({'id': index, 'strategy': widthDT.name, 'signal': 'LONG_SELL', 'order': 'SELL_LIMIT',  'price': row['open']})

            widthDT.run(previous=data.loc[index - 1], current=row)

            orders.run(row, index)

        order_list = orders.get_order_list()

        return data.join(order_list)

    def report(self, data: pd.DataFrame, mode: str = 'default', var_take: float = None) -> pd.DataFrame:
        if var_take is None:
            var_take = self.__var_take
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
        if mode == 'default':
            deals.to_excel(os.path.join(self.__directory, 'deals.xlsx'), index=False)

        loss = len(deals[deals['P/L'] < 0])  # number of losses
        profit = len(deals[deals['P/L'] > 0])  # number of profits
        win_rate = str(round((profit / (loss + profit)) * 100, 2))+'%'  # win rate
        result = (account - init)/init*100  # result in %

        # report
        report = pd.DataFrame(columns=['var_take', 'trades', 'loss', 'profit', 'win_rate', 'account_start', 'account_end', 'result'])
        report.loc[len(report)] = [var_take, trades, loss, profit, win_rate, init, round(account, 2), str(round(result, 2))+'%']
        print(report)

        return report

    def show(self, data: pd.DataFrame) -> None:
        if 'SIGNAL' in data.columns:
            self.report(data)  # create report
        # candlestick
        data.set_index('date', inplace=True)
        data.index = pd.to_datetime(data.index).tz_localize('Etc/GMT-5')

        fplt.candlestick_ochl(data[['open', 'close', 'high', 'low']])
        fplt.plot(data[self.__indicators_aleases['fast_up']], legend='ST_FAST_UP', color='#FF0000', width=2)
        fplt.plot(data[self.__indicators_aleases['fast_down']], legend='ST_FAST_LOW', color='#228B22', width=2)
        fplt.plot(data[self.__indicators_aleases['slow_up']], legend='ST_SLOW_UP', color='#B22222', width=3)
        fplt.plot(data[self.__indicators_aleases['slow_down']], legend='ST_SLOW_LOW', color='#006400', width=3)
        fplt.plot(data['EMA 50'], legend='EMA 50')

        if 'TAKE_PROFIT' in data.columns:
            fplt.plot(data['TAKE_PROFIT'], legend='TAKE_PROFIT', width=1, color='g')
        if 'BUY_PRICE' in data.columns:
            fplt.plot(data['BUY_PRICE'], color='b', style='x', width=2)
        if 'SELL_PRICE' in data.columns:
            fplt.plot(data['SELL_PRICE'], color='b', style='x', width=2)

        if 'SIGNAL' in data.columns:
            long_buy = data.loc[data['SIGNAL'] == 'LONG_BUY', 'BUY_PRICE']
            if not long_buy.empty:
                fplt.plot(long_buy-1, color='#4a5', style='^', legend='buy', width=2)

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

    def optimize(self, data: pd.DataFrame, var_take: dict) -> None:

        start = var_take['start']
        results = pd.DataFrame()

        while start <= var_take['end']:
            data_copy = data.copy()
            result = self.calculate(data_copy, start)
            report = self.report(result, 'optimization', start)
            results = pd.concat([results, report])

            start += var_take['step']

        results.to_excel(os.path.join(self.__directory, 'optimization.xlsx'), index=False)

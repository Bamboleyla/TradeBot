import pandas as pd

from datetime import datetime
from services.orders import Orders


class WithDoubleTrend():
    def __init__(self, params: dict, orders: Orders):
        self.__var_take = params['var_take']
        self.__fast_up = params['indicators']['fast_up']
        self.__fast_down = params['indicators']['fast_down']
        self.__slow_up = params['indicators']['slow_up']
        self.__slow_down = params['indicators']['slow_down']
        self.__orders = orders

    def run(self, position: int, previous: pd.DataFrame, current: pd.DataFrame):
        if position == 0:
            return self.__long_open(previous, current)

        elif position > 0:
            return self.__long_close(current)

    def __long_open(self, previous: pd.DataFrame, current: pd.DataFrame) -> dict:
        if pd.notna(previous[self.__fast_up]) and pd.notna(previous[self.__slow_down]) and pd.notna(current[self.__fast_down]) and pd.notna(current[self.__slow_down]):
            if previous['close'] <= previous[self.__fast_up] and previous['close'] > previous[self.__slow_down]:
                if current['open'] > current[self.__fast_down] and current['open'] > current[self.__slow_down]:
                    price = previous[self.__fast_up]
                    self.__orders.create({'id': datetime.now().timestamp(), 'signal': 'LONG_BUY',
                                          'order': 'BUY_LIMIT', 'price': price, 'take_profit': price + self.__var_take})

    def __long_close(self, row: pd.DataFrame) -> dict:
        if pd.notna(row[self.__fast_down]):
            if row['close'] < row[self.__fast_down] or row['open'] < row[self.__fast_down]:
                self.__orders.create({'id': datetime.now().timestamp(), 'signal': 'LONG_SELL', 'order': 'SELL_LIMIT', 'price': row['close']})

    def __short_open(self):
        pass

    def __short_close(self):
        pass

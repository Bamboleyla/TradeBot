import pandas as pd

from strategies.doubleST.signals.orders import Order


class WithDoubleTrend():
    def __init__(self, mode, var_take):
        self.__orders = Order(mode, var_take)

    def run(self, previous: pd.DataFrame, current: pd.DataFrame):
        row = self.__orders.check(current)

        stocks = self.__orders.get_stocks()
        if (stocks == 0):
            self.__long_open(previous, current)
        elif (stocks > 0):
            self.__long_close(current)

        return row

    def __long_open(self, previous: pd.DataFrame, current: pd.DataFrame) -> dict | None:
        if pd.notna(previous['ST_FAST_UP']) and pd.notna(previous['ST_SLOW_LOW']) and pd.notna(current['ST_FAST_LOW']) and pd.notna(current['ST_SLOW_LOW']):
            if previous['close'] <= previous['ST_FAST_UP'] and previous['close'] > previous['ST_SLOW_LOW']:
                if current['open'] > current['ST_FAST_LOW'] and current['open'] > current['ST_SLOW_LOW']:
                    self.__orders.create_buy_limit(previous['ST_FAST_UP'])

    def __long_close(self, row: pd.DataFrame) -> dict | None:
        if pd.notna(row['ST_FAST_LOW']):
            if row['close'] < row['ST_FAST_LOW'] or row['open'] < row['ST_FAST_LOW']:
                self.__orders.create_sell_limit(row['close'])

    def __short_open(self):
        pass

    def __short_close(self):
        pass

    def close(self, row):
        self.__orders.close(row)

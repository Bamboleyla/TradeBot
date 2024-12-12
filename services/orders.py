import pandas as pd

from services.position import Position


class Orders():
    def __init__(self, position: Position):
        self.__orders = []
        self.__order_list = pd.DataFrame()
        self.__position = position
        self.__take_profit = None

    def create(self, order: dict):
        self.__orders.append(order)

    def run(self, row: pd.DataFrame, index: int):
        # orders
        if len(self.__orders) > 0:
            for order in self.__orders:
                if order['order'] == 'BUY_LIMIT':
                    self.__buy_limit(order, row, index)

                elif order['order'] == 'SELL_LIMIT':
                    self.__sell_limit(order, row, index)

            # take-profits
        if self.__take_profit is not None:
            if self.__take_profit <= row['high'] and self.__take_profit >= row['low']:
                self.__position.decrease('WithDoubleTrend', 10)
                self.__order_list.loc[index, 'SIGNAL'] = 'TAKE_PROFIT'
                self.__order_list.loc[index, 'SELL_PRICE'] = self.__take_profit
                self.__take_profit = None
            else:
                self.__order_list.loc[index, 'TAKE_PROFIT'] = self.__take_profit

        if self.__position.get_size() > 0 and pd.to_datetime(row['date']).time() == pd.Timestamp('23:45:00').time():
            self.__position.decrease('WithDoubleTrend', 10)
            self.__order_list.loc[index, 'SIGNAL'] = 'MARKET_STOP'
            self.__order_list.loc[index, 'SELL_PRICE'] = row['open']
            self.__take_profit = None

    def __buy_limit(self, order: dict, row: pd.DataFrame, index: int):
        if order['price'] <= row['high'] and order['price'] >= row['low']:
            self.__position.increase(order['strategy'], 10)
            self.__order_list.loc[index, 'SIGNAL'] = order['signal']
            self.__order_list.loc[index, 'BUY_PRICE'] = order['price']
            if 'take_profit' in order:
                self.__take_profit = order['take_profit']
            self.__orders = list(filter(lambda item: item['id'] != order['id'], self.__orders))

    def __sell_limit(self, order: dict, row: pd.DataFrame, index: int):
        if order['price'] <= row['high'] and order['price'] >= row['low']:
            self.__position.decrease(order['strategy'], 10)
            self.__order_list.loc[index, 'SIGNAL'] = order['signal']
            self.__order_list.loc[index, 'SELL_PRICE'] = order['price']
            self.__orders = list(filter(lambda item: item['id'] != order['id'], self.__orders))
            self.__take_profit = None

    def get_order_list(self) -> pd.DataFrame:
        return self.__order_list

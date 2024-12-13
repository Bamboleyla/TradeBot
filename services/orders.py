import pandas as pd

from services.position import Position
from datetime import datetime


class Orders():
    def __init__(self, position: Position):
        self.__orders = []
        self.__order_list = pd.DataFrame()
        self.__position = position

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

                elif order['order'] == 'TAKE_PROFIT':
                    self.__take_profit(order, row, index)

        if self.__position.get_size() > 0 and pd.to_datetime(row['date']).time() == pd.Timestamp('23:45:00').time():
            self.__position.decrease('WithDoubleTrend', 10)
            self.__order_list.loc[index, 'SIGNAL'] = 'MARKET_STOP'
            self.__order_list.loc[index, 'SELL_PRICE'] = row['open']
            self.__orders.clear()

    def __buy_limit(self, order: dict, row: pd.DataFrame, index: int):
        if order['price'] <= row['high'] and order['price'] >= row['low']:
            self.__position.increase(order['strategy'], 10)
            self.__order_list.loc[index, 'SIGNAL'] = order['signal']
            self.__order_list.loc[index, 'BUY_PRICE'] = order['price']
            self.__orders = list(filter(lambda item: item['id'] != order['id'], self.__orders))

            if 'take_profit' in order:
                self.create({'id': datetime.now().timestamp(), 'strategy': order['strategy'],
                            'signal': 'TAKE_PROFIT', 'order': 'TAKE_PROFIT', 'price': order['take_profit']})

    def __sell_limit(self, order: dict, row: pd.DataFrame, index: int):
        if order['price'] <= row['high'] and order['price'] >= row['low']:
            self.__position.decrease(order['strategy'], 10)
            self.__order_list.loc[index, 'SIGNAL'] = order['signal']
            self.__order_list.loc[index, 'SELL_PRICE'] = order['price']
            self.__orders = list(filter(lambda item: item['id'] != order['id'], self.__orders))

            if self.__position.get_size(order['strategy']) == 0:
                self.__orders = list(filter(lambda item: item['strategy'] != order['strategy'], self.__orders))

    def __take_profit(self, order: dict, row: pd.DataFrame, index: int):
        if order['price'] <= row['high'] and order['price'] >= row['low']:
            self.__position.decrease(order['strategy'], 10)
            self.__order_list.loc[index, 'SIGNAL'] = order['signal']
            self.__order_list.loc[index, 'SELL_PRICE'] = order['price']
            self.__orders = list(filter(lambda item: item['id'] != order['id'], self.__orders))
        else:
            self.__order_list.loc[index, 'TAKE_PROFIT'] = order['price']

    def get_order_list(self) -> pd.DataFrame:
        return self.__order_list

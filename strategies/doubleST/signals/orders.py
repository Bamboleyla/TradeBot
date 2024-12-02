class Order():
    def __init__(self, mode, var_take):
        self.__mode = mode
        self.__stocks = 0
        self.__orders = []
        self.__var_take = var_take
        self.__take_profit = None

    def get_stocks(self) -> int:
        return self.__stocks

    def create_buy_limit(self, price):
        if self.__mode == 'not active':
            self.__orders.append({'type': 'BUY_LIMIT', 'price': price})
        elif self.__mode == 'active':
            pass
        else:
            raise ValueError("error:001 Unknown mode value")

    def create_sell_limit(self, price):
        if self.__mode == 'not active':
            self.__orders.append({'type': 'SELL_LIMIT', 'price': price})
        elif self.__mode == 'active':
            pass
        else:
            raise ValueError("error:002 Unknown mode value")

    def create_buy_market(self):
        self.__orders.append({'type': 'BUY_MARKET'})

    def create_sell_market(self, row):
        if self.__mode == 'not active':
            self.__orders.append({'type': 'MARKET_STOP'})
        elif self.__mode == 'active':
            pass
        else:
            raise ValueError("error:003 Unknown mode value")

    def create_take_profit(self, price):
        self.__orders.append({'type': 'TAKE_PROFIT', 'price': price})

    def create_stop_loss(self, price):
        pass

    def check(self, row):
        updated_orders = []
        if len(self.__orders) > 0:
            for order in self.__orders:
                if order['type'] == 'BUY_LIMIT':
                    if order['price'] <= row['high'] and order['price'] >= row['low']:
                        self.__stocks += 10
                        row['SIGNAL'] = order['type']
                        row['BUY_PRICE'] = order['price']
                        self.__take_profit = round(order['price'] + self.__var_take, 2)
                    else:
                        updated_orders.append(order)
                elif order['type'] == 'SELL_LIMIT':
                    if order['price'] <= row['high'] and order['price'] >= row['low']:
                        self.__stocks -= 10
                        row['SIGNAL'] = order['type']
                        row['SELL_PRICE'] = order['price']
                        self.__take_profit = None
                    else:
                        updated_orders.append(order)
                elif order['type'] == 'MARKET_STOP':
                    self.__stocks -= 10
                    row['SIGNAL'] = order['type']
                    row['SELL_PRICE'] = row['open']
                    self.__take_profit = None
                    self.__orders.clear()

   # take-profits
        if self.__take_profit is not None:
            if self.__take_profit <= row['high'] and self.__take_profit >= row['low']:
                self.__stocks -= 10
                row['SIGNAL'] = 'TAKE_PROFIT'
                row['SELL_PRICE'] = self.__take_profit
                self.__take_profit = None
            else:
                row['TAKE_PROFIT'] = self.__take_profit

        self.__orders = updated_orders
        return row

    def close(self, row):
        self.__orders.clear()
        if self.get_stocks() > 0:
            self.create_sell_market(row)

import asyncio

from api.client import AlorClientService


class AlorAccount:
    def __init__(self):
        self.__client = AlorClientService()
        self.__balance = asyncio.run(self.__client.get_balance())
        self.__positions = asyncio.run(self.__client.get_positions())
        self.__orders = asyncio.run(self.__client.get_orders())

    def run(self):
        print(self.__balance)
        print(self.__positions)
        print(self.__orders)

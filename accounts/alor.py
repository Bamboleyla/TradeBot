import asyncio

from api.client import AlorClientService


class AlorAccount:
    def __init__(self):
        self.__client = AlorClientService()
        self.__balance = asyncio.run(self.__client.get_status())['buyingPower']

    def run(self):
        print(self.__balance)

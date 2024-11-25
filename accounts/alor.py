import asyncio

from api.client import AlorClientService
from configurations.alor import AlorConfiguration
from services.downloader import Downloader


class AlorAccount:
    def __init__(self):
        self.__client = AlorClientService()
        self.__config = AlorConfiguration()
        self.__balance = asyncio.run(self.__client.get_balance())
        self.__positions = asyncio.run(self.__client.get_positions())
        self.__orders = asyncio.run(self.__client.get_orders())

    def run(self):
        loader = Downloader()
        asyncio.run(loader.run())

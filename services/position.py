import pandas as pd


class Position():
    def __init__(self):
        self.__position = {}

    def get_size(self, strategy: str = None) -> int:
        if strategy is None:
            return sum(self.__position.values())
        else:
            return self.__position.get(strategy, 0)

    def increase(self, strategy: str, quantity: int):
        self.__position[strategy] = self.__position.get(strategy, 0) + quantity

    def decrease(self, strategy: str, quantity: int):
        self.__position[strategy] = self.__position.get(strategy, 0) - quantity

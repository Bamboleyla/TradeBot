

class Position():
    def __init__(self):
        self.__position = 0

    def get_size(self):
        return self.__position

    def increase(self, num: int):
        self.__position += num

    def decrease(self, num: int):
        self.__position -= num

from settings import program

__all__ = "ProgramConfiguration"


class ProgramConfiguration:
    def __init__(self) -> None:
        """
        Initialize an instance of ProgramConfiguration.

        This method reads configuration from file "settings.ini" and load
        the following settings into the instance:

        - broker: the name of the broker
        - blog: a boolean flag indicating whether the blog part of the
          program should be enabled or not

        :return: An instance of ProgramConfiguration
        """
        self.__broker: str = program['broker']
        self.__blog: bool = program['blog']

    @property
    def broker(self) -> str:
        return self.__broker

    @property
    def blog(self) -> bool:
        return self.__blog

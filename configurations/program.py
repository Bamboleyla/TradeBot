from configparser import ConfigParser

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
        config = ConfigParser()
        config.read('settings.ini')

        self.__broker = config['PROGRAM']["BROKER"]
        self.__blog: bool = config['PROGRAM']["BLOG"]  # use blog or not

    @property
    def broker(self) -> str:
        return self.__broker

    @property
    def blog(self) -> bool:
        return self.__blog

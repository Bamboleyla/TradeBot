import logging

from settings import alor
from datetime import datetime, date
from typing import Literal

__all__ = "AlorConfiguration"

logger = logging.getLogger(__name__)


class AlorConfiguration:
    def __init__(self) -> None:
        """
        Initialize an instance of AlorConfiguration.

        This method reads configuration from file "settings.ini" and load
        the following settings into the instance:

        - mode: the mode of the broker (dev or prod)
        - token: the JWT token for ALOR
        - ttl_jwt: the time to live for the JWT token
        - url_oauth: the URL for ALOR OAuth
        - open: the time when the broker starts working
        - close: the time when the broker stops working
        - work_days: a list of days when the broker works
        - websocket_url: the URL for the broker's websocket
        - websocket_dev_url: the URL for the broker's dev websocket

        :return: An instance of AlorConfiguration
        """

        self.__mode: Literal['dev', 'prod'] = alor['mode']
        self.__token: str = alor['token']
        self.__ttl_jwt: int = alor['ttl_jwt']
        self.__url_oauth: str = alor['url_oauth']
        self.__open: int = alor['open']
        self.__close: int = alor['close']
        self.__work_days: list = alor['work_days']
        self.__websocket_url: str = alor['websocket_url']
        self.__websocket_dev_url: str = alor['websocket_url_dev']

    @property
    def token(self) -> str:
        return self.__token

    @property
    def ttl_jwt(self) -> int:
        return self.__ttl_jwt

    @property
    def mode(self) -> str:
        return self.__mode

    @property
    def url_oauth(self) -> str:
        return self.__url_oauth

    @property
    def is_work(self) -> bool:
        now_weekday = date.today().weekday()
        if now_weekday in self.__work_days:
            now_hour = datetime.now().hour
            if self.__open <= now_hour < self.__close:
                return True

            else:
                logger.info("ALOR is closed, now is not a work time")
                return False

        else:
            logger.info("ALOR is closed, today is not a workday")
            return False

    @property
    def websocket_url(self) -> str:
        return self.__websocket_url

    @property
    def websocket_dev_url(self) -> str:
        return self.__websocket_dev_url

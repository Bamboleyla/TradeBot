import logging

from settings import alor
from datetime import datetime, date, timedelta
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

        self.mode: Literal['dev', 'prod'] = alor['mode']
        self.token: str = alor['token']
        self.ttl_jwt: int = alor['ttl_jwt']
        self.url_oauth: str = alor['url_oauth']
        self.open: int = alor['open']
        self.close: int = alor['close']
        self.work_days: list = alor['work_days']
        self.websocket_url: str = alor['websocket_url']
        self.websocket_dev_url: str = alor['websocket_url_dev']

    @property
    def is_work(self) -> bool:
        now_weekday = date.today().weekday()
        if now_weekday in self.work_days:
            now_hour = datetime.now().hour
            if self.open <= now_hour < self.close:
                return True

            else:
                logger.info("ALOR is closed, now is not a work time")
                return False

        else:
            logger.info("ALOR is closed, today is not a workday")
            return False

    @property
    def prev_work_day(self) -> date:
        now_weekday = date.today().weekday()
        if now_weekday == 0:
            return date.today() - timedelta(days=3)
        elif now_weekday == 6:
            return date.today() - timedelta(days=2)
        else:
            return date.today() - timedelta(days=1)

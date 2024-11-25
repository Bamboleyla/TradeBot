import logging

from settings import alor
from datetime import datetime, date, timedelta
from typing import Literal

__all__ = "AlorConfiguration"

logger = logging.getLogger(__name__)


class AlorConfiguration:
    def __init__(self) -> None:
        self.contract: str = alor['contract']  # Alor contract
        self.token: str = alor['token']  # Alor token
        self.ttl_jwt: int = alor['ttl_jwt']  # Time to live JWT
        self.url_oauth: str = alor['url_oauth']  # Alor OAuth URL
        self.open: int = alor['open']  # Open time of Alor
        self.close: int = alor['close']  # Close time of Alor
        self.work_days: list = alor['work_days']  # List of work days
        self.websocket_url: str = alor['websocket_url']  # Alor WebSocket URL
        self.https_url: str = alor['https_url']  # Alor HTTPS URL
        self.stock_market: str = alor['stock_market']  # Alor stock market
        self.tickers: list = alor['tickers']  # List of tickers

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

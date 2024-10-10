import logging

from configuration.configuration import ProgramConfiguration
from datetime import datetime, date

__all__ = "MOEXService"

logger = logging.getLogger(__name__)


class MOEXService:
    def __init__(self):
        """
        Initialize an instance of MOEXService.

        This method reads configuration from file "settings.ini" and load
        the following settings into the instance:

        - open: time when MOEX exchange is opened
        - close: time when MOEX exchange is closed
        - work_days: list of weekdays when MOEX exchange is open

        :return: An instance of MOEXService
        """
        config = ProgramConfiguration()  # Load configuration from file "settings.ini" and load

        self.__moex_config = config.get_moex_params

    @property
    def is_moex_open(self) -> bool:
        """
        Check if MOEX exchange is open now.

        The method checks current weekday and time to determine if MOEX exchange
        is open or not. If current weekday is in the list of workdays, the method
        then checks the current time to see if it is between the open and close times.

        :return: True if MOEX is open, False otherwise
        """
        now_weekday = date.today().weekday()
        if now_weekday in self.__moex_config["work_days"]:
            now_hour = datetime.now().hour

            if now_hour >= self.__moex_config["open"] and now_hour < self.__moex_config["close"]:
                logger.info("MOEX is open")
                return True

            else:
                logger.info("MOEX is closed, now is not work time")
                return False

        else:
            logger.info("MOEX is closed, today is not a workday")
            return False

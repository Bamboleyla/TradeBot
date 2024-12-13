import logging
import os
import pandas as pd

from services.file import FileService
from api.client import AlorClientService

__all__ = "Manager"

logger = logging.getLogger(__name__)


class Manager:
    def __init__(self, ticker: str):
        self.__dir = os.path.join(os.path.dirname(os.path.dirname(__file__))+'\\tickers\\', ticker)  # file path to ticker directory

    def get_quotes(self) -> pd.DataFrame:
        quotes = pd.read_csv(self.__dir+'\\data.csv', header=0)
        return quotes

    def get_directory(self) -> str:
        return self.__dir

    def get_doubleST_path(self) -> str:
        return os.path.join(self.__dir, 'dobleST.csv')

    def get_chart(self) -> pd.DataFrame | None:
        if not os.path.exists(self.__dir+'/chart.csv'):  # if file with chart doesn't exist
            return None

        return pd.read_csv(self.__dir+'/chart.csv', header=0)

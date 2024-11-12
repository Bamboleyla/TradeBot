import logging
import os
import pandas as pd

from services.file import FileService
from api.services.client import AlorClientService

__all__ = "IMOEX_Manager"

logger = logging.getLogger(__name__)


class IMOEX_Manager:
    def __init__(self):
        self.__data_path = os.path.join(self.__directory, 'data.csv')

    def get_quotes(self) -> pd.DataFrame:
        quotes = pd.read_csv(self.__data_path, header=0)

        return quotes

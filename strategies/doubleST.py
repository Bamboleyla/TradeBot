import logging
import os

__all__ = "DoubleST_Strategy"

logger = logging.getLogger(__name__)


class DoubleST:
    def __init__(self, directory: str):
        self.__export_path = os.path.join(directory, 'doubleST_data.csv')

        if not os.path.exists(self.__export_path):
            with open(self.__export_path, 'w') as f:
                f.write('TICKER,DATE,TIME,ST3,ST5,EMA,BUY,SELL\n')

    def buy(self) -> bool:
        pass

    def sell(self) -> bool:
        pass

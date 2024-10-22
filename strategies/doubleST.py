import logging
import os
import pandas as pd

from indicators.ema import EMA
from indicators.super_trend import super_trend

__all__ = "DoubleST_Strategy"

logger = logging.getLogger(__name__)


class DoubleST:
    def __init__(self, directory: str, quotes: pd.DataFrame):
        self.__export_path = os.path.join(directory, 'doubleST_data.csv')

        if not os.path.exists(self.__export_path):
            with open(self.__export_path, 'w') as f:
                f.write('ticker,date,ST3,ST5,EMA,BUY,SELL\n')
            quotes[['ticker', 'date']].to_csv(self.__export_path, mode='a', header=False, index=False)

        date = pd.read_csv(self.__export_path, header=0)

        date = EMA(5, quotes, date)
        date = super_trend(10, 3, quotes, date, 'ST3')
        date = super_trend(20, 5, quotes, date, 'ST5')

        date.to_csv(self.__export_path, index=False)  # write date to file

    def buy(self) -> bool:
        pass

    def sell(self) -> bool:
        pass

import logging
import json
import pandas as pd

from datetime import datetime, timezone, timedelta

__all__ = "FileService"

logger = logging.getLogger(__name__)


class FileService:

    def create_data_file(self, path: str) -> None:
        """
        Create a new file with the given path and write the header line to it.

        The header line is a string that contains the column names for the data that will be written to the file.
        The column names are the following:

        - ticker: the ticker symbol for the data
        - date: the date of the data in the format 'YYYYMMDD HH:MM:SS'
        - open: the opening price of the data
        - high: the highest price of the data
        - low: the lowest price of the data
        - close: the closing price of the data
        - vol: the volume of the data

        :param path: The path to the file to be created
        :return: None
        """
        with open(path, 'w') as f:  # write first line
            f.write('ticker,date,open,high,low,close,volume\n')

    def get_last_date(self, df: pd.DataFrame) -> datetime:
        """
        Retrieve the last date from a DataFrame or return the start of the current month.

        This method checks if the provided DataFrame is empty. If it is, it returns
        the first minute of the first day of the current month in the timezone UTC+3.
        If the DataFrame is not empty, it retrieves the date from the last row of the
        'date' column, converts it to a datetime object, and returns it with the timezone
        set to UTC+3.

        :param df: A pandas DataFrame containing a 'date' column with dates in the format 'YYYYMMDD HH:MM:SS'.
        :return: A datetime object representing the last date with timezone set to UTC+3.
        """
        if df.empty:
            now = datetime.now(timezone.utc)  # Get current date and time
            now = now - timedelta(days=31) # Subtract 1 month ago
            return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone(timedelta(hours=3)))  # Get first day of current month
        else:
            # Return value from the last row of column 'date' in datetime format
            return datetime.strptime(df.iloc[-1]["date"], "%Y%m%d %H:%M:%S").replace(tzinfo=timezone(timedelta(hours=3)))

    def update_file(self, ticker: str, df: pd.DataFrame, data: list[str]) -> None:
        """
        Update a DataFrame with the given by appending new data to it.

        This method takes a ticker symbol, a DataFrame, and a list of strings, where
        each string is a JSON object containing the following keys:

        - time: a timestamp in seconds
        - open: the opening price
        - high: the highest price
        - low: the lowest price
        - close: the closing price
        - volume: the volume

        The method converts each timestamp to a datetime object in the timezone
        UTC+3, and then adds data to the DataFrame in the format 'ticker,date,open,high,low,close,volume\n'.

        :param ticker: The ticker symbol for the data
        :param df: A pandas DataFrame containing a 'date' column with dates in the format 'YYYYMMDD HH:MM:SS'.
        :param data: A list of strings, where each string is a JSON object containing the keys 'time', 'open', 'high', 'low', 'close', and 'volume'.
        :return: None
        """
        for item in data:  # for each item in data
            json_item = json.loads(item)['data']  # convert item to json
            date = datetime.fromtimestamp(json_item['time'], timezone.utc).astimezone(
                timezone(offset=timedelta(hours=3))).strftime('%Y%m%d %H:%M:%S')  # convert timestamp to datetime, then to local time (UTC+3)

            df.loc[len(df)] = [ticker, date, json_item["open"],
                               json_item["high"], json_item["low"],
                               json_item["close"], json_item["volume"]]  # add row to df

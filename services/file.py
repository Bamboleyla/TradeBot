import logging
import json

from datetime import datetime, timezone, timedelta

__all__ = "FileService"

logger = logging.getLogger(__name__)


class FileService:

    def create_data_file(self, path: str) -> None:
        """
        Create a new file with the given path and write the header line to it.

        The header line is a string that contains the column names for the data that will be written to the file.
        The column names are the following:

        - TICKER: the ticker symbol for the data
        - DATE: the date of the data in the format 'YYYYMMDD'
        - TIME: the time of the data in the format 'HHMMSS'
        - OPEN: the opening price of the data
        - HIGH: the highest price of the data
        - LOW: the lowest price of the data
        - CLOSE: the closing price of the data
        - VOL: the volume of the data

        :param path: The path to the file to be created
        :return: None
        """
        with open(path, 'w') as f:  # write first line
            f.write('<TICKER>,<DATE>,<TIME>,<OPEN>,<HIGH>,<LOW>,<CLOSE>,<VOL>\n')

    def last_line_date(self, file_path: str) -> str:
        """
        Get the last date from the given file.

        This method reads the file and returns the last date in the format 'YYYYMMDD HHMMSS'.
        If the last line is the header, it returns the first day of the current month.

        :param file_path: The path to the file to be read
        :return: The last date in the file as a string in the format 'YYYYMMDD HHMMSS'
        """
        with open(file_path, 'r') as f:  # read file
            lines = f.readlines()  # read all lines
            last_line = lines[-1].strip()  # get last line
            last_line_list = last_line.split(',')  # split last line

            if last_line_list[1] == '<DATE>' and last_line_list[2] == '<TIME>':  # if last line is header
                now = datetime.now()  # get current date and time
                first_day = now.replace(day=1, hour=0, minute=0, second=1, microsecond=0)  # get first day of current month
                return first_day.strftime('%Y%m%d %H%M%S')  # return formatted date

            return f'{last_line_list[1]} {last_line_list[2]}'  # return formatted date

    def update_file(self, ticker: str, data: list[str], file_path: str) -> None:
        """
        Update the given file with new data.

        This method writes the given data to the file with the given path. It assumes that the data is a list of strings,
        where each string is a JSON object with the following keys:

        - time: the timestamp of the data in seconds
        - open: the opening price of the data
        - high: the highest price of the data
        - low: the lowest price of the data
        - close: the closing price of the data
        - volume: the volume of the data

        The method converts the timestamp to a datetime object, then to a string in the format 'YYYYMMDD HHMMSS',
        and writes it to the file along with the other data.

        :param ticker: The ticker symbol for the data
        :param data: The data to be written to the file
        :param file_path: The path to the file to be written
        :return: None
        """
        with open(file_path, 'a') as f:  # write new data to file
            for item in data:  # for each item in data
                json_item = json.loads(item)['data']  # convert item to json
                date = datetime.fromtimestamp(json_item['time'], timezone.utc).astimezone(
                    timezone(offset=timedelta(hours=3)))  # convert timestamp to datetime, then to local time (UTC+3)

                str_date = date.strftime('%Y%m%d')  # convert date to string
                str_time = date.strftime('%H%M%S')  # convert time to string

                result = f'{ticker},{str_date},{str_time},{json_item["open"]},{
                    json_item["high"]},{json_item["low"]},{json_item["close"]},{json_item["volume"]}'  # create result string

                f.write(result + '\n')  # write result to file

        logger.info("Data for %s was updated", ticker)

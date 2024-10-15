import logging
import os
import json

from datetime import datetime, timezone, timedelta

__all__ = "FileService"

logger = logging.getLogger(__name__)


class FileService:
    def create_file(self, directory: str) -> None:
        """
        Create a new file with the given name in the given directory.

        The file is created with one line: "<TICKER>,<DATE>,<TIME>,<OPEN>,<HIGH>,<LOW>,<CLOSE>,<VOL>"

        :param directory: The directory where the file should be created
        :type directory: str
        """
        file_path = os.path.join(directory, 'date.txt')  # create file with name "date.txt"
        with open(file_path, 'w') as f:  # write first line
            f.write('<TICKER>,<DATE>,<TIME>,<OPEN>,<HIGH>,<LOW>,<CLOSE>,<VOL>\n')

    def last_line_date(self, directory: str) -> str:
        """
        Get the last date from the file.

        This method reads the file and returns the last date in the format "<DATE> <TIME>".
        If the last line is the header, it returns the first day of the current month.

        :param directory: The directory where the file is located
        :type directory: str
        :return: The last date in the format "<DATE> <TIME>"
        :rtype: str
        """
        file_path = os.path.join(directory, 'date.txt')  # get file with name "date.txt"
        with open(file_path, 'r') as f:  # read file
            lines = f.readlines()  # read all lines
            last_line = lines[-1].strip()  # get last line
            last_line_list = last_line.split(',')  # split last line

            if last_line_list[1] == '<DATE>' and last_line_list[2] == '<TIME>':  # if last line is header
                now = datetime.now()  # get current date and time
                first_day = now.replace(day=1, hour=0, minute=0, second=1, microsecond=0)  # get first day of current month
                return first_day.strftime('%Y%m%d %H%M%S')  # return formatted date

            return f'{last_line_list[1]} {last_line_list[2]}'  # return formatted date

    def update_file(self, ticker: str, directory: str, data: list[str]) -> None:
        """
        Update the file with the given data.

        This method appends the given data to the file. The data is expected to be a list of strings, where each string
        is a JSON object containing the following keys:

        - time: a float representing the timestamp of the data
        - open: a float representing the opening price of the data
        - high: a float representing the highest price of the data
        - low: a float representing the lowest price of the data
        - close: a float representing the closing price of the data
        - volume: an int representing the volume of the data

        The method converts the timestamp to the local time (UTC+3) and formats it as "<DATE> <TIME>"

        :param ticker: The ticker of the data
        :type ticker: str
        :param directory: The directory where the file is located
        :type directory: str
        :param data: The data to be written to the file
        :type data: list
        :return: None
        :rtype: None
        """
        with open(os.path.join(directory, 'date.txt'), 'a') as f:  # write new data to file
            for item in data:  # for each item in data
                json_item = json.loads(item)['data']  # convert item to json
                date = datetime.fromtimestamp(json_item['time'], timezone.utc).astimezone(
                    timezone(offset=timedelta(hours=3)))  # convert timestamp to datetime, then to local time (UTC+3)

                str_date = date.strftime('%Y%m%d')  # convert date to string
                str_time = date.strftime('%H%M%S')  # convert time to string

                result = f'{ticker},{str_date},{str_time},{json_item["open"]},{
                    json_item["high"]},{json_item["low"]},{json_item["close"]},{json_item["volume"]}'  # create result string

                f.write(result + '\n')  # write result to file

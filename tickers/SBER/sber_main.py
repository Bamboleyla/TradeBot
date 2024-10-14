import logging
import os
import json


from datetime import datetime, timezone
from services.history import HistoryService
from services.file import FileService
from api.services.client import AlorClientService
from configurations.alor import AlorConfiguration

__all__ = "SBER_Manager"

logger = logging.getLogger(__name__)


class SBER_Manager:
    def __init__(self):
        self.ticker = 'SBER'

    async def __prepare(self):
        directory = os.path.dirname(__file__)

        hs = HistoryService()
        is_there_date_file = hs.check_date_file(directory)  # is there date file in directory?

        client = AlorClientService()
        config = AlorConfiguration()

        if not is_there_date_file:
            fs = FileService()
            fs.create_file(directory)  # create date file in directory

        prev_date = config.prev_work_day
        data = await client.ws_history_date(self.ticker, str(prev_date))
        with open(os.path.join(directory, 'date.txt'), 'a') as f:
            for item in data:
                json_item = json.loads(item)['data']
                date = datetime.fromtimestamp(json_item['time'], timezone.utc)

                str_date = date.strftime('%Y%m%d')
                str_time = date.strftime('%H%M%S')

                result = f'{self.ticker},{str_date},{str_time},{json_item["open"]},{
                    json_item["high"]},{json_item["low"]},{json_item["close"]},{json_item["volume"]}'

                f.write(result + '\n')
        print(data)

    async def run(self):
        logger.info("Start %s manager", self.ticker)
        await self.__prepare()
        logger.info(" %s manager prepared", self.ticker)

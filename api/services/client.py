import logging
import uuid
import websockets
import json
import asyncio
import requests

from typing import Literal
from datetime import datetime, timezone, timedelta
from configurations.alor import AlorConfiguration
from api.services.token import AlorTokenService


__all__ = "AlorClientService"

logger = logging.getLogger(__name__)

TickerType = Literal['SBER', 'GASP', 'ALRS']


class AlorClientService:

    def __init__(self):
        """
        Initialize an instance of AlorClientService.

        This method reads configuration from file "settings.ini" and load
        the following settings into the instance:

        - access_token: access token for ALOR
        - guid: a unique identifier for the client
        - ws_url: URL for ALOR WebSocket

        :return: An instance of AlorClientService
        """
        config = AlorConfiguration()  # Load ALOR broker configuration
        token = AlorTokenService()  # Load token service

        self.access_token = token.get_access_token()['access_token']
        self.guid = uuid.uuid4().hex
        self.ws_url = config.websocket_url
        self.is_work = config.is_work

    async def create_subscription_for_order_book(self, ticker: TickerType) -> None:
        if self.access_token is None:
            logger.error("No access token")
            return
        elif not self.is_work:
            logger.error("ALOR broker is not working")
            return

        else:
            try:
                async with websockets.connect(self.ws_url) as websocket:
                    message = {
                        "opcode": "OrderBookGetAndSubscribe",
                        "code": ticker,
                        "depth": 10,
                        "exchange": "MOEX",
                        "format": "Simple",
                        "frequency": 0,
                        "guid": self.guid,
                        "token": self.access_token
                    }
                    await websocket.send(json.dumps(message))
                    print("Subscription sent. Waiting for response...")
                    response = await websocket.recv()
                    print("Response received:", response)

                    while True:
                        await asyncio.sleep(5)
                        await websocket.send(b'\x89')  # отправка пинг-фрейма
                        try:
                            response = await asyncio.wait_for(websocket.recv(), timeout=10)
                            if response == b'\x8a':  # pong-фрейм
                                logger.info('Pong received')
                            else:
                                logger.info('Received unexpected response: %s', json.dumps(response))
                        except asyncio.TimeoutError:
                            logger.warning('Timeout waiting for response')
                        except websockets.ConnectionClosed:
                            logger.error('WebSocket connection closed')
                            break

            except Exception as e:
                logger.error('Error connecting to websocket: %s', e)

    async def ws_history_date(self, ticker: TickerType, start_date: str) -> None:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        start_date = start_date.replace(tzinfo=timezone.utc)
        start_date += timedelta(hours=10)
        start_date = int(start_date.timestamp())
        responses = []
        async with websockets.connect(self.ws_url) as websocket:
            message = {
                "opcode": "BarsGetAndSubscribe",
                "code": ticker,
                "tf": "300",
                "from": start_date,
                "delayed": False,
                "skipHistory": False,
                "exchange": "MOEX",
                "format": "Simple",
                "frequency": 100,
                "guid": "c328fcf1-e495-408a-a0ed-e20f95d6b813",
                "token": self.access_token
            }
            await websocket.send(json.dumps(message))
            while True:
                try:
                    response = await websocket.recv()
                    response_dict = json.loads(response)
                    if 'httpCode' in response_dict:
                        if response_dict['httpCode'] == 200:
                            if not websocket.closed:
                                await websocket.close()
                    responses.append(response)
                except websockets.ConnectionClosed:
                    break

        return responses

    def transform_date_to_utc(self, date: str) -> int:

        date_object = datetime.strptime(date, "%d.%m.%y %H:%M:%S")

        utc_date = date_object.astimezone(timezone.utc)

        print(utc_date.timestamp())
        return int(utc_date.timestamp())

    async def history_date(self, ticker: TickerType, start_date="11.10.24 21:45:00", end_date="11.10.24 23:45:00") -> None:

        url = "https://apidev.alor.ru/md/v2/history"

        payload = {'symbol': ticker,
                   'exchange': 'MOEX',
                   'tf': 300,
                   'from': self.transform_date_to_utc(start_date),
                   'to': self.transform_date_to_utc(end_date),
                   }
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }

        response = requests.request("GET", url, headers=headers, params=payload)

        print(response.text)

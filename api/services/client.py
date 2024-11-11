import logging
import uuid
import websockets
import json
import asyncio
import requests

from typing import Literal, List
from datetime import datetime, timedelta
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
                        "guid": uuid.uuid4().hex,
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

    async def ws_history_date(self, ticker: TickerType, start_date: datetime) -> List:

        start_date += timedelta(minutes=5)  # add 5 minutes to the start date, because we need data from the past 5 minutes

        responses = []  # list to store responses

        try:
            async with websockets.connect(self.ws_url) as websocket:  # connect to websocket
                message = {
                    "opcode": "BarsGetAndSubscribe",
                    "code": ticker,
                    "tf": "300",
                    "from": start_date.timestamp(),
                    "delayed": False,
                    "skipHistory": False,
                    "exchange": "MOEX",
                    "format": "Simple",
                    "frequency": 100,
                    "guid": uuid.uuid4().hex,
                    "token": self.access_token
                }
                await websocket.send(json.dumps(message))  # send message
                # receive response
                while True:
                    try:
                        response = await websocket.recv()  # receive response
                        response_dict = json.loads(response)  # convert response to dictionary

                        if 'httpCode' in response_dict:  # check if response contains 'httpCode'
                            return responses  # return responses because httpCode is last field in response

                        responses.append(response)  # append response to list
                    except websockets.ConnectionClosed:
                        break

        except Exception as e:
            logger.error(f'Error connecting to websocket with {ticker}: {e}')

        return responses

    async def get_status(self) -> str:
        try:            
            async with websockets.connect(self.ws_url) as websocket:  # connect to websocket
                message = {
                    "opcode": "SummariesGetAndSubscribeV2",
                    "portfolio": "D90320",
                    "skipHistory": False,
                    "exchange": "MOEX",
                    "format": "Simple",
                    "frequency": 100,
                    "guid": uuid.uuid4().hex,
                    "token": self.access_token
                }
                await websocket.send(json.dumps(message))  # send message
                # receive response
                while True:
                    try:
                        response = await websocket.recv()  # receive response
                        data = json.loads(response)['data']  # convert response to dictionary
                        print(data)  # print data
                        return data
                    except websockets.ConnectionClosed:
                        break

        except Exception as e:
                logger.error('Error connecting to websocket: %s', e)

        

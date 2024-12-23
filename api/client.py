import logging
import uuid
import websockets
import json
import requests

from typing import Literal, List
from datetime import datetime, timedelta
from configurations.alor import AlorConfiguration
from api.token import AlorTokenService

__all__ = "AlorClientService"

logger = logging.getLogger(__name__)

TickerType = Literal['SBER', 'GASP', 'ALRS']


class AlorClientService:

    def __init__(self):
        config = AlorConfiguration()  # Load ALOR broker configuration
        token = AlorTokenService()  # Load token service

        self.access_token = token.get_access_token()['access_token']  # Get access token
        self.ws_url = config.websocket_url  # Get websocket url
        self.__url = config.https_url+'/md/v2/Clients/'+config.stock_market+'/'+config.contract  # Get https url
        self.__headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + self.access_token}

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

    async def get_balance(self) -> dict:
        """
        Get current balance from ALOR.

        The method makes a GET request to the ALOR service with the JWT token as a parameter.
        If the response is 200, it extracts the balance from the JSON response and returns it.
        If the response is not 200, it logs an error. If there is an error while decoding
        the JSON response, it logs an error.

        :return: A dictionary containing the balance, or None if an error occurred
        """
        try:

            response = requests.request("GET", self.__url+'/summary', headers=self.__headers, data={})
            return response.json()

        except Exception as e:
            logger.error('Error getting balance: %s', e)

    async def get_positions(self) -> list:
        """
        Retrieve the current positions from ALOR.

        This method makes a GET request to the ALOR service with the JWT token as a parameter
        to retrieve the current positions. If the response is successful, it returns the positions
        as a list. If an error occurs during the request or processing the response, it logs an error.

        :return: A list containing the current positions, or an empty list if an error occurred.
        """
        try:

            response = requests.request("GET", self.__url+'/positions', headers=self.__headers, data={})
            return response.json()

        except Exception as e:
            logger.error('Error getting positions: %s', e)

    async def get_orders(self) -> list:
        """
        Retrieve the current orders from ALOR.

        This method makes a GET request to the ALOR service with the JWT token as a parameter
        to retrieve the current orders. If the response is a string, it returns an empty list.
        Otherwise, it returns the orders as a list. If an error occurs during the request or
        processing the response, it logs an error.

        :return: A list containing the current orders, or an empty list if a string response or an error occurred.
        """
        try:

            response = requests.request("GET", self.__url+'/orders', headers=self.__headers, data={})
            return response.json()

        except Exception as e:
            logger.error('Error getting orders: %s', e)

import logging
import uuid
import websockets
import json

from configuration.configuration import ProgramConfiguration
from api.services.token import AlorTokenService

__all__ = "AlorClientService"

logger = logging.getLogger(__name__)


class AlorClientService:

    def __init__(self):
        """
        Initialize an instance of AlorClientService.

        This method reads configuration from file "settings.ini" and load
        the following settings into the instance:

        - access_token: aceess token for ALOR
        - guid: a unique identifier for the client
        - ws_url: URL for ALOR WebSocket

        :return: An instance of AlorClientService
        """
        config = ProgramConfiguration()  # Load configuration from file "settings.ini"
        token = AlorTokenService()  # Load token service

        self.access_token = token.get_access_token()['access_token']
        self.guid = uuid.uuid4().hex
        self.ws_url = config.websocket_url

    async def create_subscription_for_order_book(self):
        if self.access_token is None:
            logger.error("No access token")
            return
        else:
            async with websockets.connect(self.ws_url) as websocket:
                subscription_message = {
                    "opcode": "OrderBookGetAndSubscribe",
                    "code": "SBER",
                    "depth": 10,
                    "exchange": "MOEX",
                    "format": "Simple",
                    "frequency": 0,
                    "guid": self.guid,
                    "token": self.access_token
                }
            await websocket.send(json.dumps(subscription_message))
            print("Subscription sent. Waiting for response...")
            response = await websocket.recv()
            print("Response received:", response)

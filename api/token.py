import logging
import requests

from json import JSONDecodeError
from datetime import datetime
from typing import Union
from configurations.alor import AlorConfiguration

__all__ = "AlorTokenService"

logger = logging.getLogger(__name__)


class AlorTokenService:

    def __init__(self):
        """
        Initialize an instance of AlorTokenService.

        This method reads configuration from file "settings.ini" and load
        the following settings into the instance:

        - url_oauth: URL for ALOR OAuth service
        - token: refresh token for ALOR
        """
        config = AlorConfiguration()  # Load configuration

        self.url_oauth = config.url_oauth
        self.token = config.token

    def get_access_token(self) -> dict[str, Union[str, None]]:
        """
        Get a JWT token from ALOR by using refresh token.

        The method makes a POST request to the ALOR service with the refresh
        token as a parameter. If the response is 200, it extracts the JWT token
        from the JSON response and returns it. If the response is not 200, it logs
        an error. If there is an error while decoding
        the JSON response, it logs an error.

        :return: A JWT token as a string, or None if an error occurred
        """
        payload = {"token": self.token}
        response = requests.post(url=f"{self.url_oauth}/refresh", params=payload)

        try:
            if response.status_code == 200:
                res_json = response.json()
                access_token: str = res_json.get("AccessToken")
                logger.info(f"JWT received: {access_token}")
                return {"access_token": access_token, "created_at": int(datetime.now().timestamp())}

            else:
                logger.error(f"JWT return Error: {response.status_code}")
                return None

        except JSONDecodeError as e:  # JSONDecodeError is raised if the response is not in JSON format
            logger.error(f"JWT decoding error: {e}")
            return None

import logging
import requests

from json import JSONDecodeError
from datetime import datetime, date
from configuration.configuration import ProgramConfiguration

__all__ = "AlorTokenService"

logger = logging.getLogger(__name__)


class AlorTokenService:

    def __init__(self):
        """
        Initialize an instance of AlorTokenService.

        This method reads configuration from file "settings.ini" and load
        the following settings into the instance:

        - ttl_jwt_token: Time to live for JWT token in seconds
        - refresh_token: None - because first we need to get it from ALOR
        - url_oauth: URL for ALOR for getting JWT token

        :return: An instance of AlorTokenService
        """

        config = ProgramConfiguration("settings.ini")  # Load configuration

        self._ttl_jwt_token = config.ttl_jwt_token  # time to live for JWT token in seconds
        self.refresh_token = None  # because first we need to get it from ALOR
        self.url_oauth = config.url_oauth  # URL for ALOR for getting JWT token

    def _get_jwt_token(self):
        """
        Get a JWT token from ALOR by using refresh token.

        The method makes a POST request to the ALOR service with the refresh
        token as a parameter. If the response is 200, it extracts the JWT token
        from the JSON response and returns it. If the response is not 200, it logs
        an error. If there is an error while decoding
        the JSON response, it logs an error.

        :return: A JWT token as a string, or None if an error occurred
        """
        payload = {"token": self.refresh_token}
        response = requests.post(url=f"{self.url_oauth}/refresh", params=payload)

        try:
            if response.status_code == 200:
                res_json = response.json()
                jwt = res_json.get("AccessToken")
                self.token_ttl = int(datetime.timestamp(datetime.now()))  # time to live for JWT token in seconds
                logger.info(f"JWT токен получен успешно: {jwt}")
                return jwt
            else:
                logger.error(f"Ошибка получения JWT токена: {response.status_code}")
                return None

        except JSONDecodeError as e:  # JSONDecodeError is raised if the response is not in JSON format

            logger.error(f"Ошибка декодирования JWT токена: {e}")
            return None


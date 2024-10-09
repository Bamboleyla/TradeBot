from configparser import ConfigParser

__all__ = "ProgramConfiguration"


class ProgramConfiguration:
    def __init__(self, file_name: str) -> None:
        # classic ini file
        config = ConfigParser()
        config.read(file_name)

        self.__token = config["ALOR_API"]["TOKEN"]
        self.__ttl_jwt_token = config["ALOR_API"]["TTL_JWT_TOKEN"]
        self.__mode = config["ALOR_API"]["MODE"]
        self.__url_oauth = config["ALOR_API"]["URL_OAUTH"]

    @property
    def token(self) -> str:
        return self.__token

    @property
    def ttl_jwt_token(self) -> str:
        return self.__ttl_jwt_token

    @property
    def mode(self) -> str:
        return self.__mode

    @property
    def url_oauth(self) -> str:
        return self.__url_oauth

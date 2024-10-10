from configparser import ConfigParser

__all__ = "ProgramConfiguration"


class ProgramConfiguration:
    def __init__(self) -> None:
        # classic ini file
        config = ConfigParser()
        config.read('settings.ini')

        self.__token = config["ALOR_API"]["TOKEN"]
        self.__ttl_jwt: int = config["ALOR_API"]["TTL_JWT"]
        self.__mode = config["ALOR_API"]["MODE"]
        self.__url_oauth = config["ALOR_API"]["URL_OAUTH"]
        self.__moex_open: int = config["MOEX"]["OPEN"]
        self.__moex_close: int = config["MOEX"]["CLOSE"]
        self.__moex_work_days: list = config["MOEX"]["WORK_DAYS"]
        self.__websocket_url = config["ALOR_API"]["WEBSOCKET_URL"]
        self.__websocket_dev_url = config["ALOR_API"]["WEBSOCKET_DEV_URL"]

    @property
    def token(self) -> str:
        return self.__token

    @property
    def ttl_jwt(self) -> int:
        return self.__ttl_jwt

    @property
    def mode(self) -> str:
        return self.__mode

    @property
    def url_oauth(self) -> str:
        return self.__url_oauth

    @property
    def get_moex_params(self) -> dict:
        return {
            "open": self.__moex_open,
            "close": self.__moex_close,
            "work_days": self.__moex_work_days
        }

    @property
    def websocket_url(self) -> str:
        return self.__websocket_url

    @property
    def websocket_dev_url(self) -> str:
        return self.__websocket_dev_url

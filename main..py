import logging
import os

from logging.handlers import RotatingFileHandler
from configuration.configuration import ProgramConfiguration

logger = logging.getLogger(__name__)


def prepare_logs() -> None:
    """Prepare logging system for the bot.

    This function does the following:
        - Ensure "logs/" directory exists in the current working directory.
        - Set up basic configuration for the logging module.
        - Configure a rotating file handler which logs to robot.log in the logs/ directory.
    """
    # Ensure "logs/" directory exists in the current working directory
    if not os.path.exists("logs/"):
        # Create "logs/" directory
        os.makedirs("logs/")

    # Set up basic configuration for the logging module
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
        handlers=[
            RotatingFileHandler(
                "logs/robot.log", maxBytes=100000000, backupCount=10, encoding="utf-8"
            )
        ],
        encoding="utf-8",
    )


if __name__ == "__main__":
    # Prepare logging system
    prepare_logs()

    logger.info("Program start")

    try:
        # Load configuration
        config = ProgramConfiguration("settings.ini")
        logger.info("Configuration has been loaded")

    except Exception as ex:
        logger.critical("Load configuration error: %s", repr(ex))
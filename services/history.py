import logging
import os

__all__ = "HistoryService"

logger = logging.getLogger(__name__)


class HistoryService:
    def __init__(self):
        pass

    def check_date_file(self, directory: str):
        file_path = os.path.join(directory, 'data.txt')
        return os.path.exists(file_path)

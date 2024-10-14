import logging
import os

__all__ = "FileService"

logger = logging.getLogger(__name__)


class FileService:
    def create_file(self, directory: str):
        file_path = os.path.join(directory, 'date.txt')
        with open(file_path, 'w') as f:
            f.write('<TICKER>,<DATE>,<TIME>,<OPEN>,<HIGH>,<LOW>,<CLOSE>,<VOL>\n')

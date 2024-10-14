import logging

from datetime import datetime, timezone

__all__ = "DateService"

logger = logging.getLogger(__name__)


class DateService:
    def __init__(self):
        self.today = datetime.now(timezone.utc).date()

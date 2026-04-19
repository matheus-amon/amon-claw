from abc import ABC, abstractmethod
from datetime import datetime


class ICalendarAdapter(ABC):
    @abstractmethod
    async def get_free_slots(
        self,
        calendar_id: str,
        start_date: datetime,
        end_date: datetime,
        duration_minutes: int
    ) -> list[datetime]:
        """Fetch available time slots for a given duration."""
        pass

    @abstractmethod
    async def create_event(
        self,
        calendar_id: str,
        summary: str,
        description: str,
        start_time: datetime,
        end_time: datetime
    ) -> str:
        """Create an event and return the external event ID."""
        pass

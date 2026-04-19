import uuid
from datetime import datetime, timedelta
from typing import List
from amon_claw.application.interfaces.calendar import ICalendarAdapter

class DummyCalendarAdapter(ICalendarAdapter):
    """Adapter de calendário falso para testes de MVP."""
    
    async def get_free_slots(self, calendar_id: str, start_date: datetime, end_date: datetime, duration_minutes: int) -> List[datetime]:
        """Retorna slots fixos a partir das 09:00, 14:00 e 16:00 do dia."""
        slots = []
        current_day = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        while current_day < end_date:
            slots.extend([
                current_day + timedelta(hours=9),
                current_day + timedelta(hours=14),
                current_day + timedelta(hours=16)
            ])
            current_day += timedelta(days=1)
            
        return [s for s in slots if start_date <= s <= end_date]

    async def create_event(self, calendar_id: str, summary: str, description: str, start_time: datetime, end_time: datetime) -> str:
        """Simula a criação de um evento."""
        return f"mock_evt_{uuid.uuid4().hex[:8]}"

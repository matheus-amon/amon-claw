import pytest
from datetime import datetime
from amon_claw.infrastructure.llm.adapters.dummy_calendar import DummyCalendarAdapter

@pytest.mark.asyncio
async def test_dummy_calendar_get_free_slots():
    adapter = DummyCalendarAdapter()
    slots = await adapter.get_free_slots("cal_1", datetime(2026, 4, 21), datetime(2026, 4, 22), 30)
    assert len(slots) > 0

@pytest.mark.asyncio
async def test_dummy_calendar_create_event():
    adapter = DummyCalendarAdapter()
    ext_id = await adapter.create_event("cal_1", "Test", "Test Desc", datetime(2026, 4, 21), datetime(2026, 4, 21, 10, 30))
    assert ext_id.startswith("mock_")

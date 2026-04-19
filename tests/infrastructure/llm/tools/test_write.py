import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from unittest.mock import AsyncMock
from amon_claw.infrastructure.llm.tools.write import book_appointment
from amon_claw.domain.entities.professional import Professional
from amon_claw.domain.entities.service import Service
from amon_claw.infrastructure.llm.agents.deps import AgentDeps

@pytest.fixture
def mock_deps():
    return AgentDeps(
        tenant_id=uuid4(),
        customer_id=uuid4(),
        tenant_repository=AsyncMock(),
        service_repository=AsyncMock(),
        professional_repository=AsyncMock(),
        appointment_repository=AsyncMock(),
        calendar_adapter=AsyncMock()
    )

@pytest.fixture
def mock_ctx(mock_deps):
    class MockContext:
        deps = mock_deps
    return MockContext()

@pytest.mark.asyncio
async def test_book_appointment(mock_ctx):
    prof_id = uuid4()
    serv_id = uuid4()
    mock_ctx.deps.professional_repository.get_by_id = AsyncMock(return_value=Professional(
        id=prof_id, tenant_id=mock_ctx.deps.tenant_id, name="Amon", services=[serv_id], calendar_id="cal_1"
    ))
    mock_ctx.deps.service_repository.get_by_id = AsyncMock(return_value=Service(
        id=serv_id, tenant_id=mock_ctx.deps.tenant_id, name="Corte", price=50.0, duration=30
    ))
    mock_ctx.deps.calendar_adapter.create_event = AsyncMock(return_value="ext_cal_id_123")
    
    result = await book_appointment(mock_ctx, professional_id=prof_id, service_id=serv_id, start_time=datetime(2026, 4, 21, 10, 0))
    assert "confirmado com sucesso" in result

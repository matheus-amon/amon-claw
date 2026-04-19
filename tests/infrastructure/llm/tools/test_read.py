import pytest
from uuid import uuid4
from unittest.mock import AsyncMock
from datetime import datetime, date
from pydantic_ai import RunContext
from amon_claw.infrastructure.llm.agents.deps import AgentDeps
from amon_claw.infrastructure.llm.tools.read import list_services, list_professionals, check_availability
from amon_claw.domain.entities.service import Service
from amon_claw.domain.entities.professional import Professional

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
async def test_list_services(mock_ctx):
    mock_ctx.deps.service_repository.get_all = AsyncMock(return_value=[
        Service(tenant_id=mock_ctx.deps.tenant_id, name="Corte", price=50.0, duration=30)
    ])
    result = await list_services(mock_ctx)
    assert "Corte" in result
    assert "50.0" in result

@pytest.mark.asyncio
async def test_list_professionals(mock_ctx):
    mock_ctx.deps.professional_repository.get_all = AsyncMock(return_value=[
        Professional(tenant_id=mock_ctx.deps.tenant_id, name="Amon", services=[uuid4()], calendar_id="cal_1")
    ])
    result = await list_professionals(mock_ctx)
    assert "Amon" in result

@pytest.mark.asyncio
async def test_check_availability(mock_ctx):
    prof_id = uuid4()
    mock_ctx.deps.professional_repository.get_by_id = AsyncMock(return_value=Professional(
        id=prof_id, tenant_id=mock_ctx.deps.tenant_id, name="Amon", services=[], calendar_id="cal_1"
    ))
    mock_ctx.deps.calendar_adapter.get_free_slots = AsyncMock(return_value=[
        datetime(2026, 4, 21, 10, 0)
    ])
    
    result = await check_availability(mock_ctx, professional_id=prof_id, target_date=date(2026, 4, 21), service_duration_min=30)
    assert "2026-04-21 10:00" in result

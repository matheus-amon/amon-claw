import pytest
from uuid import uuid4
from unittest.mock import AsyncMock
from pydantic_ai import RunContext
from amon_claw.infrastructure.llm.agents.deps import AgentDeps
from amon_claw.infrastructure.llm.tools.read import list_services, list_professionals
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
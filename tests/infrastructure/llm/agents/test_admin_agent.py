import os
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from pydantic_ai.models.test import TestModel

from amon_claw.infrastructure.llm.agents.admin_agent import AdminAgent
from amon_claw.infrastructure.llm.agents.deps import AgentDeps
from amon_claw.domain.entities.tenant import Tenant, BusinessHours
from amon_claw.domain.entities.service import Service


from amon_claw.infrastructure.database.mongodb.repositories.tenant_repository import TenantRepository
from amon_claw.infrastructure.database.mongodb.repositories.service_repository import ServiceRepository
from amon_claw.infrastructure.database.mongodb.repositories.professional_repository import ProfessionalRepository
from amon_claw.infrastructure.database.mongodb.repositories.appointment_repository import AppointmentRepository

@pytest.fixture
def mock_deps():
    tenant_id = uuid4()
    customer_id = uuid4()
    
    tenant_repo = MagicMock(spec=TenantRepository)
    # Mocking async methods
    tenant_repo.get_by_id = AsyncMock()
    tenant_repo.update = AsyncMock()
    
    service_repo = MagicMock(spec=ServiceRepository)
    service_repo.get_all = AsyncMock()
    service_repo.create = AsyncMock()
    service_repo.update = AsyncMock()
    
    professional_repo = MagicMock(spec=ProfessionalRepository)
    appointment_repo = MagicMock(spec=AppointmentRepository)
    calendar_adapter = MagicMock()
    
    return AgentDeps(
        tenant_id=tenant_id,
        customer_id=customer_id,
        tenant_repository=tenant_repo,
        service_repository=service_repo,
        professional_repository=professional_repo,
        appointment_repository=appointment_repo,
        calendar_adapter=calendar_adapter
    )


@patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key"})
def test_admin_agent_instantiation():
    agent = AdminAgent()
    assert "gemini-1.5-flash" in agent.agent.model.model_name
    
    tool_names = list(agent.agent._function_toolset.tools.keys())
    assert 'update_business_hours' in tool_names
    assert 'upsert_service' in tool_names
    assert 'list_catalog' in tool_names


@pytest.mark.asyncio
@patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key"})
async def test_admin_agent_run(mock_deps):
    agent = AdminAgent()
    agent.agent.model = TestModel(call_tools=[])
    
    result = await agent.run(mock_deps, "Listar catálogo")
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_update_business_hours_tool(mock_deps):
    from amon_claw.infrastructure.llm.agents.admin_agent import update_business_hours
    
    tenant = Tenant(
        id=mock_deps.tenant_id,
        name="Test Tenant",
        phone="123456789",
        business_hours={}
    )
    mock_deps.tenant_repository.get_by_id.return_value = tenant
    
    ctx = MagicMock()
    ctx.deps = mock_deps
    
    result = await update_business_hours(ctx, "segunda", "08:00", "18:00")
    
    assert "segunda" in result
    assert "08:00" in result
    assert "18:00" in result
    assert tenant.business_hours["segunda"].open == "08:00"
    assert tenant.business_hours["segunda"].close == "18:00"
    mock_deps.tenant_repository.update.assert_called_once_with(tenant)


@pytest.mark.asyncio
async def test_upsert_service_tool_create(mock_deps):
    from amon_claw.infrastructure.llm.agents.admin_agent import upsert_service
    
    mock_deps.service_repository.get_all.return_value = []
    
    ctx = MagicMock()
    ctx.deps = mock_deps
    
    result = await upsert_service(ctx, "Corte de Cabelo", 50.0, 30)
    
    assert "criado" in result
    assert "Corte de Cabelo" in result
    mock_deps.service_repository.create.assert_called_once()
    args, _ = mock_deps.service_repository.create.call_args
    service = args[0]
    assert service.name == "Corte de Cabelo"
    assert service.price == 50.0
    assert service.duration == 30
    assert service.tenant_id == mock_deps.tenant_id


@pytest.mark.asyncio
async def test_upsert_service_tool_update(mock_deps):
    from amon_claw.infrastructure.llm.agents.admin_agent import upsert_service
    
    existing_service = Service(
        tenant_id=mock_deps.tenant_id,
        name="Corte de Cabelo",
        price=40.0,
        duration=25
    )
    mock_deps.service_repository.get_all.return_value = [existing_service]
    
    ctx = MagicMock()
    ctx.deps = mock_deps
    
    result = await upsert_service(ctx, "Corte de Cabelo", 55.0, 35)
    
    assert "atualizado" in result
    assert "Corte de Cabelo" in result
    mock_deps.service_repository.update.assert_called_once_with(existing_service)
    assert existing_service.price == 55.0
    assert existing_service.duration == 35


@pytest.mark.asyncio
async def test_list_catalog_tool(mock_deps):
    from amon_claw.infrastructure.llm.agents.admin_agent import list_catalog
    
    tenant = Tenant(
        id=mock_deps.tenant_id,
        name="Test Tenant",
        phone="123456789",
        business_hours={"segunda": BusinessHours(open="09:00", close="17:00")}
    )
    mock_deps.tenant_repository.get_by_id.return_value = tenant
    
    service = Service(
        tenant_id=mock_deps.tenant_id,
        name="Barba",
        price=30.0,
        duration=20
    )
    mock_deps.service_repository.get_all.return_value = [service]
    
    ctx = MagicMock()
    ctx.deps = mock_deps
    
    result = await list_catalog(ctx)
    
    assert "Segunda" in result
    assert "09:00 - 17:00" in result
    assert "Barba" in result
    assert "R$ 30.00" in result
    assert "20 min" in result

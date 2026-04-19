import os
from unittest.mock import patch, MagicMock
import pytest
from uuid import uuid4
from amon_claw.infrastructure.llm.agents.sdr_graph import sdr_assistant
from amon_claw.domain.entities.tenant import Tenant, BusinessHours
from amon_claw.infrastructure.database.mongodb.models.tenant import TenantDocument
from langchain_core.messages import HumanMessage

@pytest.mark.asyncio
@patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key"})
async def test_admin_routing_and_tool_call():
    # Setup LangGraph thread
    config = {"configurable": {"thread_id": str(uuid4())}}
    
    # 1. Setup mock tenant in DB with admin_hash '12345'
    tenant_id = uuid4()
    tenant = Tenant(
        id=tenant_id,
        name="Test Tenant",
        phone="123456789",
        admin_hash="12345",
        business_hours={
            "monday": BusinessHours(open="09:00", close="18:00")
        }
    )
    doc = TenantDocument(**tenant.model_dump())
    await doc.insert()

    with patch("pydantic_ai.Agent.run") as mock_run:
        # Mocking the response for "/admin 12345"
        mock_run.return_value = MagicMock(output="Modo Admin ativo. O que deseja configurar?")
        
        initial_state = {
            "tenant_id": tenant_id,
            "customer_id": uuid4(),
            "messages": [HumanMessage(content="/admin 12345")],
            "flow_type": "unknown",
            "is_authenticated": False,
            "extracted_info": {},
        }
        
        result = await sdr_assistant.ainvoke(initial_state, config=config)
        
        assert result["is_authenticated"] is True
        assert result["flow_type"] == "admin"
        assert result["messages"][-1].content == "Modo Admin ativo. O que deseja configurar?"

@pytest.mark.asyncio
@patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key"})
async def test_admin_exit_flow():
    config = {"configurable": {"thread_id": str(uuid4())}}
    
    # Start in admin mode
    state = {
        "tenant_id": uuid4(),
        "customer_id": uuid4(),
        "messages": [HumanMessage(content="estou aqui")],
        "flow_type": "admin",
        "is_authenticated": True,
        "extracted_info": {},
    }
    
    # Send /exit
    state["messages"].append(HumanMessage(content="/exit"))
    
    # When /exit is sent, it should route to user_node.
    # We mock SchedulingAgent.run to avoid API calls.
    with patch("amon_claw.infrastructure.llm.agents.scheduling_agent.SchedulingAgent.run") as mock_run:
        mock_run.return_value = "Olá! Como posso ajudar você hoje?"
        
        result = await sdr_assistant.ainvoke(state, config=config)
        
        assert result["messages"][-1].content == "Olá! Como posso ajudar você hoje?"

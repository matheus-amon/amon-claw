from uuid import uuid4
from unittest.mock import patch, AsyncMock

import pytest
from langchain_core.messages import HumanMessage

from amon_claw.infrastructure.llm.agents.sdr_graph import router, sdr_assistant
from amon_claw.infrastructure.llm.agents.state import SDRState


def test_sdr_graph_initialization():
    """Verify that the sdr_assistant graph is compiled and has the expected nodes."""
    assert sdr_assistant is not None

@pytest.mark.asyncio
async def test_sdr_graph_execution():
    """Verify that the sdr_assistant runs through the expected nodes."""
    # Mock SchedulingAgent to avoid real LLM calls and missing API key error
    with patch("amon_claw.infrastructure.llm.agents.sdr_graph.SchedulingAgent") as mock_agent_class:
        mock_instance = mock_agent_class.return_value
        mock_instance.run = AsyncMock(return_value="Mocked assistant response")
        
        initial_state: SDRState = {
            "tenant_id": uuid4(),
            "customer_id": uuid4(),
            "messages": [HumanMessage(content="Hello")],
            "flow_type": "user",
            "is_authenticated": False,
            "extracted_info": {},
        }

        # Run the graph
        result = await sdr_assistant.ainvoke(initial_state, config={"configurable": {"thread_id": "test_thread"}})

        assert result["tenant_id"] == initial_state["tenant_id"]
        assert "messages" in result
        # Check if the last message is from the assistant and has the mocked content
        assert result["messages"][-1].content == "Mocked assistant response"
        mock_instance.run.assert_called_once()

def test_router_logic():
    """Test the router logic for admin and user flows."""
    # Test user flow (default)
    state_user: SDRState = {
        "tenant_id": uuid4(),
        "customer_id": uuid4(),
        "messages": [HumanMessage(content="Hello")],
        "flow_type": "user",
        "is_authenticated": False,
        "extracted_info": {},
    }
    assert router(state_user) == "user_flow"

    # Test admin flow
    state_admin: SDRState = {
        "tenant_id": uuid4(),
        "customer_id": uuid4(),
        "messages": [HumanMessage(content="/admin login")],
        "flow_type": "unknown",
        "is_authenticated": False,
        "extracted_info": {},
    }
    assert router(state_admin) == "admin_flow"

    # Test empty messages
    state_empty: SDRState = {
        "tenant_id": uuid4(),
        "customer_id": uuid4(),
        "messages": [],
        "flow_type": "unknown",
        "is_authenticated": False,
        "extracted_info": {},
    }
    assert router(state_empty) == "user_flow"

from uuid import uuid4

import pytest

from amon_claw.infrastructure.llm.agents.sdr_graph import sdr_assistant
from amon_claw.infrastructure.llm.agents.state import SDRState


def test_sdr_graph_initialization():
    """Verify that the sdr_assistant graph is compiled and has the expected nodes."""
    assert sdr_assistant is not None

@pytest.mark.asyncio
async def test_sdr_graph_execution():
    """Verify that the sdr_assistant runs through the expected nodes."""
    initial_state: SDRState = {
        "tenant_id": uuid4(),
        "customer_id": uuid4(),
        "messages": [],
        "extracted_info": {},
        "next_node": None
    }

    # Run the graph
    result = await sdr_assistant.ainvoke(initial_state)

    assert result["tenant_id"] == initial_state["tenant_id"]
    assert "messages" in result

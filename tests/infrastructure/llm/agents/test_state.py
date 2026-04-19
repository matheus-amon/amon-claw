import uuid
from typing import get_type_hints

from amon_claw.infrastructure.llm.agents.state import SDRState


def test_sdr_state_structure():
    # Verify fields exist
    hints = get_type_hints(SDRState)
    assert "tenant_id" in hints
    assert "customer_id" in hints
    assert "messages" in hints
    assert "extracted_info" in hints
    assert "next_node" in hints

def test_sdr_state_instantiation():
    state: SDRState = {
        "tenant_id": uuid.uuid4(),
        "customer_id": uuid.uuid4(),
        "messages": [],
        "extracted_info": {"service_id": "123"},
        "next_node": "greeting"
    }
    assert isinstance(state["tenant_id"], uuid.UUID)
    assert state["extracted_info"]["service_id"] == "123"

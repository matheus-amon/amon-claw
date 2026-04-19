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
    assert "flow_type" in hints
    assert "is_authenticated" in hints
    assert "next_node" in hints
    assert "intent_type" in hints
    assert "security_flag" in hints
    assert "off_topic_count" in hints

def test_sdr_state_instantiation():
    state: SDRState = {
        "tenant_id": uuid.uuid4(),
        "customer_id": uuid.uuid4(),
        "messages": [],
        "extracted_info": {"service_id": "123"},
        "flow_type": "user",
        "is_authenticated": False
    }
    assert isinstance(state["tenant_id"], uuid.UUID)
    assert state["extracted_info"]["service_id"] == "123"

def test_sdr_state_includes_security_fields():
    # Verify fields exist in type hints
    hints = get_type_hints(SDRState)
    assert "intent_type" in hints
    assert "security_flag" in hints
    assert "off_topic_count" in hints
    assert "next_node" in hints

    state: SDRState = {
        "messages": [],
        "tenant_id": uuid.uuid4(),
        "customer_id": uuid.uuid4(),
        "extracted_info": {},
        "next_node": None,
        "intent_type": "scheduling",
        "security_flag": "none",
        "off_topic_count": 0,
        "flow_type": "user",
        "is_authenticated": False
    }
    assert state["intent_type"] == "scheduling"
    assert state["security_flag"] == "none"
    assert state["off_topic_count"] == 0

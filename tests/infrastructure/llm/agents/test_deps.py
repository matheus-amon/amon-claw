from uuid import uuid4
from amon_claw.infrastructure.llm.agents.deps import AgentDeps

def test_agent_deps_instantiation():
    deps = AgentDeps(
        tenant_id=uuid4(),
        customer_id=uuid4(),
        tenant_repository="mock_repo",
        service_repository="mock_repo",
        professional_repository="mock_repo",
        appointment_repository="mock_repo",
        calendar_adapter="mock_adapter"
    )
    assert deps.tenant_id is not None

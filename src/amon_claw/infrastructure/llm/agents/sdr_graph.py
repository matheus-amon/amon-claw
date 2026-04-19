from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from amon_claw.infrastructure.llm.agents.scheduling_agent import SchedulingAgent
from amon_claw.infrastructure.llm.agents.admin_agent import AdminAgent
from amon_claw.infrastructure.llm.agents.state import SDRState
from amon_claw.infrastructure.llm.agents.deps import AgentDeps
from amon_claw.infrastructure.database.mongodb.repositories.tenant_repository import TenantRepository
from amon_claw.infrastructure.database.mongodb.repositories.service_repository import ServiceRepository
from amon_claw.infrastructure.database.mongodb.repositories.professional_repository import ProfessionalRepository
from amon_claw.infrastructure.database.mongodb.repositories.appointment_repository import AppointmentRepository
from amon_claw.infrastructure.llm.adapters.dummy_calendar import DummyCalendarAdapter
from amon_claw.infrastructure.llm.agents.nodes.security import (
    intent_security_node,
    off_topic_responder_node,
    security_action_node,
)


async def user_node(state: SDRState):
    """
    Node for the user flow.
    Calls the SchedulingAgent with injected dependencies.
    """
    if not state.get("messages"):
        return {"messages": [("assistant", "Olá! Como posso ajudar você hoje?")]}
    
    agent = SchedulingAgent()
    
    # Initialize repositories (they are stateless wrappers over Beanie models)
    deps = AgentDeps(
        tenant_id=state["tenant_id"],
        customer_id=state["customer_id"],
        tenant_repository=TenantRepository(),
        service_repository=ServiceRepository(),
        professional_repository=ProfessionalRepository(),
        appointment_repository=AppointmentRepository(),
        calendar_adapter=DummyCalendarAdapter()
    )
    
    response = await agent.run(deps=deps, message=state["messages"][-1].content)
    return {"messages": [("assistant", response)]}

async def admin_node(state: SDRState):
    """
    Node for the admin flow.
    Calls the AdminAgent with injected dependencies.
    """
    last_message = state["messages"][-1].content
    
    agent = AdminAgent()
    deps = AgentDeps(
        tenant_id=state["tenant_id"],
        customer_id=state["customer_id"],
        tenant_repository=TenantRepository(),
        service_repository=ServiceRepository(),
        professional_repository=ProfessionalRepository(),
        appointment_repository=AppointmentRepository(),
        calendar_adapter=DummyCalendarAdapter()
    )
    
    response = await agent.run(deps=deps, message=last_message)
    return {
        "messages": [("assistant", response)],
        "flow_type": "admin",
        "is_authenticated": True
    }

def should_continue(state: SDRState) -> str:
    """
    Decide where to route based on security and intent analysis.
    """
    if state.get("security_flag") == "potential_injection":
        return "security_threat"
    
    if state.get("intent_type") == "off_topic":
        return "off_topic"
        
    last_message = state["messages"][-1].content
    
    # If already in admin mode, stay there unless /exit
    if state.get("flow_type") == "admin":
        if isinstance(last_message, str) and last_message.strip().lower() == "/exit":
             return "user_flow"
        return "admin_flow"

    if isinstance(last_message, str) and last_message.startswith("/admin"):
        return "admin_flow"
        
    return "user_flow"

# Create the graph
workflow = StateGraph(SDRState)

# Add nodes
workflow.add_node("intent_security", intent_security_node)
workflow.add_node("security_action", security_action_node)
workflow.add_node("off_topic_responder", off_topic_responder_node)
workflow.add_node("user_node", user_node)
workflow.add_node("admin_node", admin_node)

# Set entry point
workflow.set_entry_point("intent_security")

# Set conditional edges from intent_security
workflow.add_conditional_edges(
    "intent_security",
    should_continue,
    {
        "security_threat": "security_action",
        "off_topic": "off_topic_responder",
        "admin_flow": "admin_node",
        "user_flow": "user_node"
    }
)

# Define remaining edges
workflow.add_edge("security_action", END)
workflow.add_edge("off_topic_responder", "user_node") # Or END, but user_node can give a generic response
workflow.add_edge("user_node", END)
workflow.add_edge("admin_node", END)

# Memory for persistence
memory = MemorySaver()

# Compile the graph
sdr_assistant = workflow.compile(checkpointer=memory)

# Keep router for backward compatibility or if needed by tests
def router(state: SDRState) -> str:
    return should_continue(state)

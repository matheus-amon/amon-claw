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
    # For now, if router sent here, we assume it's an admin attempt
    last_message = state["messages"][-1].content
    
    agent = AdminAgent()
    deps = AgentDeps(
        tenant_id=state["tenant_id"],
        customer_id=state["customer_id"], # Admin usually doesn't need this but it's in Deps
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

def router(state: SDRState) -> str:
    """
    Decide which flow to follow based on message content.
    """
    if not state["messages"]:
        return "user_flow"
        
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
workflow.add_node("user_node", user_node)
workflow.add_node("admin_node", admin_node)

# Set conditional entry point
workflow.set_conditional_entry_point(
    router,
    {
        "admin_flow": "admin_node",
        "user_flow": "user_node"
    }
)

# Define edges
workflow.add_edge("user_node", END)
workflow.add_edge("admin_node", END) # Or back to router if we want multi-turn

# Memory for persistence
memory = MemorySaver()

# Compile the graph
sdr_assistant = workflow.compile(checkpointer=memory)

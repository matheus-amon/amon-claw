from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from amon_claw.infrastructure.llm.agents.scheduling_agent import SchedulingAgent
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

def router(state: SDRState) -> str:
    """
    Decide which flow to follow based on message content.
    """
    if not state["messages"]:
        return "user_flow"
    
    last_message = state["messages"][-1].content
    if isinstance(last_message, str) and last_message.startswith("/admin"):
        return "admin_flow"
    return "user_flow"

# Create the graph
workflow = StateGraph(SDRState)

# Add nodes
workflow.add_node("user_node", user_node)

# Set conditional entry point
workflow.set_conditional_entry_point(
    router,
    {
        "admin_flow": END,  # To be implemented
        "user_flow": "user_node"
    }
)

# Define edges
workflow.add_edge("user_node", END)

# Memory for persistence
memory = MemorySaver()

# Compile the graph
sdr_assistant = workflow.compile(checkpointer=memory)

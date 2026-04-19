from langgraph.graph import END, StateGraph

from amon_claw.infrastructure.llm.agents.scheduling_agent import SchedulingAgent
from amon_claw.infrastructure.llm.agents.state import SDRState


async def user_node(state: SDRState):
    """
    Node for the user flow.
    Calls the SchedulingAgent.
    """
    agent = SchedulingAgent()
    # No futuro injetaremos deps aqui
    response = await agent.run(deps=None, message=state["messages"][-1].content)
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
workflow.add_node("router_node", lambda x: x)  # Entry placeholder
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

# Compile the graph
sdr_assistant = workflow.compile()

from langgraph.graph import END, StateGraph

from amon_claw.infrastructure.llm.agents.state import SDRState


def greeting(state: SDRState) -> SDRState:
    """Stub node for greeting."""
    return state

def collect_info(state: SDRState) -> SDRState:
    """Stub node for collecting information."""
    return state

def check_availability(state: SDRState) -> SDRState:
    """Stub node for checking professional availability."""
    return state

def finalize_booking(state: SDRState) -> SDRState:
    """Stub node for finalizing the booking."""
    return state

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
workflow.add_node("greeting", greeting)
workflow.add_node("collect_info", collect_info)
workflow.add_node("check_availability", check_availability)
workflow.add_node("finalize_booking", finalize_booking)

# Set entry point
workflow.set_entry_point("greeting")

# Define edges (simple path for now)
workflow.add_edge("greeting", "collect_info")
workflow.add_edge("collect_info", END)

# Compile the graph
sdr_assistant = workflow.compile()

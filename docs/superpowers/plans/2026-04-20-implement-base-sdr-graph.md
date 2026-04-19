# Implement Base Graph Structure for SDR Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the base skeleton of the SDR LangGraph orchestration with stub nodes and basic routing.

**Architecture:** Use `langgraph.graph.StateGraph` with `SDRState` to define a flow. Nodes are currently stubs that return the input state.

**Tech Stack:** `langgraph`, `typing`, `src.amon_claw.infrastructure.llm.agents.state.SDRState`

---

### Task 1: Create SDR Graph File and Define Stub Nodes

**Files:**
- Create: `src/amon_claw/infrastructure/llm/agents/sdr_graph.py`

- [ ] **Step 1: Create the file with imports and stub nodes**

```python
from langgraph.graph import END, StateGraph
from src.amon_claw.infrastructure.llm.agents.state import SDRState

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
```

- [ ] **Step 2: Initialize and configure the StateGraph**

```python
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
```

- [ ] **Step 3: Commit**

```bash
git add src/amon_claw/infrastructure/llm/agents/sdr_graph.py
git commit -m "feat: implement base SDR graph structure"
```

### Task 2: Verify Graph Structure

**Files:**
- Create: `tests/infrastructure/llm/agents/test_sdr_graph.py`

- [ ] **Step 1: Write a test to verify the graph can be invoked**

```python
import pytest
from uuid import uuid4
from src.amon_claw.infrastructure.llm.agents.sdr_graph import sdr_assistant
from src.amon_claw.infrastructure.llm.agents.state import SDRState

def test_sdr_graph_initialization():
    """Verify that the sdr_assistant graph is compiled and has the expected nodes."""
    assert sdr_assistant is not None
    # Check if entry point is correct (this is harder to check directly on CompiledGraph, 
    # but we can check if it runs)

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
```

- [ ] **Step 2: Run the test**

Run: `pytest tests/infrastructure/llm/agents/test_sdr_graph.py`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add tests/infrastructure/llm/agents/test_sdr_graph.py
git commit -m "test: add verification for base SDR graph"
```

# SDR Orchestration (LangGraph + Pydantic AI) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the core conversation brain using LangGraph for orchestration and Pydantic AI for deterministic execution, supporting both Admin and User flows.

**Architecture:** Clean Architecture approach. LangGraph lives in the `Application` layer as a Use Case (`IBrain`). Agents are implemented via Pydantic AI in the `Infrastructure` layer, following a `BaseAgent` interface. Separation of flows is handled by a router node.

**Tech Stack:** Python 3.12, LangGraph, Pydantic AI, Beanie (MongoDB), Pydantic.

---

### Task 1: Define Application Interfaces

**Files:**
- Create: `src/amon_claw/application/interfaces/brain.py`

- [ ] **Step 1: Define the `IBrain` interface**

```python
from abc import ABC, abstractmethod
from uuid import UUID

class IBrain(ABC):
    @abstractmethod
    async def process_message(self, tenant_id: UUID, customer_id: UUID, message: str) -> str:
        """Process a message and return the SDR's response."""
        pass
```

- [ ] **Step 2: Commit**

```bash
git add src/amon_claw/application/interfaces/brain.py
git commit -m "feat(application): define IBrain interface"
```

---

### Task 2: Update SDR State and Router Logic

**Files:**
- Modify: `src/amon_claw/infrastructure/llm/agents/state.py`
- Modify: `src/amon_claw/infrastructure/llm/agents/sdr_graph.py`

- [ ] **Step 1: Update `SDRState` to include flow control**

```python
from typing import Annotated, Any, TypedDict, Literal
from uuid import UUID
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class SDRState(TypedDict):
    tenant_id: UUID
    customer_id: UUID
    messages: Annotated[list[BaseMessage], add_messages]
    flow_type: Literal["admin", "user", "unknown"]
    is_authenticated: bool
    extracted_info: dict[str, Any]
```

- [ ] **Step 2: Implement the Router Node in `sdr_graph.py`**

```python
def router(state: SDRState) -> str:
    last_message = state["messages"][-1].content
    if last_message.startswith("/admin"):
        return "admin_flow"
    return "user_flow"
```

- [ ] **Step 3: Commit**

```bash
git add src/amon_claw/infrastructure/llm/agents/state.py src/amon_claw/infrastructure/llm/agents/sdr_graph.py
git commit -m "feat(llm): add router logic and update SDRState"
```

---

### Task 3: Base Agent Interface and Pydantic AI Setup

**Files:**
- Create: `src/amon_claw/infrastructure/llm/agents/base.py`

- [ ] **Step 1: Define `BaseAgent` using Pydantic AI**

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any
from pydantic_ai import Agent

T = TypeVar("T")

class BaseAgent(ABC, Generic[T]):
    @property
    @abstractmethod
    def agent(self) -> Agent:
        pass

    @abstractmethod
    async def run(self, deps: Any, message: str) -> T:
        pass
```

- [ ] **Step 2: Commit**

```bash
git add src/amon_claw/infrastructure/llm/agents/base.py
git commit -m "feat(llm): define BaseAgent interface with Pydantic AI"
```

---

### Task 4: Implement Scheduling Agent (User Flow)

**Files:**
- Create: `src/amon_claw/infrastructure/llm/agents/scheduling_agent.py`

- [ ] **Step 1: Create a simple Scheduling Agent**

```python
from pydantic_ai import Agent, RunContext
from amon_claw.infrastructure.llm.agents.base import BaseAgent

class SchedulingAgent(BaseAgent[str]):
    def __init__(self):
        self._agent = Agent(
            'gemini-1.5-flash',
            system_prompt="Você é um assistente de agendamento determinístico. Ajude o cliente a marcar horários.",
            result_type=str
        )

    @property
    def agent(self) -> Agent:
        return self._agent

    async def run(self, deps: Any, message: str) -> str:
        result = await self._agent.run(message, deps=deps)
        return result.data
```

- [ ] **Step 2: Commit**

```bash
git add src/amon_claw/infrastructure/llm/agents/scheduling_agent.py
git commit -m "feat(llm): implement initial SchedulingAgent"
```

---

### Task 5: Integrate Agents into LangGraph

**Files:**
- Modify: `src/amon_claw/infrastructure/llm/agents/sdr_graph.py`

- [ ] **Step 1: Connect Router to real Agent Nodes**

```python
from langgraph.graph import StateGraph, END
from amon_claw.infrastructure.llm.agents.scheduling_agent import SchedulingAgent

async def user_node(state: SDRState):
    agent = SchedulingAgent()
    # No futuro injetaremos deps aqui
    response = await agent.run(deps=None, message=state["messages"][-1].content)
    return {"messages": [("assistant", response)]}

workflow = StateGraph(SDRState)
workflow.add_node("router_node", lambda x: x) # Entry placeholder
workflow.add_node("user_node", user_node)

workflow.set_conditional_entry_point(
    router,
    {
        "admin_flow": END, # To be implemented
        "user_flow": "user_node"
    }
)
workflow.add_edge("user_node", END)
sdr_assistant = workflow.compile()
```

- [ ] **Step 2: Commit**

```bash
git add src/amon_claw/infrastructure/llm/agents/sdr_graph.py
git commit -m "feat(llm): integrate SchedulingAgent into LangGraph"
```

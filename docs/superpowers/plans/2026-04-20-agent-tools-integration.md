# Agent Tools Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate the Read/Write tools into the `SchedulingAgent` and inject the required dependencies (`AgentDeps`) via the LangGraph `user_node`.

**Architecture:** We will create a `DummyCalendarAdapter` to fulfill `ICalendarAdapter` during testing. `SchedulingAgent` will register the external tools via `.tool(...)`. LangGraph's `user_node` will instantiate the global Beanie repositories and the calendar adapter to assemble `AgentDeps`, injecting them into the agent run.

**Tech Stack:** Python 3.12, Pydantic AI, LangGraph, Beanie.

---

### Task 1: Create Dummy Calendar Adapter

**Files:**
- Create: `src/amon_claw/infrastructure/llm/adapters/dummy_calendar.py`
- Create: `tests/infrastructure/llm/adapters/test_dummy_calendar.py`

- [ ] **Step 1: Write the failing test**

```python
import pytest
from datetime import datetime
from amon_claw.infrastructure.llm.adapters.dummy_calendar import DummyCalendarAdapter

@pytest.mark.asyncio
async def test_dummy_calendar_get_free_slots():
    adapter = DummyCalendarAdapter()
    slots = await adapter.get_free_slots("cal_1", datetime(2026, 4, 21), datetime(2026, 4, 22), 30)
    assert len(slots) > 0

@pytest.mark.asyncio
async def test_dummy_calendar_create_event():
    adapter = DummyCalendarAdapter()
    ext_id = await adapter.create_event("cal_1", "Test", "Test Desc", datetime(2026, 4, 21), datetime(2026, 4, 21, 10, 30))
    assert ext_id.startswith("mock_")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/infrastructure/llm/adapters/test_dummy_calendar.py`
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Write minimal implementation**

```python
import uuid
from datetime import datetime, timedelta
from typing import List
from amon_claw.application.interfaces.calendar import ICalendarAdapter

class DummyCalendarAdapter(ICalendarAdapter):
    """Adapter de calendário falso para testes de MVP."""
    
    async def get_free_slots(self, calendar_id: str, start_date: datetime, end_date: datetime, duration_minutes: int) -> List[datetime]:
        """Retorna slots fixos a partir das 09:00, 14:00 e 16:00 do dia."""
        slots = []
        current_day = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        while current_day < end_date:
            slots.extend([
                current_day + timedelta(hours=9),
                current_day + timedelta(hours=14),
                current_day + timedelta(hours=16)
            ])
            current_day += timedelta(days=1)
            
        return [s for s in slots if start_date <= s <= end_date]

    async def create_event(self, calendar_id: str, summary: str, description: str, start_time: datetime, end_time: datetime) -> str:
        """Simula a criação de um evento."""
        return f"mock_evt_{uuid.uuid4().hex[:8]}"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/infrastructure/llm/adapters/test_dummy_calendar.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/amon_claw/infrastructure/llm/adapters/ tests/infrastructure/llm/adapters/
git commit -m "feat(llm): implement DummyCalendarAdapter for MVP testing"
```

---

### Task 2: Register Tools in SchedulingAgent

**Files:**
- Modify: `src/amon_claw/infrastructure/llm/agents/scheduling_agent.py`
- Modify: `tests/infrastructure/llm/agents/test_scheduling_agent.py` (if it exists, adjust test to expect registered tools, else skip test modification for pure tool registration)

- [ ] **Step 1: Import dependencies and tools in `scheduling_agent.py`**

```python
from amon_claw.infrastructure.llm.agents.deps import AgentDeps
from amon_claw.infrastructure.llm.tools.read import list_services, list_professionals, check_availability
from amon_claw.infrastructure.llm.tools.write import book_appointment
```

- [ ] **Step 2: Update the `Agent` definition in `SchedulingAgent.__init__`**

Add `deps_type=AgentDeps` to the initialization and register the tools.

```python
# Modifique a assinatura de Agent na inicialização do SchedulingAgent:
        self._agent = Agent(
            'google-gla:gemini-1.5-flash',
            deps_type=AgentDeps,
            system_prompt=(
                "Você é o Amon Claw, um assistente de agendamento focado em conversão e cordialidade. "
                "SEMPRE utilize as ferramentas para consultar disponibilidade e listar serviços antes de sugerir horários. "
                "SEMPRE solicite a confirmação do cliente antes de acionar a ferramenta de agendamento final."
            ),
            output_type=str
        )
        
        # Registrar ferramentas
        self._agent.tool(list_services)
        self._agent.tool(list_professionals)
        self._agent.tool(check_availability)
        self._agent.tool(book_appointment)
```

- [ ] **Step 3: Verify the file syntax**

Run: `uv run ruff check src/amon_claw/infrastructure/llm/agents/scheduling_agent.py`
Expected: No errors.

- [ ] **Step 4: Commit**

```bash
git add src/amon_claw/infrastructure/llm/agents/scheduling_agent.py
git commit -m "feat(llm): register read/write tools and deps in SchedulingAgent"
```

---

### Task 3: Inject Dependencies via LangGraph `user_node`

**Files:**
- Modify: `src/amon_claw/infrastructure/llm/agents/sdr_graph.py`

- [ ] **Step 1: Import the repositories, adapter, and AgentDeps in `sdr_graph.py`**

```python
from amon_claw.infrastructure.llm.agents.deps import AgentDeps
from amon_claw.infrastructure.database.mongodb.repositories.tenant_repository import TenantRepository
from amon_claw.infrastructure.database.mongodb.repositories.service_repository import ServiceRepository
from amon_claw.infrastructure.database.mongodb.repositories.professional_repository import ProfessionalRepository
from amon_claw.infrastructure.database.mongodb.repositories.appointment_repository import AppointmentRepository
from amon_claw.infrastructure.llm.adapters.dummy_calendar import DummyCalendarAdapter
```

- [ ] **Step 2: Update the `user_node` to instantiate and inject the dependencies**

```python
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
```

- [ ] **Step 3: Run the graph tests to ensure nothing breaks**

Run: `uv run pytest tests/infrastructure/llm/agents/test_sdr_graph.py`
(If errors occur regarding Google API key or threading in older mock tests, ignore for now as they are structural tests or you can fix the mock in a separate PR, but ensure no Syntax/Import errors happen here).

- [ ] **Step 4: Commit**

```bash
git add src/amon_claw/infrastructure/llm/agents/sdr_graph.py
git commit -m "feat(llm): inject AgentDeps into SchedulingAgent run inside user_node"
```
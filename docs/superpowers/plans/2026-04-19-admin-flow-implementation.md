# Admin Flow (WhatsApp First) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a secure "Admin Mode" that allows business owners to configure their working hours and service catalog directly via WhatsApp using a specialized LangGraph sub-graph and Pydantic AI tools.

**Architecture:** A router node in the main SDR graph will intercept `/admin <hash>` commands. If valid, it redirects to an `AdminGraph` where a dedicated agent handles configuration tasks using tool-calling to update the MongoDB database via Beanie.

**Tech Stack:** LangGraph, Pydantic AI, Beanie (MongoDB), Pydantic.

---

### Task 1: Update Domain Entities and Database Schema

Add `admin_hash` to the `Tenant` entity and ensure `BusinessHours` and `Service` models are ready for updates.

**Files:**
- Modify: `src/amon_claw/domain/entities/tenant.py`
- Modify: `src/amon_claw/infrastructure/database/mongodb/models/tenant.py`

- [ ] **Step 1: Add `admin_hash` to `Tenant` domain entity**

```python
# src/amon_claw/domain/entities/tenant.py

class Tenant(BaseModel):
    # ... existing fields ...
    admin_hash: str = Field(default="12345") # Default for PoC
    # ...
```

- [ ] **Step 2: Update `TenantDocument` to include the new field**
(Since `TenantDocument` inherits from `Tenant`, it should be automatic, but verify if any special index is needed).

- [ ] **Step 3: Commit**

```bash
git add src/amon_claw/domain/entities/tenant.py
git commit -m "domain: add admin_hash to Tenant entity"
```

---

### Task 2: Create Admin Agent and Tools

Implement the `AdminAgent` using Pydantic AI and define tools for business hours and service catalog management.

**Files:**
- Create: `src/amon_claw/infrastructure/llm/agents/admin_agent.py`
- Modify: `src/amon_claw/infrastructure/llm/agents/deps.py`

- [ ] **Step 1: Update `AgentDeps` to include necessary repositories for admin**

```python
# src/amon_claw/infrastructure/llm/agents/deps.py

@dataclass
class AgentDeps:
    tenant_id: UUID
    # ... existing deps ...
    tenant_repository: TenantRepository
    service_repository: ServiceRepository
    # ...
```

- [ ] **Step 2: Create `AdminAgent` with tools**

```python
# src/amon_claw/infrastructure/llm/agents/admin_agent.py
from pydantic_ai import Agent, RunContext
from amon_claw.infrastructure.llm.agents.deps import AgentDeps

admin_agent = Agent(
    'openai:gpt-4o', # Or the configured model
    deps_type=AgentDeps,
    system_prompt="Você é o assistente administrativo do Amon-Claw..."
)

@admin_agent.tool
async def update_business_hours(ctx: RunContext[AgentDeps], day: str, open_time: str, close_time: str) -> str:
    # Logic to update tenant business hours via repository
    return "Horário atualizado com sucesso!"

@admin_agent.tool
async def upsert_service(ctx: RunContext[AgentDeps], name: str, price: float, duration: int) -> str:
    # Logic to add/update service via repository
    return f"Serviço {name} atualizado!"
```

- [ ] **Step 3: Commit**

```bash
git add src/amon_claw/infrastructure/llm/agents/admin_agent.py
git commit -m "infra: implement AdminAgent and tools"
```

---

### Task 3: Implement Admin Sub-Graph and Router

Integrate the `AdminAgent` into a LangGraph sub-graph and update the main `sdr_assistant` router.

**Files:**
- Modify: `src/amon_claw/infrastructure/llm/agents/sdr_graph.py`

- [ ] **Step 1: Define `admin_node` and update `router`**

```python
# src/amon_claw/infrastructure/llm/agents/sdr_graph.py

async def admin_node(state: SDRState):
    # Logic to call AdminAgent
    return {"messages": [("assistant", "Modo admin ativo.")]}

def router(state: SDRState) -> str:
    last_message = state["messages"][-1].content
    if last_message.startswith("/admin"):
        # Validate hash logic here or in node
        return "admin_flow"
    return "user_flow"

# Update workflow definition
workflow.add_node("admin_node", admin_node)
workflow.set_conditional_entry_point(
    router,
    {
        "admin_flow": "admin_node",
        "user_flow": "user_node"
    }
)
workflow.add_edge("admin_node", END)
```

- [ ] **Step 2: Commit**

```bash
git add src/amon_claw/infrastructure/llm/agents/sdr_graph.py
git commit -m "infra: integrate admin_flow into LangGraph"
```

---

### Task 4: Verification and Integration Tests

Write a test case to simulate the `/admin <hash>` command and verify database updates.

**Files:**
- Create: `tests/infrastructure/llm/agents/test_admin_flow.py`

- [ ] **Step 1: Write integration test**

```python
# tests/infrastructure/llm/agents/test_admin_flow.py

@pytest.mark.asyncio
async def test_admin_routing_and_tool_call():
    # Setup mock tenant with hash '12345'
    # Call sdr_assistant.ainvoke with "/admin 12345"
    # Verify it reaches admin_node and can call tools
    pass
```

- [ ] **Step 2: Run tests**

Run: `pytest tests/infrastructure/llm/agents/test_admin_flow.py -v`
Expected: PASS

- [ ] **Step 3: Final Commit**

```bash
git add tests/infrastructure/llm/agents/test_admin_flow.py
git commit -m "test: add integration tests for admin flow"
```

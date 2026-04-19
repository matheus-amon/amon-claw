# SDR LangGraph Conversation State Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Define the conversation state schema for the SDR LangGraph assistant.

**Architecture:** We use a `TypedDict` to define the LangGraph state, ensuring it includes message history management (`add_messages`) and business-specific context (tenant, customer, and extracted info).

**Tech Stack:** LangGraph, LangChain Core, Pydantic, Python Typing, UUID.

---

### Task 1: Setup Directory Structure

**Files:**
- Create: `src/amon_claw/infrastructure/llm/__init__.py`
- Create: `src/amon_claw/infrastructure/llm/agents/__init__.py`

- [ ] **Step 1: Create __init__.py files**

```bash
touch src/amon_claw/infrastructure/llm/__init__.py
touch src/amon_claw/infrastructure/llm/agents/__init__.py
```

- [ ] **Step 2: Verify files exist**

Run: `ls src/amon_claw/infrastructure/llm/__init__.py src/amon_claw/infrastructure/llm/agents/__init__.py`
Expected: Success

---

### Task 2: Define SDRState

**Files:**
- Create: `src/amon_claw/infrastructure/llm/agents/state.py`
- Test: `tests/infrastructure/llm/agents/test_state.py`

- [ ] **Step 1: Write the test to verify TypedDict structure**

```python
import uuid
from typing import get_type_hints
from amon_claw.infrastructure.llm.agents.state import SDRState
from langchain_core.messages import BaseMessage

def test_sdr_state_structure():
    # Verify fields exist
    hints = get_type_hints(SDRState)
    assert "tenant_id" in hints
    assert "customer_id" in hints
    assert "messages" in hints
    assert "extracted_info" in hints
    assert "next_node" in hints

def test_sdr_state_instantiation():
    state: SDRState = {
        "tenant_id": uuid.uuid4(),
        "customer_id": uuid.uuid4(),
        "messages": [],
        "extracted_info": {"service_id": "123"},
        "next_node": "greeting"
    }
    assert isinstance(state["tenant_id"], uuid.UUID)
    assert state["extracted_info"]["service_id"] == "123"
```

- [ ] **Step 2: Create test directory and run test to verify it fails**

Run: `mkdir -p tests/infrastructure/llm/agents && pytest tests/infrastructure/llm/agents/test_state.py`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Implement SDRState**

```python
from typing import Annotated, Any, Dict, Optional, TypedDict
from uuid import UUID

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class SDRState(TypedDict):
    """
    State for the SDR LangGraph assistant.
    """
    tenant_id: UUID
    customer_id: UUID
    messages: Annotated[list[BaseMessage], add_messages]
    extracted_info: Dict[str, Any]
    next_node: Optional[str]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/infrastructure/llm/agents/test_state.py`
Expected: PASS

- [ ] **Step 5: Run ruff to ensure style compliance**

Run: `uv run ruff check src/amon_claw/infrastructure/llm/agents/state.py`
Expected: No errors

---

### Task 3: Finalize Task 1

- [ ] **Step 1: Commit changes**

```bash
git add docs/superpowers/specs/2026-04-20-sdr-langgraph-state.md \
        docs/superpowers/plans/2026-04-20-sdr-langgraph-state.md \
        src/amon_claw/infrastructure/llm/agents/state.py \
        src/amon_claw/infrastructure/llm/agents/__init__.py \
        src/amon_claw/infrastructure/llm/__init__.py \
        tests/infrastructure/llm/agents/test_state.py
git commit -m "feat(llm): define SDRState for LangGraph"
```

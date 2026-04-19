# Base Agent Interface Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Define the `BaseAgent` interface using Pydantic AI to standardize agent creation and execution.

**Architecture:** Use an Abstract Base Class (ABC) with Python Generics to support structured outputs. Standardize on Pydantic AI's `Agent` class.

**Tech Stack:** Python 3.12, Pydantic AI, pytest.

---

### Task 1: Define BaseAgent Interface

**Files:**
- Create: `src/amon_claw/infrastructure/llm/agents/base.py`
- Create: `tests/infrastructure/llm/agents/test_base.py`

- [ ] **Step 1: Write the failing test for BaseAgent**

```python
import pytest
from pydantic_ai import Agent
from amon_claw.infrastructure.llm.agents.base import BaseAgent
from typing import Any

def test_base_agent_interface():
    class MockAgent(BaseAgent[str]):
        @property
        def agent(self) -> Agent:
            return Agent('google-gla:gemini-1.5-flash')

        async def run(self, deps: Any, message: str) -> str:
            return "mock response"

    mock = MockAgent()
    assert isinstance(mock, BaseAgent)
    assert isinstance(mock.agent, Agent)

@pytest.mark.asyncio
async def test_mock_agent_run():
    class MockAgent(BaseAgent[str]):
        @property
        def agent(self) -> Agent:
            return Agent('google-gla:gemini-1.5-flash')

        async def run(self, deps: Any, message: str) -> str:
            return f"Processed: {message}"

    mock = MockAgent()
    result = await mock.run(None, "hello")
    assert result == "Processed: hello"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/infrastructure/llm/agents/test_base.py -v`
Expected: FAIL (ModuleNotFoundError or ImportError)

- [ ] **Step 3: Implement BaseAgent interface**

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any
from pydantic_ai import Agent

T = TypeVar("T")

class BaseAgent(ABC, Generic[T]):
    @property
    @abstractmethod
    def agent(self) -> Agent:
        """Return the Pydantic AI Agent instance."""
        pass

    @abstractmethod
    async def run(self, deps: Any, message: str) -> T:
        """Run the agent with the given dependencies and message."""
        pass
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/infrastructure/llm/agents/test_base.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/amon_claw/infrastructure/llm/agents/base.py tests/infrastructure/llm/agents/test_base.py
git commit -m "feat(llm): define BaseAgent interface with Pydantic AI"
```

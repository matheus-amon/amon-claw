# Design Spec: Base Agent Interface and Pydantic AI Setup

## Overview
This spec defines the `BaseAgent` interface using Pydantic AI. This interface standardizes how agents are created and executed in the infrastructure layer, supporting structured outputs and dependency injection.

## Architecture
The `BaseAgent` is an abstract base class (ABC) that uses generics to define the return type of the agent.

### Components
- `BaseAgent`: The abstract base class.
- `Agent`: The Pydantic AI agent instance.
- `run`: The standard method to execute the agent.

## Implementation Details

### Base Interface
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

## Testing Strategy
- Create a mock agent that implements `BaseAgent`.
- Verify that `run` correctly returns the expected type.
- Verify that the `agent` property is correctly implemented.

## Success Criteria
- `src/amon_claw/infrastructure/llm/agents/base.py` exists with the defined interface.
- All tests pass.
- Linting and type checking pass.

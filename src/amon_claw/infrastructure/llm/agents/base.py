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

import pytest
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel
from amon_claw.infrastructure.llm.agents.base import BaseAgent
from typing import Any

def test_base_agent_interface():
    class MockAgent(BaseAgent[str]):
        @property
        def agent(self) -> Agent:
            return Agent(TestModel())

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
            return Agent(TestModel())

        async def run(self, deps: Any, message: str) -> str:
            return f"Processed: {message}"

    mock = MockAgent()
    result = await mock.run(None, "hello")
    assert result == "Processed: hello"

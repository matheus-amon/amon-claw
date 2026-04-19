from typing import Any
from pydantic_ai import Agent
from amon_claw.infrastructure.llm.agents.base import BaseAgent

class SchedulingAgent(BaseAgent[str]):
    def __init__(self):
        # Na versão 1.70.0+ o parâmetro é output_type e o resultado está em .output
        self._agent = Agent(
            'google-gla:gemini-1.5-flash',
            system_prompt="Você é um assistente de agendamento determinístico. Ajude o cliente a marcar horários.",
            output_type=str
        )

    @property
    def agent(self) -> Agent:
        return self._agent

    async def run(self, deps: Any, message: str) -> str:
        result = await self._agent.run(message, deps=deps)
        return result.output

from typing import Any

from pydantic_ai import Agent

from amon_claw.infrastructure.llm.agents.base import BaseAgent
from amon_claw.infrastructure.llm.agents.deps import AgentDeps
from amon_claw.infrastructure.llm.tools.read import (
    check_availability,
    list_professionals,
    list_services,
)
from amon_claw.infrastructure.llm.tools.write import book_appointment


class SchedulingAgent(BaseAgent[str]):
    def __init__(self):
        # Na versão 1.70.0+ o parâmetro é output_type e o resultado está em .output
        self._agent = Agent(
            'google-gla:gemini-1.5-flash',
            deps_type=AgentDeps,
            system_prompt=(
                'Você é o Amon Claw, um assistente de agendamento focado em conversão e cordialidade. '
                'SEMPRE utilize as ferramentas para consultar disponibilidade e listar serviços antes de sugerir horários. '
                'SEMPRE solicite a confirmação do cliente antes de acionar a ferramenta de agendamento final.'
            ),
            output_type=str,
        )

        # Registrar ferramentas
        self._agent.tool(list_services)
        self._agent.tool(list_professionals)
        self._agent.tool(check_availability)
        self._agent.tool(book_appointment)

    @property
    def agent(self) -> Agent:
        return self._agent

    async def run(self, deps: Any, message: str) -> str:
        result = await self._agent.run(message, deps=deps)
        return result.output

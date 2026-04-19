import pytest
from pydantic_ai.models.test import TestModel
from amon_claw.infrastructure.llm.agents.scheduling_agent import SchedulingAgent
from pydantic_ai import Agent

def test_scheduling_agent_instantiation():
    agent = SchedulingAgent()
    assert isinstance(agent.agent, Agent)
    # Na versão atual ele normaliza o nome do modelo
    assert "gemini-1.5-flash" in agent.agent.model.model_name

@pytest.mark.asyncio
async def test_scheduling_agent_run():
    agent = SchedulingAgent()
    # Usamos TestModel para evitar chamadas reais
    agent._agent.model = TestModel()
    
    # O TestModel por padrão retorna o input se for string e o output_type for str
    # Ou uma string fixa dependendo da configuração. 
    # Para o teste ser resiliente, apenas verificamos se retorna uma string.
    result = await agent.run(None, "Quero marcar um horário")
    assert isinstance(result, str)
    assert len(result) > 0

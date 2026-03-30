from typing import cast

from langchain_core.messages import AIMessage, HumanMessage
from pydantic_ai.agent import AgentRunResult

from amon_claw.agents.calculator_agent import agent_factory
from amon_claw.models.response import MathResult
from amon_claw.state import AmonClawState


def input_node(state: AmonClawState):
    user_message: str = input('USER: ')
    human_message = HumanMessage(user_message)
    return {'messages': [human_message]}


def call_llm_node(state: AmonClawState):
    agent = agent_factory()
    result: AgentRunResult[str] = agent.run_sync(user_prompt=str(state['messages']))
    message = cast(MathResult, result.output)
    ai_message = AIMessage(message.explication)

    print(f'AI: {message.explication}. {message.result}')
    return {
        'user_id': 'amon',
        'messages': [ai_message],
        'ai_calls': state['ai_calls'] + 1,
        'last_result': message.result,
    }

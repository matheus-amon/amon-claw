import uuid
from typing import Literal, cast

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, MessagesState, StateGraph
from pydantic import EmailStr
from pydantic_ai.run import AgentRunResult

from amon_claw.agents.calculator_agent import agent_factory
from amon_claw.models.response import MathResult


class AmonClawState(MessagesState):
    thread_id: uuid.UUID | None
    user_id: str | int | EmailStr | None

    ai_calls: int
    last_result: float


def input_node(state: AmonClawState):
    user_message: str = input('USER: ')
    human_message = HumanMessage(user_message)
    return {'messages': [human_message]}


def call_llm_node(state: AmonClawState):
    agent = agent_factory()
    last_message = str(state['messages'][-1].content)
    result: AgentRunResult[str] = agent.run_sync(user_prompt=last_message)
    message = cast(MathResult, result.output)
    ai_message = AIMessage(message.explication)

    print(f'AI: {message.explication}: {message.result}')
    return {
        'user_id': 'amon',
        'messages': [ai_message],
        'ai_calls': state['ai_calls'] + 1,
        'last_result': message.result,
    }


def should_continue(state: AmonClawState) -> Literal['END', 'call_llm_node']:
    last_message = state['messages'][-1].content

    if last_message == 'sair':
        return 'END'

    return 'call_llm_node'


graph = StateGraph(AmonClawState)  # ty: ignore[invalid-argument-type]

graph.add_node(input_node)
graph.add_node(call_llm_node)

graph.add_edge(START, 'input_node')
graph.add_edge('call_llm_node', 'input_node')

graph.add_conditional_edges(
    'input_node', should_continue, {'END': END, 'call_llm_node': 'call_llm_node'}
)


if __name__ == '__main__':
    with SqliteSaver.from_conn_string('amonclaw_checkpoints.sqlite') as checkpointer:
        app = graph.compile(checkpointer=checkpointer)
        app.invoke(
            {
                'thread_id': None,
                'user_id': 'amon',
                'messages': [],
                'ai_calls': 0,
                'last_result': 0.0,
            },
            config={'configurable': {'thread_id': uuid.uuid8()}},
        )
        with open('grafo.png', 'wb') as f:
            f.write(app.get_graph().draw_mermaid_png())

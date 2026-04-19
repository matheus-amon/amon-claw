import uuid
from typing import Literal

from langgraph.graph import END, START, StateGraph
from amon_claw.infrastructure.database.redis.client import get_redis_saver # Novo import para RedisSaver

from amon_claw.application.use_cases.nodes import call_llm_node, input_node
from amon_claw.application.use_cases.state import AmonClawState


def build_graph() -> StateGraph:
    graph = StateGraph(AmonClawState)  # ty: ignore[invalid-argument-type]

    graph.add_node(input_node)
    graph.add_node(call_llm_node)

    graph.add_edge(START, 'input_node')
    graph.add_edge('call_llm_node', 'input_node')

    def should_continue(state: AmonClawState) -> Literal['END', 'call_llm_node']:
        last_message = state['messages'][-1].content

        if last_message == 'sair':
            return 'END'

        return 'call_llm_node'

    graph.add_conditional_edges(
        'input_node', should_continue, {'END': END, 'call_llm_node': 'call_llm_node'}
    )

    return graph


def main():
    graph = build_graph()

    checkpointer = get_redis_saver() # Usar RedisSaver
    app = graph.compile(checkpointer=checkpointer)
    app.invoke(
        {
            'thread_id': str(uuid.uuid8()), # Fornecer um UUID como string para thread_id
            'user_id': 'amon',
            'messages': [],
            'ai_calls': 0,
            'last_result': 0.0,
        },
        config={'configurable': {'thread_id': str(uuid.uuid8())}},
    )


if __name__ == '__main__':
    main()

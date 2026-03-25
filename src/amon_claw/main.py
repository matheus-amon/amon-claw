import operator
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langgraph.graph import END, START, StateGraph

from amon_claw.agents.calculator_agent import MathResult, agent_factory


class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    ai_calls: int
    last_result: float


def input_node(state: MessagesState):
    user_message = input('USER: ')
    human_message = HumanMessage(user_message)
    return {'messages': [human_message]}


def call_llm_node(state: MessagesState):
    agent = agent_factory()
    last_message = str(state['messages'][-1].content)
    result = agent.run_sync(last_message)
    message = result.output
    ai_message = AIMessage(message.explication)

    print(f'AI: {message}')
    return {
        'messages': [ai_message],
        'ai_calls': state['ai_calls'] + 1,
        'last_result': message.result,
    }


def should_continue(state: MessagesState):
    last_message = str(state['messages'][-1].content)

    if last_message == 'sair':
        return 'END'

    return 'call_llm_node'


graph = StateGraph(MessagesState)

graph.add_node(input_node)
graph.add_node(call_llm_node)

graph.add_edge(START, 'input_node')
graph.add_edge('call_llm_node', 'input_node')

graph.add_conditional_edges(
    'input_node', should_continue, {'END': END, 'call_llm_node': 'call_llm_node'}
)

app = graph.compile()

if __name__ == '__main__':
    app.invoke({'messages': [], 'ai_calls': 0, 'last_result': 0.0})
    with open('grafo.png', 'wb') as f:
        f.write(app.get_graph().draw_mermaid_png())

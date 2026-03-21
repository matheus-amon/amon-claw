import operator
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langgraph.graph import END, START, StateGraph


class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    ai_calls: int


def input_node(state: MessagesState):
    user_message = input("USER: ")
    human_message = HumanMessage(user_message)
    return {"messages": [human_message]}


def calculator_node(state: MessagesState):
    last_message = state["messages"][-1]
    result = eval(str(last_message.content))
    message = f"Aqui está o resultado: {result}"
    ai_message = AIMessage(message)

    print(f"AI: {message}")
    return {"messages": [ai_message], "ai_calls": state["ai_calls"] + 1}


def should_continue(state: MessagesState):
    last_message = str(state["messages"][-1].content)

    if last_message == "sair":
        return "END"

    return "calculator_node"


graph = StateGraph(MessagesState)

graph.add_node("input_node", input_node)
graph.add_node("calculator_node", calculator_node)

graph.add_edge(START, "input_node")
graph.add_edge("calculator_node", "input_node")

graph.add_conditional_edges(
    "input_node", should_continue, {"END": END, "calculator_node": "calculator_node"}
)

app = graph.compile()

if __name__ == "__main__":
    app.invoke({"messages": [], "ai_calls": 0})
    with open("grafo.png", "wb") as f:
        f.write(app.get_graph().draw_mermaid_png())

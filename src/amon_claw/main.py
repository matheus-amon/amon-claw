import uuid
import operator
from typing import Literal, TypedDict, Annotated, List
import asyncio

from langgraph.graph import END, START, StateGraph
from amon_claw.infrastructure.database.redis.client import get_redis_saver
from amon_claw.application.use_cases.appointment_persistence import save_appointment_to_db # Novo import
from amon_claw.application.use_cases.nodes import call_llm_node, input_node # Existing imports
# Re-defining AmonClawState for example purposes to include appointment_details
# In a real scenario, this would be updated in amon_claw/application/use_cases/state.py
# and imported.
class AmonClawState(TypedDict):
    """
    Representa o estado do agente AmonClaw.

    Atributos:
        messages: Uma lista de mensagens no histórico da conversa, acumuladas.
        ai_calls: Contador de chamadas para a LLM.
        last_result: O último resultado numérico de alguma operação.
        thread_id: ID da thread para checkpointing.
        user_id: ID do usuário.
        appointment_details: Detalhes do agendamento a ser persistido.
    """
    messages: Annotated[List[str], operator.add]
    ai_calls: int
    last_result: float
    thread_id: str
    user_id: str
    appointment_details: dict # Novo campo para detalhes do agendamento

# Define um nó que simula a decisão de salvar no MongoDB
async def save_to_mongo_node(state: AmonClawState):
    print(f"Executando save_to_mongo_node. Estado: {state}") # Usar print para exemplo
    if state.get("appointment_details"):
        result = await save_appointment_to_db(state["appointment_details"])
        print(f"Resultado da persistência no MongoDB: {result}") # Usar print para exemplo
        return {"messages": [f"Agendamento persistido. Status: {result.get('status')}"]}
    return {"messages": ["Nenhum detalhe de agendamento para persistir."]}

def build_graph() -> StateGraph:
    graph = StateGraph(AmonClawState)  # ty: ignore[invalid-argument-type]

    # Redefinir agent_node para incluir lógica de agendamento para o exemplo
    def agent_node(state: AmonClawState):
        print(f"Executando agent_node com estado: {state}") # Usar print para exemplo
        current_messages = state.get("messages", [])
        # Simula o agente identificando um agendamento e adicionando detalhes ao estado
        if any("marcar corte" in msg.lower() for msg in current_messages):
            print("Agente identificou intenção de marcar corte.") # Usar print para exemplo
            appointment_details = {
                "service": "Corte de Cabelo",
                "date": "2026-04-25",
                "time": "10:00",
                "priority": True, # A informação temporária de prioridade
                "client_name": state.get("user_id", "Unknown")
            }
            return {"messages": ["Ok, vamos marcar seu corte!"], "appointment_details": appointment_details}
        return {"messages": ["Agent response!"]} # Fallback se não for agendamento

    # Usar os nós existentes ou novos
    # graph.add_node(input_node) # Removido para simplificar o exemplo conforme plano
    # graph.add_node(call_llm_node) # Removido para simplificar o exemplo conforme plano

    graph.add_node("agent", agent_node) # Adiciona o nó do agente redefinido
    graph.add_node("persist_appointment", save_to_mongo_node) # Adiciona o novo nó de persistência

    graph.set_entry_point("agent")
    graph.add_edge("agent", "persist_appointment") # Agente -> Persistir
    graph.add_edge("persist_appointment", END) # Persistir -> Fim

    return graph


async def run_app_example():
    graph = build_graph() # Obter o grafo
    checkpointer = get_redis_saver() # Obter o RedisSaver
    app = graph.compile(checkpointer=checkpointer)

    # Simula uma conversa onde um agendamento é marcado e persistido
    # Usar um thread_id configurável para a persistência
    thread_id_val = str(uuid.uuid8())
    config = {"configurable": {"thread_id": thread_id_val}}

    initial_state = {
        'thread_id': thread_id_val,
        'user_id': 'amon_user_123',
        'messages': ["Quero marcar um corte de cabelo com prioridade!"],
        'ai_calls': 0,
        'last_result': 0.0,
        'appointment_details': {} # Inicializar o campo
    }
    response = await app.ainvoke(initial_state, config=config)
    print("Primeira invocação (agendamento):") # Usar print para exemplo
    print(response) # Usar print para exemplo

    # Invocação subsequente com o mesmo thread_id deve retomar o estado
    inputs_2 = {
        'thread_id': thread_id_val,
        'user_id': 'amon_user_123',
        'messages': ["Obrigado!"],
        'ai_calls': 0,
        'last_result': 0.0,
        'appointment_details': {} # Manter o campo
    }
    response_2 = await app.ainvoke(inputs_2, config=config)
    print("Segunda invocação (mesmo thread_id):") # Usar print para exemplo
    print(response_2) # Usar print para exemplo


if __name__ == "__main__":
    asyncio.run(run_app_example())

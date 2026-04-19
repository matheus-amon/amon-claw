# src/amon_claw/application/use_cases/state.py

from typing import List, TypedDict, Annotated
import operator

class AmonClawState(TypedDict):
    """
    Representa o estado do agente AmonClaw.

    Atributos:
        messages: Uma lista de mensagens no histórico da conversa, acumuladas.
        ai_calls: Contador de chamadas para a LLM.
        last_result: O último resultado numérico de alguma operação.
        thread_id: ID da thread para checkpointing.
        user_id: ID do usuário.
    """
    messages: Annotated[List[str], operator.add]
    ai_calls: int
    last_result: float
    thread_id: str
    user_id: str

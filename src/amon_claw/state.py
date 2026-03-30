import uuid

from langgraph.graph import MessagesState
from pydantic import EmailStr


class AmonClawState(MessagesState):
    thread_id: uuid.UUID | None
    user_id: str | int | EmailStr | None

    ai_calls: int
    last_result: float

from typing import Annotated, Any, TypedDict
from uuid import UUID

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class SDRState(TypedDict):
    """
    State for the SDR LangGraph assistant.
    """

    tenant_id: UUID
    customer_id: UUID
    messages: Annotated[list[BaseMessage], add_messages]
    extracted_info: dict[str, Any]
    next_node: str | None

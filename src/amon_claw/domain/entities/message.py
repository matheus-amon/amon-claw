from datetime import UTC, datetime
from enum import StrEnum, auto


class MessageRole(StrEnum):
    USER = auto()
    AI = auto()
    SYSTEM = auto()
    TOOL = auto()


class Message:
    def __init__(self, content: str, role: MessageRole):
        self.content = content
        self.role = role
        self.created_at = datetime.now(UTC)

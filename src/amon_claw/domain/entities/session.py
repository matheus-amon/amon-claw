from datetime import UTC, datetime
from enum import StrEnum, auto
from uuid import uuid4

from amon_claw.domain.entities.message import Message
from amon_claw.domain.exceptions import SessionDeletedError


class SessionEvents(StrEnum):
    ADD_MESSAGE = auto()
    CREATED = auto()
    RENAMED = auto()
    DELETED = auto()
    PINNED = auto()
    UNPINNED = auto()


class Session:
    def __init__(
        self,
        id: str | None = None,
        name: str | None = None,
        messages: list[Message] | None = None,
        is_pin: bool = False,
        is_deleted: bool = False,
        events: list[SessionEvents] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        self.id = id or str(uuid4())
        self.messages = messages or []
        self.name = name or 'New Chat'
        self.is_pin = is_pin
        self.is_deleted = is_deleted
        self._events = events if events is not None else [SessionEvents.CREATED]
        self.created_at = created_at or datetime.now(UTC)
        self.updated_at = updated_at or datetime.now(UTC)

    def add_message(self, message: Message):
        if self.is_deleted:
            raise SessionDeletedError('Cannot add message to a deleted session')

        self.messages.append(message)
        self._update(SessionEvents.ADD_MESSAGE)

    def get_last_message(self) -> Message | None:
        return self.messages[-1] if self.messages else None

    def get_history(self, limit: int | None = None) -> list[Message]:
        return self.messages[-limit:] if limit else self.messages

    def delete(self):
        if self.is_deleted:
            return

        self.is_deleted = True
        self._update(SessionEvents.DELETED)

    def pin(self):
        if not self.unpin:
            return

        self.is_pin = True
        self._update(SessionEvents.PINNED)

    def unpin(self):
        if not self.unpin:
            return

        self.is_pin = False
        self._update(SessionEvents.UNPINNED)

    def rename(self, new_name: str):
        self.name = new_name

        self._update(SessionEvents.RENAMED)

    def _update(self, event: SessionEvents) -> None:
        self.updated_at = datetime.now(UTC)
        self._events.append(event)

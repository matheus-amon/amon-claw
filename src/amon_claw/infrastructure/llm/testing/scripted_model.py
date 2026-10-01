"""A scripted BaseChatModel for tests.

langchain_core ships two fakes and neither works for an agent test:
`GenericFakeChatModel` rejects a plain list (it wants an Iterator) and neither
one implements `bind_tools`, which `create_react_agent` calls unconditionally.

This is a real `BaseChatModel` so it satisfies the whole interface, and it
replays a fixed script so a multi-agent graph can be driven through a handoff
without an API key. That is the only way to test routing: with a live model the
test either costs money or asserts nothing.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult


class ScriptedChatModel(BaseChatModel):
    """Replays `script` in order, then answers with `fallback`.

    `bind_tools` returns `self` rather than raising, because the real models
    return a bound copy and anything checking identity of the return value
    would otherwise break.
    """

    script: list[AIMessage] = []
    fallback: str = 'done'

    @property
    def _llm_type(self) -> str:
        return 'scripted'

    @property
    def _identifying_params(self) -> dict[str, Any]:
        return {'remaining': len(self.script)}

    def bind_tools(self, tools: Sequence[Any], **kwargs: Any) -> ScriptedChatModel:
        return self

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        # Mutating `self.script` rather than a copy: the same model instance is
        # reused across the steps of one graph run, and the script has to be
        # consumed in order.
        message = self.script.pop(0) if self.script else AIMessage(content=self.fallback)
        return ChatResult(generations=[ChatGeneration(message=message)])

    def remaining(self) -> int:
        """How many scripted messages are left. Used by tests to assert the script was fully consumed."""
        return len(self.script)

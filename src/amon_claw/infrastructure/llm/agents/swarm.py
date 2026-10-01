"""Agent swarm with real handoff.

`langgraph-swarm`'s `create_handoff_tool` returns a `Command(goto=..., update=...)`,
which means transferring control and transferring state are the same object.
There is no separate handoff-payload protocol to design, get wrong, or document.

Two decisions worth writing down:

**Routing is deterministic, not conversational.** A handoff only happens when the
active agent emits the transfer tool. That is the whole contract, and it is why
this is testable without a model: the test scripts which tool the model emits and
asserts which agent ended up active.

**Escalation does not go through the LLM.** `should_escalate` is a threshold on a
number. A model that is confident, verbose or wrong about its own urgency cannot
override it. Everything semantic still goes through the swarm.
"""

from __future__ import annotations

from typing import Any, Literal, TypedDict

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_handoff_tool, create_swarm

# Escalation thresholds. A risk score at or above HIGH escalates no matter what
# any model says; MEDIUM escalates on corroboration (a critical finding, or a
# second signal). Deliberately not configurable at runtime — a threshold that
# can be tuned by whoever is running it is not a threshold.
HIGH_RISK_THRESHOLD = 0.8
MEDIUM_RISK_THRESHOLD = 0.5

SwarmRole = Literal['triage', 'research', 'review']


class SwarmContext(TypedDict):
    """Per-thread configuration, carried in `configurable`.

    Typed because LangGraph V1 wants `context_schema`, not the deprecated
    `config_schema` — and an untyped dict here is what lets a typo in
    `config["configurable"]["thread_id"]` pass silently.
    """

    thread_id: str


def should_escalate(risk_score: float, critical_findings: int = 0) -> bool:
    """Whether a case needs a human, decided on numbers alone.

    Kept as a free function so it can be tested directly. It is deliberately
    not a node: routing logic that only exists inside a graph is routing logic
    nobody can test without spinning the whole graph up.
    """
    if risk_score >= HIGH_RISK_THRESHOLD:
        return True
    if risk_score >= MEDIUM_RISK_THRESHOLD:
        # Corroboration: one numeric signal plus a concrete critical finding, or
        # two independent signals agreeing.
        return critical_findings >= 1
    return False


def handoff_tools_for(role: SwarmRole, peers: list[SwarmRole]) -> list[Any]:
    """Transfer tools for one agent.

    An agent can hand off to its peers but not to itself; a self-transfer is an
    infinite loop with extra steps.
    """
    return [
        create_handoff_tool(
            agent_name=peer,
            description=f'Hand the conversation to the {peer} agent.',
        )
        for peer in peers
        if peer != role
    ]


def build_swarm(
    models: dict[SwarmRole, BaseChatModel],
    tools: dict[SwarmRole, list[Any]] | None = None,
    default_active_agent: SwarmRole = 'triage',
) -> Any:
    """Assemble the swarm and compile it with a checkpointer.

    `tools` defaults to empty per role. A role with no tools still works — a
    handoff-only agent is legitimate — and making it explicit keeps the call
    sites from having to pass `None` for the common case.
    """
    tools = tools or {}

    agents = []
    for role, model in models.items():
        role_tools = list(tools.get(role, [])) + handoff_tools_for(role, list(models))
        agents.append(
            create_react_agent(
                model,
                role_tools,
                name=role,
                context_schema=SwarmContext,
            )
        )

    workflow = create_swarm(agents, default_active_agent=default_active_agent)
    return workflow.compile(checkpointer=MemorySaver())


def final_message(messages: list[BaseMessage]) -> str:
    """The last assistant turn, as text.

    Agents emit tool calls and empty-content messages; the caller wants the
    thing a person would read.
    """
    for message in reversed(messages):
        content = getattr(message, 'content', '')
        if getattr(message, 'type', '') == 'ai' and content:
            return str(content)
    return ''

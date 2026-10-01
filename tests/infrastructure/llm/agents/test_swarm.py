"""The swarm: handoff routing and threshold escalation.

Every test here runs with a scripted model and no API key. That is the whole
point of the design — a multi-agent routing test that needs a live model either
costs money or asserts nothing.
"""

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from amon_claw.infrastructure.llm.agents.swarm import (
    HIGH_RISK_THRESHOLD,
    MEDIUM_RISK_THRESHOLD,
    build_swarm,
    final_message,
    handoff_tools_for,
    should_escalate,
)
from amon_claw.infrastructure.llm.testing.scripted_model import ScriptedChatModel


def echo_tool() -> str:
    """A tool with a docstring, which langchain_core requires."""
    return 'ok'


def run(swarm, message: str = 'hello', thread_id: str = 't1') -> dict:
    return swarm.invoke(
        {'messages': [HumanMessage(content=message)]},
        config={'configurable': {'thread_id': thread_id}},
    )


class TestHandoffRouting:
    def test_a_handoff_moves_control_to_the_named_agent(self):
        # The regression this file exists for. Before there was a swarm, routing
        # was a keyword match on the user's text.
        swarm = build_swarm(
            models={
                'triage': ScriptedChatModel(
                    script=[
                        AIMessage(
                            content='',
                            tool_calls=[
                                {'name': 'transfer_to_research', 'args': {}, 'id': 'h1'}
                            ],
                        )
                    ]
                ),
                'research': ScriptedChatModel(
                    script=[AIMessage(content='research done')]
                ),
            }
        )

        result = run(swarm)

        assert result['active_agent'] == 'research'

    def test_the_receiving_agent_is_the_one_that_answers(self):
        swarm = build_swarm(
            models={
                'triage': ScriptedChatModel(
                    script=[
                        AIMessage(
                            content='',
                            tool_calls=[
                                {'name': 'transfer_to_review', 'args': {}, 'id': 'h1'}
                            ],
                        )
                    ]
                ),
                'review': ScriptedChatModel(script=[AIMessage(content='reviewed')]),
            }
        )

        result = run(swarm)

        assert final_message(result['messages']) == 'reviewed'

    def test_without_a_handoff_the_default_agent_answers_and_reports_none(self):
        # `active_agent` is absent from the returned state rather than set to
        # the default. That is the library's behaviour, and the assertion pins
        # it: code that reads `state["active_agent"]` unconditionally would raise
        # KeyError on every turn that does not hand off, which is most turns.
        # Read it with .get() and treat None as "still the entry agent".
        swarm = build_swarm(
            models={
                'triage': ScriptedChatModel(script=[AIMessage(content='handled here')]),
                'research': ScriptedChatModel(
                    script=[AIMessage(content='never reached')]
                ),
            }
        )

        result = run(swarm)

        assert result.get('active_agent') is None
        assert final_message(result['messages']) == 'handled here'
        assert 'never reached' not in [str(m.content) for m in result['messages']]

    def test_an_agent_cannot_hand_off_to_itself(self):
        # A self-transfer is an infinite loop with extra steps.
        tools = handoff_tools_for('triage', ['triage', 'research'])

        names = [tool.name for tool in tools]

        assert 'transfer_to_research' in names
        assert 'transfer_to_triage' not in names

    def test_state_is_carried_across_the_handoff(self):
        # The message history is the handoff payload, because create_handoff_tool
        # returns Command(update={...}). Losing it would be the classic bug.
        swarm = build_swarm(
            models={
                'triage': ScriptedChatModel(
                    script=[
                        AIMessage(
                            content='',
                            tool_calls=[
                                {'name': 'transfer_to_research', 'args': {}, 'id': 'h1'}
                            ],
                        )
                    ]
                ),
                'research': ScriptedChatModel(script=[AIMessage(content='done')]),
            }
        )

        result = run(swarm, message='the original question')

        assert result['messages'][0].content == 'the original question'

    def test_the_script_is_fully_consumed(self):
        # Guards against a test that passes because the fallback fired instead of
        # the handoff it was supposed to exercise.
        triage_model = ScriptedChatModel(
            script=[
                AIMessage(
                    content='',
                    tool_calls=[{'name': 'transfer_to_research', 'args': {}, 'id': 'h1'}],
                )
            ]
        )
        swarm = build_swarm(
            models={
                'triage': triage_model,
                'research': ScriptedChatModel(script=[AIMessage(content='x')]),
            }
        )

        run(swarm)

        assert triage_model.remaining() == 0


class TestShouldEscalate:
    def test_a_high_risk_score_escalates_on_its_own(self):
        assert should_escalate(HIGH_RISK_THRESHOLD) is True

    def test_high_risk_escalates_even_with_no_corroboration(self):
        assert should_escalate(0.95, critical_findings=0) is True

    def test_medium_risk_needs_a_critical_finding(self):
        assert should_escalate(MEDIUM_RISK_THRESHOLD, critical_findings=0) is False
        assert should_escalate(MEDIUM_RISK_THRESHOLD, critical_findings=1) is True

    def test_low_risk_does_not_escalate_even_with_findings(self):
        assert should_escalate(0.49, critical_findings=5) is False

    def test_the_boundary_belongs_to_escalation(self):
        # Off-by-one here decides whether a case reaches a person.
        assert should_escalate(HIGH_RISK_THRESHOLD - 0.001, critical_findings=0) is False
        assert should_escalate(HIGH_RISK_THRESHOLD, critical_findings=0) is True

    @pytest.mark.parametrize('score', [0.0, 0.25, 0.49, 0.5, 0.79, 0.8, 1.0])
    def test_it_always_returns_a_bool(self, score: float):
        assert isinstance(should_escalate(score), bool)


class TestFinalMessage:
    def test_returns_the_last_non_empty_ai_message(self):
        messages = [
            HumanMessage(content='question'),
            AIMessage(content='first answer'),
            AIMessage(content=''),
            AIMessage(content='second answer'),
        ]

        assert final_message(messages) == 'second answer'

    def test_returns_empty_when_there_is_no_ai_message(self):
        assert final_message([HumanMessage(content='only a question')]) == ''

    def test_ignores_tool_messages(self):
        messages = [
            AIMessage(content='the answer'),
            AIMessage(content='', tool_calls=[{'name': 't', 'args': {}, 'id': '1'}]),
        ]

        assert final_message(messages) == 'the answer'

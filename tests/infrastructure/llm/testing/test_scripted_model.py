"""The scripted model is the thing every agent test depends on.

If it silently returned the wrong thing, the agent tests would still pass while
testing nothing. So it gets its own tests.
"""

from langchain_core.messages import AIMessage, HumanMessage

from amon_claw.infrastructure.llm.testing.scripted_model import ScriptedChatModel


def test_returns_the_scripted_message():
    model = ScriptedChatModel(script=[AIMessage(content='first')])

    result = model.invoke([HumanMessage(content='hi')])

    assert result.content == 'first'


def test_consumes_the_script_in_order():
    model = ScriptedChatModel(
        script=[AIMessage(content='first'), AIMessage(content='second')]
    )

    first = model.invoke([HumanMessage(content='1')])
    second = model.invoke([HumanMessage(content='2')])

    assert first.content == 'first'
    assert second.content == 'second'


def test_falls_back_once_the_script_is_exhausted():
    model = ScriptedChatModel(script=[], fallback='fallback answer')

    result = model.invoke([HumanMessage(content='hi')])

    assert result.content == 'fallback answer'


def test_bind_tools_returns_self_because_create_react_agent_calls_it():
    # create_react_agent calls model.bind_tools(...) unconditionally. The
    # langchain_core fakes raise NotImplementedError here, which is why this
    # class exists at all.
    model = ScriptedChatModel(script=[])

    assert model.bind_tools([]) is model


def test_reports_remaining_script_so_a_test_can_assert_it_ran_out():
    model = ScriptedChatModel(script=[AIMessage(content='a'), AIMessage(content='b')])

    assert model.remaining() == 2

    model.invoke([HumanMessage(content='1')])
    assert model.remaining() == 1

    model.invoke([HumanMessage(content='2')])
    assert model.remaining() == 0


def test_returns_tool_calls_when_the_script_has_them():
    model = ScriptedChatModel(
        script=[
            AIMessage(
                content='',
                tool_calls=[{'name': 'some_tool', 'args': {'x': 1}, 'id': 'call-1'}],
            )
        ]
    )

    result = model.invoke([HumanMessage(content='call it')])

    assert result.tool_calls[0]['name'] == 'some_tool'
    assert result.tool_calls[0]['args'] == {'x': 1}


def test_llm_type_is_distinct_from_a_real_provider():
    # Keeps scripted runs from being mistaken for a real provider in logs.
    assert ScriptedChatModel(script=[])._llm_type == 'scripted'

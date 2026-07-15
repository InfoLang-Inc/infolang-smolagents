"""Integration tests that plug the tools into real SmolAgents agents.

A scripted stub ``Model`` drives a ``ToolCallingAgent`` end to end (no LLM), so
the full framework path is exercised: tool registration/validation, tool-call
dispatch, and tool execution against the mocked InfoLang HTTP layer.
"""

from __future__ import annotations

from typing import Any

import respx
from smolagents import CodeAgent, ToolCallingAgent
from smolagents.models import (
    ChatMessage,
    ChatMessageToolCall,
    ChatMessageToolCallFunction,
    MessageRole,
    Model,
)

from infolang_smolagents import infolang_tools
from tests.conftest import BASE_URL, FakeRuntime


class ScriptedModel(Model):
    """A ``Model`` that returns pre-scripted assistant messages in order."""

    def __init__(self, messages: list[ChatMessage]) -> None:
        super().__init__(model_id="scripted")
        self._messages = messages
        self._index = 0

    def generate(self, messages: Any, **kwargs: Any) -> ChatMessage:
        message = self._messages[self._index]
        self._index += 1
        return message


def _tool_call(name: str, arguments: dict[str, Any], call_id: str) -> ChatMessage:
    return ChatMessage(
        role=MessageRole.ASSISTANT,
        tool_calls=[
            ChatMessageToolCall(
                id=call_id,
                type="function",
                function=ChatMessageToolCallFunction(name=name, arguments=arguments),
            )
        ],
    )


def test_tools_register_in_tool_calling_agent() -> None:
    tools = infolang_tools(api_key="il_test", base_url=BASE_URL, namespace="ns")
    agent = ToolCallingAgent(tools=tools, model=ScriptedModel([]))
    assert {"recall", "investigate", "remember", "forget"} <= set(agent.tools)


def test_tools_register_in_code_agent() -> None:
    tools = infolang_tools(api_key="il_test", base_url=BASE_URL, namespace="ns")
    agent = CodeAgent(tools=tools, model=ScriptedModel([]))
    assert {"recall", "investigate", "remember", "forget"} <= set(agent.tools)


@respx.mock
def test_tool_calling_agent_runs_recall(runtime: FakeRuntime) -> None:
    runtime.register(respx)
    runtime.seed("test-ns", "the user likes teal")
    model = ScriptedModel(
        [
            _tool_call("recall", {"query": "teal"}, "call-1"),
            _tool_call(
                "final_answer", {"answer": "The user likes teal."}, "call-2"
            ),
        ]
    )
    agent = ToolCallingAgent(
        tools=infolang_tools(api_key="il_test", base_url=BASE_URL, namespace="test-ns"),
        model=model,
    )
    result = agent.run("What does the user like?")
    assert "teal" in str(result)
    assert runtime.recall_calls == 1


@respx.mock
def test_tool_calling_agent_runs_remember(runtime: FakeRuntime) -> None:
    runtime.register(respx)
    model = ScriptedModel(
        [
            _tool_call(
                "remember",
                {"text": "the user likes teal", "tags": "pref"},
                "call-1",
            ),
            _tool_call("final_answer", {"answer": "Saved."}, "call-2"),
        ]
    )
    agent = ToolCallingAgent(
        tools=infolang_tools(api_key="il_test", base_url=BASE_URL, namespace="test-ns"),
        model=model,
    )
    agent.run("Remember that I like teal.")
    assert runtime.remember_calls == 1

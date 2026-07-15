from __future__ import annotations

import httpx
import pytest
import respx
from infolang.errors import NotFoundError

from infolang_smolagents import (
    InfoLangForgetTool,
    InfoLangInvestigateTool,
    InfoLangRecallTool,
    InfoLangRememberTool,
)
from tests.conftest import BASE_URL, FakeRuntime, make_client


def test_recall_tool_attributes() -> None:
    tool = InfoLangRecallTool(api_key="il_test", base_url=BASE_URL, namespace="ns")
    assert tool.name == "recall"
    assert tool.output_type == "string"
    assert set(tool.inputs) == {"query", "top_k"}
    assert tool.inputs["top_k"]["nullable"] is True


def test_all_tools_pass_hub_serialization() -> None:
    for cls in (
        InfoLangRecallTool,
        InfoLangInvestigateTool,
        InfoLangRememberTool,
        InfoLangForgetTool,
    ):
        tool = cls(api_key="il_test", base_url=BASE_URL, namespace="ns")
        assert tool.to_dict()["name"] == tool.name


def test_client_and_credentials_conflict_raises() -> None:
    client = make_client("ns")
    try:
        with pytest.raises(ValueError, match="not both"):
            InfoLangRecallTool(client=client, api_key="il_test")
    finally:
        client.close()


@respx.mock
def test_recall_returns_formatted_hits(runtime: FakeRuntime) -> None:
    runtime.register(respx)
    runtime.seed("test-ns", "the user loves teal")
    tool = InfoLangRecallTool(api_key="il_test", base_url=BASE_URL, namespace="test-ns")
    out = tool.forward("teal")
    assert "the user loves teal" in out
    assert runtime.recall_calls == 1
    assert runtime.last_recall_body is not None
    assert runtime.last_recall_body["namespace"] == "test-ns"


@respx.mock
def test_recall_default_top_k_is_five(runtime: FakeRuntime) -> None:
    runtime.register(respx)
    tool = InfoLangRecallTool(api_key="il_test", base_url=BASE_URL, namespace="test-ns")
    tool.forward("anything")
    assert runtime.last_recall_body is not None
    assert runtime.last_recall_body["top_k"] == 5


@respx.mock
def test_recall_explicit_top_k(runtime: FakeRuntime) -> None:
    runtime.register(respx)
    for i in range(3):
        runtime.seed("test-ns", f"memory {i}")
    tool = InfoLangRecallTool(api_key="il_test", base_url=BASE_URL, namespace="test-ns")
    tool.forward("memory", top_k=1)
    assert runtime.last_recall_body is not None
    assert runtime.last_recall_body["top_k"] == 1


@respx.mock
def test_recall_empty_returns_no_hits_message(runtime: FakeRuntime) -> None:
    runtime.register(respx)
    tool = InfoLangRecallTool(api_key="il_test", base_url=BASE_URL, namespace="empty")
    assert tool.forward("x") == "No relevant memories found."


@respx.mock
def test_investigate_uses_namespace_hint_and_default_top_k(
    runtime: FakeRuntime,
) -> None:
    runtime.register(respx)
    runtime.seed("test-ns", "how auth works")
    tool = InfoLangInvestigateTool(
        api_key="il_test", base_url=BASE_URL, namespace="test-ns"
    )
    out = tool.forward("auth")
    assert "how auth works" in out
    assert runtime.last_recall_body is not None
    assert runtime.last_recall_body["namespace"] == "test-ns"
    assert runtime.last_recall_body["top_k"] == 5


@respx.mock
def test_remember_returns_id_and_sends_metadata(runtime: FakeRuntime) -> None:
    runtime.register(respx)
    tool = InfoLangRememberTool(
        api_key="il_test", base_url=BASE_URL, namespace="test-ns"
    )
    memory_id = tool.forward("remember this", tags="fact,demo")
    assert memory_id.startswith("mem-")
    assert runtime.remember_calls == 1
    assert runtime.last_remember_body is not None
    assert runtime.last_remember_body["text"] == "remember this"
    assert runtime.last_remember_body["source"] == "smolagents"
    assert runtime.last_remember_body["tags"] == "fact,demo"
    assert runtime.last_remember_body["namespace"] == "test-ns"


@respx.mock
def test_remember_without_tags_omits_tags(runtime: FakeRuntime) -> None:
    runtime.register(respx)
    tool = InfoLangRememberTool(
        api_key="il_test", base_url=BASE_URL, namespace="test-ns"
    )
    tool.forward("no tags here")
    assert runtime.last_remember_body is not None
    assert "tags" not in runtime.last_remember_body


@respx.mock
def test_remember_empty_id_falls_back() -> None:
    respx.post(f"{BASE_URL}/v1/remember").mock(
        return_value=httpx.Response(200, json={})
    )
    tool = InfoLangRememberTool(
        api_key="il_test", base_url=BASE_URL, namespace="test-ns"
    )
    assert tool.forward("x") == "Stored memory."


@respx.mock
def test_forget_deletes_and_confirms(runtime: FakeRuntime) -> None:
    runtime.register(respx)
    mid = runtime.seed("test-ns", "delete me")
    tool = InfoLangForgetTool(api_key="il_test", base_url=BASE_URL, namespace="test-ns")
    out = tool.forward(mid)
    assert out == f"Deleted memory {mid}."
    assert runtime.forget_calls == 1
    assert mid not in runtime.store["test-ns"]


@respx.mock
def test_forget_missing_raises_not_found(runtime: FakeRuntime) -> None:
    runtime.register(respx)
    tool = InfoLangForgetTool(api_key="il_test", base_url=BASE_URL, namespace="test-ns")
    with pytest.raises(NotFoundError):
        tool.forward("does-not-exist")


@respx.mock
def test_recall_weak_flag_in_output(runtime: FakeRuntime) -> None:
    runtime.register(respx)
    runtime.seed("test-ns", "completely different content")
    tool = InfoLangRecallTool(api_key="il_test", base_url=BASE_URL, namespace="test-ns")
    out = tool.forward("zzz-no-match")
    assert "low confidence" in out


@respx.mock
def test_investigate_empty_returns_no_hits_message(runtime: FakeRuntime) -> None:
    runtime.register(respx)
    tool = InfoLangInvestigateTool(
        api_key="il_test", base_url=BASE_URL, namespace="empty"
    )
    assert tool.forward("x") == "No relevant memories found."


@respx.mock
def test_remember_then_recall_roundtrip(runtime: FakeRuntime) -> None:
    runtime.register(respx)
    remember = InfoLangRememberTool(
        api_key="il_test", base_url=BASE_URL, namespace="test-ns"
    )
    recall = InfoLangRecallTool(
        api_key="il_test", base_url=BASE_URL, namespace="test-ns"
    )
    remember.forward("the sky is teal today")
    assert "teal" in recall.forward("teal")


@respx.mock
def test_recall_none_namespace_omits_namespace(runtime: FakeRuntime) -> None:
    runtime.register(respx)
    tool = InfoLangRecallTool(api_key="il_test", base_url=BASE_URL, namespace=None)
    tool.forward("anything")
    assert runtime.last_recall_body is not None
    assert "namespace" not in runtime.last_recall_body


@respx.mock
def test_forget_removes_only_target(runtime: FakeRuntime) -> None:
    runtime.register(respx)
    keep = runtime.seed("test-ns", "keep me")
    drop = runtime.seed("test-ns", "drop me")
    tool = InfoLangForgetTool(api_key="il_test", base_url=BASE_URL, namespace="test-ns")
    tool.forward(drop)
    assert drop not in runtime.store["test-ns"]
    assert keep in runtime.store["test-ns"]


def test_all_tools_have_descriptions() -> None:
    for cls in (
        InfoLangRecallTool,
        InfoLangInvestigateTool,
        InfoLangRememberTool,
        InfoLangForgetTool,
    ):
        tool = cls(api_key="il_test", base_url=BASE_URL, namespace="ns")
        assert tool.description
        assert tool.output_type == "string"

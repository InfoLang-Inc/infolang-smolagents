from __future__ import annotations

import pytest

from infolang_smolagents import infolang_tools
from tests.conftest import BASE_URL, make_client


def _names(tools: list) -> set[str]:
    return {tool.name for tool in tools}


def test_default_builds_all_four_tools() -> None:
    tools = infolang_tools(api_key="il_test", base_url=BASE_URL, namespace="ns")
    assert _names(tools) == {"recall", "investigate", "remember", "forget"}


def test_tools_share_one_client() -> None:
    tools = infolang_tools(api_key="il_test", base_url=BASE_URL, namespace="ns")
    first = tools[0].client
    assert all(tool.client is first for tool in tools)


def test_include_selects_subset() -> None:
    tools = infolang_tools(
        api_key="il_test", base_url=BASE_URL, namespace="ns", include=["recall", "remember"]
    )
    assert _names(tools) == {"recall", "remember"}


def test_include_single() -> None:
    tools = infolang_tools(
        api_key="il_test", base_url=BASE_URL, namespace="ns", include=["forget"]
    )
    assert _names(tools) == {"forget"}


def test_include_unknown_raises() -> None:
    with pytest.raises(ValueError, match="Unknown InfoLang tool"):
        infolang_tools(api_key="il_test", base_url=BASE_URL, include=["recall", "nope"])


def test_include_empty_raises() -> None:
    with pytest.raises(ValueError, match="no tools"):
        infolang_tools(api_key="il_test", base_url=BASE_URL, include=[])


def test_client_and_credentials_conflict_raises() -> None:
    client = make_client("ns")
    try:
        with pytest.raises(ValueError, match="not both"):
            infolang_tools(client=client, api_key="il_test")
    finally:
        client.close()


def test_reuse_existing_client() -> None:
    client = make_client("ns")
    try:
        tools = infolang_tools(client=client, namespace="ns")
        assert all(tool.client is client for tool in tools)
    finally:
        client.close()


def test_namespace_propagates_to_tools() -> None:
    tools = infolang_tools(api_key="il_test", base_url=BASE_URL, namespace="crew-1")
    assert all(tool.namespace == "crew-1" for tool in tools)


def test_default_source_propagates_to_tools() -> None:
    tools = infolang_tools(api_key="il_test", base_url=BASE_URL, namespace="ns")
    assert all(tool.source == "smolagents" for tool in tools)


def test_custom_source_propagates_to_tools() -> None:
    tools = infolang_tools(
        api_key="il_test", base_url=BASE_URL, namespace="ns", source="my-app"
    )
    assert all(tool.source == "my-app" for tool in tools)

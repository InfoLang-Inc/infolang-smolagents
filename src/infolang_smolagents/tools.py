"""InfoLang memory ``Tool`` subclasses for SmolAgents.

Each tool wraps one InfoLang SDK call and follows the SmolAgents ``Tool``
contract (class-level ``name`` / ``description`` / ``inputs`` / ``output_type``
plus a ``forward`` whose parameters match ``inputs``). They work with both
``CodeAgent`` and ``ToolCallingAgent``.

Construct them individually::

    from infolang_smolagents import InfoLangRecallTool

    tool = InfoLangRecallTool(api_key="il_live_...", namespace="user-42")

or build the whole set (sharing one client) with :func:`infolang_tools`.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from infolang import InfoLang
from smolagents import Tool

DEFAULT_SOURCE = "smolagents"


def _build_client(
    *,
    client: InfoLang | None,
    api_key: str | None,
    dev_key: str | None,
    base_url: str | None,
    namespace: str | None,
    client_kwargs: dict[str, Any],
) -> InfoLang:
    if client is not None:
        if api_key or dev_key or base_url or client_kwargs:
            raise ValueError(
                "Pass either client= or api_key/dev_key/base_url, not both."
            )
        return client
    return InfoLang(
        api_key=api_key,
        dev_key=dev_key,
        base_url=base_url,
        namespace=namespace,
        **client_kwargs,
    )


class _InfoLangToolBase(Tool):
    """Shared construction/config for the InfoLang SmolAgents tools."""

    def __init__(
        self,
        *,
        client: InfoLang | None = None,
        api_key: str | None = None,
        dev_key: str | None = None,
        base_url: str | None = None,
        namespace: str | None = None,
        source: str | None = DEFAULT_SOURCE,
        **client_kwargs: Any,
    ) -> None:
        super().__init__()
        self.client = _build_client(
            client=client,
            api_key=api_key,
            dev_key=dev_key,
            base_url=base_url,
            namespace=namespace,
            client_kwargs=client_kwargs,
        )
        self.namespace = namespace
        self.source = source


class InfoLangRecallTool(_InfoLangToolBase):
    name = "recall"
    description = (
        "Search long-term memory for information relevant to a query. Returns "
        "the most semantically similar stored memories as text, best match "
        "first, each with its id so it can be forgotten later."
    )
    inputs = {
        "query": {
            "type": "string",
            "description": "What to search memory for.",
        },
        "top_k": {
            "type": "integer",
            "description": "Maximum number of memories to return (default 5).",
            "nullable": True,
        },
    }
    output_type = "string"

    def forward(self, query: str, top_k: int | None = None) -> str:
        from infolang_smolagents._format import format_hits

        result = self.client.recall(
            query,
            namespace=self.namespace,
            top_k=top_k if top_k is not None else 5,
        )
        return format_hits(result)


class InfoLangInvestigateTool(_InfoLangToolBase):
    name = "investigate"
    description = (
        "Investigate long-term memory for background on how or why something is "
        "the way it is. Like recall but tuned for open-ended questions; returns "
        "supporting memories as text."
    )
    inputs = {
        "query": {
            "type": "string",
            "description": "The question to investigate.",
        },
        "top_k": {
            "type": "integer",
            "description": "Maximum number of memories to return (default 5).",
            "nullable": True,
        },
    }
    output_type = "string"

    def forward(self, query: str, top_k: int | None = None) -> str:
        from infolang_smolagents._format import format_hits

        result = self.client.investigate(
            query,
            namespace_hint=self.namespace,
            top_k=top_k if top_k is not None else 5,
        )
        return format_hits(result)


class InfoLangRememberTool(_InfoLangToolBase):
    name = "remember"
    description = (
        "Save a fact to long-term memory so it can be recalled in later turns "
        "or sessions. Returns the id of the stored memory."
    )
    inputs = {
        "text": {
            "type": "string",
            "description": "The information to store.",
        },
        "tags": {
            "type": "string",
            "description": "Optional comma-separated tags for later filtering.",
            "nullable": True,
        },
    }
    output_type = "string"

    def forward(self, text: str, tags: str | None = None) -> str:
        result = self.client.remember(
            text, namespace=self.namespace, source=self.source, tags=tags
        )
        return result.memory_id or "Stored memory."


class InfoLangForgetTool(_InfoLangToolBase):
    name = "forget"
    description = (
        "Delete a memory by its id (as shown by recall or returned by "
        "remember). Use for information that is outdated or should be removed."
    )
    inputs = {
        "memory_id": {
            "type": "string",
            "description": "Id of the memory to delete.",
        },
    }
    output_type = "string"

    def forward(self, memory_id: str) -> str:
        self.client.forget(memory_id, namespace=self.namespace)
        return f"Deleted memory {memory_id}."


_TOOL_CLASSES: dict[str, type[_InfoLangToolBase]] = {
    "recall": InfoLangRecallTool,
    "investigate": InfoLangInvestigateTool,
    "remember": InfoLangRememberTool,
    "forget": InfoLangForgetTool,
}


def infolang_tools(
    *,
    client: InfoLang | None = None,
    api_key: str | None = None,
    dev_key: str | None = None,
    base_url: str | None = None,
    namespace: str | None = None,
    source: str | None = DEFAULT_SOURCE,
    include: Iterable[str] | None = None,
    **client_kwargs: Any,
) -> list[Tool]:
    """Build the InfoLang tool set, sharing a single client across the tools.

    Args:
        client: An existing ``InfoLang`` to reuse. Mutually exclusive with
            ``api_key``/``dev_key``/``base_url``.
        api_key / dev_key / base_url: Credentials/target for a new client.
        namespace: InfoLang namespace (bank) the tools read/write.
        source: ``source`` tag written on every ``remember``.
        include: Optional subset of tool names, from
            ``{"recall", "investigate", "remember", "forget"}``. Defaults to all.
        **client_kwargs: Forwarded to ``InfoLang(...)`` when building a client.

    Returns:
        A list of SmolAgents ``Tool`` instances ready for
        ``CodeAgent(tools=...)`` / ``ToolCallingAgent(tools=...)``.

    Raises:
        ValueError: If ``include`` names an unknown tool or is empty.
    """

    if include is None:
        names = list(_TOOL_CLASSES)
    else:
        names = list(include)
        unknown = [name for name in names if name not in _TOOL_CLASSES]
        if unknown:
            raise ValueError(
                f"Unknown InfoLang tool(s): {sorted(unknown)}. "
                f"Available: {sorted(_TOOL_CLASSES)}."
            )
        if not names:
            raise ValueError("infolang_tools(include=[]) would build no tools.")

    shared = _build_client(
        client=client,
        api_key=api_key,
        dev_key=dev_key,
        base_url=base_url,
        namespace=namespace,
        client_kwargs=client_kwargs,
    )
    return [
        _TOOL_CLASSES[name](client=shared, namespace=namespace, source=source)
        for name in names
    ]

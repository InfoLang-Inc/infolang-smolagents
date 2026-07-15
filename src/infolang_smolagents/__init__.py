"""InfoLang semantic-memory tools for the SmolAgents framework.

Quickstart::

    from smolagents import CodeAgent, InferenceClientModel
    from infolang_smolagents import infolang_tools

    agent = CodeAgent(
        tools=infolang_tools(api_key="il_live_...", namespace="user-42"),
        model=InferenceClientModel(),
    )
    agent.run("Remember that my favorite language is Rust.")
"""

from __future__ import annotations

from ._format import format_hits
from ._version import __version__
from .tools import (
    DEFAULT_SOURCE,
    InfoLangForgetTool,
    InfoLangInvestigateTool,
    InfoLangRecallTool,
    InfoLangRememberTool,
    infolang_tools,
)

__all__ = [
    "__version__",
    "DEFAULT_SOURCE",
    "InfoLangRecallTool",
    "InfoLangInvestigateTool",
    "InfoLangRememberTool",
    "InfoLangForgetTool",
    "infolang_tools",
    "format_hits",
]

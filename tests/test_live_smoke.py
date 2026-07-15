"""Optional live smoke test against the real InfoLang API.

Skipped unless ``INFOLANG_API_KEY`` is set -- NOT part of the default ``pytest``
run and excluded from the coverage gate. Only touches namespaces prefixed
``ittest-smolagents-`` and cleans up in a ``finally`` block.

Run it with::

    INFOLANG_API_KEY=il_live_... pytest tests/test_live_smoke.py -v
"""

from __future__ import annotations

import os
import uuid

import pytest

from infolang_smolagents import (
    InfoLangForgetTool,
    InfoLangRecallTool,
    InfoLangRememberTool,
)

pytestmark = pytest.mark.skipif(
    not os.environ.get("INFOLANG_API_KEY"),
    reason="live smoke test requires INFOLANG_API_KEY",
)


def test_live_round_trip() -> None:
    namespace = f"ittest-smolagents-{uuid.uuid4().hex[:8]}"
    api_key = os.environ["INFOLANG_API_KEY"]
    remember = InfoLangRememberTool(api_key=api_key, namespace=namespace)
    recall = InfoLangRecallTool(api_key=api_key, namespace=namespace)
    forget = InfoLangForgetTool(api_key=api_key, namespace=namespace)

    memory_id = ""
    try:
        memory_id = remember.forward("InfoLang smolagents live smoke fact", tags="smoke")
        assert memory_id and memory_id != "Stored memory."

        out = recall.forward("smoke fact")
        assert "smoke" in out
    finally:
        if memory_id and memory_id != "Stored memory.":
            forget.forward(memory_id)
        remember.client.close()

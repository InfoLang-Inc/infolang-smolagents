"""Rendering helpers for InfoLang recall results.

SmolAgents tools return a single ``output_type`` value; for recall/investigate
that is a ``string``. These helpers turn an SDK :class:`~infolang.RecallResult`
into a compact, model-readable block that keeps the memory ids visible (so the
agent can pass them back to ``forget``) and flags low-confidence recalls.
"""

from __future__ import annotations

from infolang import RecallResult

NO_HITS = "No relevant memories found."


def format_hits(result: RecallResult) -> str:
    """Render a recall result as a numbered, model-readable text block."""

    if not result.chunks:
        return NO_HITS
    lines = []
    for index, chunk in enumerate(result.chunks, start=1):
        score = f"{chunk.score:.2f}" if chunk.score is not None else "n/a"
        tags = f", tags={chunk.tags}" if chunk.tags else ""
        lines.append(f"{index}. (id={chunk.id}, score={score}{tags}) {chunk.text}")
    header = "Recalled memories"
    if result.weak:
        header += " (low confidence: top match below the 0.85 floor)"
    return header + ":\n" + "\n".join(lines)

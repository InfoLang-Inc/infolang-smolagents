from __future__ import annotations

from infolang import Chunk, RecallResult

from infolang_smolagents import format_hits
from infolang_smolagents._format import NO_HITS


def test_format_empty_returns_no_hits() -> None:
    assert format_hits(RecallResult(chunks=[])) == NO_HITS


def test_format_single_hit_includes_id_and_score() -> None:
    result = RecallResult(chunks=[Chunk(id="mem-1", text="hello world", score=0.91)])
    out = format_hits(result)
    assert "id=mem-1" in out
    assert "score=0.91" in out
    assert "hello world" in out
    assert out.startswith("Recalled memories:")


def test_format_includes_tags_when_present() -> None:
    result = RecallResult(chunks=[Chunk(id="m1", text="x", score=0.9, tags="a,b")])
    assert "tags=a,b" in format_hits(result)


def test_format_omits_tags_when_absent() -> None:
    result = RecallResult(chunks=[Chunk(id="m1", text="x", score=0.9)])
    assert "tags=" not in format_hits(result)


def test_format_score_none_renders_na() -> None:
    result = RecallResult(chunks=[Chunk(id="m1", text="x")])
    assert "score=n/a" in format_hits(result)


def test_format_weak_adds_low_confidence_header() -> None:
    result = RecallResult(chunks=[Chunk(id="m1", text="x", score=0.4)])
    assert "low confidence" in format_hits(result)


def test_format_numbers_multiple_hits() -> None:
    result = RecallResult(
        chunks=[
            Chunk(id="m1", text="first", score=0.9),
            Chunk(id="m2", text="second", score=0.88),
        ]
    )
    out = format_hits(result)
    assert "1. " in out
    assert "2. " in out

# infolang-smolagents — agent instructions

InfoLang semantic-memory `Tool`s for the **SmolAgents** (Hugging Face) agent
framework. Package name: `infolang-smolagents`; import path:
`infolang_smolagents`.

## Architecture

- `src/infolang_smolagents/tools.py` — the four `Tool` subclasses
  (`InfoLangRecallTool`, `InfoLangInvestigateTool`, `InfoLangRememberTool`,
  `InfoLangForgetTool`), a shared `_build_client` helper, and the
  `infolang_tools()` factory.
- `src/infolang_smolagents/_format.py` — renders a `RecallResult` into the
  model-readable string the recall/investigate tools return.

## Contract

- Depends only on the **published** `infolang` Python SDK (`>=0.2,<0.3`) via the
  synchronous `InfoLang` client. Never reimplement HTTP or import runtime/engine
  internals.
- Each tool follows the SmolAgents `Tool` contract: class-level `name` /
  `description` / `inputs` / `output_type` and a `forward` whose parameters match
  `inputs`. Keep `forward` self-contained (imports inside the method) so
  `to_dict()` / hub serialization keeps working.

## Rules

- Verify the SmolAgents `Tool` API (`AUTHORIZED_TYPES`, nullable rules,
  `validate_arguments`) against the installed package before changing tool
  shapes — do not assume.

## Commands

```bash
pip install -e ".[dev]"
ruff check .
mypy
pytest
```

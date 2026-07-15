# infolang-smolagents

[InfoLang](https://infolang.ai) semantic-memory tools for
[SmolAgents](https://github.com/huggingface/smolagents). Give any `CodeAgent` or
`ToolCallingAgent` durable, cross-session memory through four `Tool`s the agent
can call: `recall`, `investigate`, `remember`, and `forget`.

> Repository: `InfoLang-Inc/infolang-smolagents`. Package:
> `infolang-smolagents` (PyPI). Import path: `infolang_smolagents`.

## Install

```bash
pip install infolang-smolagents
```

This pulls in the `infolang` SDK (`>=0.2,<0.3`) and `smolagents`.

> **Note:** until `infolang` is published to PyPI, install both from source:
>
> ```bash
> pip install "infolang @ git+ssh://git@github.com/InfoLang-Inc/infolang-sdk-python.git"
> pip install "infolang-smolagents @ git+ssh://git@github.com/InfoLang-Inc/infolang-smolagents.git"
> ```

## Quickstart

```python
from smolagents import CodeAgent, InferenceClientModel
from infolang_smolagents import infolang_tools

agent = CodeAgent(
    # INFOLANG_API_KEY is read from the environment (or pass api_key=...).
    tools=infolang_tools(namespace="user-42"),
    model=InferenceClientModel(),
)

# First run stores a fact.
agent.run("My favorite language is Rust. Remember that.")

# A later run (even a new process) recalls it.
print(agent.run("What is my favorite language?"))
```

A runnable version is in [`examples/quickstart.py`](examples/quickstart.py).

## The tools

| Tool | `name` | InfoLang SDK call | Returns |
|------|--------|-------------------|---------|
| `InfoLangRecallTool` | `recall` | `client.recall(...)` | ranked memories (text) |
| `InfoLangInvestigateTool` | `investigate` | `client.investigate(...)` | supporting memories (text) |
| `InfoLangRememberTool` | `remember` | `client.remember(...)` | stored memory id |
| `InfoLangForgetTool` | `forget` | `client.forget(...)` | confirmation |

`recall`/`investigate` return a numbered, model-readable block that keeps each
memory's `id` visible (so the agent can pass it back to `forget`) and flags
low-confidence recalls (top match below InfoLang's 0.85 floor).

## Wiring options

**Bundle (recommended)** — builds all four tools sharing one client:

```python
tools = infolang_tools(api_key="il_live_...", namespace="user-42")
```

Select a subset:

```python
infolang_tools(namespace="user-42", include=["recall", "remember"])
```

Reuse an existing client:

```python
from infolang import InfoLang
tools = infolang_tools(client=InfoLang.from_api_key("il_live_..."), namespace="user-42")
```

**Individual tools:**

```python
from infolang_smolagents import InfoLangRecallTool, InfoLangRememberTool

agent = CodeAgent(
    tools=[
        InfoLangRecallTool(api_key="il_live_...", namespace="user-42"),
        InfoLangRememberTool(api_key="il_live_...", namespace="user-42"),
    ],
    model=model,
)
```

## Scoping (workspace vs namespace)

InfoLang scopes memory by **workspace** (tenant) and **namespace** (bank). Pass a
per-user or per-agent `namespace` so recalls stay isolated; managed API-key
requests honor `namespace` on both reads and writes:

```python
infolang_tools(api_key="il_live_...", namespace="user-42", workspace="acme")
```

## Development

```bash
pip install -e ".[dev]"
ruff check .
mypy
pytest
```

Unit tests mock the HTTP layer (`respx`) against a small in-memory fake of the
`il-runtime` memory routes; an integration test drives a `ToolCallingAgent` end
to end with a stub model (no LLM needed). An optional live smoke test
(`tests/test_live_smoke.py`) runs against the real InfoLang API when
`INFOLANG_API_KEY` is set and only touches namespaces prefixed
`ittest-smolagents-`:

```bash
INFOLANG_API_KEY=il_live_... pytest tests/test_live_smoke.py -v
```

## Links

- [InfoLang docs](https://docs.infolang.ai)
- [InfoLang Python SDK](https://github.com/InfoLang-Inc/infolang-sdk-python)
- [SmolAgents](https://github.com/huggingface/smolagents)

## License

Apache-2.0

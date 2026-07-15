"""Runnable quickstart for infolang-smolagents.

Requires a real InfoLang API key and a SmolAgents-supported model (e.g. a
Hugging Face inference token for ``InferenceClientModel``). Run with::

    INFOLANG_API_KEY=il_live_... HF_TOKEN=hf_... python examples/quickstart.py
"""

from __future__ import annotations

from smolagents import CodeAgent, InferenceClientModel

from infolang_smolagents import infolang_tools


def main() -> None:
    agent = CodeAgent(
        tools=infolang_tools(namespace="quickstart-user"),
        model=InferenceClientModel(),
    )

    agent.run("My favorite programming language is Rust. Please remember that.")
    answer = agent.run("What is my favorite programming language?")
    print(answer)


if __name__ == "__main__":
    main()

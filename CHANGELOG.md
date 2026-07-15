# Changelog

All notable changes to `infolang-smolagents` are documented here. This project
adheres to [Semantic Versioning](https://semver.org).

## [0.1.0] - 2026-07-15

### Added
- Initial release: InfoLang semantic-memory `Tool`s for
  [SmolAgents](https://github.com/huggingface/smolagents).
- Four tools — `InfoLangRecallTool`, `InfoLangInvestigateTool`,
  `InfoLangRememberTool`, `InfoLangForgetTool` — compatible with `CodeAgent`
  and `ToolCallingAgent`, built on the published `infolang` Python SDK.
- `infolang_tools(...)` factory that builds the set sharing a single client,
  with an `include=` subset filter.
- Self-contained `forward` methods, so the tools also pass SmolAgents'
  `to_dict()` / hub-serialization validation.
- Offline tests mock the HTTP layer with `respx`; an integration test drives a
  `ToolCallingAgent` end to end with a stub model. Optional live smoke test
  gated on `INFOLANG_API_KEY`.

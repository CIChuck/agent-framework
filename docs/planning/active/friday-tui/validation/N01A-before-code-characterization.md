# TUI-N01A before-code configuration characterization

**Date/source:** 2026-10-18; `feature/friday-tui` at `26f5d090`.

**Authority/evidence limit:** Read-only comparison baseline for the proposed
neutral configuration loader. No N01A source code, package metadata, TUI,
provider connection or user UAT was changed or verified.

The existing `friday_chat.config.load_friday_py_config()` was exercised with
synthetic YAML under a temporary directory and explicit test-only environment
mappings. The temporary files were discarded. These outcomes must be captured
as regression cases **before** moving the loader, then compared with both the
old Chat import path and the neutral import path on the same fixtures after
implementation.

| Case | Observed result at the baseline |
| --- | --- |
| Minimal legacy `llm.model` with relative memory and transcript directories | `FridayChatConfig`; `llm.model` retained; raw `./memory` and `./exports` retained; one legacy-LLM deprecation diagnostic. No path reinterpretation during loading. |
| Renamed `chat.name`, deprecated `llm.temperature`, unknown `zzz`, legacy LLM | Diagnostics in this order: `renamed_key chat.name`, `deprecated_key llm.temperature`, `unknown_key zzz`, `deprecated_key llm`. The renamed/deprecated dictionaries were replaced on the Chat module just before the call and restored afterward. |
| `${MISSING}` in a known field or an unknown top-level field | `FridayChatConfigError: Environment variable MISSING is required by config.` Interpolation happens before unknown-section omission. No chained cause/context. |
| Missing file | `FridayChatConfigError: Config file not found: <selected path>`; no chained cause/context. |
| Malformed YAML | `FridayChatConfigError: Invalid YAML in config file: <selected path>` with a YAML `ParserError` as cause/context. |
| Sequence root | `FridayChatConfigError: Config root must be a mapping.`; no chained cause/context. |
| Empty document | `FridayChatConfigError: Missing required config: llm.model`; no chained cause/context. |
| Existing directory passed as file | Native `IsADirectoryError` propagates; the loader does not normalize every read failure into a Chat error. |
| Canonical triplet through a symlinked runtime YAML | A catalog beside the **target** runtime YAML resolves; deliberately invalid same-named catalog beside the link is ignored. Chat and embedding specs resolve to `openai/test` and `openai/embed`, with no diagnostics. An explicit `FRIDAY_MODELS_CONFIG` pointing to the invalid link-side catalog is ignored. |
| Chat YAML passed to headless `RuntimeConfig.from_yaml()` | The separate parser raises `ValueError` on `memory.persist_directory`; it cannot substitute for the Chat-compatible application loader. |

Further existing regression fixtures cover canonical service credentials,
typed LLM migration, MCP reference validation before interpolation, literal
streamable-HTTP fields, warning ordering, sanitized example files and the
Chat-specific traceability map. The N01A directive names these suites and
requires new paired neutral/facade tests for the exact gap.

One representation limit is part of the baseline: `repr()` of a legacy
`FridayChatConfig` with `llm.api_key: synthetic-canary` contains that synthetic
value, while resolved canonical service specs are excluded from the model
representation. N01A must preserve existing behavior and must not describe
legacy `repr()` as a credential-safe output channel. This probe used only a
synthetic canary, not a real credential.

Baseline command:

```text
uv run pytest -q packages/friday-chat/tests_chat/compat/test_config_compatibility.py packages/friday-chat/tests_chat/test_llm_config_migration.py packages/friday-chat/tests_chat/test_mcp_config_compatibility.py packages/friday-chat/tests_chat/test_cli.py packages/friday-runtime/tests_runtime/test_config.py packages/friday-runtime/tests_runtime/test_mcp_runtime_config.py packages/friday-runtime/tests_runtime/test_model_library.py packages/friday-cli/tests_cli
```

Result: **369 passed**. The probe and tests used no real credentials or live
provider request. This establishes the before-code result only. Full Chat and
Runtime suites, changed-file static checks, installed-wheel closure and fresh
independent validation are after-code gates, not claims of this report.

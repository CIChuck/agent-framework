# FridayV2 Framework Upgrade Log

This document records framework package changes discovered while building
FridayV2. During the first FridayV2 parity pass, existing framework packages are
frozen so FridayV2 can be compared against the reference CLI at
`tests/integration/memory/friday.py` without moving the baseline.

## Freeze Directive

FridayV2 must be implemented as an app layer over the existing framework
packages. Do not modify existing framework package source or tests during the
FridayV2 parity implementation pass.

Frozen packages:

- `packages/friday-agent`
- `packages/friday-cli`
- `packages/friday-core`
- `packages/friday-finance`
- `packages/friday-llm`
- `packages/friday-mcp`
- `packages/friday-memory`
- `packages/friday-moltbook`
- `packages/friday-runtime`
- `packages/friday-sandbox`
- `packages/friday-speech`
- `packages/friday-telemetry`
- `packages/friday-tools`
- `packages/friday-transcript`

Allowed implementation targets:

- `packages/friday-chat/`
- `packages/friday-chat/tests_chat/`
- Workspace metadata required to register and run `packages/friday-chat`.
- FridayV2 planning documents under `docs/planning/`.

If FridayV2 exposes a missing capability, bug, type contract problem, or
awkward interface in a frozen framework package, do not patch that package
during the parity pass. Record the requested framework change below with source
evidence, impact, the FridayV2 workaround, and suggested follow-up tests. A
secondary framework-upgrade pass can then improve the framework package content
without weakening the FridayV2-to-`friday.py` comparison.

## Entry Template

```text
## FU-000: Short Title

Status: proposed | accepted | deferred | resolved
Discovered During: FridayV2 phase or test
Framework Package: packages/friday-...
Requested Change:
Reason:
Impact If Not Changed:
FridayV2 Workaround:
Compatibility Risk:
Suggested Follow-Up Tests:
Source Evidence:
```

## Upgrade Items

## FU-001: Align Graph Store Protocol With Runtime Graph Consumers

Status: proposed
Discovered During: FridayV2 real-runtime adapter validation
Framework Package: `packages/friday-memory`
Requested Change: Add the graph operations used by runtime diagnostics to the
declared graph-store interface, or provide a typed diagnostic/listing facade.
Reason: FridayV2 needs `/entities` parity with `friday.py`, which calls graph
lookup/list operations. The concrete graph stores expose `find_by_label()` and
`get_all_nodes()`, but the public `GraphStoreAdapter` protocol does not.
Impact If Not Changed: App-layer integrations must cast at the framework
boundary even when using supported concrete graph stores.
FridayV2 Workaround: `FrameworkMemoryAdapter.list_entities()` casts the graph
store to `Any` only at the protocol boundary and keeps the rest of the adapter
typed.
Compatibility Risk: Low behavior risk, but medium type-safety risk because
future graph-store implementations may not provide the diagnostic methods.
Suggested Follow-Up Tests: Add framework-level protocol conformance tests for
entity listing and label lookup, then remove the FridayV2 boundary cast.
Source Evidence: `uv run mypy packages tests main.py` reported
`packages/friday-chat/src/friday_chat/adapters.py` errors for missing
`find_by_label` and `get_all_nodes` on `GraphStoreAdapter` before the local
adapter cast was added.

## FU-002: Restore Repository-Wide Validation Gates Outside FridayV2

Status: proposed
Discovered During: FridayV2 release-gate validation
Framework Package: `packages/friday-agent`, `packages/friday-runtime`,
`packages/friday-sandbox`, `packages/friday-tools`, and legacy integration
fixtures under `tests/integration`
Requested Change: Repair existing repository-wide pytest, Ruff, and mypy
failures that are outside `packages/friday-chat`.
Reason: FridayV2 package-level gates pass, but repository-wide gates currently
fail in frozen framework packages and legacy prototype/test files.
Impact If Not Changed: FridayV2 can be validated in isolation, but the root
repository cannot use its standard all-repo commands as a clean release signal.
FridayV2 Workaround: Scope FridayV2 validation to
`packages/friday-chat/tests_chat`, `uv run ruff check packages/friday-chat`,
`uv run mypy packages/friday-chat`, compatibility tests, and CLI startup smoke.
Compatibility Risk: Medium operational risk because unrelated framework
failures can obscure FridayV2 regressions in CI.
Suggested Follow-Up Tests: After a framework-upgrade pass, rerun
`uv run pytest`, `uv run ruff check .`, and `uv run mypy packages tests main.py`
as required root release gates.
Source Evidence: `uv run pytest` reported 11 failures outside Friday Chat
(`friday-agent` CopilotAgent tests and `friday-runtime` DI tests);
`uv run ruff check .` reported 12 existing issues outside Friday Chat;
`uv run mypy packages tests main.py` still exits 1 with no remaining
`packages/friday-chat` errors.

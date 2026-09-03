# Build Plan: Friday Framework Enhancements

**Status:** Planned
**Target:** Framework packages under `packages/friday-*`
**Objective:** Restore repository-wide validation gates and address framework
contract gaps discovered after the Friday Chat V2 implementation pass.

---

## 1. Overview

### 1.1 Background

The Friday Chat V2 code-generation unit is complete, committed, and pushed.
`packages/friday-chat` now acts as the FridayV2 app layer over the existing
framework packages.

During closeout, Friday Chat package-level gates passed, but repo-wide gates
still failed for issues outside Friday Chat. Those failures were intentionally
logged as framework follow-up work rather than patched during the FridayV2
parity pass, because the existing framework packages were frozen while parity
with `tests/integration/memory/friday.py` was established.

This plan defines the next framework-focused unit of work.

### 1.2 Current Validation Snapshot

Commands run from the repository root:

```bash
uv run pytest packages/friday-chat/tests_chat
uv run pytest packages/friday-cli/tests_cli
uv run pytest
uv run mypy packages tests main.py
uv run ruff check .
uv run pytest packages/friday-agent/tests_agent packages/friday-runtime/tests_runtime
```

Observed results:

| Command | Result | Notes |
| --- | --- | --- |
| `uv run pytest packages/friday-chat/tests_chat` | pass | `169 passed` |
| `uv run pytest packages/friday-cli/tests_cli` | pass | `155 passed` |
| `uv run pytest` | fail | collection stops on duplicate top-level test module `test_display` |
| `uv run mypy packages tests main.py` | fail | duplicate module named `test_display` prevents full check |
| `uv run ruff check .` | fail | 12 issues: 1 import ordering issue and 11 long docstring/reference lines |
| `uv run pytest packages/friday-agent/tests_agent packages/friday-runtime/tests_runtime` | fail | 11 known framework test failures |

The worktree also had generated/local memory state modified under
`tests/integration/memory/vector/`; this plan must not clean or overwrite that
state unless explicitly requested.

## 2. Problem Statement

### 2.1 Root Test Discovery Is Structurally Broken

Root `pytest` and root `mypy` both fail before meaningful all-repo validation.
The immediate cause is inconsistent package marking for package-local test
trees.

Package test directories with `__init__.py`:

- `packages/friday-agent/tests_agent`
- `packages/friday-core/tests_core`
- `packages/friday-llm/tests_llm`
- `packages/friday-mcp/tests_mcp`
- `packages/friday-memory/tests_memory`
- `packages/friday-runtime/tests_runtime`
- `packages/friday-sandbox/tests_sandbox`
- `packages/friday-telemetry/tests_telemetry`
- `packages/friday-tools/tests_tools`

Package test directories without `__init__.py`:

- `packages/friday-chat/tests_chat`
- `packages/friday-cli/tests_cli`
- `packages/friday-finance/tests`
- `packages/friday-moltbook/tests_moltbook`
- `packages/friday-speech/tests_speech`
- `packages/friday-transcript/tests`

Because some test trees are not Python packages, duplicate basenames collide
under root discovery. The currently blocking example is:

- `packages/friday-chat/tests_chat/test_display.py`
- `packages/friday-cli/tests_cli/test_display.py`

Other duplicate test basenames already exist, including `test_config.py`,
`test_models.py`, `test_protocols.py`, and `test_base.py`.

### 2.2 Framework Tests Fail After Collection Is Narrowed

After bypassing the root collection failure by targeting the affected packages,
`friday-agent` and `friday-runtime` still have 11 failing tests.

`friday-agent` failures:

- 9 `CopilotAgent` tests fail in
  `packages/friday-agent/src/friday_agent/base.py`.
- `_archive_turn()` passes `getattr(self.llm, "model", None)` directly into
  `InteractionTurn.model_name`.
- Test doubles expose `.model` as a `MagicMock`, which Pydantic rejects because
  `InteractionTurn.model_name` requires a string.

`friday-runtime` failures:

- 2 DI tests expect builtin runtime tools `recall_memory` and `store_fact`.
- `DIContainer._create_tool_registry()` calls `register_runtime_tools()`, but
  the builtin catalog path currently returns no memory builtin tools in the
  failing tests.

### 2.3 Ruff Gate Has Small Existing Debt

Root Ruff currently reports 12 issues:

- 1 import-order issue in `packages/friday-agent/src/friday_agent/base.py`
- 2 long reference lines in `packages/friday-sandbox`
- 9 long reference/docstring lines in `packages/friday-tools`

These are low-risk formatting and lint cleanup items, but they block
`uv run ruff check .`.

### 2.4 Graph Store Contract Is Incomplete

Friday Chat's framework upgrade log records a real cross-package contract gap:

- `MemoryController` and Friday Chat entity diagnostics need
  `get_all_nodes()` and `find_by_label()`.
- Concrete graph stores expose those operations.
- The public `GraphStoreAdapter` contract in `friday-core` does not declare
  them.
- Friday Chat currently works around the gap with a boundary `Any` cast in
  `FrameworkMemoryAdapter`.

This is a package-boundary issue and should be fixed as a framework contract
enhancement, not by adding more casts in app code.

## 3. Scope

### 3.1 In Scope

- Package test-tree packaging needed to unblock root pytest and mypy discovery.
- `friday-agent` fix for archived turn model-name normalization.
- `friday-runtime` fix for builtin runtime tool registration.
- Ruff cleanup needed for the current root lint gate.
- Graph-store protocol alignment for diagnostic/listing operations.
- Focused regression tests for each behavioral or contract fix.
- Documentation updates to framework upgrade status where appropriate.

### 3.2 Out of Scope

- New Friday Chat V2 features.
- Reopening the completed Friday Chat parity checklist.
- Broad type-debt cleanup across all `# mypy: ignore-errors` files.
- Cleaning `.friday/`, Chroma, transcript, vector, cache, or generated runtime
  state.
- Replacing framework package internals for stylistic reasons.
- Implementing tool, web, or integration stubs unrelated to the validation
  gates.

## 4. Operating Rules

- Preserve unrelated local changes and generated state.
- Follow `docs/reference/policies/repository-engineering-policy.md`.
- Do not add `# mypy: ignore-errors` to source files.
- Prefer contract fixes over repeated `cast(...)`.
- Do not rely on `assert` as the sole enforcement for essential runtime
  invariants.
- When changing package boundaries, document affected packages and run the
  narrowest meaningful package tests plus the relevant root gate.
- Keep each task independently reviewable.

## 5. Implementation Plan

### Task 1: Unblock Root Test And Type Discovery

**Goal:** Make root pytest and mypy collect the repository consistently.

Work:

- Add missing `__init__.py` files to package-local test directories that are
  currently unmarked:
  - `packages/friday-chat/tests_chat/__init__.py`
  - `packages/friday-cli/tests_cli/__init__.py`
  - `packages/friday-finance/tests/__init__.py`
  - `packages/friday-moltbook/tests_moltbook/__init__.py`
  - `packages/friday-speech/tests_speech/__init__.py`
  - `packages/friday-transcript/tests/__init__.py`
- Add nested `__init__.py` files only where needed for subpackages such as
  Friday Chat compatibility tests.
- Confirm root pytest no longer stops on import-file mismatch.
- Confirm root mypy no longer stops on duplicate test module names.

Validation:

```bash
uv run pytest --collect-only
uv run mypy packages tests main.py
```

Acceptance:

- No `import file mismatch` error from pytest.
- No duplicate module error from mypy.
- Any remaining failures are real test/type failures, not discovery collisions.

### Task 2: Fix `friday-agent` Archived Turn Model Name Handling

**Goal:** Ensure agent turn archiving writes a valid string model name without
weakening `InteractionTurn`.

Work:

- In `packages/friday-agent/src/friday_agent/base.py`, normalize the LLM model
  value before constructing `InteractionTurn`.
- Accept real string model identifiers.
- Use `None` or a clear fallback for non-string mock/provider values.
- Keep the Pydantic `InteractionTurn.model_name` contract intact.
- Add or update tests proving mocked LLMs and real string model names archive
  successfully.

Validation:

```bash
uv run pytest packages/friday-agent/tests_agent/test_copilot.py
uv run pytest packages/friday-agent/tests_agent
```

Acceptance:

- The 9 `CopilotAgent` failures are resolved.
- No broad type suppression is added.
- Turn metadata still preserves real model names when available.

### Task 3: Fix Runtime Builtin Tool Registration

**Goal:** Restore expected runtime builtin tools in `DIContainer` without
coupling runtime to incidental globals.

Work:

- Trace `register_runtime_tools()` and `_builtin_tool_catalog()`.
- Ensure `recall_memory` and `store_fact` from `friday-agent` builtins are
  loaded when the builtin provider is enabled.
- Keep provider filtering behavior intact for selected/all modes.
- Preserve dependency binding in `DIContainer._create_tool_registry()`.
- Add or update regression coverage for default builtin loading and selected
  Friday tools provider loading.

Validation:

```bash
uv run pytest packages/friday-runtime/tests_runtime/test_di.py
uv run pytest packages/friday-runtime/tests_runtime
```

Acceptance:

- `test_di_loads_builtin_tools_by_default` passes.
- `test_di_loads_friday_tools_provider_with_category_filter` passes.
- Runtime builtin provider semantics are explicit and documented in tests.

### Task 4: Restore Root Ruff Gate

**Goal:** Make `uv run ruff check .` pass without semantic changes.

Work:

- Fix the import ordering issue in `friday-agent`.
- Wrap or mark long documentation/reference lines in `friday-sandbox` and
  `friday-tools`.
- Avoid unrelated reformatting.

Validation:

```bash
uv run ruff check .
```

Acceptance:

- Ruff passes at repository root.
- Changes are limited to formatting/import organization.

### Task 5: Align Graph Store Protocol With Runtime Consumers

**Goal:** Resolve FU-001 by making graph diagnostic/listing operations explicit
at the framework boundary.

Work:

- Add the graph operations used by runtime diagnostics to the public graph-store
  contract, or introduce a typed diagnostic/listing facade if that is cleaner.
- Cover at least:
  - `get_all_nodes()`
  - `find_by_label(label, node_type=None)`
- Confirm concrete graph stores conform:
  - `ElementXGraphStore`
  - `NullGraphStore`
- Remove the Friday Chat boundary cast if the stronger protocol makes it
  unnecessary.
- Add framework-level protocol/conformance tests.

Validation:

```bash
uv run pytest packages/friday-memory/tests_memory/test_adapters
uv run pytest packages/friday-chat/tests_chat
uv run mypy packages/friday-core packages/friday-memory packages/friday-chat
```

Acceptance:

- Runtime graph consumers use a declared typed contract.
- Friday Chat no longer needs an `Any` cast for graph diagnostic methods.
- FU-001 can be marked resolved in the framework upgrade log.

### Task 6: Update User And Developer Guides

**Goal:** Keep guide content aligned with the framework validation and contract
enhancement work before closeout.

Work:

- Update `docs/guides/15-contributing.md` with the restored root validation
  expectations, package-local test packaging rules, and guidance for preserving
  repo-wide pytest/mypy discovery.
- Update `docs/guides/13-troubleshooting.md` with common root validation
  failures, including duplicate test module discovery, Ruff gate failures, and
  framework package validation debt triage.
- Update any directly affected user-facing guide if the implementation changes
  observable configuration or runtime behavior.

Validation:

```bash
git diff --check -- docs/guides
```

Acceptance:

- Guide updates describe what changed, why it matters, and how to validate it.
- Guide updates separate restored validation expectations from known legacy debt.
- Implementation is not considered complete until these guide updates are done.

### Task 7: Run Full Framework Closeout Gates

**Goal:** Prove the framework enhancement unit restores the intended repository
signals.

Validation:

```bash
uv run pytest
uv run ruff check .
uv run mypy packages tests main.py
git diff --check
```

Acceptance:

- Root pytest runs past collection and all expected tests pass, or any remaining
  failures are documented as separate explicit legacy debt.
- Root Ruff passes.
- Root mypy runs past discovery; any remaining type debt is documented with
  exact package/file boundaries.
- No unrelated local/generated state is removed or overwritten.

## 6. Recommended Task Order

1. Task 1: unblock discovery.
2. Task 2: fix `friday-agent` archived turn model names.
3. Task 3: fix runtime builtin tool registration.
4. Task 4: restore Ruff.
5. Task 5: resolve graph-store protocol gap.
6. Task 6: update user and developer guides.
7. Task 7: run closeout gates.

This order is intentional: root discovery must be fixed before repo-wide test
and type results can be trusted.

## 7. Risks And Mitigations

| Risk | Mitigation |
| --- | --- |
| Adding test `__init__.py` changes import paths or fixture lookup | Run package-local tests and root collection immediately after Task 1 |
| Mock normalization hides a real provider contract issue | Preserve real string model names and test both mock and real-string paths |
| Builtin tool loading depends on decorator side effects | Make imports explicit where needed and cover expected tools in runtime tests |
| Graph protocol expansion creates a broad cross-package change | Keep the contract narrow and limited to already-used diagnostic/listing methods |
| Root mypy reveals additional legacy debt after duplicate modules are fixed | Report exact remaining failures; do not hide them with broad suppressions |

## 8. Completion Criteria

- Root pytest collection is no longer blocked by duplicate test module names.
- Known `friday-agent` and `friday-runtime` test failures are fixed.
- Root Ruff passes.
- The graph-store protocol gap is resolved or explicitly deferred with updated
  rationale.
- `docs/guides/15-contributing.md` and `docs/guides/13-troubleshooting.md` are
  updated for the restored framework validation workflow.
- Root validation commands have fresh recorded outcomes.
- `docs/planning/backlog/friday-chat-framework-followups/upgrade-log.md` is updated
  for FU-001/FU-002 status as appropriate.

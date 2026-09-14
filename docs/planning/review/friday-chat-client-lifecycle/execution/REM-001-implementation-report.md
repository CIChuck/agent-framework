# REM-001 Implementation Report

## Scope

Separate bounded remediator `/root/friday_chat_client_lifecycle_rem_001`
implemented only VAL-001-F01 under REM-001. Product and test changes are limited
to:

- `packages/friday-chat/src/friday_chat/app.py`
- `packages/friday-chat/tests_chat/test_app_lifecycle.py`

No coordinator, reorganization algorithm, provider/model behavior, Friday LLM,
dependency, lock, configuration, version, or unrelated test was changed.

## Implementation

- Removed client cleanup from the pre-reorganization
  `close_for_shutdown()` drain hook.
- Added an app-owned final cleanup operation using the existing content-safe
  `_run_step` diagnostic boundary and snapshot-sensitive failure behavior.
- Invoked final cleanup exactly once after coordinator shutdown returns or is
  contained, including invalid or unavailable exit requests and coordinator
  failures.
- Added deterministic ordering and exact-once tests for success, preflight
  failure, mutation failure, rollback or recovery failure, unavailable or
  invalid requests, and cleanup failure.

## Deterministic Evidence

- Focused lifecycle/input/runtime/LLM tests: `55 passed`.
- Friday LLM package: `186 passed, 8 skipped`.
- Friday Chat package: `434 passed, 5 skipped`, with the same three declared
  PTY baseline failures.
- Focused Ruff: passed.
- Focused mypy: passed for four source files.
- Board validation: passed with 22 tasks.
- Authorized-delta whitespace check: passed.

No credential, live provider, paid service, external mutation, persistent
runtime state, push, merge, release, deployment, or publication was used.

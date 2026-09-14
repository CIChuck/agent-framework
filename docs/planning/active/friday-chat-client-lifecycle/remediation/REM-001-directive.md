# REM-001 Final Client-Cleanup Ordering Directive

Status: authorized bounded remediation

## Finding And Authority

This directive remediates exactly one independent-validation finding:
VAL-001-F01. Authority remains the repository policies, Friday Chat behavioral
contract, approved build and tactical plans, CD-001, and the stored VAL-001
report. No other feature or refactor is authorized.

## Objective

Move process-scoped client cleanup from the pre-reorganization drain hook to
the Friday Chat application's true final asynchronous shutdown boundary so it
runs exactly once after all coordinator-owned exit reorganization, rollback,
and recovery termination, but before `FridayChatApp.run()` returns and its event
loop can close.

## Allowed Files

- `packages/friday-chat/src/friday_chat/app.py`
- `packages/friday-chat/tests_chat/test_app_lifecycle.py`
- this initiative's packet, validation, and remediation artifacts

Do not modify coordinator, mutation, Friday LLM, dependency, lock, config,
provider, model, tool-loop, generation, retry, timeout, version, or unrelated
test behavior.

## Required Implementation

1. Remove process-client cleanup from
   `AppMaintenanceRuntimeHooks.close_for_shutdown()`.
2. Give the app-owned maintenance hooks a narrow final client-cleanup method
   that reuses `_run_step` for content-safe diagnostics and preserves the
   existing snapshot-sensitive fatal/contained behavior.
3. Invoke that method exactly once after
   `ReorganizationCoordinator.shutdown()` has returned or raised and after the
   application has contained the coordinator result.
4. Ensure cleanup still executes when exit-request construction fails, execute
   capability is unavailable, reorganization succeeds, or coordinator
   preflight, mutation, rollback, or recovery terminates with an exception.
5. Keep cleanup before `FridayChatApp.run()` exits and before event-loop
   teardown. Do not suppress or duplicate exposed cleanup diagnostics.

## Required Tests

- Existing ordinary shutdown asserts cleanup exactly once.
- An execution-capable exit request records reorganization work before cleanup.
- Parameterized coordinator termination cases representing success, preflight
  failure, mutation failure, and rollback or recovery failure all record
  exact-once cleanup last.
- Cleanup failure remains content-safe and contained when no snapshot execute
  was requested.
- Cleanup failure on an executing exit request participates in the existing
  shutdown-coordinator warning/failure path without exposing its message.
- Existing focused and package validations are rerun.

## Verification

- focused app lifecycle, input, runtime, and Friday LLM lifecycle tests;
- complete Friday LLM and Friday Chat package tests;
- focused Ruff and mypy;
- board and documentation lifecycle validation;
- exact candidate diff/scope and whitespace checks; and
- fresh delta review followed by aggregate review.

No credential, live provider, paid service, external network, persistent runtime
state, push, merge, release, deployment, or publication is authorized.

## Stop Conditions

Stop if remediation requires changing the coordinator protocol, reorganization
algorithm, provider/model behavior, another package, configuration schema,
dependency lock, package versions, or files outside the allowed list.

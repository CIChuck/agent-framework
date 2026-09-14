# VAL-001 Independent Validation Report

## Outcome

`CHANGES_REQUESTED`

## Candidate And Review Identity

- Initiative: `friday-chat-client-lifecycle`
- Work unit: `CD-001-client-lifecycle`
- Review mode: full
- Base: `fe15552cc83caa2590be2e73158091dd15826d1e`
- Candidate: `ad65ec05974656c580bd928840b44b5c9a87902c`
- Diff: `fe15552cc83caa2590be2e73158091dd15826d1e..ad65ec05974656c580bd928840b44b5c9a87902c`
- Reviewer: fresh-context read-only subagent
  `/root/friday_chat_client_lifecycle_val_001`
- First observed: `2026-09-14T15:33:38-04:00`
- Evidence closed: `2026-09-14T15:38:48-04:00`

All ten authority hashes, the candidate, its parent, and the selected diff
matched the request before and after validation. The shared checkout was not
detached, but governed paths stayed unchanged and dirty state matched the
declared exclusions plus the controller-owned request. No implementer context,
credential, provider call, external mutation, or repository write was used.

## Finding

### VAL-001-F01 — High — provider clients close before configured exit reorganization

Affected modules:

- `packages/friday-chat/src/friday_chat/app.py`
- `packages/friday-chat/src/friday_chat/reorganization/coordinator.py`
- `packages/friday-chat/src/friday_chat/reorganization/mutation.py`
- `packages/friday-chat/tests_chat/test_app_lifecycle.py`

Violated authority:

- build-plan AC-05 and AC-09;
- build-plan final-quiescence design requirement;
- CD-001 required implementation item 5 and shutdown-order test requirement;
- tactical task TP-07; and
- Friday Chat behavioral-contract final-resource ordering.

Evidence: `AppMaintenanceRuntimeHooks.close_for_shutdown()` closes clients
before returning to `ReorganizationCoordinator.shutdown()`. The coordinator
then finalizes the transcript and may execute configured exit reorganization,
whose provider registry can perform LLM and embedding work. The validator's
deterministic reproduction observed:

```text
clients_close -> transcript_finalize -> reorganization_execute
```

This can reuse already-closed cached clients or create new clients after the
only cleanup call, recreating the unclosed-session condition.

Required mitigation: run process-client cleanup exactly once after optional
exit reorganization and all of its rollback or recovery work terminates, while
still running before event-loop teardown on both success and failure. Preserve
content-safe diagnostics and snapshot-sensitive shutdown containment.

Required regression evidence:

- no provider work occurs after cleanup on an execution-capable exit path;
- exact-once cleanup follows reorganization success, preflight failure,
  mutation failure, and rollback or recovery termination;
- cleanup failure remains content-safe and participates in shutdown accounting;
  and
- all VAL-001 checks are rerun.

No configuration change is required.

## Requirement Disposition

- PASS: AC-01 through AC-04, AC-06 through AC-08, AC-10, and AC-11.
- FAIL: AC-05 and AC-09 through VAL-001-F01.
- NOT SATISFIED: AC-12 because the candidate is not verified.
- PASS: TP-01 through TP-06 and TP-08 through TP-13.
- FAIL: TP-07 through VAL-001-F01.

## Commands And Results

- Friday LLM lifecycle tests: `3 passed`.
- Focused Friday Chat tests: `46 passed`.
- Friday LLM package: `186 passed, 8 skipped`.
- Friday Chat package: `428 passed, 5 skipped`, with exactly the three declared
  unchanged PTY baseline failures.
- Focused Ruff: passed.
- Focused mypy: passed for four source files.
- Board validation: passed with 22 tasks.
- Candidate `git diff --check`: passed.
- Deterministic order reproduction: failed with
  `clients_close -> transcript_finalize -> reorganization_execute`.

The default root pytest collection conflict, broader mypy dependency-stub
failure, and three PTY failures remain declared baselines rather than candidate
regressions.

## Residual Risk And Next Gate

Live-provider cleanup remains untested because it was not authorized. LiteLLM
may suppress individual internal handler-close errors, limiting Friday's
visibility to errors its public cleanup call exposes.

Keep the initiative `started`, record `validation_state: changes_requested`,
remediate VAL-001-F01 under a bounded directive, freeze a new candidate, and
dispatch fresh delta and aggregate validation. This report does not authorize
acceptance, push, merge, release, deployment, or publication.

# Construction directive CD-001: local telemetry assembly

Status: Approved construction directive.
Approved by: repository maintainer.
Approved at: 2026-10-05.
Approval evidence: explicit "proceed" in response to CD-001 approval request.
Amendment A01 approved at: 2026-10-05.
Amendment evidence: maintainer's "approved, proceed" after independent directive
review requested CDR-001 and CDR-002 corrections. Scope: verification authority
and reporting only; no product contract, remediation, or waiver is approved.
Date: 2026-10-04.
Initiative: `friday-telemetry-rewire`. Work unit: `TELEM-01`.
Branch: `feature/friday-telemetry-rewire`.
Preparation base: `2155a0fc51f5b20dea4e35c6cfc70f1d52002735`.

## Builder role and authority

Implement one bounded local telemetry slice under this approved directive once
the board records `started` on the named branch. Authority precedence is
explicit maintainer direction, repository engineering and independent
validation policies, accepted MCP contracts, the [build plan](../build-plan.md),
[first-slice contract](../telemetry-contract.md), [tactical plan](../tactical-plan.md),
then this directive. Plan approval on 2026-10-04 is recorded; approval of this
new directive was granted on 2026-10-05. No lightweight exemption is claimed for code.

## Objective and acceptance

Implement T01-01 through T01-06 and satisfy AC-01 through AC-06 from the tactical
plan. The real CLI must assemble the same provider-neutral local observer used
by embedded runtimes, report its state, and record truthful runtime/application
lifecycle outcomes. Two independent injected providers must receive equivalent
safe events and correctly paired nested spans through `CompositeProvider`.
This slice establishes wiring and inspection; it does not claim full turn,
LLM, tool, memory, persistence, or remote tracing.

## Exact allowed product manifest

| Package | Allowed source paths | Allowed test paths |
| --- | --- | --- |
| Chat | `packages/friday-chat/src/friday_chat/telemetry.py` (new), `config.py`, `runtime.py`, `cli.py`, `app.py` in that same directory | `packages/friday-chat/tests_chat/test_telemetry.py` (new), `test_cli.py`, `test_runtime.py`, `test_app_lifecycle.py`, `compat/test_config_compatibility.py` in that test directory |
| Telemetry | `packages/friday-telemetry/src/friday_telemetry/providers/composite.py` | `packages/friday-telemetry/tests_telemetry/test_providers.py` |

Planning, execution, authority, and validation artifacts may be written inside
this initiative packet. Package README updates may be made in
`packages/friday-chat/README.md` and `packages/friday-telemetry/README.md` to
document the new local behavior and composite mapping. Board/dashboard updates
are limited to this initiative and must preserve unrelated existing edits.

All other product files, including the dirty Chat example YAML, are outside the
manifest. Do not edit framework LLM, memory, runtime, core, MCP, transcript,
telemetry interface/config/OTel provider, dependency metadata, packaged config
templates, or command registry. A necessary extra file requires scope
reconciliation before editing it.

## Implementation requirements

1. Add the strict local Chat config and traceability mapping described by the
   contract. Preserve old config compatibility and Langfuse behavior. No YAML
   provider imports, remote endpoints, credentials, or vendor dependencies.
2. Implement immutable typed lifecycle events and diagnostics and an observer
   using the existing public `TelemetryInterface`. Keep the newest 256 events,
   cumulative failure/drop counts, and safe snapshots. Preserve caller-owned
   injection; exceptions must not change application behavior.
3. Assemble and retain the observer before runtime services are constructed in
   fake and real paths. Route existing MCP telemetry through strict validation
   of its public event contract. Do not connect raw legacy LLM/memory helpers.
4. Emit runtime-ready only after successful assembly. Emit app lifecycle
   outcomes around the existing startup and cleanup flow without changing
   ownership, shutdown ordering, maintenance/drain, async-client close, or
   cancellation behavior. Surface a concise safe CLI startup diagnostic.
5. Repair composite IDs, parent mapping, snapshot membership, independent
   payload dictionaries, exactly-once end behavior, empty-composite behavior,
   and best-effort failure fan-out exactly as the first-slice contract specifies.

## Non-goals, security, and migration

Do not implement later tactical units, activate Langfuse or an exporter,
resolve remote sampling/retention policy, change tool admission/budget/manual
selection, add new commands, modify storage or schema, or inspect real
conversations. No live-provider calls, costs, external services, credentials,
publication, push, merge, release, or deployment are permitted.

Use temporary storage and synthetic providers for all tests. Preserve existing
`.friday`, Chroma, transcript, and local config state. No content-bearing text,
arbitrary exceptions, or environment values enter diagnostic payloads. Default
disabled behavior and caller injection are backward compatible. Composite IDs
keep the first child ID, while downstream children now receive their own IDs.
No persisted migration is needed. Add no typing suppressions or global typing
relaxations; essential invariants use explicit checks, not only assertions.

## Verification and closeout

Run required commands with `UV_CACHE_DIR=/private/tmp/friday-uv-cache` and
`LITELLM_LOCAL_MODEL_COST_MAP=true` for tests:

```text
uv run pytest packages/friday-chat/tests_chat/test_telemetry.py packages/friday-chat/tests_chat/test_cli.py packages/friday-chat/tests_chat/test_runtime.py packages/friday-chat/tests_chat/test_app_lifecycle.py packages/friday-chat/tests_chat/compat/test_config_compatibility.py packages/friday-telemetry/tests_telemetry/test_providers.py
uv run pytest packages/friday-chat/tests_chat packages/friday-telemetry/tests_telemetry
uv run ruff check .
uv run pytest --ignore=packages/friday-chat/tests_chat/test_live_lmstudio.py --ignore=packages/friday-llm/tests_llm/test_live_lmstudio.py
uv run ruff check <exact changed Python files>
uv run mypy --python-version 3.10 <exact changed source files>
uv run mypy --python-version 3.13 <exact changed source files>
uv run python scripts/friday-dev-board.py validate
uv run python scripts/check-documentation-lifecycle.py
git diff --check
```

The mandatory [verification profile](../verification-profile.md) binds the exact
changed-file lists, Python 3.10 syntax/API evidence, broad-test safety preflight,
two live-module safety exclusions, baseline handling, and report fields.
Repository-wide Ruff and deterministic root pytest are required alongside
focused/package checks, regardless of observed coupling. The safety exclusions
implement the existing prohibition on live services; they waive no deterministic
test or failing requirement. If preflight identifies another unsafe test, stop
that execution and obtain a precise authority decision; do not invent exclusions
or substitute package suites for the root gate.

Include positive, negative, integration, privacy, cancellation, and regression
coverage mapped to each tactical criterion. Record baseline failures separately;
do not silence them or claim checks not run. Record baseline command results
before implementation and preserve the local path manifest in the execution log.
For A01's newly required checks, use the original preparation base and unchanged
product candidate; label this as retrospective evidence, not a pre-build run.

Document local configuration, inspection, injection ownership, privacy, and
deferred telemetry coverage. Produce an implementation report with exact paths,
behavior, commands/results, criteria mapping, exclusions, and residual risks.
Commit only authorized files to create a stable candidate. Freeze base/candidate,
exact diff, SHA-256 authority manifest (including the verification profile),
known baselines, and every required command and exclusion
in a validation request. A fresh-context, read-only validator must review that
candidate, returning `VERIFIED`, `CHANGES_REQUESTED`, or `BLOCKED` with evidence.
The builder may not self-verify, accept the work, or apply unapproved remediation.

Stop for unapproved files, conflicting authority, missing baseline/candidate,
external effects, changed ownership, unsafe payloads, or broader architectural
requirements. Stop after the committed candidate and report for independent
review. TELEM-01 verification does not authorize later units or full closeout.

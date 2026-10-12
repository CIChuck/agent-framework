# Approved REM-002: reconcile TELEM-01 verification execution

Status: Approved by repository maintainer on 2026-10-05.
Approval evidence: "Approve of your recommendations. Proceed with all tasks you've outlined. Require any other approvals?"
Scope: verification setup and required reruns, including the three named
loopback fixtures and locked public PyPI downloads if needed. No waiver. REM-001's collision fix was independently supported at `3a69050`.
[VAL-002](../validation/VAL-002/report.md) returned CHANGES_REQUESTED for the
single finding VAL-002-F01: unresolved mandatory aggregate verification gates.
This directive maps that finding once, through the execution steps and the
separate lint/timing dispositions below. CD-001 A03 and the amended verification profile record this approval.

The next bounded step is verification setup, followed by fresh required runs.
No product source, existing test body/deadline, package minimum version, dependency
constraint, shared `.venv`, user config, or existing application data may change.

1. Reconcile root test collection through an explicitly frozen test invocation:
   use `--import-mode=importlib` and an isolated Chat test-helper PYTHONPATH entry
   for existing bare sibling imports. Prove complete collection on preparation
   base and candidate before full execution. Preserve root testpaths and exactly
   the two currently approved live-module exclusions; do not drop any additional
   test. Retain the originally failed default-root invocation as evidence.
2. Approved bounded permission covers the three synthetic HTTP fixture tests in
   `packages/friday-chat/tests_chat/test_llm_adapter_migration.py`:
   `test_chat_adapter_controls_reach_final_http_json`,
   `test_chat_adapter_typed_stream_reuses_generation_defaults`, and
   `test_provider_option_target_mismatch_fails_before_http`. Permit only their
   127.0.0.1 fixtures to bind ephemeral loopback ports. Use the same external
   non-loopback DNS/connect/sendto guard, isolated sources, credential-free
   environment and temporary files. Record test-runtime permission effects.
   No other privileged execution or network destination is included.
3. Build a separate Python 3.10 test environment from the existing frozen lock
   and supported workspace metadata. Reuse cached distributions first; if needed,
   this approval permits package downloads from public PyPI solely for
   this temporary test environment, with frozen integrity hashes and no
   credentials. Never alter the existing shared environment or package metadata.
   Rerun genuine observer/composite import and lifecycle smoke checks; no stubbed
   dependency may substitute for real runtime evidence.
   Lock resolution must preserve the supported Python 3.10 dependency branch;
   if the current lock cannot supply a compatible environment, stop and report
   the exact incompatibility rather than update the lock or dependencies.
4. Rerun the prescribed baseline/candidate root, affected-package, static,
   compatibility and governance gates; obtain fresh read-only independent
   delta/aggregate review after authority changes. Stop for new failures or scope.

Documentation authority targets only: this directive, CD-001,
verification-profile.md, authority-manifest.yaml, execution log/index, request
and evidence records, and telemetry-only board/dashboard metadata. Product
source/test/configuration targets: none. A01/A02 remain controlling except for the explicit A03 verification amendment.
A fresh readiness review must assess the frozen authority before new execution.

## Existing repository lint debt

The required root Ruff command reports 337 identical baseline diagnostics;
there are zero introduced/removed normalized diagnostics. The immutable
[root lint baseline](../validation/VAL-002/root-lint-baseline-diagnostics.json) identifies each path, rule, line, column
and message; SHA-256:
`d3753f4ba46c9b7d2aa1920bade124aaa26a30587acba193151f292ddc7821c7`.

| Rule | Existing diagnostics |
| --- | --- |
| E702 | 172 |
| E701 | 144 |
| E501 | 11 |
| F401 | 4 |
| I001 | 3 |
| B023 | 2 |
| SIM115 | 1 |

A separate scope decision is required for lint cleanup or an explicit narrow
baseline gate exception. This directive performs neither and contains no lint
suppression. Any proposed exception must identify the exact frozen list,
maintainer owner, reason, follow-up and expiry, require affected-file lint and
zero introduced diagnostics, and never cover new source defects or prohibited
typing/invariant behavior. A baseline listing is not itself approval.

WVR-001's unchanged timing failure persists. Keep that decision deferred until
other gates have a defensible disposition; its existing all-other-gates-pass
condition is presently unmet. No exception, acceptance or delivery follows from
this directive or an independently sound collision delta.

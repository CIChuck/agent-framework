# REM-003 Implementation Report

Status: Stable correction candidate prepared; fresh independent validation required
Date: 2026-09-27
Branch: `feature/friday-mcp-ws02-lifecycle`
Remediator: separate Codex agent `/root/mcp_ws02_rem003`
Authorization revision: `0ab969275561b1c239d54c786074fdc8e900766c`
Failed candidate: `5a2856dea0f57208906fbd6eae5419d716bbf55a`
Directive: [Approved REM-003](../remediation/REM-003-directive.md)
Finding: [VAL-005 F-001](../validation/VAL-005-report.md#f-001--high-startup-retry-discards-ownership-after-cleanup-failure)
Candidate identity: the local commit containing this report; the controller pins
its full hash and exact delta/aggregate ranges in the fresh validation request.

## F-001 Correction

`RuntimeMCPProvider.start()` attempts public cleanup through its existing
manager before constructing a replacement. A failed or cancelled cleanup
propagates and leaves that manager reachable, regardless of started or client
connection flags. No additional client is constructed during a blocked retry.
After successful cleanup, the existing approved startup path may construct the
next manager and discover tools.

`DIContainer.boot()` constructs an MCP provider only when its owner slot is
empty. Failed boot retries reuse the retained provider, so public
`RuntimeKernel.stop()` continues to reach the original manager and every retained
client. This also preserves the provider after successful shutdown and recovery.
No public startup signature, configuration schema, package contract, or global
ownership mechanism changed.

`RuntimeMCPProvider.stop()` clears its untrusted handoff and resets its started
flag before attempting cleanup. Cleanup failure or cancellation therefore
retains ownership and safe diagnostic history without retaining a startup
handoff. Existing static cleanup errors still propagate. The manager continues
to drain successful peers while retaining any client whose cleanup fails.

## Exact Changed-Path Manifest

- `packages/friday-runtime/src/friday_runtime/mcp_loading.py`
- `packages/friday-runtime/src/friday_runtime/di.py`
- `packages/friday-runtime/tests_runtime/test_mcp_loading.py`
- `docs/planning/active/friday-mcp/execution/REM-003-implementation-report.md`
- `docs/planning/active/friday-mcp/execution/WS-02-implementation-report.md`

The WS-02 report has only a bounded status and ownership/cleanup correction.
Board, packet index, execution log, authority, historical VAL-005, kernel source,
MCP source, config, metadata, and other tests are excluded from this correction.

Unrelated work is preserved and excluded from staging: modified `.DS_Store`,
deleted `family-tree.md`, untracked `docker-bench-security/`,
`packages/friday-chat/config.example.yaml.pre-typed-llm-20260828.bak`, and
`packages/friday-sandbox/docker/Dockerfile.audit`.

## Regression Evidence

Five added cases first reproduced the pre-correction failure. Both provider
variants replaced their manager; both public-kernel variants replaced their
provider; the cancelled retry could not clean through the replaced owner.
After correction, all five pass alongside the 27 existing cases.

| Criterion | Deterministic regression/check evidence |
| --- | --- |
| REM-003-AC-01 | `test_provider_retry_retains_manager_until_cleanup_and_recovers[False/True]` proves discovery plus cleanup failure, unchanged manager/client count after retry, and retained transport despite false client connection state. |
| REM-003-AC-02 | `test_public_kernel_retry_retains_provider_and_stop_releases_every_client[False/True]` exercises public startup twice and proves unchanged provider, manager, and client count. |
| REM-003-AC-03 | The same kernel tests permit transport cleanup and use only public `kernel.stop()` to release all retained clients, before fixture teardown. Saved owner references are used for assertions, never to perform this cleanup. |
| REM-003-AC-04 | Both `with_peer=True` cases prove the successful peer drains while the failing peer remains owned; lifecycle and typed diagnostics remain inspectable, sentinel exception text is excluded, the handoff is empty, and failed MCP tools never enter the actual registry. |
| REM-003-AC-05 | Provider recovery succeeds directly after cleanup becomes possible; kernel stop then recovery succeeds. Repeated successful provider/kernel starts and DI boot retain the active owner, and repeated shutdown releases every client. `test_cancellation_during_retry_cleanup_preserves_owner_for_public_stop` proves bounded cancellation, retained ownership, and subsequent public cleanup. Existing optional/required failure, timeout, worker cancellation, caps, native registry, binding, workspace, and redaction cases pass. |
| REM-003-AC-06 | Exact five-path scope; affected Ruff and Python 3.13 mypy pass; no source suppression, private cross-package reach-through, public API, or config change. This report and the bounded WS-02 correction describe fail-closed retry and retained ownership. |

The in-process test fixture explicitly releases every synthetic transport and
receiver even when an assertion fails. The retry-cancellation test also drains
its task in `finally`. Required existing local fake-stdio tests were rerun;
their fixtures reap subprocesses even on assertion failure.

## Required Checks

Every uv command uses `UV_CACHE_DIR=/private/tmp/friday-uv-cache`. Python tests
also use `LITELLM_LOCAL_MODEL_COST_MAP=true`.

| Command | Result |
| --- | --- |
| `uv run pytest packages/friday-runtime/tests_runtime/test_mcp_loading.py -q` | 32 passed, 6.93 s |
| `uv run pytest packages/friday-core/tests_core packages/friday-mcp/tests_mcp packages/friday-runtime/tests_runtime tests/integration/test_mcp_runtime_lifecycle.py -q` | 321 passed, 11.74 s |
| `uv run pytest packages/friday-chat/tests_chat/test_mcp_config_compatibility.py packages/friday-chat/tests_chat/compat/test_config_compatibility.py packages/friday-chat/tests_chat/test_llm_config_migration.py -q` | 46 passed, 1.59 s |
| `uv run ruff check packages/friday-runtime packages/friday-mcp tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py` | Passed |
| `uv run mypy --python-version 3.13 packages/friday-runtime packages/friday-mcp tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py` | Passed, 42 source files |
| `uv run python scripts/friday-dev-board.py validate` | Passed, 23 tasks |
| `uv run python scripts/friday-dev-board.py render --check` | Passed |
| `uv run python scripts/check-documentation-lifecycle.py` | Passed after report additions, 331 Markdown files |
| `git diff --check` | Passed |

No required check was skipped. These are remediator implementation checks,
not an independent validation verdict or maintainer acceptance.

## Declared Baselines And Remaining Gates

- `uv run pytest tests/integration -q --tb=short`: 38 passed, one unchanged
  baseline failure at `test_development_board.py:75`; it expects 22 tasks,
  while canonical board validation reports 23. Elapsed: 9.34 s.
- `uv run mypy packages/friday-runtime packages/friday-mcp`: exit 2 at
  installed NumPy `__init__.pyi:737`, whose type-statement syntax requires
  Python 3.12+ while the repository's default target is Python 3.10. No
  project code is checked by that failed invocation; the prescribed Python
  3.13 check passes without weakening repository settings.
- `git diff --exit-code a64e423cffca6162c43b8cfa193792508cf87fd6 --
  tests/integration/test_development_board.py pyproject.toml`: passed,
  confirming the baseline test and target settings are unchanged.

No scope stop condition occurred. The correction remains local. No real
provider/MCP endpoint, credential use, paid model, remote transport, external
effect, push, merge, release, or deployment occurred. Registry insertion and
later workstreams remain separately controlled by their draft directives.

Controller must freeze this commit and obtain fresh independent REM-003 delta
and complete WS-02 aggregate review. VAL-005 remains historical evidence; its
decision is not reused for this changed candidate. Initiative remains `started`
and validation remains `changes_requested` until the controller records fresh
evidence. No self-validation, completion, acceptance, or delivery is claimed.

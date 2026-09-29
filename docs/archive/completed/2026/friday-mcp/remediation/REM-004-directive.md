# REM-004 — MCP-WS-02 Bounded Stdio Pipe And Process Cleanup

Status: Approved; separate remediator authorized, dispatch pending
Date: 2026-09-27
Approved at: 2026-09-28
Approved by: repository maintainer
Approval evidence: "aproved... make a list of next steps in our task queue"
Initiative: `friday-mcp`
Work unit: `MCP-WS-02`
Finding: [VAL-006 F-001](../validation/VAL-006-report.md#val-006-f-001--high-stdio-shutdown-can-hang-after-killing-a-child-with-paused-stdout)
Reviewed candidate: `26f4d7d4bfd0514b6eb76bed71cb4797da91a067`

## Authority And Role

Repository engineering and independent-validation policies, the approved
[WS-02 directive](../directives/ws-02-runtime-lifecycle-provider-loading.md),
its incorporated cleanup amendment, and the complete
[VAL-006 report](../validation/VAL-006-report.md) control this bounded correction.
The maintainer explicitly approved this directive and its separate remediator
on 2026-09-28. Approval covers only the stated finding, exact allowed files,
regressions, checks, and fresh independent review. The approval-recording turn
updates planning and the task queue only; no remediator is dispatched and no
product edits are made in that turn.

VAL-006 independently verifies REM-003's retained-owner correction, but the
complete WS-02 aggregate remains `CHANGES_REQUESTED`. Resource integrity and
untrusted subprocess behavior require separate remediation, not a silent repair
by the original builder or reviewer. Preserve REM-003's working ownership
behavior; do not undo it or count the deliberately perpetual synthetic kernel
disconnect observation as a second finding.

Authorized sequence: implement only the single numbered finding below, commit a
stable bounded candidate, and obtain fresh independent delta followed by
complete WS-02 aggregate review against accepted WS-01 checkpoint `a64e423`.
This is the second WS-02 remediation cycle. If its aggregate review
is unsuccessful, stop and return unresolved findings to the maintainer under
the policy's two-cycle rule; do not automatically launch another correction.

## VAL-006 F-001 — High: Finish Cleanup With Paused Output Pipes

The production transport has a five-second graceful-termination wait, but its
post-kill process wait has no deadline. A local child that emits oversized,
unterminated stdout and ignores SIGTERM can cause the receive task to stop and
the unread stdout pipe to pause. The child is killed, yet `Process.wait()`
continues waiting for pipe closure. Public `kernel.stop()` does not finish.
VAL-006 reproduces direct transport and public kernel paths, confirms retained
ownership, and explicitly drains/reaps every probe resource.

Required correction:

- Keep stdout/stderr pipe and process cleanup inside `StdioTransport`'s
  ownership boundary. Do not make runtime callers reach into MCP transport
  state or Python subprocess private internals.
- Ensure teardown makes progress after the MCP receiver stops, including
  oversized/unterminated output, already-exited children, graceful termination,
  and forced kill. Discard untrusted output without logging or persisting it.
- Use bounded incremental draining rather than accumulating arbitrary peer
  output in memory. Ensure any cleanup/drain tasks are explicitly owned and
  completed/cancelled as appropriate; avoid competing active readers.
- Document a finite teardown budget, including the post-kill wait and cleanup
  tasks. Preserve the existing graceful-termination policy unless a change is
  strictly necessary and documented. A watchdog that merely abandons owned
  resources is not a successful fix.
- If cleanup genuinely cannot complete, retain resources through their current
  explicit owner and raise a static, redacted error. Do not erase process/task
  references or report success prematurely. Later public shutdown must remain
  able to finish cleanup.
- Preserve cancellation propagation, repeated-disconnect safety, successful
  peer draining, REM-003 ownership/recovery, and existing connection/discovery
  deadlines, caps, workspace confinement, and native registration behavior.
- Correct the implementation report's cleanup claims and record precise
  before/after regression evidence and residual limits. No config schema or
  public startup signature change is required.

## Allowed Files

Product correction is limited to:

- `packages/friday-mcp/src/friday_mcp/client/stdio.py`
- `packages/friday-mcp/tests_mcp/client/test_lifecycle.py`
- `tests/integration/mcp_fake_server.py`
- `tests/integration/test_mcp_runtime_lifecycle.py`

The remediator may add
`docs/planning/active/friday-mcp/execution/REM-004-implementation-report.md`
and make a bounded cleanup/status correction in
`docs/planning/active/friday-mcp/execution/WS-02-implementation-report.md`.
Controller owns review requests, historical review status notes, board, packet
index, and execution log. Do not change MCP base/manager/adapter source,
runtime/kernel/DI source, configuration models, metadata, authority documents,
historical reviewer findings, or unrelated tests. Stop before expanding this
exact scope if implementation proves another file is necessary.

## Regression And Acceptance Criteria

- `REM-004-AC-01`: Direct real stdio transport teardown completes within its
  documented finite termination budget after a local child ignores SIGTERM
  and fills stdout with oversized/unterminated content. Forced kill releases
  process, pipe, and owned task state without manual caller pipe intervention.
- `REM-004-AC-02`: The real public kernel path completes normal discovery then
  public shutdown against that peer, releasing its manager/client/transport
  state without saved/private owner references for the asserted cleanup.
- `REM-004-AC-03`: A discovery/partial-startup failure variant with paused
  output also finishes public cleanup and leaves no child or worker/receiver/
  drain task behind. No failed tool is registered.
- `REM-004-AC-04`: Large stdout and stderr output is discarded with bounded
  memory; raw sentinel peer content, command/argument/environment values, and
  exception details do not appear in logs or lifecycle diagnostics.
- `REM-004-AC-05`: Cancellation, already-exited child cleanup, repeated
  disconnect/start/stop, spawn cancellation, EOF, configured RPC timeouts,
  successful peer draining, and all REM-003 retained-owner/recovery regressions
  still pass. Genuine incomplete cleanup preserves inspectable ownership and
  a later successful public cleanup path.
- `REM-004-AC-06`: Exact six-path source/test/report scope, compatible public
  signatures/configuration, meaningful typing, no new broad suppression, no
  private cross-package or subprocess reach-through, and accurate documentation.

Use only deterministic in-process doubles and authorized local synthetic
stdio subprocesses. Tests must document their wall-clock bound relative to
the implementation's teardown budget; VAL-006's seven-second detector is not
a new universal two- or seven-second shutdown SLA. Avoid sleep-only races:
coordinate observable readiness/output states when feasible. Fixture teardown
must reap/drain its own synthetic resources even if a regression assertion
fails, and must not be mistaken for successful public cleanup under test.

## Required Checks

All uv commands use `UV_CACHE_DIR=/private/tmp/friday-uv-cache`; tests and
diagnostic imports also use `LITELLM_LOCAL_MODEL_COST_MAP=true`.

```text
uv run pytest packages/friday-mcp/tests_mcp/client/test_lifecycle.py tests/integration/test_mcp_runtime_lifecycle.py -q
uv run pytest packages/friday-runtime/tests_runtime/test_mcp_loading.py -q
uv run pytest packages/friday-core/tests_core packages/friday-mcp/tests_mcp packages/friday-runtime/tests_runtime tests/integration/test_mcp_runtime_lifecycle.py -q
uv run pytest packages/friday-chat/tests_chat/test_mcp_config_compatibility.py packages/friday-chat/tests_chat/compat/test_config_compatibility.py packages/friday-chat/tests_chat/test_llm_config_migration.py -q
uv run pytest tests/integration -q --tb=short
uv run ruff check packages/friday-runtime packages/friday-mcp tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py
uv run mypy packages/friday-runtime packages/friday-mcp
uv run mypy --python-version 3.13 packages/friday-runtime packages/friday-mcp tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py
uv run python scripts/friday-dev-board.py validate
uv run python scripts/friday-dev-board.py render --check
uv run python scripts/check-documentation-lifecycle.py
git diff --check
```

Keep the declared default-target NumPy mypy failure and integration board-count
failure separate from regressions; do not fix those unrelated baselines.
Fresh independent review must reproduce the production direct/public-kernel
cleanup scenarios, reassess the full WS-02 aggregate, and verify pinned
authority/candidate stability. Passing existing tests alone does not close F-001.

## Non-Goals And Stops

No tool registry insertion, final filters, schema sanitization, Chat turn
behavior, execution provenance, memory/transcript storage, telemetry emitters,
CLI, resources/prompts, remote transport, server exposure, refresh, or external
includes. No live MCP/provider endpoint, credentials, paid call, external
effect, opportunistic refactor, workspace cleanup, push, merge, release, or
deployment. WS-03 and later workstreams remain separately controlled drafts.

Stop before product editing if this directive/separate remediator is not
approved, the candidate/authority is unstable, or the correction requires more
source/test files, public signature/schema changes, private boundary access,
global ownership, or broader lifecycle redesign. Report the exact authority
decision required. Initiative remains `started` and local; no acceptance or
delivery follows from this correction.

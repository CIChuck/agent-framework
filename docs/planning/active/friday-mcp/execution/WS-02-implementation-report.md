# MCP-WS-02 Implementation Report

Status: VAL-005 changes requested; REM-003 correction prepared for fresh validation
Date: 2026-09-27
Branch: `feature/friday-mcp-ws02-lifecycle`
Authorization revision: `5c31f7c`
Predecessor accepted checkpoint: `a64e423`
Directive: [Approved WS-02 with cleanup amendment](../directives/ws-02-runtime-lifecycle-provider-loading.md)

## Implementation And Boundaries

- `register_runtime_tools` remains synchronous and registers native providers.
  DI boot separately awaits `RuntimeMCPProvider.start()` before kernel binding
  validation. Public runtime startup signatures are unchanged. Repeated
  successful DI boot does not replace a live owner.
- New public runtime module `friday_runtime.mcp_loading` owns one explicit
  `MCPClientManager`. `RuntimeKernel.mcp_provider` exposes the owner and typed
  diagnostics even after failed startup. REM-003 corrects failed-start retry:
  DI reuses its provider, and provider startup completes cleanup through its
  existing manager before replacement. Cleanup failure retains the owner and
  propagates. There is no global manager or new package dependency.
- Only server-specific stdio inputs reach protocol-local config, never the
  full Friday config. Cwd is revalidated at startup and defaults to the
  configured workspace. This scopes cwd, not arbitrary executable behavior
  or arguments through an OS filesystem sandbox.
- Discovery uses bounded batches. Connection retries share one effective
  deadline: `min(server.timeout_seconds, limits.connection_timeout_seconds)`.
  Discovery gets the same deadline separately. Stdio config timeout reaches
  internal RPC waits without the old hidden 30-second cap.
- Optional connection/list failures and timeouts are diagnosed and skipped;
  required failures abort startup and release successful peers. Disabled
  servers are not constructed. `auto_connect: false` skips optional servers
  and fails when an enabled required server would be skipped. Cleanup failure
  is fatal even for optional servers; failed clients remain owned for retry.
- Count and byte caps produce deterministic, size-bounded untrusted JSON
  handoffs in configured server/catalog order. Pre-registry schema token
  accounting conservatively reserves one token per encoded byte. Final
  model-aware schema cost, naming/collisions, filters, sanitization, and
  executable registry entries belong to WS-03. Invalid/oversized definitions
  are rejected before handoff. Peer content is absent from diagnostics and
  model context, and excluded from handoff representations.
- `MCPDiscoveryState` records safe server state/counts/codes;
  `MCPProviderDiagnostics` records startup counters. Typed
  `MCPServerLifecycleDiagnostic` distinguishes disabled, auto-connect skipped,
  connected, connection/list failure, timeout, cancellation, and cleanup
  failure. Diagnostics contain no raw exceptions, env, args, paths, stderr,
  or peer content.
- `registered_tools` and `selected_tools` stay zero. Real binding validation
  runs after discovery and rejects MCP names absent from the actual registry.
  Discovery success does not mean MCP tools are executable in agents or Chat.

## Cleanup And API Compatibility

Changed MCP source: `client/base.py`, `client/stdio.py`, `client/manager.py`.
Changed runtime source: `di.py`, `kernel.py`, `tool_loading.py`, new
`mcp_loading.py`. No adapter, core contract, Chat, memory, transcript,
telemetry, CLI, or server-exposure implementation changed.

Partial startup and cancellation now use public cleanup regardless of the
success flag. Receiver tasks and pending requests are cleared. EOF/malformed
messages terminate the receiver instead of busy-looping or logging peer
exceptions. Stdio drains stderr without logging/storing it, handles exited
processes, and reaps children when cancellation races subprocess creation.
Worker cancellation is drained before manager shutdown. Shutdown is
idempotent and retains safe diagnostic history. REM-003 clears the untrusted
handoff and started flag before cleanup, including failed or cancelled cleanup;
the retained manager remains reachable for another shutdown attempt.

Manager adds `connect_or_raise` while preserving legacy boolean `connect` and
unknown-server `KeyError`. Repeated connects do not replace live clients.
Disconnect failures now propagate instead of silently dropping ownership;
`disconnect_all` attempts other peers, retains failed clients, and reports a
static cleanup error. Embedders that relied on swallowed cleanup errors should
handle that failure and retry cleanup. Successful stdio/SSE APIs remain;
SSE transport was not changed or tested live.

The three touched MCP source modules no longer carry `# mypy: ignore-errors`.
Suppressions in untouched protocol/config/adapter/SSE modules remain separate
legacy debt, not evidence of strong typing.

## Verification

Python tests use `LITELLM_LOCAL_MODEL_COST_MAP=true` and
`UV_CACHE_DIR=/private/tmp/friday-uv-cache`; other uv checks use the cache
override. No provider call, credential use, remote MCP connection, paid model,
push, merge, release, or deployment was performed.

- Core/MCP/runtime tests plus
  `tests/integration/test_mcp_runtime_lifecycle.py`: **316 passed**, including
  54 new lifecycle checks, 15 of them local-subprocess integration cases.
  New kernel tests stub unrelated LLM/storage services; real native registry,
  agent binding validation, and MCP transport/lifecycle paths are exercised.
- Existing Chat MCP config/legacy config/LLM migration tests: **46 passed**.
  This proves config compatibility, not MCP Chat turn integration.
- Ruff on both affected packages and the two integration files: **passed**.
- Mypy `--python-version 3.13` on those packages/files: **passed**, 42 files.
- Default-target mypy: known installed NumPy `__init__.pyi:737` syntax failure;
  the repository target is 3.10 while that stub needs Python 3.12+. Checking
  stops before project code. No typing settings were weakened.
- Broad integration initially: **36 passed, 1 known baseline failure** before
  adding the final two cancellation cases. The unchanged board test expects
  22 tasks but the accepted baseline already has 23. Final broad recheck and
  planning checks are recorded in the execution log.

Builder-stage fixture corrections created required runtime roots, explicitly
enabled native providers in partial configs, and handled expected receiver
cancellation in the EOF test. Local integration fixtures reap their own
processes even on assertion failure. These corrections are not formal-review
remediation.

## Remaining Gates

VAL-005 found startup-retry ownership loss in the original candidate. The bounded
[REM-003 report](REM-003-implementation-report.md) records the correction and
new provider/public-kernel regressions. Freeze the correction candidate, then
obtain fresh-context read-only independent delta and complete WS-02 aggregate
review of the exact diff and approved authority. Implementation checks do not
establish independent `VERIFIED`, maintainer acceptance, wider initiative
completion, or delivery authority. WS-03 and later remain Draft.

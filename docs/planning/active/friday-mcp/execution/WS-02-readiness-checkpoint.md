# MCP-WS-02 Readiness Checkpoint And Proposed Scope Amendment

Status: Original WS-02 approved; implementation stopped; amendment proposed only
Date: 2026-09-27
Maintainer decision: "ws-02 approved"
Branch: `feature/friday-mcp-ws02-lifecycle`
Baseline: `a64e423cffca6162c43b8cfa193792508cf87fd6`
Execution phase: `planning`
Validation state: `not_ready`

## Approved Boundary

The [WS-02 directive](../directives/ws-02-runtime-lifecycle-provider-loading.md)
authorizes runtime-owned connection, discovery, bounded startup, redacted
diagnostics, and shutdown. WS-00 and WS-01 are independently verified and
maintainer-accepted. This approval does not authorize WS-03, Friday Chat turns,
memory, transcript, telemetry emitters, resources/prompts, external includes,
remote services, or delivery operations.

No WS-02 source or tests were modified. This checkpoint is planning and
diagnostic evidence, not a candidate freeze or independent validation result.

## Evidence And Stop Condition

1. `packages/friday-mcp/src/friday_mcp/client/base.py:74-83` creates and connects
   a transport and starts its receiver before completing the handshake.
   `disconnect()` at lines 90-106 returns immediately when `_connected` is
   false. A handshake exception or timeout therefore leaves cleanup outside
   the public API's effective behavior. Manager retention and calls to public
   `disconnect()` alone cannot repair this.
2. A read-only, in-process diagnostic subclass returned a fake transport from
   `_create_transport()` and raised a synthetic exception from `_initialize()`.
   After `connect()` raised and public `disconnect()` returned, the observed
   result was:

   ```text
   transport_still_connected: True
   disconnect_calls: 0
   receiver_still_present: True
   ```

   The probe then canceled/awaited its fake receiver and explicitly disconnected
   the fake transport. It ran with `LITELLM_LOCAL_MODEL_COST_MAP=true` and
   `UV_CACHE_DIR=/private/tmp/friday-uv-cache`; no external connection or
   subprocess occurred. This reproduces a lifecycle defect, not a live-server
   interoperability result.
3. `packages/friday-mcp/src/friday_mcp/client/stdio.py:57` logs command and raw
   arguments. Line 121 logs raw server stderr. Safe runtime diagnostics cannot
   suppress these lower-layer logs when debug logging is enabled. No actual
   secrets were used or printed in this inspection.
4. Stdio disconnect at lines 73-89 unconditionally terminates a retained
   process; an already-exited process also needs safe, idempotent cleanup.

The directive's allowed MCP source modules are manager and adapter only. Its
stop condition prohibits proceeding when cleanup cannot be guaranteed after
partial startup. Cross-package inspection/mutation of private transport state,
global logger suppression, or recreating a parallel transport in runtime is
not an acceptable workaround.

## Proposed Amendment — Not Yet Authorized

Add only these source files to the WS-02 allowed scope:

- `packages/friday-mcp/src/friday_mcp/client/base.py`
- `packages/friday-mcp/src/friday_mcp/client/stdio.py`

Changes would be limited to the existing WS-02 lifecycle and redaction duties:

- Make public client cleanup effective after partial connect, handshake
  failure, timeout, cancellation, and normal shutdown. Release owned receiver
  tasks, pending requests, and transport state without changing public runtime
  startup signatures or reaching into private state across package boundaries.
- Make stdio process/stderr-task cleanup safe when startup fails or the process
  has already exited, and idempotent on repeated shutdown.
- Remove raw command/argument/stderr logging and use static, bounded lifecycle
  diagnostics. Continue draining stderr without persisting its content. Audit
  touched receive/error paths so untrusted payloads or exception messages are
  not logged as diagnostics.
- Preserve successful programmatic MCP use and the existing SSE API; integrated
  runtime remains stdio-only. No protocol-version migration, SSE transport
  rewrite, new server exposure, live refresh, or tool-execution feature is
  included.
- Apply meaningful typing to touched code; do not add or extend broad source
  suppressions. Record any remaining legacy typing debt separately rather than
  treating ignored modules as strong validation evidence.

The existing package-test directories already allowed by the directive would
receive regressions for failed/timeout/canceled handshake cleanup, receiver
cleanup, already-exited subprocesses, repeated disconnect, successful stdio
startup/shutdown, and sentinel-secret absence from captured debug logs. The
fake stdio integration test remains local and deterministic; no credentials,
real MCP service, paid model, or external effects are authorized.

Before resuming code generation, record the maintainer's amendment decision
and reconcile the directive/tactical plan's WS-02/WS-03 handoff. Canonical
naming, collision rules, final filters/schema sanitization, and registry
insertion must remain clearly assigned to WS-03; WS-02 may preserve bounded
discovered state using the directive's explicit handoff option. Do not claim
discovered tools are usable by agents before registration is implemented.

After implementation, commit a stable candidate and obtain fresh-context,
read-only independent validation under the repository policy. Neither this
checkpoint nor the original approval establishes completion or acceptance.

## Planning Validation

- Development board validation: passed, 23 tasks.
- Generated dashboard check: passed.
- Documentation lifecycle/link validation: passed, 327 Markdown files.
- Diff whitespace check: passed.

No implementation test suite or independent WS-02 review was run: product
source/tests remain unchanged and there is no WS-02 candidate to review.

## Preserved Unrelated Work

At inspection, the unrelated worktree manifest was:

```text
 M .DS_Store
 D family-tree.md
?? docker-bench-security/
?? packages/friday-chat/config.example.yaml.pre-typed-llm-20260828.bak
?? packages/friday-sandbox/docker/Dockerfile.audit
```

These paths are not part of the amendment, staging, or delivery scope.

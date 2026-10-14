# REM-MCP-UP-006: Server header errors and stdio ownership

Status: **proposed; remediation implementation authority not granted**.

This is a bounded correction of the fresh full-unit MCP-UP-05 review in
[VAL-UP05-01](../validation/VAL-UP05-01/report.md). The original report and raw
probes remain immutable. The approved CD-MCP-UP-005 and AMEND001/002 continue to
control all unaffected behavior; no scope or specification exception is added.
The reviewer-reproduced findings below are the sole remediation objectives.

## Separation and authorization

A separate remediator is required for the security/resource-lifecycle/architecture
finding under [independent validation policy](../../../../reference/policies/independent-validation-policy.md).
The original builder may prepare this packet and preserve evidence, but will not
repair these sources or approve the result. Exact maintainer approval of this
directive/profile/manifest is the final prerequisite for source changes.

## Exact product scope

Only these six existing paths may change; all are already within the original
18-path UP-05 budget:

- `packages/friday-mcp/src/friday_mcp/server/http_policy.py`
- `packages/friday-mcp/src/friday_mcp/server/modern_stdio.py`
- `packages/friday-mcp/tests_mcp/server/test_streamable_http.py`
- `packages/friday-mcp/tests_mcp/server/test_modern_stdio.py`
- `packages/friday-mcp/tests_mcp/server/test_server_lifecycle.py`
- `docs/guides/18-mcp-server.md`

No other product file, client/legacy server/Core/Runtime/Chat/telemetry source,
metadata, dependency, guard, runner or installed distribution may change.
Process-only preconstruction/final mappings, reports and raw receipts are allowed
in this packet. Preserve the six unrelated shared-checkout hashes and two-task/
three-event board overlay. No broad stage/reset/stash/clean or protected-state read.

## Required bounded corrections

1. VAL-UP05-004: Recognized mirrored parameter headers with CR/LF/NUL, invalid characters or
   duplicates must fail closed before any handler and return exact HTTP400 with
   JSON-RPC HeaderMismatch -32020. Retain byte bounds, authentication, Host/Origin,
   TLS, Base64 decoding and standard-header/body equality. Do not leak header
   values or relax generic HTTP/access validation to satisfy a code assertion.
2. VAL-UP05-003: Capture the stdio frame's original absolute deadline when its first byte is
   received. Partial/oversized frame accumulation and completion cannot refresh
   the budget. A late completed frame must not invoke a handler. Preserve idle
   connection behavior, fragmentation, subsequent valid frames where safe, EOF
   cleanup, actual wire caps and the configured lower-only budgets.
3. VAL-UP05-001: Error/oversize/rejection response writes must not block the
   stdio reader's processing of cancellation or EOF. Use explicitly bounded
   connection-owned output work with serialized writes and original deadlines.
   No unbounded queue/executor, task shedding or handler replay.
4. VAL-UP05-002: Track the serving loop and every asynchronous write/owner under
   its captured connection generation and owned signal registrations, including cancellation-resistant drains
   and lock waits. Shutdown must report incomplete settlement and block restart
   while old owners remain. An old serve finalizer, write callback, EOF or
   cancellation must never clear, stop, close or publish into a newer connection.
   Require connection-token ownership checks for teardown as well as response
   emission and ID-map removal. No false quiescence or stale cleanup.

## Preconstruction and regression evidence

Before changing source, the separate remediator reads the exact authority chain,
reviewed candidate/diff, both changed source modules and their public lifecycle/
protocol dependencies, all six allowed files and the review's original probes.
Freeze a prospective finding-to-field/clause/source/test/command plan. Extend the
corrected modern2026 actual mapping without modifying original controls or the
historical wrong2025 plan. Each finding appears once in the finding ledger below.

Tests must independently reproduce malformed recognized parameter headers with
zero-handler counts and exact wire codes; partial frames spanning a short original
deadline with zero invocation; cancellation received while an error/oversize/
rejection write is blocked; cancellation-resistant error drain and truthful owners;
failed stop/restart blocking until settlement; released old owners unable to close
or corrupt the new connection; EOF/partial-start/native subprocess shutdown and
multiple simultaneous writers/operations under budgets1..4. Use events/counters
and actual synthetic streams, not an assertion that mirrors a helper implementation.
Keep existing positive fragmentation, JSON-only stdout, handler output, real SDK
stdio/TLS JSON/SSE, and cancellation-isolation regressions.

## Verification and acceptance criteria

Each numbered finding must resolve with concrete new regression assertions and
preserved original probe evidence. All12 original SRV-AC criteria remain required.
Repeat the unchanged20-check profile on a stable committed corrected candidate,
plus explicit-column Mypy comparisons, the supplemental finding probes and all
22009 library-file/192-distribution hashes captured before the first check and
after the last check. The corrected-candidate review must independently satisfy
this chronology; historical samples taken during checks are not before-first evidence. Exact327 root Ruff full
objects/fixes,4 Mypy diagnostics including columns, full skip locations/reasons
and warnings must match the freshly executed accepted baseline; changed/narrow
Ruff and Mypy remain clean. Preserve19 metadata and60 accepted product hashes.

A **fresh-context read-only remediation delta review followed by full UP-05 review**
must return VERIFIED before any unit completion proposal. Validator receives all
18 current product paths, all12 criteria and all20 checks, not just six correction
files. Acceptance belongs to the maintainer. Whole MCP/UP06 aggregate closeout,
Langfuse and remote delivery remain later gates.

## Effects, non-goals and stop conditions

Only already-approved synthetic Friday subprocess stdio, literal127.0.0.1 ephemeral
verified TLS JSON/SSE and deterministic/ASGI fixtures under the unchanged private
guard/environment may run. No public DNS/network, user stores/real tools/providers,
ambient secrets, install/sync/shared environment writes, non-loopback listener,
OAuth/session/Tasks/callback features, new metadata, publication or deployment.
Store exact raw failures/results and safe explicit evidence allowlists; exclude
runtime caches/stores/private keys. Do not edit any prior report/control/source
capture or rewrite a failure into a pass. Stop on scope ambiguity/unexpected
external effects and after two unsuccessful formal remediation cycles.

## Original numbered finding ledger

```json
{
  "id": "VAL-UP05-001",
  "number": 1,
  "severity": "high",
  "title": "Inline stdio rejection writes block cancellation processing",
  "classification": [
    "security",
    "resource lifecycle",
    "transport architecture"
  ],
  "locations": [
    {
      "path": "packages/friday-mcp/src/friday_mcp/server/modern_stdio.py",
      "line": 148
    },
    {
      "path": "packages/friday-mcp/src/friday_mcp/server/modern_stdio.py",
      "line": 197
    },
    {
      "path": "packages/friday-mcp/src/friday_mcp/server/modern_stdio.py",
      "line": 105
    }
  ],
  "criteria": [
    "SRV-AC-04",
    "SRV-AC-07"
  ],
  "violated_requirements": [
    {
      "path": "docs/planning/active/friday-mcp-protocol-upgrade/up05-server-contract.md",
      "line": 101,
      "requirement": "Concurrent owned dispatch keeps the reader responsive to cancellation."
    },
    {
      "path": "docs/planning/active/friday-mcp-protocol-upgrade/up05-server-contract.md",
      "line": 153,
      "requirement": "Bound admission/lock waits and preserve connection-owned cancellation and unrelated operation progress."
    }
  ],
  "normative_source": {
    "capture": "specification--2026-07-28--basic--transports--stdio.md",
    "line": 86,
    "requirement": "Servers should stop work on cancelled requests as soon as practical; cancellation messages share the stdio reader."
  },
  "observation": "With one admitted synthetic held handler, {} followed by a cancellation notification enters inline writer.drain(). At40ms the cancellation remains buffered (84 bytes), handler has not seen cancellation and core ownership is1. Releasing the writer immediately allows cancellation to settle. The same inline path handles malformed, duplicate-active-ID, admission-rejection and oversized frames. A default timeout can therefore defer a cooperative cancellation for up to30 seconds solely because an unrelated error write is backpressured.",
  "evidence": [
    "checks/independent-probes/stdout",
    "checks/independent-probes-final/stdout",
    "checks/independent-probes-final/receipt.json",
    "test_independent_probes.py::test_blocked_rejection_stalls_stdio_cancellation"
  ],
  "risk": "Peer-controlled malformed traffic and stdout backpressure can prevent the reader from observing cancellation and EOF promptly, retaining admitted handler effects and preventing unrelated messages from progressing.",
  "required_bounded_mitigation": "Move rejection delivery off the read loop into explicitly bounded connection-owned output work. Preserve serialized writes and original deadlines, prevent unbounded rejection tasks/queues, and keep the reader able to consume valid cancellation and EOF while any response drain or output lock is blocked. Coordinate this with VAL-UP05-002; do not add a thread/executor, replay or public side effect.",
  "required_tests": [
    "Held cooperative handler plus blocked malformed-frame rejection: process cancellation promptly before releasing output.",
    "Repeat for duplicate active ID, admission-limit and oversized-frame rejection with limits1..4; assert no duplicate handler and bounded owners/output work.",
    "EOF/stop while a rejection drain or output lock is blocked; no orphan tasks or stale writes."
  ],
  "documentation_configuration_impact": "Reconcile guide18 responsive-cancellation/ownership claims and tests with final behavior; no default/config enum/dependency change.",
  "remediation_role": "Separate remediator required by independent-validation policy because this is security and transport architecture."
}
```

```json
{
  "id": "VAL-UP05-002",
  "number": 2,
  "severity": "high",
  "title": "Untracked stdio serving work permits false shutdown and stale cleanup of a newer connection",
  "classification": [
    "security",
    "resource lifecycle",
    "transport architecture",
    "state integrity"
  ],
  "locations": [
    {
      "path": "packages/friday-mcp/src/friday_mcp/server/modern_stdio.py",
      "line": 47
    },
    {
      "path": "packages/friday-mcp/src/friday_mcp/server/modern_stdio.py",
      "line": 71
    },
    {
      "path": "packages/friday-mcp/src/friday_mcp/server/modern_stdio.py",
      "line": 215
    }
  ],
  "criteria": [
    "SRV-AC-04",
    "SRV-AC-07"
  ],
  "violated_requirements": [
    {
      "path": "docs/planning/active/friday-mcp-protocol-upgrade/up05-server-contract.md",
      "line": 104,
      "requirement": "An old task cannot publish into a newer connection or remove a newer owner."
    },
    {
      "path": "docs/planning/active/friday-mcp-protocol-upgrade/up05-server-contract.md",
      "line": 155,
      "requirement": "Stop cancels and settles owned tasks; incomplete settlement retains honest bounded owners and blocks unsafe restart until explicit retry drains them."
    }
  ],
  "normative_source": {
    "capture": "specification--2026-07-28--basic--transports--stdio.md",
    "line": 107,
    "requirement": "Servers should exit promptly when stdin closes or EOF occurs; the stronger truthful-owner/restart requirement is explicitly in the approved contract."
  },
  "observation": "A cancellation-resistant malformed-frame drain remains pending after the30ms operation budget. stop() nevertheless returns success: old serving task is unfinished, core owners0, dispatchers0, writer cleared. A second serve() is admitted and replies to new. Releasing the old drain runs the old serve finally: its unconditional self.stop() closes the new writer/connection and finishes the new serving task.",
  "evidence": [
    "checks/resistant-rejection-probe/stdout",
    "checks/resistant-rejection-probe/receipt.json",
    "checks/independent-probes-final/stdout",
    "checks/independent-probes-final/receipt.json",
    "test_independent_probes.py::test_resistant_rejection_writer_untracked_shutdown_and_stale_restart"
  ],
  "risk": "Shutdown reports an inaccurate terminal state; an old task can tear down a healthy replacement connection. This is a demonstrated ownership-generation violation, even though normal cooperative subprocess fixtures pass.",
  "required_bounded_mitigation": "Track the serving loop and all rejection/response output work under their original connection generation, including cancellation-resistant drain/lock work. Incomplete stop must raise a fixed incomplete-cleanup error, retain honest ownership, and prohibit restart until retry drains it. Scope finally cleanup to its captured generation so an old task cannot close/remove new streams, transports, dispatchers or owners. Keep existing public async API and bounded budgets.",
  "required_tests": [
    "Cancellation-resistant rejection drain: stop reports incomplete and retains the old serving/output owner after timeout; start/serve is rejected until explicit release and retry.",
    "After drain and retry stop, new serve works; late old completion cannot close the replacement writer or remove new dispatchers.",
    "Stop/restart races and partial startup/read/write failures at limits1..4, with exact task/stream/connection counts."
  ],
  "documentation_configuration_impact": "Guide18 claims about truthful incomplete shutdown and restart must reflect all serving/output owners. No new configuration defaults, metadata or dependency changes.",
  "remediation_role": "Separate remediator required for security, architecture and state integrity; coordinate bounded ownership fix with VAL-UP05-001."
}
```

```json
{
  "id": "VAL-UP05-003",
  "number": 3,
  "severity": "medium",
  "title": "Stdio frame assembly starts a fresh deadline after body processing",
  "classification": [
    "security",
    "resource budgeting",
    "transport lifecycle"
  ],
  "locations": [
    {
      "path": "packages/friday-mcp/src/friday_mcp/server/modern_stdio.py",
      "line": 124
    },
    {
      "path": "packages/friday-mcp/src/friday_mcp/server/modern_stdio.py",
      "line": 181
    },
    {
      "path": "packages/friday-mcp/src/friday_mcp/server/modern_stdio.py",
      "line": 194
    }
  ],
  "criteria": [
    "SRV-AC-07",
    "SRV-AC-04"
  ],
  "violated_requirements": [
    {
      "path": "docs/planning/active/friday-mcp-protocol-upgrade/up05-server-contract.md",
      "line": 150,
      "requirement": "Deadline starts before operation waits/body processing and is never reset by phase."
    },
    {
      "path": "docs/planning/active/friday-mcp-protocol-upgrade/directives/CD-MCP-UP-005-modern-tools-server.md",
      "line": 91,
      "requirement": "SRV-AC-07 original absolute deadlines and bounded body work apply across the modern transport profile."
    }
  ],
  "normative_source": {
    "capture": "modelcontextprotocol.io--specification--2026-07-28--basic--patterns--cancellation.md",
    "line": 49,
    "requirement": "Timeout guidance is SHOULD; the violated mandatory stronger server-body deadline is the approved SRV-AC-07 contract."
  },
  "observation": "A discover frame split after20 bytes waits100ms with timeout_seconds0.03, then the remaining bytes/newline are delivered and the server returns a successful result. Frame read/assembly has no deadline, line() creates a new deadline after full assembly, and oversized/partial-EOF rejection also receives a new budget.",
  "evidence": [
    "checks/independent-probes/stdout",
    "checks/independent-probes-final/stdout",
    "checks/independent-probes-final/receipt.json",
    "test_independent_probes.py::test_partial_stdio_frame_absolute_deadline"
  ],
  "risk": "A peer can retain a partial or oversized frame indefinitely and reset the allowed request budget by eventually completing it. The configured deadline does not bound all body work as promised.",
  "required_bounded_mitigation": "Establish a connection-owned absolute deadline when a nonempty frame first arrives, retain it across split reads, assembly/oversize discard, parse, admission, handler and output, and reject/close an expired frame before any handler admission. Preserve indefinitely idle connections separately from an in-progress frame. Do not reset the deadline on newline or error handling.",
  "required_tests": [
    "Real or owned-stream split frame completing after a lowered deadline: no success and zero handler invocation.",
    "Many fragments before expiry followed by handler/output phases cannot extend the original budget.",
    "Oversized discard, partial EOF, idle connection, timeout cleanup, next-frame behavior and restart with limits1..4; no unbounded owner or task."
  ],
  "documentation_configuration_impact": "Clarify frame deadline semantics in guide18 while keeping current timeout defaults and lower-only ServerLimits.",
  "remediation_role": "Separate remediator required because the budget weakness is security-related; no self-repair."
}
```

```json
{
  "id": "VAL-UP05-004",
  "number": 4,
  "severity": "medium",
  "title": "Malformed recognized custom headers emit InvalidRequest instead of HeaderMismatch",
  "classification": [
    "protocol conformance",
    "HTTP security boundary"
  ],
  "locations": [
    {
      "path": "packages/friday-mcp/src/friday_mcp/server/http_policy.py",
      "line": 142
    },
    {
      "path": "packages/friday-mcp/src/friday_mcp/server/http_policy.py",
      "line": 152
    },
    {
      "path": "packages/friday-mcp/src/friday_mcp/server/http.py",
      "line": 245
    },
    {
      "path": "packages/friday-mcp/tests_mcp/server/test_server_security.py",
      "line": 142
    }
  ],
  "criteria": [
    "SRV-AC-05",
    "SRV-AC-06",
    "SRV-AC-01"
  ],
  "violated_requirements": [
    {
      "path": "docs/planning/active/friday-mcp-protocol-upgrade/up05-server-contract.md",
      "line": 110,
      "requirement": "Header failures are HTTP400/-32020; validate every recognized custom binding and reject duplicate headers before handler effects."
    },
    {
      "path": "docs/planning/active/friday-mcp-protocol-upgrade/up05-server-contract.md",
      "line": 120,
      "requirement": "Exact duplicate/case/sentinel and recognized Mcp-Param-* validation."
    }
  ],
  "normative_source": {
    "capture": "specification--2026-07-28--basic--transports--streamable-http.md",
    "line": 597,
    "requirement": "Header validation failure must return HTTP400 with JSON-RPC -32020. Recognized custom headers with invalid characters must be rejected, per lines553-560. Pinned HeaderMismatchError.error.code is -32020."
  },
  "observation": "For a registered string x-mcp-header:X binding, each CR/LF/NUL header value and conflicting case-insensitive duplicate Mcp-Param-X receives HTTP400 with code-32600/message Invalid request and no handler call. Only three standard metadata headers enter the -32020 branch; custom-header invalid bytes/duplicates are converted to HTTPAccessError and then the generic error. The existing generic duplicate test asserts only HTTP400, allowing the wrong code.",
  "evidence": [
    "checks/independent-probes/stdout",
    "checks/independent-probes-final/stdout",
    "checks/independent-probes-final/receipt.json",
    "test_independent_probes.py::test_recognized_header_invalid_char_exact_wire_code",
    "test_independent_probes.py::test_recognized_duplicate_header_exact_wire_code"
  ],
  "risk": "The endpoint violates its dated error contract and conceals the required HeaderMismatch category from clients/middleware. Rejection is fail-closed and all reproduced handler counts are0; no authorization bypass or replay was observed.",
  "required_bounded_mitigation": "Preserve fail-closed access handling while classifying malformed/duplicate recognized Mcp-Param-* metadata as fixed HeaderMismatch HTTP400/-32020 before any handler. Keep access-specific Host/Origin/bearer handling distinct and diagnostic values private; preserve no-id grammar when rejection happens before a body ID is safely read. No accepted client changes or SDK retry path.",
  "required_tests": [
    "Exact status, error code/message/field grammar and zero handlers for CR/LF/NUL/invalid characters and case-insensitive conflicting/equal duplicates on recognized custom bindings.",
    "Standard metadata header cases still return400/-32020; Host/Origin/bearer failures retain their exact access status and safe body.",
    "Raw/ASGI negatives complement real TLS JSON/SSE tests; bypass SDK automatic HeaderMismatch retries."
  ],
  "documentation_configuration_impact": "Guide18 exact HeaderMismatch claims remain controlling; update final field/assertion mapping and strengthen exact-code tests. No new headers or configuration defaults.",
  "remediation_role": "Separate remediator required for HTTP security-boundary code, under a bounded approved directive."
}
```

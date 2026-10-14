# Independent UP-05 full work-unit review

**Outcome: CHANGES_REQUESTED.** Four numbered findings remain, including two high-severity stdio transport/lifecycle failures. No product or controlling document was repaired by this reviewer.

## Candidate, reviewer and authority

- Candidate: `b57c25d9fc4933059f64ed836783291f5753b9a8`; base: `f876603c74d8a90639fb5dc90d287d17ab523705`.
- Reviewer: `/root/up05_fresh_full_validator`, independent fresh context; model: GPT-6/Codex (exact runtime service label is not exposed). Review date2026-10-13 UTC. Full read-only CD-MCP-UP-005/MCP-UP-05 work-unit review.
- Request: `docs/planning/active/friday-mcp-protocol-upgrade/validation-request-UP05.json`. Current controlling execution authority: `authority-UP-05-amendment-002.json`, SHA256 `0d1ccb9a5a68fa8b3be25c728cb4de7b08d8cd9bf62265a36caee30fb062d13f`.
- Read AGENTS.md and canonical repository engineering, lifecycle and independent-validation policies, original CD/contract/profile, original approval/authority/proposal and separate AMEND001/002 approval/authority/proposal/document chains. Preserved original proposed text is reconciled by explicit receipts, not silently rewritten. UP04 acceptance establishes the accepted product baseline only; its historical review is not this review's conclusion.
- Board/packet remains started/granted/local, with a fresh full review next gate and no completion/acceptance/publication grant. Full diff is retained as `candidate-full.diff`; exactly18 product paths change, and all other changed paths are planning/process/evidence. No protected user stores, ambient provider credentials, public network or installs/sync were used. The reviewer used the sparse private frozen snapshot because it already omits protected tracked state.

The original runner/guard remain immutable. `review_runner_final.py` changes only reviewer evidence/HOME/TMP/cache destinations; `runner-final-destination-only.diff` records every byte change. All20 commands use exactly the request argv and original environment allowlist/guard. Loopback fixture escalation was explicitly authorized. The runner wrapper's exit0 was never treated as child success; child exits below come from receipts. Executable `/venv/bin/python` is the exact request path and resolves pinned CPython3.13.10; the dispatch's nonexistent version-suffixed path was corrected with controller acknowledgment. `setup-observations.json` records the initial copy-preparation error and timing of hash samples without hiding it.

## Findings

### 1. VAL-UP05-001 — Inline stdio rejection writes block cancellation processing (high)

**Classification and role:** security, resource lifecycle, transport architecture. Separate remediator required by independent-validation policy because this is security and transport architecture.

**Location:** `packages/friday-mcp/src/friday_mcp/server/modern_stdio.py:148`, `packages/friday-mcp/src/friday_mcp/server/modern_stdio.py:197`, `packages/friday-mcp/src/friday_mcp/server/modern_stdio.py:105`.

**Violated authority:** SRV-AC-04, SRV-AC-07. `docs/planning/active/friday-mcp-protocol-upgrade/up05-server-contract.md:101`: Concurrent owned dispatch keeps the reader responsive to cancellation.; `docs/planning/active/friday-mcp-protocol-upgrade/up05-server-contract.md:153`: Bound admission/lock waits and preserve connection-owned cancellation and unrelated operation progress.

**Pinned normative source:** `specification--2026-07-28--basic--transports--stdio.md:86`: Servers should stop work on cancelled requests as soon as practical; cancellation messages share the stdio reader.

**Observed evidence:** With one admitted synthetic held handler, {} followed by a cancellation notification enters inline writer.drain(). At40ms the cancellation remains buffered (84 bytes), handler has not seen cancellation and core ownership is1. Releasing the writer immediately allows cancellation to settle. The same inline path handles malformed, duplicate-active-ID, admission-rejection and oversized frames. A default timeout can therefore defer a cooperative cancellation for up to30 seconds solely because an unrelated error write is backpressured. Evidence: `checks/independent-probes/stdout`, `checks/independent-probes-final/stdout`, `checks/independent-probes-final/receipt.json`, `test_independent_probes.py::test_blocked_rejection_stalls_stdio_cancellation`.

**Risk:** Peer-controlled malformed traffic and stdout backpressure can prevent the reader from observing cancellation and EOF promptly, retaining admitted handler effects and preventing unrelated messages from progressing.

**Required bounded mitigation:** Move rejection delivery off the read loop into explicitly bounded connection-owned output work. Preserve serialized writes and original deadlines, prevent unbounded rejection tasks/queues, and keep the reader able to consume valid cancellation and EOF while any response drain or output lock is blocked. Coordinate this with VAL-UP05-002; do not add a thread/executor, replay or public side effect.

**Required regression/verification coverage:**

- Held cooperative handler plus blocked malformed-frame rejection: process cancellation promptly before releasing output.
- Repeat for duplicate active ID, admission-limit and oversized-frame rejection with limits1..4; assert no duplicate handler and bounded owners/output work.
- EOF/stop while a rejection drain or output lock is blocked; no orphan tasks or stale writes.

**Documentation/configuration impact:** Reconcile guide18 responsive-cancellation/ownership claims and tests with final behavior; no default/config enum/dependency change.

### 2. VAL-UP05-002 — Untracked stdio serving work permits false shutdown and stale cleanup of a newer connection (high)

**Classification and role:** security, resource lifecycle, transport architecture, state integrity. Separate remediator required for security, architecture and state integrity; coordinate bounded ownership fix with VAL-UP05-001.

**Location:** `packages/friday-mcp/src/friday_mcp/server/modern_stdio.py:47`, `packages/friday-mcp/src/friday_mcp/server/modern_stdio.py:71`, `packages/friday-mcp/src/friday_mcp/server/modern_stdio.py:215`.

**Violated authority:** SRV-AC-04, SRV-AC-07. `docs/planning/active/friday-mcp-protocol-upgrade/up05-server-contract.md:104`: An old task cannot publish into a newer connection or remove a newer owner.; `docs/planning/active/friday-mcp-protocol-upgrade/up05-server-contract.md:155`: Stop cancels and settles owned tasks; incomplete settlement retains honest bounded owners and blocks unsafe restart until explicit retry drains them.

**Pinned normative source:** `specification--2026-07-28--basic--transports--stdio.md:107`: Servers should exit promptly when stdin closes or EOF occurs; the stronger truthful-owner/restart requirement is explicitly in the approved contract.

**Observed evidence:** A cancellation-resistant malformed-frame drain remains pending after the30ms operation budget. stop() nevertheless returns success: old serving task is unfinished, core owners0, dispatchers0, writer cleared. A second serve() is admitted and replies to new. Releasing the old drain runs the old serve finally: its unconditional self.stop() closes the new writer/connection and finishes the new serving task. Evidence: `checks/resistant-rejection-probe/stdout`, `checks/resistant-rejection-probe/receipt.json`, `checks/independent-probes-final/stdout`, `checks/independent-probes-final/receipt.json`, `test_independent_probes.py::test_resistant_rejection_writer_untracked_shutdown_and_stale_restart`.

**Risk:** Shutdown reports an inaccurate terminal state; an old task can tear down a healthy replacement connection. This is a demonstrated ownership-generation violation, even though normal cooperative subprocess fixtures pass.

**Required bounded mitigation:** Track the serving loop and all rejection/response output work under their original connection generation, including cancellation-resistant drain/lock work. Incomplete stop must raise a fixed incomplete-cleanup error, retain honest ownership, and prohibit restart until retry drains it. Scope finally cleanup to its captured generation so an old task cannot close/remove new streams, transports, dispatchers or owners. Keep existing public async API and bounded budgets.

**Required regression/verification coverage:**

- Cancellation-resistant rejection drain: stop reports incomplete and retains the old serving/output owner after timeout; start/serve is rejected until explicit release and retry.
- After drain and retry stop, new serve works; late old completion cannot close the replacement writer or remove new dispatchers.
- Stop/restart races and partial startup/read/write failures at limits1..4, with exact task/stream/connection counts.

**Documentation/configuration impact:** Guide18 claims about truthful incomplete shutdown and restart must reflect all serving/output owners. No new configuration defaults, metadata or dependency changes.

### 3. VAL-UP05-003 — Stdio frame assembly starts a fresh deadline after body processing (medium)

**Classification and role:** security, resource budgeting, transport lifecycle. Separate remediator required because the budget weakness is security-related; no self-repair.

**Location:** `packages/friday-mcp/src/friday_mcp/server/modern_stdio.py:124`, `packages/friday-mcp/src/friday_mcp/server/modern_stdio.py:181`, `packages/friday-mcp/src/friday_mcp/server/modern_stdio.py:194`.

**Violated authority:** SRV-AC-07, SRV-AC-04. `docs/planning/active/friday-mcp-protocol-upgrade/up05-server-contract.md:150`: Deadline starts before operation waits/body processing and is never reset by phase.; `docs/planning/active/friday-mcp-protocol-upgrade/directives/CD-MCP-UP-005-modern-tools-server.md:91`: SRV-AC-07 original absolute deadlines and bounded body work apply across the modern transport profile.

**Pinned normative source:** `modelcontextprotocol.io--specification--2026-07-28--basic--patterns--cancellation.md:49`: Timeout guidance is SHOULD; the violated mandatory stronger server-body deadline is the approved SRV-AC-07 contract.

**Observed evidence:** A discover frame split after20 bytes waits100ms with timeout_seconds0.03, then the remaining bytes/newline are delivered and the server returns a successful result. Frame read/assembly has no deadline, line() creates a new deadline after full assembly, and oversized/partial-EOF rejection also receives a new budget. Evidence: `checks/independent-probes/stdout`, `checks/independent-probes-final/stdout`, `checks/independent-probes-final/receipt.json`, `test_independent_probes.py::test_partial_stdio_frame_absolute_deadline`.

**Risk:** A peer can retain a partial or oversized frame indefinitely and reset the allowed request budget by eventually completing it. The configured deadline does not bound all body work as promised.

**Required bounded mitigation:** Establish a connection-owned absolute deadline when a nonempty frame first arrives, retain it across split reads, assembly/oversize discard, parse, admission, handler and output, and reject/close an expired frame before any handler admission. Preserve indefinitely idle connections separately from an in-progress frame. Do not reset the deadline on newline or error handling.

**Required regression/verification coverage:**

- Real or owned-stream split frame completing after a lowered deadline: no success and zero handler invocation.
- Many fragments before expiry followed by handler/output phases cannot extend the original budget.
- Oversized discard, partial EOF, idle connection, timeout cleanup, next-frame behavior and restart with limits1..4; no unbounded owner or task.

**Documentation/configuration impact:** Clarify frame deadline semantics in guide18 while keeping current timeout defaults and lower-only ServerLimits.

### 4. VAL-UP05-004 — Malformed recognized custom headers emit InvalidRequest instead of HeaderMismatch (medium)

**Classification and role:** protocol conformance, HTTP security boundary. Separate remediator required for HTTP security-boundary code, under a bounded approved directive.

**Location:** `packages/friday-mcp/src/friday_mcp/server/http_policy.py:142`, `packages/friday-mcp/src/friday_mcp/server/http_policy.py:152`, `packages/friday-mcp/src/friday_mcp/server/http.py:245`, `packages/friday-mcp/tests_mcp/server/test_server_security.py:142`.

**Violated authority:** SRV-AC-05, SRV-AC-06, SRV-AC-01. `docs/planning/active/friday-mcp-protocol-upgrade/up05-server-contract.md:110`: Header failures are HTTP400/-32020; validate every recognized custom binding and reject duplicate headers before handler effects.; `docs/planning/active/friday-mcp-protocol-upgrade/up05-server-contract.md:120`: Exact duplicate/case/sentinel and recognized Mcp-Param-* validation.

**Pinned normative source:** `specification--2026-07-28--basic--transports--streamable-http.md:597`: Header validation failure must return HTTP400 with JSON-RPC -32020. Recognized custom headers with invalid characters must be rejected, per lines553-560. Pinned HeaderMismatchError.error.code is -32020.

**Observed evidence:** For a registered string x-mcp-header:X binding, each CR/LF/NUL header value and conflicting case-insensitive duplicate Mcp-Param-X receives HTTP400 with code-32600/message Invalid request and no handler call. Only three standard metadata headers enter the -32020 branch; custom-header invalid bytes/duplicates are converted to HTTPAccessError and then the generic error. The existing generic duplicate test asserts only HTTP400, allowing the wrong code. Evidence: `checks/independent-probes/stdout`, `checks/independent-probes-final/stdout`, `checks/independent-probes-final/receipt.json`, `test_independent_probes.py::test_recognized_header_invalid_char_exact_wire_code`, `test_independent_probes.py::test_recognized_duplicate_header_exact_wire_code`.

**Risk:** The endpoint violates its dated error contract and conceals the required HeaderMismatch category from clients/middleware. Rejection is fail-closed and all reproduced handler counts are0; no authorization bypass or replay was observed.

**Required bounded mitigation:** Preserve fail-closed access handling while classifying malformed/duplicate recognized Mcp-Param-* metadata as fixed HeaderMismatch HTTP400/-32020 before any handler. Keep access-specific Host/Origin/bearer handling distinct and diagnostic values private; preserve no-id grammar when rejection happens before a body ID is safely read. No accepted client changes or SDK retry path.

**Required regression/verification coverage:**

- Exact status, error code/message/field grammar and zero handlers for CR/LF/NUL/invalid characters and case-insensitive conflicting/equal duplicates on recognized custom bindings.
- Standard metadata header cases still return400/-32020; Host/Origin/bearer failures retain their exact access status and safe body.
- Raw/ASGI negatives complement real TLS JSON/SSE tests; bypass SDK automatic HeaderMismatch retries.

**Documentation/configuration impact:** Guide18 exact HeaderMismatch claims remain controlling; update final field/assertion mapping and strengthen exact-code tests. No new headers or configuration defaults.

## Complete criterion assessment

Every criterion and the whole18-path source/test/documentation delta were evaluated. The table reports the bounded evidence examined; it does not turn an individual passing scenario into exhaustive conformance. Identified requirements remain unsatisfied even though every prescribed test command completed.

| Criterion | Assessment | Evidence examined |
| --- | --- | --- |
| SRV-AC-01 | Met boundary evidence except VAL-UP05-004 | protocol.py metadata/envelope/errors;489 focused tests and actual SDK stdio/TLS. AMEND002 complete required error data verified; inactive-32021 blocked. |
| SRV-AC-02 | Met in reviewed scenarios | Atomic _stage/replace_tools, immutable exports, page count/byte worst IDs, stale/forged/null/oversized cursors; registry snapshots and definitions fail before invocation. |
| SRV-AC-03 | Met in reviewed scenarios | Captured handler/schema, bounded args and result validation, null/scalar/mixed text ordering, safe errors and mutation while call issued; exact single counts. |
| SRV-AC-04 | Not met: VAL-UP05-001/002/003 | Real stdio framing/cooperative EOF/cancel/pipe/start/SIGTERM tests pass. Independent blocked/resistant output and slow assembly expose remaining failures. |
| SRV-AC-05 | Not met: VAL-UP05-004 | Actual TLS JSON/SSE/ASGI single endpoint,405/404/-32601/version400/-32022 pass. Recognized custom invalid/duplicate headers select wrong wire code. |
| SRV-AC-06 | Partly met; VAL-UP05-004 affects exact error grammar | Host/Origin/bearer/TLS/query/bind policies fail closed with zero calls, tokens nonrepr, no clientInfo trust. No OAuth conformance claimed. |
| SRV-AC-07 | Not met: VAL-UP05-001/002/003 | Core/HTTP original deadlines,1..4 admission and resistant owner retention pass. Stdio serving/error output and partial-body lifetime are incomplete. |
| SRV-AC-08 | Met in reviewed scenarios | Real public DefaultToolRegistry with synthetic async tools, typed Core public interfaces, filters/prefix/collision/schema snapshots and captured bound method. |
| SRV-AC-09 | Met in reviewed scenarios | 19 metadata/60 accepted product hashes unchanged; new public strict typed exports; preserved legacy constructors/version/config and optional HTTP import tests; no accepted client/Core/Runtime/Chat edit. |
| SRV-AC-10 | Met in reviewed scenarios | Optional TelemetryInterface only; fixed method/outcome and hashed trusted tool ID; one start/terminal for admitted cooperative handler; observer failures isolate effects; sentinels absent from diagnostics. |
| SRV-AC-11 | Required actual counterparts run and pass; semantic issues remain separately identified | SDK/mcp-types2.3.0 Client explicit2026/cacheNone/no callbacks/extensions, actual Friday subprocess stdio and verified private literal TLS JSON/SSE; counters/errors/cancel/disconnect/childexit. |
| SRV-AC-12 | Not met until findings corrected and fresh VERIFIED | 18-path diff and20 exact commands checked, unchanged dependencies/libraries/captures; prospective modern plan distinguished from invalid historical plan. Guide lifecycle/header assertions exceed actual behavior identified above. |

## Primary-source and schema assessment

All19 captured compressed and decompressed originals match artifact/content SHA256 and byte counts. Sources were read against the pinned upstream commit `271ecc9accafdd9b83a3c869fa67c22953b2af80`, with modern schema SHA256 `742750af0bb8c716e7030c4977c992b55d1adc4407e9e66997db5846baedc2cd`. Independent extraction verifies155 modern declarations/337 field references and separately145 historical2025 declarations/355 fields. The builder's declaration hashes/field locations and168 source/assertion pointers match the originals; pointer integrity is only an inventory check.

`independent-normative-inventory.json` contains all source text paragraphs with normative keywords and every complete declaration. Its366-paragraph inventory comprises the builder's316 Markdown paragraphs plus32 modern and18 historical schema-comment blocks. This difference is extraction scope, not50 new obligations or50 passing assertions. The actual modern obligations and conditional roles were independently assessed rather than accepted from the builder's disposition labels. `independent-role-field-assessment.json` records all155 declarations and337 field references with reviewer-owned role groups and source/test evidence.

Modern applicable requirements cover base JSON-RPC/IDs and complete/errors; per-request metadata/capabilities/version and self-reported identity; discovery even empty; stale private cacheable metadata; immutable complete tool/catalog/annotations and bounded pagination; argument/output schema evaluation and safe complete text/structured/error results; stateless POST JSON/SSE/header grammar; stdio framing/cancellation; and security/access/rate-limit/output/privacy/lifecycle requirements. The four findings arise from those active duties. AMEND0010/private cacheable fields and AMEND002 supported/requested errors and explicit requestState/inputResponses refusal have direct positive/negative SDK/source/test evidence and no new conflict found.

Optional server-to-client requests, MRTR input_required/input requests, sampling/roots/elicitation, subscriptions/list-change notifications, progress/logging RPCs, prompts/resources/completions/media, Tasks/extensions and OAuth authorization-server/resource-owner roles remain inactive. Their conditional fields are not claimed implemented. Notification metadata is nevertheless separately validated, supported request capability shapes are validated without exercising callbacks, and inactive-32021 construction is refused. Non-text and interactive output cannot be emitted by ToolCallResult. Icon rendering/fetching/intermediary forwarding, client fallback/cache/retry obligations and2025 handshake/session/Tasks clauses are other-role or historical evidence. No blanket MCP/OAuth/legacy-server redesign conformance is inferred.

The guide explicitly records permitted SHOULD tradeoffs: static administrative access rather than OAuth, bounded Unicode tool names with sentinel encoding, no peer cancellation-reason logging, no version hint for malformed legacy initialize, and consent/UI owned by the explicit application. ServerInfo is included in all successful results, schemas use bounded draft2020-12 with no automatic network reference retrieval, and tool starts are rate-limited per instance. These deliberate tradeoffs do not waive the mandatory active header/ownership/body-budget violations.

## Required command evidence and inherited debt

All20 exact request commands completed sequentially against one unchanged candidate and the current accepted baseline snapshot. Full commands/preflights/environments/timestamps/raw stdout/stderr and child exits are in `final-checks/<id>/`; `comparison.json` independently checks every argv/receipt, raw output hash, candidate/source/metadata/preserved-product/control/guard/runner preflight and the following complete comparisons.

| Exact request check ID | Child exit | Result |
| --- | ---: | --- |
| board | 0 | Development board validation passed: 26 tasks |
| next | 0 | IN_PROGRESS friday-mcp-protocol-upgrade: Fresh-context read-only full MCP-UP-05/CD-MCP-UP-005 independent validation against approved AMEND001 and AMEND002 |
| show | 0 | approved_at: '2026-10-12' |
| server-focused | 0 | 489 passed in 16.08s |
| server-http | 0 | 140 passed in 12.61s |
| original-clients | 0 | 1505 passed in 23.69s |
| mcp | 0 | 2011 passed in 39.35s |
| core-runtime-chat-telemetry | 0 | 1528 passed, 5 skipped, 1 warning in 49.51s |
| root | 0 | 5233 passed, 14 skipped, 15 warnings in 138.56s (0:02:18) |
| baseline-root | 0 | 4744 passed, 14 skipped, 15 warnings in 118.45s (0:01:58) |
| ruff | 0 | All checks passed! |
| root-ruff | 1 | 327 complete normalized objects, including fixes |
| baseline-root-ruff | 1 | 327 complete normalized objects, including fixes |
| narrow-mypy | 0 | Success: no issues found in 7 source files |
| mcp-mypy | 0 | Success: no issues found in 28 source files |
| full-mypy | 1 | Found 4 errors in 1 file (checked 117 source files) |
| baseline-full-mypy | 1 | Found 4 errors in 1 file (checked 111 source files) |
| docs | 0 | Documentation lifecycle validation passed: 552 Markdown files checked |
| render | 0 | Planning dashboard is current |
| whitespace | 0 |  |

Supplemental `full-mypy-columns` and `baseline-full-mypy-columns` use the same bound scope plus `--show-column-numbers --no-pretty`; each returns raw exit1 with the same four complete objects: profiles.py77:9 and82:9 VectorStoreAdapter,110:9 and115:9 GraphStoreAdapter, all no-any-return. Complete normalized Ruff327 objects include full fixes, edits, ranges, messages, filenames and codes; Counters are equal. Complete normalized warning sections and every skip location/reason are equal, with14 skips/15 warnings on each root run. No waiver/checker weakening was needed or introduced.

Independent probes deliberately assert the observed deficient behavior so evidence collection completes: initial6 scenarios, one additional resistant-write scenario, then all7 against the unchanged final candidate. Their exit0 is reproduction success, never candidate acceptance. Original attempts are preserved, including `checks/independent-probes`, `checks/resistant-rejection-probe` and `checks/independent-probes-final`. Actual SDK stdio and verified literal127 TLS JSON/SSE tests passed with explicit2026/cacheNone/no interactive callbacks/extensions, recorded real wire request/version/capability/handler counters and successful child settlement. Raw ASGI/owned-stream probes are supplemental tests of uncovered invariants; they do not replace actual counterpart evidence.

## Stability, archive and exit gate

Complete stability samples strictly before the first decisive-profile check and after its final supplemental column check confirm candidate HEAD/clean status, all18 products,19 metadata,60 accepted-product hashes, all current/original control and prior authority hashes, all19 captures and all22009 copied library files/192 distributions. `stability-before-final-profile.json` and `stability-after-final-profile.json` carry exact actual hashes; `profile-bracketing.json` proves their chronological relationship to every decisive check. No drift is observed. The first run sampled libraries during initial focused checks; an attempted repeat reused its HOME cache destinations. Both raw profiles are retained as supplemental history. The final decisive profile uses a new immutable runner with fresh per-command HOME/checker/pytest caches and a new private profile TMPDIR base with unique per-command pytest fixture directories, under unchanged original runner semantics. All independent probes precede that final full-profile prehash; the final afterhash follows all its20 checks and both column checks. The immutable original runner hashes are ceec1b2316f4be3bce36fb778eb80b5d472561920d6d6fe35b8b30735e1776f0 (run_check.py), e302adaef56d824be9ee962ee6c648624330f0d0d6aa1c992f5b0dbeced8e017 (run_check_UP05.py), and guard38f6a7483d66a066336d63c14980f1acfe307ec38848f0761c6928a66989a7a8. Uncommitted whitespace/status checks are clean.

`evidence-manifest.json` names exact original evidence files with bytes/SHA256 and the verbatim structured findings. RuntimeHOME/TMP/cache/stores, private TLS keys and generated secret material are excluded. This original report and scripts/probes/inputs/raw checks/comparisons/inventories/stability evidence are included. The manifest cannot include its own hash recursively.

The controller must convert each numbered finding exactly once into a bounded approved remediation directive. Security/architecture/state-integrity changes require a separate remediator. No source change is authorized by this review. A stable corrected candidate requires a fresh independent context, required remediation delta and full work-unit review/profile with library hashes before its first check and after all checks. Work remains started; completion, maintainer acceptance, UP06 aggregate validation and delivery/publication are separate gates.

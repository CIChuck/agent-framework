# CHANGES_REQUESTED

Independent full work-unit review of **MCP-UP-04 / CD-MCP-UP-004**. Two mandatory findings remain. All 20 frozen profile commands were independently reproduced; passing tests do not discharge the two reproduced semantic failures.

## Candidate, authority, and independence

- Reviewer: fresh independent Codex subagent `/root/mcp_up04_validator`; inherited serving model, exact deployment/version not exposed. Report time: `2026-10-13T13:36:58.449830+00:00`. Review mode: fresh-context, read-only **FULL work-unit**.
- Candidate: `138fb68e33b94d20c17bbaff79ec6be3c8bfc3fb`, branch `feature/friday-mcp-protocol-upgrade`; product commit `8170c26b541433dcd5b9107d44a1c7a4a92fdd83`.
- Base: `3fd5437088c5ddf5d68be3a2a097770c294cba6b`; diff: base..candidate. Candidate and baseline remained clean at their exact HEADs. See `inputs/candidate-status`, `inputs/work-final-status`, `inputs/work-final-head`, `inputs/up04-baseline-final-status`, and `product-scope.json`.
- Handoff: `docs/planning/active/friday-mcp-protocol-upgrade/validation-request-UP-04.json`. Approved authority hash: `a5799eb167c5ede63f9cc00a5e578bab2194d2e1f21f88e18338fd637b782329`; directive: `ea4bc460c1f06f21f77f9cfa9855412b5dfaeb5d83a4c7126be067c2dd9b4593`; contract: `dc70e082544c61b01091a0a678ac57f9270b2a68eb7d11bd1601fce97ab68365`; profile: `6ec68f8b8252ef33e3675486da5e987952f68f36977e9595ec17ef8df00c5ba9`.
- `approval-UP-04.json` records Chuck Russell's exact approval, proposal commit and hashes. Board checks independently show `started`, `granted`, named branch and fresh full-review next gate. The immutable proposed wording in the directive is reconciled by this separate approval receipt, not rewritten.
- Read AGENTS, engineering/lifecycle/independent-validation policies and repository validator skill first, then approved controls, current and prior authority manifests, complete pinned public captures, selected schema definitions, full product diff, tests and documentation. Builder execution reports, claimed test results and private reasoning were not used to reach the outcome. The supplied requirement/criterion ledgers were inspected as artifacts requiring proof, not accepted conclusions. No builder conversation was inherited; no shared-context exception.
- Recursive pin inventory contains 130 entries (`inputs/pins.json`). Current controlling documents and request product/metadata/control pins match. Five queued-path hashes inside the original UP-02A approval are historical **original-proposal** hashes; current active bytes differ after the explicitly recorded clarification/relocation and have separate matching approved execution pins. No matching original queued blobs were located in available Git history. Those five historical bytes are not claimed reverified; their unchanged receipt bytes and current controlling pins were verified. See `inputs/pins-reconciled.json`. This does not make the current UP-04 directive ambiguous, and is separate from the conclusive product failures below.

## Findings

### VAL-UP04-001 — High: refresh admission invalidates too late

**Requirement:** contract lines 48–51 require only a currently usable snapshot and rejection of retired generations before mutating I/O. Lines 63–70 require explicit refresh to invalidate new generation-bound admission, including limited refresh; lines 75–85 require stale wrappers to fail locally and lower concurrency/owned-refresh budgets to hold. Violates RES-AC-01/02/03/08.

**Evidence:** `base.py:491-515` checks `_refresh_tasks` capacity and spawns a child before invalidating the catalog inside that child. `refresh_limit_constructor_probe.py` normally constructs a modern client with `ProtocolLimits(concurrent_requests=1)`, discovers a catalog through `MCPToolAdapter.get_tools()`, schedules two public `refresh_tool_catalog()` operations, and catches the second operation's rejection before executing the previously created public wrapper. No private task-set injection or candidate patch is used. Raw `checks/refresh-limit-constructor/stdout` records `limit_exceeded`, `snapshot_still_available: true`, **one mutating tools/call** from the old wrapper, and a first refresh `ProtocolFailure`. The original instance-budget version and its raw receipt are retained separately in `refresh_limit_probe.py` and `checks/refresh-limit/`. The parser's output schema remained captured; the violated invariant is admission during explicit refresh, not a claim of observed schema-free output.

**Risk:** a caller can execute under a retired catalog in a supported lower-budget configuration after explicit refresh has begun or failed its capacity gate. The old call can consume capacity that makes the first refresh fail.

**Required mitigation:** invalidate generation-bound admission in the public operation before scheduling/yielding or capacity rejection. Preserve ownership ordering so older operations cannot clear/publish over a newer success; retain absolute deadlines, bounded waits, captured already-issued call schemas/headers and zero replay. Add deterministic constructor-budget 1–4 races for public cached reads, stale execute, successful later recovery, cancellation/disconnect and HTTP/stdio parity, asserting zero new mutating I/O during invalid admission. Update final ledgers to actual tests. Keep existing documented guarantees; no new configuration API.

**Remediation role:** dispatch a **separate remediator**, as required by the independent-validation policy's Remediation section for security/architecture findings. This is a mutating-admission safeguard and concurrency-ownership change, not a mechanical builder repair.

### VAL-UP04-002 — Medium: InputRequest variants and form schemas are misclassified

**Requirement:** contract lines 100–102 require declared variant mandatory fields before disposition; lines 122–125 require well-formed modern `input_required` to yield `input_required_unsupported` and malformed results to fail as invalid. RES-AC-05 and RES-AC-10 bind this distinction and selected-schema proof.

**Source:** pinned modern schema at upstream `271ecc9accafdd9b83a3c869fa67c22953b2af80`: `InputRequest` (line 537), `InputRequests` (553), `CreateMessageRequestParams` (2104), `SamplingMessageContentBlock` (2258), `ToolUseContent` (2406), `ToolResultContent` (2445), and `ElicitRequestFormParams` (2788) and `PrimitiveSchemaDefinition` (2867). Sampling content allows text/image/audio/tool_use/tool_result, while ordinary `ContentBlock` also has resource variants and lacks tool-use variants. Form `properties` values require the declared primitive schema union.

**Evidence:** `protocol.py:468-512` sends sampling message blocks to `_validate_content_block`, an ordinary result-content validator, and checks only the outer form-schema shape. The independently authored `supplemental_probe.py` runs via the actual modern base request/receive loop and public `call_tool`; raw `checks/supplemental-work/stdout` records:

| Input case | Required disposition | Observed |
| --- | --- | --- |
| Valid sampling text | input_required_unsupported | input_required_unsupported |
| Valid tool_use | input_required_unsupported | invalid_result |
| Valid paired tool_use/tool_result | input_required_unsupported | invalid_result |
| Sampling resource_link (outside sampling union) | invalid result/protocol failure | input_required_unsupported |
| Form property value `42` | invalid result/protocol failure | input_required_unsupported |
| Form primitive property with missing required type | invalid result/protocol failure | input_required_unsupported |

Every case issues exactly one original call, no continuation/fetch/provider call, and leaves zero pending requests after disconnect. The identical baseline probe shows valid sampling variants were formerly safely unsupported; the new valid-variant rejection is a regression. Invalid form acceptance also exists in the baseline, but UP-04 expressly requires closing this classification boundary. Original supplied ledgers retain 98 selected interfaces/231 fields and map `InputRequest` generically; they do not supply proof for these dependent variant shapes.

**Risk/mitigation:** protocol-invalid and valid-unsupported interactions are conflated. Validate the correct dated InputRequest unions and mandatory nested fields, including bounded primitive form schemas. Add meaningful public stdio-like and modern HTTP positive/negative cases with exact fixed codes, zero follow-up I/O, sentinel privacy and cleanup. Extend dependent-schema mappings. Keep all interaction features unsupported; no callback, provider, schema fetching, continuation, dependency or YAML expansion is required. Public documentation already states the desired boundary and should remain accurate after repair.

## Acceptance-criterion matrix

| Criterion | Outcome | Independent evidence and practical limit |
| --- | --- | --- |
| RES-AC-01 | FAIL | `catalog.py` frozen/non-repr snapshot and exported runtime-checkable seam; `test_failed_refresh_retires_cached_and_validated_wrappers_before_io` and custom-base-subclass compatibility pass in focused/MCP. Snapshot usability while refresh begins fails VAL-UP04-001. |
| RES-AC-02 | FAIL | Full page/failure/overlap tests pass (`test_serial_refresh_returns_own_generation_after_failure`, HTTP catalog-page failures); limited refresh invalidation fails VAL-UP04-001. |
| RES-AC-03 | FAIL | `test_call_keeps_old_output_schema_across_successful_refresh` and `test_modern_http_headers_and_schema_are_captured_before_scheduling_exchange` independently pass; real refresh/reconnect wire counters pass. New stale invocation during a limited overlapping attempt issues one mutating call in VAL-UP04-001. |
| RES-AC-04 | PASS | Ordinary complete/error result boundary: `ToolResult.parse`, base call order, touched `test_modern_protocol`, structured-values/object-only tests and malformed-error-content tests pass. Independent baseline/candidate probe confirms malformed error changes from tool_error to invalid_result. No success-schema requirement is imposed on legitimate ordinary errors. InputRequest shape finding is separately RES-AC-05. |
| RES-AC-05 | FAIL | 2025 required-task exclusion, missing/forbidden/optional candidates and safe unsupported media pass. Valid/invalid InputRequest disposition fails VAL-UP04-002. No continuation, Tasks RPC or content fetch observed. |
| RES-AC-06 | PASS | Constructor lower-only caps, page/wire/depth/node/result bounds and regex/remote/cyclic schema negatives pass in focused/http/MCP/root. Source uses bounded subset and empty `Registry`; schema/validation exceptions are fixed and peer details suppressed. Supported numeric caps preserved; admission race is separately VAL-UP04-001. |
| RES-AC-07 | PASS | Five public refresh interop cases plus original/http suites use real SDK stdio subprocess and private TLS JSON/SSE fixtures, modern and explicit 2025. Exact counter=3, failure/removal/reconnect, child exit and zero owned handles asserted. These do not prove untested InputRequest variants. |
| RES-AC-08 | FAIL | Original absolute deadlines, serialized lock waiting and normal cancellation/disconnect ownership tests pass. Lower-budget overlap allows stale admission and competing tools/list failure in VAL-UP04-001; required complete concurrency proof fails. |
| RES-AC-09 | PASS | Independent focused and Core/Runtime/Chat/telemetry/root runs cover real startup/admission/selection/call/shutdown, unsafe output quarantine, atomic transcript provenance and explicit memory opt-in, filters/collisions/count/schema/token caps/native and borrowed ownership. Real Chat test asserts exactly one injected call start/finish and no auth/argument/trace sentinels. No out-of-scope application source delta. |
| RES-AC-10 | FAIL | Exact 20-path allowlist (15 changed, 5 intentionally unchanged), frozen metadata/control hashes, 19 captures, source/field accounting and all 20 commands reproduced. Exact inherited debt/skip/warnings match. Mandatory semantic criteria and dependent-schema proof remain unsatisfied; independent VERIFIED is therefore unavailable. |

Each ordinary PASS is grounded in retained product source, named assertions and independently captured command receipts. A passing test count is not treated as coverage for the numbered failures.

## Commands and exact results

All commands used the private Python **3.13.10** environment with no install/sync. `review_run_check.py` is a private copy of the pinned UP-04 runner; only evidence, HOME/TMPDIR/cache destinations were redirected under this review directory. Per-check preflights retain concrete argv, allowlisted environment, source hashes and control hashes; receipts retain child exit/stdout/stderr hashes and UTC timing. The wrapper's own exit0 is not substituted for child status. Checks ran sequentially. No checker option was weakened. Supplemental Mypy column flags expose complete location objects rather than relaxing typing.

| ID | Child exit | Observed result |
| --- | --- | --- |
| board | 0 | Development board validation passed: 26 tasks |
| next | 0 | IN_PROGRESS friday-mcp-protocol-upgrade: Fresh-context read-only independent full CD-MCP-UP-004 result/manual-refresh validation |
| show | 0 | started/granted/named branch and independent-review next gate |
| focused | 0 | 611 passed in 22.69s |
| http | 0 | 297 passed in 10.32s |
| original | 0 | 228 passed in 3.53s |
| mcp | 0 | 622 passed in 17.35s |
| core-runtime-chat-telemetry | 0 | 1528 passed, 5 skipped, 1 warning in 45.24s |
| root | 0 | 3844 passed, 14 skipped, 15 warnings in 110.53s (0:01:50) |
| baseline-root | 0 | 3793 passed, 14 skipped, 15 warnings in 106.97s (0:01:46) |
| ruff | 0 | All checks passed! |
| root-ruff | 1 | 327 complete diagnostic/fix objects; inherited debt |
| baseline-root-ruff | 1 | 327 complete diagnostic/fix objects; inherited debt |
| narrow-mypy | 0 | Success: no issues found in 6 source files |
| mcp-mypy | 0 | Success: no issues found in 22 source files |
| full-mypy | 1 | Found 4 errors in 1 file (checked 111 source files) |
| baseline-full-mypy | 1 | Found 4 errors in 1 file (checked 110 source files) |
| docs | 0 | Documentation lifecycle validation passed: 536 Markdown files checked |
| render | 0 | Planning dashboard is current |
| whitespace | 0 | No output; successful |

Exact original argv for all 20 checks follow; raw evidence is under `checks/<ID>/{preflight.json,receipt.json,stdout,stderr}`.

```text
board [work]: /private/tmp/friday-mcp-upgrade/venv/bin/python scripts/friday-dev-board.py validate
next [work]: /private/tmp/friday-mcp-upgrade/venv/bin/python scripts/friday-dev-board.py next
show [work]: /private/tmp/friday-mcp-upgrade/venv/bin/python scripts/friday-dev-board.py show friday-mcp-protocol-upgrade
focused [work]: /private/tmp/friday-mcp-upgrade/venv/bin/python -m pytest packages/friday-mcp/tests_mcp/client/test_modern_protocol.py packages/friday-mcp/tests_mcp/client/test_http_protocol.py packages/friday-mcp/tests_mcp/client/test_http_lifecycle.py packages/friday-mcp/tests_mcp/client/test_lifecycle.py packages/friday-mcp/tests_mcp/client/test_adapter.py packages/friday-mcp/tests_mcp/client/test_result_refresh.py packages/friday-mcp/tests_mcp/client/test_result_refresh_interop.py packages/friday-runtime/tests_runtime/test_mcp_http_integration.py packages/friday-chat/tests_chat/test_mcp_http_integration.py -q
http [work]: /private/tmp/friday-mcp-upgrade/venv/bin/python -m pytest packages/friday-mcp/tests_mcp/client/test_http_protocol.py packages/friday-mcp/tests_mcp/client/test_http_lifecycle.py packages/friday-mcp/tests_mcp/client/test_http_interop.py -q
original [work]: /private/tmp/friday-mcp-upgrade/venv/bin/python -m pytest packages/friday-mcp/tests_mcp/client/test_modern_protocol.py packages/friday-mcp/tests_mcp/client/test_stdio_interop.py packages/friday-mcp/tests_mcp/client/test_execution.py packages/friday-mcp/tests_mcp/client/test_lifecycle.py -q
mcp [work]: /private/tmp/friday-mcp-upgrade/venv/bin/python -m pytest packages/friday-mcp/tests_mcp -q
core-runtime-chat-telemetry [work]: /private/tmp/friday-mcp-upgrade/venv/bin/python -m pytest packages/friday-core/tests_core packages/friday-runtime/tests_runtime packages/friday-chat/tests_chat packages/friday-telemetry/tests_telemetry -q
root [work]: /private/tmp/friday-mcp-upgrade/venv/bin/python -m pytest -q -rs
baseline-root [up04-baseline]: /private/tmp/friday-mcp-upgrade/venv/bin/python -m pytest -q -rs
ruff [work]: /private/tmp/friday-mcp-upgrade/venv/bin/ruff check packages/friday-mcp/src/friday_mcp/client/base.py packages/friday-mcp/src/friday_mcp/client/protocol.py packages/friday-mcp/src/friday_mcp/client/http.py packages/friday-mcp/src/friday_mcp/client/adapter.py packages/friday-mcp/src/friday_mcp/client/__init__.py packages/friday-mcp/src/friday_mcp/client/catalog.py packages/friday-mcp/tests_mcp/client/test_modern_protocol.py packages/friday-mcp/tests_mcp/client/test_http_protocol.py packages/friday-mcp/tests_mcp/client/test_http_lifecycle.py packages/friday-mcp/tests_mcp/client/test_lifecycle.py packages/friday-mcp/tests_mcp/client/test_adapter.py packages/friday-mcp/tests_mcp/fixtures/modern_sdk_server.py packages/friday-mcp/tests_mcp/fixtures/http_sdk_server.py packages/friday-mcp/tests_mcp/fixtures/http_compat_server.py packages/friday-mcp/tests_mcp/client/test_result_refresh.py packages/friday-mcp/tests_mcp/client/test_result_refresh_interop.py packages/friday-runtime/tests_runtime/test_mcp_http_integration.py packages/friday-chat/tests_chat/test_mcp_http_integration.py
root-ruff [work]: /private/tmp/friday-mcp-upgrade/venv/bin/ruff check . --output-format=json
baseline-root-ruff [up04-baseline]: /private/tmp/friday-mcp-upgrade/venv/bin/ruff check . --output-format=json
narrow-mypy [work]: /private/tmp/friday-mcp-upgrade/venv/bin/python -m mypy packages/friday-mcp/src/friday_mcp/client/base.py packages/friday-mcp/src/friday_mcp/client/protocol.py packages/friday-mcp/src/friday_mcp/client/http.py packages/friday-mcp/src/friday_mcp/client/adapter.py packages/friday-mcp/src/friday_mcp/client/__init__.py packages/friday-mcp/src/friday_mcp/client/catalog.py
mcp-mypy [work]: /private/tmp/friday-mcp-upgrade/venv/bin/python -m mypy packages/friday-mcp/src/friday_mcp
full-mypy [work]: /private/tmp/friday-mcp-upgrade/venv/bin/python -m mypy packages/friday-core/src/friday_core packages/friday-mcp/src/friday_mcp packages/friday-runtime/src/friday_runtime packages/friday-chat/src/friday_chat
baseline-full-mypy [up04-baseline]: /private/tmp/friday-mcp-upgrade/venv/bin/python -m mypy packages/friday-core/src/friday_core packages/friday-mcp/src/friday_mcp packages/friday-runtime/src/friday_runtime packages/friday-chat/src/friday_chat
docs [work]: /private/tmp/friday-mcp-upgrade/venv/bin/python scripts/check-documentation-lifecycle.py
render [work]: /private/tmp/friday-mcp-upgrade/venv/bin/python scripts/friday-dev-board.py render --check
whitespace [work]: git diff --check 3fd5437088c5ddf5d68be3a2a097770c294cba6b HEAD
```

Additional independently executed checks: initial board/next/show/focused attempt; identical baseline/candidate public API probe; instance-budget and constructor-budget limit probes; baseline/candidate full Mypy with explicit columns; uncommitted whitespace; current/base/control/metadata/source/library hash inspections and final Git stability. Each executed supplemental subprocess has its own original raw receipt. Inspection evidence is in the named JSON audits and original probe sources.

The initial sandbox focused attempt was retained (`checks/focused-initial`): **588 passed, 23 failed**, all failed fixture cases stopped at `reservation.bind(("127.0.0.1", 0))` with OS PermissionError. The already-authorized literal-loopback profile was repeated with `require_escalated`; focused then passed611. No public/provider network or ambient credential effect was approved or used. No mandatory profile command was skipped. Root skip reasons are inherited opt-in live LM Studio gates and absent scipy, reproduced at the baseline with exact locations and counts.

## Baseline separation and supplemental inspections

- Root Ruff raw exits are 1 at both snapshots. **All 327 complete normalized objects, locations, messages, fixes and applicability match exactly**. Normalization only replaces the two snapshot roots with a common marker; see `ruff-candidate-normalized.json`, `ruff-baseline-normalized.json` and `comparison.json`.
- Full Mypy raw exits are 1. Four identical no-any-return errors remain in untouched `friday_core/profiles.py` at **77:9, 82:9, 110:9, 115:9**, returning Any from declared VectorStoreAdapter (first two) / GraphStoreAdapter (last two). Exact path/line/column/severity/message/code objects match. Explicit-column outputs and complete objects are retained. Narrow six-source and entire22-source MCP checks pass.
- Candidate root **3844 passed /14 skipped /15 warnings**; base root **3793/14/15**. Full normalized warning sections and every skip line/location/reason/count match byte-exact after snapshot-root normalization. No warning or skip was dropped to obtain equality (`comparison.json`).
- `product-scope.json` proves all 20 approved baseline/current hashes; actual15 changed product paths are exactly the15 non-process delta paths. Remaining412 paths are scoped planning/approval/acceptance/process/evidence changes. Full diff path inventory and actual product diff are retained. Nineteen metadata/lock files are byte-identical to base. No source suppression, cast workaround, checker relaxation, dependency change or new waiver appears in the product diff.
- All **19 complete captures** are decompressed into `inputs/normative`, verified at both compressed artifact and full-content hashes/lengths. Both TypeScript schemas remain at upstream commit `271ecc9accafdd9b83a3c869fa67c22953b2af80`. Independent raw mandatory-keyword accounting gives **349 original18 /393 all19**; the old347 terminology discrepancy is preserved as history. All241 mapped paragraphs match complete source text; all98 retained selected definition fragments match complete schema;48 referenced named tests exist. See normative/schema audits. This structural match does not excuse VAL-UP04-002's missing dependent-field semantic proof.
- Role exclusions remain bounded and honest: Friday is a non-task tools client, not a task requestor/receiver, OAuth authorization-flow agent, icon/media renderer, subscription/listen client, or modern Friday server. Required2025 task tools are excluded even without matching capability. No optional interaction/tracing/extension capability is advertised; no polling, callback, implicit catalog refresh, GET stream/resume, cross-call result cache, resource fetch or publication was added. Server-only and conditional unsupported-role clauses cannot be claimed as implemented conformance. Original ledgers are unchanged.
- Original guard and original runners equal captured bytes. Guard SHA256 `38f6a7483d66a066336d63c14980f1acfe307ec38848f0761c6928a66989a7a8`; original runner `ceec1b2316f4be3bce36fb778eb80b5d472561920d6d6fe35b8b30735e1776f0`; UP-04 runner `5e5c9901bf66117ee11669d32de857ea2087738add9eef3c7ae6aa6f3c8592a6`. Reviewer copy hash is in the evidence manifest and preflights.
- Independently rehashed **22,009 library files across192 distributions**:18,781/152 reused plus3,228/40 additional validation files, zero missing or mismatched files. `library-integrity.json` and `additional-libraries.json` contain exact private paths/hash objects. `dependency-artifacts-edges.json` retains selected complete lock artifacts/edges: mcp/mcp-types2.3.0, jsonschema4.25.1, referencing0.37.0, httpcore1.0.9, httpx0.28.1, idna3.20, Ruff0.14.10, Mypy1.19.1, uvicorn0.40.0. Unchanged19 metadata/lock hashes preserve the complete dependency graph. Private library files were read; original shared-environment contents were not reread.
- Sparse baseline HEAD is exact base, with267 protected tracked state paths omitted before checkout; safe manifest copied in `inputs/baseline-snapshot.json`. No protected root/user credential/store/audit-content reads, unrelated dirty-file reads or root checkout mutation occurred. Runtime stores and generated fixture TLS keys are excluded from the safe evidence manifest. Synthetic token mappings and controlled model doubles stayed within permitted fixtures.

## Residual risk and next gate

The tested private transport profile is not live-provider or whole-initiative conformance. Private environment reuse and the absent historical proposal blobs are disclosed separately from current dependency/control integrity. No new high-severity failure was found in normal generation-schema/header capture, complete ordinary results or the tested Runtime/Chat safety boundaries; the two numbered mandatory gaps prevent verification.

Keep the initiative **started**. The controller should freeze a bounded remediation directive containing both findings exactly once, assign a separate remediator for VAL-UP04-001, update actual dependent-schema evidence for VAL-UP04-002, and obtain fresh read-only independent review of a new stable candidate under the required scope. This review grants no completion, acceptance, push, merge, release or publication authority. Candidate product, tests, controls, board and Git history were not edited.

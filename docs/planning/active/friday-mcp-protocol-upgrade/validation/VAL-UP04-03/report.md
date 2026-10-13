# VERIFIED

Formal outcome: **VERIFIED** for the read-only **REM-MCP-UP-005 delta followed by full MCP-UP-04 / CD-MCP-UP-004 work-unit review**. No mandatory finding remains in this reviewed scope. This is independent validation, not maintainer acceptance or delivery authority.

## Candidate, authority and independence

Reviewer: fresh separate Codex agent `/root/rem005_final_validator`, inherited serving model (exact deployment/version unavailable), 2026-10-13. No builder session or private reasoning was received. Original reports were treated as finding records; their verdicts and builder/controller successes were not inherited. Supplied plans and mappings were verified against actual source/assertions and independently executed commands.

Candidate: clean immutable `47fcdb76035306c8aa7494ca1e1962049e984a3d`, branch `feature/friday-mcp-protocol-upgrade`, product commit `a9c913e41cdbd5bd824f36fe7b15001e6c126e17`. Delta base: `0fac03d69d0fb74eb52429970e5c0910b65922fe`; full accepted base: `3fd5437088c5ddf5d68be3a2a097770c294cba6b`. Both private candidate and sparse accepted baseline remained clean and stable, as recorded in `candidate-final-stability.json` and every check's candidate freeze.

Read private AGENTS.md and full canonical engineering/lifecycle/independent-validation policies, current handoff `validation-request-REM-MCP-UP-005.json`, approved REM005 authority/receipt/proposal/directive/profile, original UP04/CD004/contract/authority/profile/approval and original REM004 controls/requests/reports. Independent board validate/next/show agree on started/granted, named branch and this review gate. Current controlling execution pins match, including REM005 authority `1df83146e2974d1bcddd2de001fee92f04752abd6c63a3f4bc90ab7665bb8979`, exact approved proposal `8b769b234214301dbd8f781c4b6c8dfd53493bdd3a29deef38274ab7fef0281e`, and profile `350be5831c7d19d34a17614ea85c7c37cbd803f7034fc3f346f597f96afda26e`.

`product-scope.json` establishes exactly two remediation product paths, http.py and test_result_refresh.py; other18 original products and all19 metadata/lock files remain unchanged. Full original20-path budget contains15 changed and5 intentionally unchanged paths. `original-controls-preserved.json` and `prior-evidence-probe-integrity.json` establish preservation of original authorities/reports/captures/matrices against the REM005 proposal base. VAL-UP04-02 was first added after its reviewed0fac commit; its addition is not misclassified as a modification of old evidence.

Recursive pin inventory is in `authority-audit.json`. Historical original queued UP02A proposal/baseline blobs, an earlier SDK amendment revision and relocated accepted telemetry provenance are separately disclosed in `authority-current-vs-historical.json`. Those historical bytes are not claimed currently reverified, and unrelated units are not reaccepted. They do not conflict with the matching current UP04/REM004/REM005 execution pins. No additional historical reconstruction was used to obtain this verdict.

## Findings resolved and delta proof

**VAL-UP04-003 — resolved.** `http.py:676-704` binds recovery raw-catalog publication and failure catalog cleanup to the captured catalog epoch as well as existing transport/lifecycle ownership. A newer explicit invalidation changes catalog ownership even without transport generation change. No await occurs between the equality checks and publication/clear.

Unchanged `probes/recovery_overlap.py` independently observes limit_exceeded, failed disconnected refresh, unavailable snapshots before/after recovery settlement, original call invalid_protocol, subsequent raw call catalog_unavailable, **zero new mutating calls**, and zero remaining owners. The unchanged original budget probe remains preserved byte-for-byte with original raw exit1: its sole unsafe-count assertion still expects1. `budget-assertion-only.diff` discloses exactly literal `new_direct_mutating_calls==1` to `==0` in a separate copy. That copy passes budgets1–4, with zero stale calls, zero owners and all streams closed; original sources/failed raw evidence were not rewritten.

The independent `recovery_failure_ownership.py` also constructs budgets1–4 and stalls a failing initialize response while a newer public refresh retires admission. Raw and retained wrapper calls remain catalog_unavailable with zero stale wire calls; public reconnect and successful refresh preserve the fresh snapshot, then disconnect drains all owners. This checks failure cleanup through public operations, without manipulating private catalog/task/lock state.

The67 new executed variants cover before/during/after retirement, rejected/failed/partial/cancelled/deadline refresh, adapter rediscovery, ordinary2025 captured-schema compatibility, disconnect/reconnect, late404/newer successful catalog, and already-issued schema/HTTP header retention across both dates. Source ownership and exact public coverage/exclusions are recorded in `inspection-proof.md` and `dependent-schema-audit.json`.

**VAL-UP04-001 — remaining duty resolved.** Unchanged original constructor/instance probes now expose no usable snapshot after limited admission, reject the old wrapper locally and issue0 new calls. The constructor probe's first operation completes as its own MCPCatalogSnapshot. Public admission tests independently cover1–4 across stdio/2026/2025. REM005 closes the remaining recovered raw-call retirement route.

**VAL-UP04-002 — preserved and independently confirmed.** The unchanged original supplemental probe now returns input_required_unsupported for valid text/tool_use/paired tool_result and invalid_result for outer sampling resources/malformed form primitives, one original call per case, no continuation and zero pending requests. The same probe is rerun against the accepted baseline as a meaningful regression comparison. Independently reconciled33 dependent schema definitions and380 case definitions are exercised across two public paths (760 tests) in focused/MCP runs. Neither broad counts nor prior conclusions substitute for those exact disposition assertions.

## All ten original acceptance criteria

| Criterion | Disposition | Independent evidence |
| --- | --- | --- |
| RES-AC-01 | PASS | catalog.py typed exported runtime-checkable seam/frozen non-repr snapshot; adapter.py exact returned-generation cache/routing; custom virtual-client compatibility and bounded/mutation/stale-generation tests in focused/MCP. Original constructor admission probe now safe. |
| RES-AC-02 | PASS | base.py synchronous retirement and serialized atomic publication; failed/partial/cancel/overlap public tests;67 new recovery variants and unchanged overlap/failure-ownership probes prevent older restoration/clearing. |
| RES-AC-03 | PASS | base.py captures output schema and HTTP ContextVar captures matching bindings before request; issued-call schema/wire-header tests pass both HTTP dates/budgets1–4. Retired/removed/reconnected/excluded calls issue0; ordinary2025 raw compatibility retains the prior schema only absent newer retirement. No replay. |
| RES-AC-04 | PASS | ToolResult.parse and base call order validate bounded complete/error shapes before classification; modern ordered/mixed/scalar/array/null and absent/null tests, explicit2025 object-only and dated metadata tests, malformed-error original probe. Legitimate tool_error has no success-schema requirement. |
| RES-AC-05 | PASS | Correct sampling versus ordinary content unions and bounded primitive form grammar,33 schema definitions/760 public cases, original supplemental probe and2025 required-task exclusion tests; safe unsupported media/input dispositions. No interaction fulfillment/fetch/Tasks/subscriptions. |
| RES-AC-06 | PASS | Lower-only ProtocolLimits, bounded JSON/schema/result/adaptation and empty reference Registry source; focused/http/MCP cap/remote-ref/regex/deep/oversized/privacy regressions. Current correction adds no bound or dependency change. |
| RES-AC-07 | PASS | Independently executed real SDK stdio subprocess plus literal127 TLS JSON/SSE modern/2025 fixtures in focused/http/original/MCP. Public refresh/removal/reconnect interop asserts exactly3 intended calls, terminated children and settled owners. Controlled overlap probes are not mislabeled live interop. |
| RES-AC-08 | PASS | Original absolute operation deadlines, admission/issued-owner caps, serialized lifecycle and retryable cleanup source/tests; new public budget/cancel/disconnect/recovery wire/owner proofs. No abandoned request or mutating replay observed. |
| RES-AC-09 | PASS | Real Runtime/YAML/Chat startup/admission/selection/TurnProcessor/call/shutdown tests execute in focused/cross/root. Assertions cover sanitization/quarantine, matching atomic transcript provenance/correlation, explicit memory opt-in, native/borrowed ownership and exactly one injected start/finish observer; synthetic secret/argument/trace payloads stay absent from records/logs/telemetry. |
| RES-AC-10 | PASS | Accurate20-path product docs/scope,19 immutable metadata files, current authority pins, complete capture/clause/schema mapping, destination-only library integrity, all20 independent commands and exact baseline comparison. No blanket conformance, later-unit, acceptance or publication claim. |

The named source locations/assertion families and practical limits are detailed in `inspection-proof.md`; original complete product/delta diffs and safe source copies are retained. No new source suppression, broad cast workaround, checker weakening, dependency, waiver, application source or provider was introduced.

## Required commands and original raw results

All20 commands ran in prescribed order against one fixed candidate and accepted sparse baseline using the pinned private Python3.13.10 environment. Each `checks/<id>` retains actual argv/allowlisted environment, fresh private HOME/TMP/checker/pytest caches, candidate/source20/control/metadata19/guard/runner freezes, UTC timing and original stdout/stderr/child receipt. Wrapper exit0 never substitutes for child exit.

| ID | Child exit | Observed result |
| --- | --- | --- |
| board | 0 |26 tasks valid |
| next | 0 |Current REM005 delta then full-unit review gate |
| show | 0 |started/granted/named branch |
| focused | 0 |1511 passed |
| http | 0 |297 passed |
| original | 0 |228 passed |
| mcp | 0 |1522 passed |
| core-runtime-chat-telemetry | 0 |1528 passed,5 skipped,1 warning |
| root | 0 |4744 passed,14 skipped,15 warnings |
| baseline-root | 0 |3793 passed,14 skipped,15 warnings |
| ruff | 0 |All touched checks pass |
| root-ruff | 1 |327 inherited full diagnostic/fix objects |
| baseline-root-ruff | 1 |Same327 objects |
| narrow-mypy | 0 |6 source files clean |
| mcp-mypy | 0 |22 source files clean |
| full-mypy | 1 |4 inherited errors in untouched Core profiles.py;111 checked files |
| baseline-full-mypy | 1 |Same4 errors;110 checked files |
| docs | 0 |542 Markdown files valid |
| render | 0 |Dashboard current |
| whitespace | 0 |Clean |

`comparison.json`, `normalized-ruff-327.json`, `normalized-mypy-4.json`, `normalized-root-skips.txt` and `normalized-root-warnings.txt` compare **complete objects/sections**, not counts. Supplemental Mypy `--show-column-numbers --no-pretty` independently matches path/line/column/severity/code/message objects at77:9,82:9,110:9,115:9 in profiles.py. Exact skip locations/counts/reasons and the entire normalized15-warning section equal the successful accepted-baseline run; only snapshot root prefixes were normalized.

Pinned guard SHA256 `38f6a7483d66a066336d63c14980f1acfe307ec38848f0761c6928a66989a7a8`, immutable original runner `ceec1b2316f4be3bce36fb778eb80b5d472561920d6d6fe35b8b30735e1776f0`, UP04 runner `5e5c9901bf66117ee11669d32de857ea2087738add9eef3c7ae6aa6f3c8592a6` remain exact. `runner-destination-only.diff` discloses the private copy's output/HOME/TMP/cache redirection only. The guarded profile was run directly with approved escalation for named literal127 fixture effects, because prior original evidence already establishes OS sandbox bind denial. No redundant known-failing sandbox profile was run.

Supplemental original raw checks include all retained original probes, baseline/candidate regression probe, budget assertion-only copy, independent failed-handshake ownership, schema/variant audits, Mypy columns, uncommitted whitespace, exact comparisons, prior artifact/probe integrity and final library/source integrity. One reviewer-owned `schema-mapping` attempt exits1 solely because importing pytest test helpers directly lacks tests_mcp package registration. Its source/raw stderr/receipt remain. A separately retained data-only AST audit evaluates only the three case-construction functions with pytest/copy and passes; it neither changes candidate/import options nor weakens product checks. This infrastructure/data-enumeration failure is not concealed as a product success.

## Integrity and limits

`normative-audit.json` independently verifies compressed/complete-content hashes and sizes for all19 captures. `independent-clause-mapping-audit.json` reconciles all241 paragraph mappings with393 mandatory-keyword occurrences (original18=349; old347 terminology history preserved). `dependent-schema-audit.json` verifies98 original selected schema definitions/231 declared-field locations plus33 supplemental fragments and380 actual variants against complete schemas selected at upstream `271ecc9accafdd9b83a3c869fa67c22953b2af80`. Both preconstruction plans and actual final67-variant mapping remain available as inspected evidence. `archive-integrity.json` independently verifies REM005250 and REM004257 lossless safe artifacts; prior independent report/probe archives also match their stored hashes.

`library-integrity.json` rehashes **destination only**22,009 files across192 distributions (18,781 reused/152 plus3,228 additional/40) before and after checks. No shared environment originals were read. Exact dependency versions/artifacts/edges are retained in `dependency-artifacts-edges.json`; all19 unchanged metadata files preserve the complete lock graph. No install/sync or shared environment write occurred.

Successful catalog publication while recovery is disconnected is unreachable through public discovery; connect waits on the serialized lifecycle lock. Failure cleanup's catalog-epoch guard is source-proven, with public failing-handshake/newer-retirement/reconnect and late404/newer-success executions supporting its reachable behavior. At budget1 an issued call consumes the only HTTP slot, excluding before-capture wire partial/cancel/deadline refresh; the separate before-capture limit case and all1–4 during/after-retirement cases cover the lower-budget safety requirement.2026 has no2025 session-expiry recovery; both dates are exercised for issued schema/header retention. No private-state fabrication was used to claim unreachable coverage.

Effects stayed within controlled synthetic peers, named SDK subprocess stdio and literal127 TLS/cross/root fixtures under the pinned guard. No public network, ambient credentials/OTEL, real model providers, protected user stores, URL/media/schema fetching, remote action or publication occurred. Homes/tmp/caches/runtime stores/generated TLS keys are excluded from `evidence-manifest.json`.

The candidate, source/tests, authority/control bytes, board, metadata and root workspace were untouched. This VERIFIED result closes only this frozen delta and original UP04 work-unit review; completion proposal, maintainer acceptance, later units and delivery remain separate gates.

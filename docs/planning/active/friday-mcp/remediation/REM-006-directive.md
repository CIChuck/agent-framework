# REM-006 — MCP-WS-05 Transcript Privacy And Cross-Iteration Correlation

Status: Approved; separate remediator authorized for bounded execution
Date: 2026-09-28
Approved by: repository maintainer
Approved at: 2026-09-28
Approval evidence: "fix them - proceed" after the complete REM-006 proposal and separate-remediator request
Remediation base: `dd6a337eb2928ab4050ea70fb41dc77072210e34`
Initiative: `friday-mcp`
Work unit: `MCP-WS-05`
Reviewed candidate: `2388e747ba1bf8157881230ad36ae3ef3272b807`
Original work-unit base: `a609f948fe2d869ac29d0cce29d22d9334cd7d08`
Branch: `feature/friday-mcp-ws05-execution`
Findings: [complete independent VAL-011 report](../validation/VAL-011-report.md), F-001 and F-002

## Authority And Approval Boundary

Explicit maintainer direction, repository engineering/lifecycle/independent-validation
policies, accepted WS-00 through WS-04 contracts, the approved
[WS-05 directive](../directives/ws-05-execution-provenance-transcript.md), and
[VAL-011](../validation/VAL-011-report.md) control this proposed correction.
The original request and reviewed report stay byte-exact historical evidence.
This directive converts each finding exactly once into bounded approved work.
The maintainer explicitly said "fix them - proceed", authorizing this complete
eight-path proposal and a separate remediator. Approval covers only both findings,
required regressions/report/checks and new independent review; no delivery. The approved WS-05
directive says: "No automatic security/package remediation is approved by this
directive." The explicit approval above now supplies that bounded remediation
authority; it does not grant later scope or acceptance.

Use a separate remediator because these findings concern security and data
integrity; the independent-validation policy explicitly requires that separation.
The builder and validator must not silently repair this candidate. Authorization/start and the exact remediation base are now recorded; dispatch a separate
remediator, freeze a new stable candidate and obtain a new fresh read-only VAL-012
with remediation delta followed by the complete original WS-05 aggregate. The
remediator must not validate its own work. This is the first WS-05 remediation
cycle; after two unsuccessful cycles return unresolved findings to the maintainer.

## Exact Allowed Implementation Manifest

Exactly eight paths are allowed: four Chat source files, three existing tests,
and one new remediation implementation report:

- `packages/friday-chat/src/friday_chat/adapters.py`
- `packages/friday-chat/src/friday_chat/tools/output.py`
- `packages/friday-chat/src/friday_chat/tools/loop.py`
- `packages/friday-chat/src/friday_chat/turns/processor.py`
- `packages/friday-chat/tests_chat/test_mcp_execution_security.py`
- `packages/friday-chat/tests_chat/test_mcp_execution_transcript.py`
- `tests/integration/test_mcp_execution_provenance.py`
- `docs/planning/active/friday-mcp/execution/REM-006-implementation-report.md`

Controller approval/start, request/review/evidence/status/closeout, index/queue/log
and board/dashboard artifacts remain separate process metadata. All Core, MCP,
Transcript, Runtime, Agent, Memory, config, dependency and other source/tests remain
frozen. Stop and request an exact amendment if another implementation path is
needed; no opportunistic refactor or inherited debt cleanup.

## F-001 — High: Transcript Session MCP Configuration Privacy

The production adapter copies the configured MCP provider stanza into the
persisted session `config_snapshot`. A synthetic configured environment value
survives there, JSONL session headers (including metadata-disabled export), and
CSV `export_all_sessions` session metadata. Ordinary per-session CSV entry
exports are not the failing surface.
This is inherited snapshot behavior, but violates the current WS-05 mandatory
MCP env/header redaction requirement. The independent report distinguishes
entry/call safety from session capture and provides exact reproduction.

Required correction:

- Produce a safe session configuration snapshot before storage. Remove MCP
  environment/header values and any raw MCP connection or launch material that
  can contain credential/argument copies. Omit the MCP provider stanza or retain
  only an explicitly bounded safe non-secret summary. No credential values,
  argument keys/value summaries, stable hashes or new config authority may be
  introduced to preserve observability.
- Preserve actual configured runtime execution, exact original routing and
  peer environment; sanitize the diagnostic copy without mutating user config.
  Keep native/non-MCP configuration snapshot behavior compatible.
- Cover production SQLite session capture as well as entry capture, JSONL
  with both metadata flags, CSV `export_all_sessions` session metadata as well
  as per-session entries, and Markdown/CSV compatibility. Metadata-disabled
  JSONL must not bypass session privacy. Do not expand scope into unrelated
  providers' configuration or general user-authored secret classification.
- Do not rewrite historical databases or add a storage migration. Document
  that existing sessions may contain prior snapshots; this work prevents new
  unsafe MCP session capture. Any historical cleanup needs separate authority.

Required regressions: synthetic env/header/launch argument sentinels with
production streaming/nonstreaming, normal/fallback MCP turns; inspect stored
session and every exported artifact, not just entry JSON; verify runtime config
and peer behavior remain unchanged, native session shape stays compatible and
no new logs/errors expose sensitive values.

## F-002 — High: Later Native ID Reuse Must Preserve MCP Pairing And Persistence

A later native tool call can reuse an earlier MCP call ID. Current MCP allocation
reserves native IDs only when the native call is already known; the later reuse
leaves duplicate continuation/record IDs. Duplicate continuation behavior is
inherited, but the new WS-05 transcript pairing guard causes production
`TurnPersistenceError` and zero stored entries where the base stores one.

Required correction:

- Reconcile MCP ID collisions across the complete turn, including later model
  iterations and mixed native/MCP calls. Preserve native IDs and native execution
  semantics. Reassign MCP IDs when necessary using safe unique opaque identifiers
  and keep the accepted valid-unique-ID behavior where no collision exists.
- Keep MCP request IDs, corresponding tool-result messages, atomic records,
  typed call/result provenance and persisted correlations consistent after any
  reassignment. Do not expose unsafe original IDs, misassociate repeated names,
  rerun completed tools, invent successful calls or lose accepted metadata.
- Preserve strict transcript pairing validation; do not disable guards, weaken
  shared DTOs, suppress persistence errors, drop MCP facts or merely repair IDs
  inside SQLite while continuation/history remains inconsistent.
- Cover both turn modes, normal/fallback completion, multiple/repeated tools and
  concurrent execution. Native-only legacy behavior remains compatible. The
  production adapter must store a valid paired turn instead of failing after
  successful executions; fake adapters must receive the same coherent facts.

Required regressions: real local peer first MCP ID `shared`, later native ID
`shared`, plus repeated/missing/invalid IDs and mixed calls across more than one
iteration; assert exact original execution and native IDs, unique coherent MCP
pairs in continuation/capture/records, successful production SQLite persistence,
actual entry correlations, JSONL round-trip and safe fallback/streaming behavior.

## Acceptance Criteria

| ID | Required independent evidence |
| --- | --- |
| REM006-AC01 | F-001 synthetic env/header/launch sentinels absent from new MCP session snapshots and all exports, including JSONL metadata-disabled; original execution/config unchanged. |
| REM006-AC02 | F-002 later-native ID reuse completes safely with native IDs unchanged and coherent unique MCP request/result/record/provenance associations and production storage. |
| REM006-AC03 | Strict paired transcript facts, actual correlations, old/native behavior, streaming/fallback, caps/security/failure/cancellation and accepted WS-04 budget/selection remain intact. |
| REM006-AC04 | Only eight allowed implementation paths change; no dependency/config/shared source drift, suppressed checks, historical DB edits, argument hashes or real secret copies. |
| REM006-AC05 | All required checks, fresh independent reproductions, public local-peer cleanup and frozen/unrelated preservation are documented and reproducible. |
| REM006-AC06 | Fresh VAL-012 verifies the exact remediation delta and complete original WS-05 aggregate, closes both findings and introduces no new violated requirement. |

## Verification, Reporting And Stop Conditions

Use the approved WS-05 directive's complete required command set and environment
limits, with frozen original base-to-new-candidate aggregate whitespace/scope
checks and a separate remediation-base-to-new-candidate delta check. Run focused
regressions first, then full Chat/Transcript/Agent/Core/MCP/Runtime/Memory/integration,
Ruff, default and unfiltered meaningful Python-3.13 typing, lock check,
board/dashboard/docs checks, offline built distribution/import verification,
independent local stdio/turn/storage/export UAT and freeze/preservation checks.
Run meaningful typing on every changed source; do not filter new errors. Independently
reproduce unchanged baseline failures and keep exact command exits and complete
logs. No live provider, external MCP service, real credential, paid model or delivery.

The remediation report must map both findings and six criteria to concrete
paths/source/tests, document safe session snapshot and cross-iteration ID
semantics/migration, full commands/exits, baseline separation, cleanup and frozen
preservation, exact remediation base/candidate and original aggregate base.
Archive original logs/scripts without runtime databases or real secrets.
Preserve the five unrelated dirty paths and accepted authorities.

Stop before source work without explicit approval/start/separate-remediator
assignment, or for scope/authority drift. Stop before closeout for missing
required evidence, new failures, unsettled cleanup or no fresh validator.
Candidate/authority changes invalidate prior results. Neither this approval,
CHANGES_REQUESTED nor a future VERIFIED result supplies maintainer acceptance
or later-phase/push/merge/release authorization. After VERIFIED, return the
complete independent report and request explicit WS-05 acceptance.

# REM-MCP-UP-001 builder report

Corrective product candidate: **58f0000b209f76b9deb8e919091c208c5d593a6d**.
Parent/controlling checkpoint: **7e998cdb0f72b1c192ebc2e00c13c10cfacbb779**.
Branch: `feature/friday-mcp-protocol-upgrade`. Date: 2026-10-12 UTC.
Role: separate remediator `/root/mcp_up02a_remediator`; runtime describes GPT-6,
exact backend version unavailable. This is builder evidence, not an independent
verification verdict, completion proposal, maintainer acceptance or delivery.

## Authority and scope

Read AGENTS, engineering/lifecycle/independent-validation policies, approved
CD-MCP-UP-001/A01 and approval receipt, protocol/build/tactical/conformance
controls, full frozen dated TypeScript schema, REM-MCP-UP-001 and immutable
VAL-UP02A-01 report. Board validate/next/show established started/granted/local
and the named feature branch before edits. All current authority control hashes,
original baseline product hashes/absence records, and all ten stored/decompressed
normative-source hashes and byte counts match. See
`initial-hash-verification.json` and `preservation-and-adversarial.json`.
Authority manifest SHA-256 remains
`b5535fe121b2a672d1319abd527b20e66faf8086fd911fe6a231f3dc7c6ba536`.
Immutable original report remains SHA-256
`1fb7603c3abbcd394a32fafd75a6bb83808920ea047d305f383cd853a91f05a6`.

Exactly four of the five remediation-allowed existing product paths changed:
`client/base.py`, `client/protocol.py`, `tests_mcp/client/test_modern_protocol.py`
and the MCP package README, all under `packages/friday-mcp`. Existing
`test_execution.py` required no changes. Delta: 494 insertions, 19 deletions.
Full exact product diff and changed-file hashes are retained in
`product.diff` and `candidate.json`. Aggregate original client-core construction
scope remains the same twelve paths; no extra product/dependency scope or waiver.
Only these four paths were explicitly staged and committed by the remediator.
Controller archive-navigation process files were left unstaged and preserved.

## Numbered findings implemented

**VAL-UP02A-001.** Auto detection recognizes exactly the three defined modern
peer wire codes `-32020/-32021/-32022`, leaving local adapter exception codes
separate. Each recognized error emits only `server/discover` and retains a fixed
safe failure; it never sends initialize/initialized or selects legacy. Existing
varied non-modern error, timeout, exact legacy version and late-ID controls pass.
`test_recognized_modern_version_error_and_no_intersection_do_not_fallback`
now covers all three modern codes and exception/log privacy. The unmodified
original executed adversarial probe independently reproduces no fallback for all
three codes; its retained raw output is `checks/adversarial/stdout`.

**VAL-UP02A-002.** Modern-only contextual validators enforce MetaObject object
shape/key grammar at declared result/notification, Tool and supported TextContent
locations; serverInfo Implementation fields are typed only in ResultMetaObject;
subscriptionId is typed only in NotificationMetaObject. Discovery validates
known boolean capability flags and experimental/extension object maps, including
mandatory extension-key prefixes. Optional Tool titles/icons/annotations and
TextContent audience/priority/lastModified fields are checked against their
named dated schema structures. Optional identity/icon URLs are strings checked
without fetching. All validators run after bounded JSON validation; Discovery
and CatalogPage now also bound their direct parser inputs before contextual
checks. Unknown metadata values retain bounded, untrusted JSON.

No recursive interpretation of application JSON is added. Positive wire coverage
preserves `_meta` arrays/arbitrary key names inside arguments, structuredContent,
inputSchema default/examples/custom annotation values and property names; unknown
metadata values and capability settings remain opaque. Reserved-looking keys
inside generic Tool/TextContent metadata remain generic values, rather than
incorrectly borrowing ResultMetaObject's serverInfo type rule.

New coverage includes sixty malformed metadata location/grammar cases, eight
known-capability failures, seven result-identity failures, thirteen optional Tool
shape failures, ten TextContent annotation failures, four notification-ID
failures, and three positive/legacy/catalog/privacy scenarios: **105 additional
passing test cases**. Tests include malformed later-page Tool metadata after a
good first page and a previously successful catalog; no partial catalog or stale
schema survives. All six original malformed-shape adversarial counterexamples
now yield ProtocolFailure. See `preservation-and-adversarial.json` for explicit
interpretation of diagnostic outcomes, not merely the script's exit status.

## Required gates and results

Exact argv, cwd, allowlisted environment, UTC intervals, exit codes, guard hash
and stdout/stderr SHA-256 appear in `command-ledger.json`; raw complete output
and receipt remain under `checks/<label>/`. Private Python directly executes the
installed locked tools as the equivalent offline/no-sync profile; no dependency
synchronization or installation occurred.

| Gate | Result | Raw label |
| --- | --- | --- |
| Board validate/next/show | all exit 0; started/granted/local/named branch | board-validate, board-next, board-show |
| Exact four focused client test files, including real SDK/legacy stdio | exit 0; 228 passed | focused-02 |
| Complete MCP package | exit 0; 264 passed | package |
| Runtime/Chat/Telemetry | exit 0; 1211 passed, 5 existing skips, 1 warning | cross-package |
| Exact original nine source/test/fixture Ruff paths | exit 0; no findings | scope-ruff-02 |
| Three touched client source Mypy | exit 0; 3 files | scope-mypy-final |
| Complete MCP source Mypy | exit 0; 18 files | package-mypy |
| Full candidate workspace pytest, no exclusions | exit 0; 3331 passed, 14 skipped, 15 warnings | root-pytest |
| Untouched original baseline full workspace pytest | exit 0; 3132 passed, 14 skipped, 15 warnings | baseline-pytest |
| Candidate/baseline skip identity details | exit 0; identical nine summary lines covering all 14 skips | candidate-skip-details, baseline-skip-details |
| Final raw candidate and baseline root Ruff JSON | both exit 1; exactly 327 identical inherited path/code/row/column identities, zero added/removed | root-ruff-final, baseline-ruff |
| Original adversarial reproducer | exit 0 diagnostic; all three modern errors and all six malformed shapes corrected | adversarial |
| Final documentation lifecycle | exit 0 | docs-final |
| Committed exact delta whitespace | exit 0 | candidate-diff-check |
| Control/dependency/original evidence preservation | all pinned hashes unchanged; approved proposal matches current full lock | initial-hash-verification.json, preservation-and-adversarial.json |

The first focused/lint development attempts are preserved: focused-01 had nine
new-test fixture-construction TypeErrors (duplicate capability kwargs), while
scope-ruff-01 reported formatting/line-length findings in the draft additions.
The helper override and formatting were corrected within the same allowed paths;
final focused/Ruff/Mypy gates above pass. No exclusions, ignores/casts, test skips,
checker/config weakening or baseline repairs were used.

The initial documentation command failed because controller checkpoint archive
compression left sixteen literal links in the immutable original review report
without their targets. The remediator reported that process-only issue and did
not edit the report, authority or board. The controller restored byte-identical
linked JSON/diff views, directory archive navigation and a declared formatting-only
Python presentation while retaining immutable executed source gzip bytes and the
unchanged report hash. Final docs and root Ruff were rerun and pass/match inherited
debt respectively. These process changes are outside this product-only commit
and will be frozen separately by the controller; the initial docs failure is retained.

## Original criteria and regression coverage

| Criterion | Current executed evidence |
| --- | --- |
| CD-AC-01 typed bounds/profiles/default compatibility | focused limits/immutable snapshots/default-profile/constructor tests; scoped and package Mypy |
| CD-AC-02 discovery/metadata/capabilities/version | modern identity/every-request metadata, legacy revision, fallback/no-intersection controls plus new finding coverage; real stdio fixtures |
| CD-AC-03 envelopes/IDs/safe errors/no fallback | malformed/wrong/late/duplicate IDs, fixed errors, modern error controls, contextual result/notification metadata tests |
| CD-AC-04 complete bounded catalog | pagination/snapshot/cycle/page/tool/byte/duplicate caps; new malformed later-page metadata invalidation test |
| CD-AC-05 typed result/schema/fidelity/no replay | tags/input-required/nontext, scalar/array/null/mixed output and schema constraints; new typed TextContent/application JSON controls; ambiguous real-child single-call counts |
| CD-AC-06 deadlines/caps/cancellation | existing connect/send/probe/fallback/catalog deadlines, bounded waiter/outgoing allocation, stalled/cancel-resistant send and stdio cancellation/oversized-frame tests |
| CD-AC-07 lifecycle/privacy/provider preservation | complete lifecycle/execution tests, fixed logs/reprs, real fixture task/process reaping, full MCP and Runtime/Chat/Telemetry/root regressions |
| CD-AC-08 interoperability/docs/dependencies/gates | real official SDK 2.3.0 and deterministic 2024-11-05 stdio fixtures executed in focused/package; final docs, exact unchanged approved lock and all original gates above |

These are builder criterion-to-test mappings, not independent PASS/VERIFIED
assertions. The original independent report and normative ledger remain retained
historical evidence; controller must freeze new inputs for a fresh finding-delta
and full original-work-unit review.

## Effects, dependencies and limitations

`effects-manifest.json` identifies the two named synthetic real stdio Python child
fixtures, exact existing literal 127.0.0.1 ephemeral HTTP/gRPC fixtures and private
synthetic filesystem stores. Escalated execution was used only for the three
approved full/cross-package regression runs that need those fixture listeners.
Audit guard SHA-256:
`38f6a7483d66a066336d63c14980f1acfe307ec38848f0761c6928a66989a7a8`.
Checks use private HOME/temp/caches, package src plus Chat tests PYTHONPATH,
importlib mode and an allowlisted environment with no ambient OTEL_* or credentials.
No live MCP/model/exporter service, user state, dependency install/sync, npm/npx,
external URL/ref/icon fetching, push/merge/release or acceptance occurred. Native
gRPC has exact-target/channel-option guards; Python audit hooks alone do not
intercept every native-library network operation.

Current `uv.lock` SHA-256 is unchanged:
`aab33ed773dcdb50a65dd86af84bd1e6e26dc3486da7b04588082d72a7b18ce2`;
MCP package metadata SHA-256 is unchanged:
`730f687c040a63e2e4347880fb7e17b536d2b0730467b6fb2eec9286ad3b0aa2`.
Original approved SDK/IDNA/artifact/context records remain untouched. SDK 2.3.0
is only a fixture/development counterpart; runtime SDK imports were not added.
Private validation libraries are the previously prepared locked/version-matching
environments, not a fresh clean network install or a new 24-context execution claim.

Raw root Ruff remains nonzero inherited debt, not a passing gate or new waiver.
Root skips independently reproduce disabled explicit live LM Studio tests and
unavailable SciPy graph adapter, with no new infrastructure skip. Candidate has
199 more passing cases than original product baseline (94 initial construction,
105 remediation). Warnings remain 15 in both full workspace runs. Existing bounded
output-schema/content/optional-capability limitations remain unchanged; no HTTP,
remote admission, modern server, subscription or automatic MRTR behavior is added.

Next authorized gate: controller process freeze and fresh read-only independent
review of the corrected candidate. No self-VERIFIED result is issued.

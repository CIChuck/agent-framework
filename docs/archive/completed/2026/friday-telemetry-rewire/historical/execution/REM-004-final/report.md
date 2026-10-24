# REM-004 execution closeout — TELEM-01 candidate

Date: 2026-10-06. Controller: Codex /root. Separate builder: /root/rem004_remediator.
Candidate: `8aedd87c8def5a6c514bdfea7505205e8db78bb6`.
Delta base: `1b28d373bb613e754947e4b13c7f7280314c560e`.
Aggregate preparation base: `2155a0fc51f5b20dea4e35c6cfc70f1d52002735`.
Authority: CD-001 A01–A06, approved REM-001 through REM-004 and exact WVR-002/WVR-003; nineteen pins and manifest in controller/product-validation-request.json.
This execution report records builder/controller evidence. The separate VAL-006 report supplies the formal verdict; no builder self-verification or maintainer acceptance is claimed.

## Resulting behavior and exact scope

The local Chat observer, CLI/runtime injection, bounded safe lifecycle diagnostics and nested composite span pairing remain the first authorized slice. REM-004 resolves the exact aggregate failures: registry fixture restores declarations; reader tests exercise missing optional dependencies with scoped mocks and valid/malformed synthetic files; URL literal classification precedes DNS; the PTY test synchronizes readiness before its unchanged acknowledgement budget; 132 live lint findings are fixed; three existing response-branch typing failures are resolved using published response types and branch-specific variables.

Exactly 88 approved source/test paths changed under the original 91-path REM-004 union. The complete aggregate Python manifest has 98 paths, 63 source files and 13 owning test directories. manifests and diffs are retained. CommandRegistry remains byte-identical and invariant under A06/WVR-003. Five converted generics retain invariance in both assignment directions; bounds, runtime Pydantic schema behavior and supported annotation consumers were probed. The MemoryLLMClient alias becomes a standard TypeAliasType; no tracked introspection caller exists, and external runtime alias-introspection compatibility is not claimed.

No additional product scope, config, lint/typing suppression, dependency change, provider/exporter activation, install, sync, push, merge or deployment occurred. TELEM-02 through TELEM-05 remain deferred pending their own construction authority.

## Required frozen-candidate commands

All command receipts are in controller-raw/ with exact argv, cwd, candidate, snapshot hash, allowlisted environment, log hash and unchanged tracked-input result. `uv run --no-sync` uses the installed shared environment read-only and offline. Root tests retain exactly the two approved live-LMStudio module safety exclusions and importlib mode; Chat/telemetry retains its existing gated skips. Owning packages use the exact aggregate list. Report-only `-rA` supplies node identifiers in owning-package and independent replay logs.

| Required check | Result |
| --- | --- |
| Six original telemetry-focused modules | 135 passed, exit 0 |
| Complete Chat + telemetry | 741 passed, 5 existing live-gated skips, exit 0 |
| Complete deterministic root collection | 2,805 collected, exit 0 |
| Complete deterministic root execution | 2,804 passed, 1 skip, exit 0 |
| All 13 owning test directories | 2,786 passed, 1 skip, exit 0 |
| Whole Agent suite followed by Runtime DI file | 223 passed, exit 0 |
| Ruff on all 98 aggregate changed Python files | Exit 0 |
| Python 3.13 mypy on all 63 aggregate changed source files | Exit 0 |
| Unchanged root Ruff | Raw exit 1, exactly 327 approved identities; disposition below |
| Board validation | 24 tracked tasks, exit 0 |
| Documentation lifecycle | 426 Markdown files, exit 0 at candidate |
| Aggregate git diff --check | Exit 0 |
| Offline uv lock --check --no-python-downloads --no-build | 201 packages, exit 0 |
| Python 3.13 AST parse | All 98 changed Python files parse |
| Metadata/source/tool/authority integrity | 18 minimums, 16 isolated package origins, 17 lint config hashes, four archive hashes, exact registry hash and 19 authority pins match |
| Genuine public Chat observer + two-provider Composite lifecycle | Exit 0 on actual Python 3.13.10 / LiteLLM 1.100.1 |
| Original/final six-generic consumer negative probes | Both incompatible assignment directions rejected identically for all six, wrapper exit 0 |

Root/owner sole skip: `packages/friday-memory/tests_memory/test_adapters/test_graph.py:250`, missing optional scipy. Exact Chat live-skip nodes/reasons and all root identities are retained in VAL-006 replay output. Actual runtime is 3.13.10; metadata rejects 3.13.3 and accepts 3.13.4. No exact-floor 3.13.4 runtime or obsolete Python 3.10 pass is claimed.

Root Ruff remains nonzero. Its full sorted path/code/start/end/message multiset exactly equals 326 immutable archival diagnostics under WVR-002 plus one unchanged CommandRegistry UP046 under WVR-003. Canonical normalized SHA-256: `b772de4b7bcd864bf9fc64c90eb9178e336c1fbc468fb40d75f8dac5429cbda4`. All 17 configuration hashes, Ruff 0.14.10 target py313, archive content and registry content match. There are no other findings. Both approved waiver expiry/follow-up conditions remain binding; WVR-001 is unapproved and unused. This report does not label raw root lint PASS.

## Criteria, baseline and safety evidence

AC-01 through AC-05 map to the unchanged first-slice implementation report and named telemetry tests: strict disabled/default config and compatibility; real/fake/CLI assembly and borrowed injection; lifecycle outcomes, cancellation and bounded counts; planted-sentinel privacy/MCP schema rejection; and two-sink parents, membership, payload isolation, failure fan-out and collision handling. The 135 focused tests and genuine observer smoke revalidate them at the final candidate. AC-06 has all commands above and the separate frozen delta plus aggregate independent review.

VAL-005 remains historical evidence: root 2,727 collected, 2,699 passed, 16 failed, 11 errors, 1 skipped; Chat/telemetry 724 passed, 1 failed, 3 errors, 5 skipped; root lint 459 findings and three expanded-source typing errors. REM-004 exactly addresses its remaining numbered finding. New registry/literal regressions run against old source yielded 19 intended failures and one previously rejecting loopback case; current regression suites pass. Old PTY failure is retained, and the synchronized new test is not claimed to reproduce the old timing failure. Remediator raw failed attempts and corrected outcomes are retained without treating expected negative consumers as failed acceptance gates.

All broad collection/execution used fresh reviewed imports/helpers/subprocess paths, synthetic providers/temp state, an environment allowlist, isolated package source precedence and the unchanged network guard. The exact eleven approved fixtures bind loopback ephemeral ports using fake payloads under normal-user sandbox escape; no external DNS/transport/service or original application data access is authorized. Protected tracked runtime artifacts were omitted before materialization in final sparse snapshots. Earlier private snapshots had committed runtime artifacts; they were not consumed by the selected tests, and corrected data-free materialization preserved root discovery. Source, configs and tests remain present. Original runtime directories were not inspected, copied or cleaned.

A pre-existing local OpenTelemetry ConsoleSpanExporter emits an atexit closed-capture-stream diagnostic after successful Chat/focused runs. Identical tracebacks are retained in the REM-003 baseline logs and the original implementation report. It is an unchanged optional adapter shutdown issue, not a new Chat observer failure. Repair belongs to a future bounded OTel directive; the message remains visible and is not suppressed.

## Preservation and process boundary

preservation.json confirms every original unrelated dirty path/hash or dirty board/dashboard line multiset. The unrelated security tree, tool-manifest packet, original dirty Chat example config, audit Dockerfile, .DS_Store and deleted family-tree.md stay outside commits. A transient externally appearing .claude/ directory during earlier review is disclosed separately without a content-preservation claim. No original .env, .friday, Chroma/transcript state or credential content was read or changed.

Independent review is formal fresh-context read-only delta plus aggregate review at the candidate above. Local evidence closeout may change only this packet and this initiative's board/dashboard metadata; it does not change reviewed product/authority or grant acceptance, publication or later-unit authority. The broader initiative remains started because later units are not completed. The next gate after a VERIFIED result is maintainer TELEM-01 acceptance and selection/approval of the next bounded unit.

# MCP-WS-06 Implementation Report

Status: Builder implementation complete; fresh independent aggregate review pending
Date: 2026-09-29
Branch: `feature/friday-mcp-ws06-memory`
Approved work-unit base: `99bde5148ee21f47d4734d2a026fb198a3d19cbd`
Approval/start commit: `4d04988`
Candidate: The stable commit containing this report; pinned by the VAL-014 request.
Authority: [approved 18-path directive](../directives/ws-06-memory-compatibility-ingestion.md)
Approval: Maintainer said "approved - proceed with speed" on 2026-09-29.

## Result And Boundary

Direct MCP semantic ingestion remains disabled by default. Explicit enabled plus
an exact server OR canonical-tool grant permits one separately sanitized snapshot
per eligible completed call. Native/conversation/file memory behavior remains
compatible. This does not prevent assistant prose from mentioning a tool-derived
fact or introduce global taint tracking.

Memory-owned immutable DTOs reuse accepted Core execution metadata and policy.
Snapshots have real call/turn/memory IDs, exact source names/trust, captured policy
and matched grant, execution and memory sanitizer facts, truncation/size and aware
capture time. Freshness is snapshot_at_capture; revocation is not_implemented.
Validated JSON metadata has a 65536-byte cap. The entire stored UTF-8 document,
including label, escaped body and untrusted wrapper, obeys max_ingested_bytes.
Unsafe/oversized output is rejected without raw quarantine, argument hashes,
secret-bearing diagnostics or graph extraction. No config/schema/dependency change.

Pending records are durable but cannot enter retrieval or promotion. Storage is
verified before marking paired per-call facts ingested. The real append-only
transcript adapter reads back the actual entry and matching call/result facts.
Only verified receipts allow publication. Returned turn records retain actual
ingestion facts. False writes, partial errors, retries, repeated calls, concurrency
and cancellation do not invent IDs or publish uncorrelated records.

Before a transcript append is attempted, failed preparation is removed best-effort.
Once an append starts, it may have committed despite a later error: retain pending
records rather than falsify an immutable receipt. Publication failure likewise
retains durable pending storage and a truthful ingested receipt; ingested means
stored, not necessarily retrievable. A crash can leave pending records excluded
indefinitely. There is no automatic recovery or remote revocation feature.

Chat applies validated source/trust/freshness labels and query exclusion before
flattening memory into strings. It forwards WS-04's exact reduced retrieval limit
once, including zero. Native snippets retain order/behavior; complete new MCP
snippets fit the residual conservative UTF-8 byte/4 estimate or are omitted.
Legacy native item-count budgeting is not exact tokenizer accounting. MCP
snapshots retain metadata through stage movement and are excluded from native
maintenance synthesis/verification/dedupe/prune/provider candidates; diagnostic
all-vector references still retain them for complete plan integrity.

## Exact Files And Tactical Coverage

All 18 authorized product/report paths changed: nine source files, eight test
files and this report. No other product/config/dependency paths changed.

| Task | Implementation and meaningful evidence |
| --- | --- |
| MCP-06-01 | Memory models/mcp.py, ingestion/mcp.py and typed storage methods in CollectionManager; DTO/storage/actual-ID/metadata/reload cases in Memory and Chat tests. |
| MCP-06-02 | Disabled gate before direct writes/embedding/IDs; optional Chat runtime capabilities preserve old adapters and ordinary store_turn; real default turns persist transcript/episodic history only. |
| MCP-06-03 | Exact server OR canonical-tool union, fixed matched grant; unit allowlist negatives and real two-server canonical-tool-only integration. |
| MCP-06-04 | Separate complete block/drop storage sanitation; final UTF-8 bound; stage/readback/append/verify/publish coordinator; false/partial/cancel/readback/publication and cleanup probes. |
| MCP-06-05 | Snapshot/no-revocation metadata, pending/malformed retrieval and promotion guards, preserved stage metadata, narrow typed maintenance eligibility/prune guards. |
| MCP-06-06 | Production adapter passes supplied limit once; no duplicate schema/result reservation; full snippet overhead/residual estimate tested at exact fit, one below, zero and native exhaustion. |
| MCP-06-07 | Public Memory retrieval helpers, source/trust/freshness labels, explicit exclusion, malformed-record rejection, old ordinary compatibility and safe string flattening. |

The exact path manifest is the approved directive. New source: Memory models,
ingestion and retrieval mcp.py; Chat memory_mcp.py. Existing source: Memory
CollectionManager/maintenance mutation and Chat runtime/adapters/turn processor.
Tests: the eight directive paths. CollectionManager's file-wide ignore was
removed; three previously hidden typing issues were fixed locally. No new broad
suppression, blanket cast, settings weakening or outside-file repair.

## Criteria Assessment By Builder

These are builder evidence mappings, not independent PASS/VERIFIED assertions.

| Criterion | Evidence |
| --- | --- |
| WS06-AC01 | Typed accepted contracts plus real safe IDs; Chroma reload, SQLite paired facts, bounded strict JSON and isolated distributions. |
| WS06-AC02 | Disabled path: zero semantic writes/IDs/embedding writes, safe transcript, actual episodic conversation and legacy optional-capability compatibility. |
| WS06-AC03 | Exact server/tool/union positives; original/prefix/case/wildcard/unlisted and failed/unchecked negatives; two local peers with one exact canonical grant. |
| WS06-AC04 | Complete unsafe/multibyte/normalization/escape/oversized/tiny-cap checks and fixed safe results; no raw unsafe storage or secret sentinels in retained output. |
| WS06-AC05 | Verified write and real receipt, paired/returned facts, repeated/mixed calls, concurrent turns, retry collision protection, false writes, partial exception/cancel/readback/publication failures. |
| WS06-AC06 | Snapshot/stale/unknown and no-revocation labels; pending crash/failed cleanup exclusion, promotion/decay/reload fidelity and native maintenance guards. |
| WS06-AC07 | Public snippet helper/real adapter labels, include_mcp false, malformed record rejection and native/old compatibility. |
| WS06-AC08 | Exact forwarded budgets, opt-in WS-04 regression, complete overhead/residual fit and zero-budget exclusion; unchanged selection/reserve/floor regressions. |
| WS06-AC09 | Real temporary Chroma, MemoryController, local stdio, SQLite, streaming/non-streaming and JSONL/Markdown/CSV privacy/export compatibility; no migration. |
| WS06-AC10 | 18-path scope, nine-file meaningful typing, broad/focused checks, independently captured base failures, 11 offline built wheels/declared closure proof, cleanup and preservation. |

## Exact Checks And Baselines

Complete commands, outputs and exits are in [builder evidence](WS-06-builder-evidence.yaml)
and its [lossless archive](WS-06-builder-evidence.tar.gz). Logs/scripts/command
records retain successful checks and failed attempts. Source hashes, package
metadata/declared version closure/file hashes and built wheels are retained.
Runtime DBs/venvs/cache and actual dependency file contents are excluded.

| Check label | Exit | Result |
| --- | --- | --- |
| focused | 0 | 161 passed in 3.08s |
| compat | 0 | 97 passed in 4.23s |
| memory | 0 | 715 passed, 1 skipped, 1 warning in 11.19s |
| chat | 1 | 1 failed, 609 passed, 5 skipped, 1 warning, 3 errors in 16.76s |
| transcript | 0 | 35 passed in 0.29s |
| agent | 0 | 209 passed, 10 warnings in 0.19s |
| framework | 0 | 416 passed in 8.21s |
| integration | 1 | 1 failed, 79 passed in 51.79s |
| ruff | 0 | All checks passed! |
| typing | 2 | Found 1 error in 1 file (errors prevented further checking) |
| source-typing | 0 | Success: no issues found in 9 source files |
| wheel-final | 0 | Built-wheel public imports and typed Chroma/SQLite round-trip passed with no editable source. |

Memory baseline before edits: 680 passed/1 skipped; candidate 715 passed/1 skipped.
Chat baseline: 591 passed/5 skipped, one PTY failure and three localhost setup
errors; candidate 609 passed with the same four failures. Transcript candidate
35 passes. Independent approved-base archive reproduction retains the exact
integration assertion: expects 22 tasks, actual valid board has 23. Candidate
integration has 79 passes and that same failure. Default broad mypy repeats
NumPy's Python-3.10 syntax failure; all nine affected files pass Python-3.13
mypy without error filtering. Ruff passes across all required packages/test.
These base failures are not repaired or waived; fresh reviewer must reproduce them.

Offline lock check passes (208 packages). Board validate (23 tasks), next/show,
render check, documentation lifecycle/links and whitespace pass. Final candidate
and request checks are separately recorded by the controller at the frozen handoff.
Local-peer tests explicitly drain/wait owned processes and stop provider/registry
in finally. No provider/paid call, credential use or real runtime DB access.

Eleven current wheels built offline. Clean offline resolver/install fails because
litellm is absent from that cache; no clean install claim. The required proof uses
a fresh -I venv, extracted newly built declared framework wheels and recursively
marker/version-validated declared third-party distributions, without editable
hooks or workspace PYTHONPATH. Public new Memory/Chat contracts and production
Chroma/SQLite receipt/retrieval round-trip pass. First isolated harness run from
repository cwd detected a cwd path inserted during dependency import; the final
run from scratch cwd passes. One supplemental manual invocation omitted the
local-cost-map setting and attempted a metadata fetch, which failed DNS; final
recorded run uses the local map. No LLM/provider request was made.

Early test harness attempts are disclosed: missing expanded config defaults,
missing adapter/interaction arguments and wrong JSONL key; then maintenance test
initially inspected complete diagnostic references rather than mutation targets,
and Transcript fixture omitted required model_name. Corrected focused suite passes.
No failed product check was hidden by filtering or skipping; subsequent changes
were verified by the focused/broad suites above.

## Preservation And Remaining Gate

Freeze proof confirms 968 outside-manifest product files unchanged, all 34
accepted VAL-013 authority inputs, five reports and 19 historical artifacts
unchanged, and exact fingerprints of the five unrelated paths preserved.
Those paths are .DS_Store, absent family-tree.md, docker-bench-security/, the
Chat pre-typed-LLM config backup and sandbox Dockerfile.audit. No broad staging,
cache/Chroma/transcript-state cleanup, later workstream or delivery operation.

Next is a new fresh-context read-only VAL-014 full WS-06 aggregate from the approved
base, all seven tasks/ten criteria/required checks and independent public/failure/
package/preservation evidence. The validator does no fixes and gets public pinned
inputs, not private builder/controller reasoning. Complete aggregate VERIFIED is
required before proposed closeout; only the maintainer accepts WS-06.

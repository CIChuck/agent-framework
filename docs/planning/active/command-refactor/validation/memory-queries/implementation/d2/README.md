# MEMQ D2 builder record — Chat memory queries and option R

Status: **implemented; documentation correction awaiting fresh D2 council**.
[Round1 reconciliation](council-round1/report.md): Sol9.6/Claude9.4 VERIFIED; Astra9.3 CHANGES_REQUESTED for MEMQ-D2-ASTRA-001. Runtime checks passed; [bounded correction](../../../../remediation/REM-CMD-MEMQ-D2-001-status-and-uat.md) changes documents only.
Execution phase: validation. Validation state: pending.
Source commit `3ed1d58ad8cc1e79522495da5cf19091185402d8`; start HEAD `39661e87`.
The exact [contract](../../../../memory-query-command-contract.md),
[directive](../../../../directives/CD-CMD-MEMQ-001-memory-queries.md) and
[current approval](../../../../approval/memory-queries-directive-correction2.md)
remain unchanged. [D1 reconciliation](../d1/verified-report.md) is VERIFIED at
9ce71581 (Sol9.7/Astra9.6/Claude9.6), with no mandatory findings.

## Delivered behavior and boundaries

Chat owns runtime reads, detached display projections, pure rendering and
compatibility wrappers. The shared neutral owner selects kinds/graph mode,
validates requests/results and awaits one capability. All six wrappers delegate
exactly once using fixed shared spec identity and the original parsed args;
custom/renamed handlers retain authority. Only the six approved registry tuple
entries change. Public preview/record-value helper source bytes and all unrelated
registry/runtime/adapter definitions are preserved by complete AST audits.

Statistics keep eight sections/24 metrics and legacy failures/formatting.
Records preserve lazy plain metadata, complete/incomplete meta behavior,
100 caps, old repeated accesses and once-only preview/formatting. Graph reads
complete before projection, with exact nodes selection and0/False suffixes.
The adapter consumes only the six typed no-error/no-effect data variants.

Option R adds only the two Chat views, public protocol/fake method and adapter
method/private projection helper. It reads short/long get_all with limit=None
and ingested_file filter, groups `(source,description)`, counts stored chunks,
sorts None-first and returns sanitized partial warnings. Decayed/source-file
reads, ingestion changes, synthesis, consolidation and framework changes are
excluded. Fake listing retains insertion order and recorded counts.

## Actual checks

| Gate | Result |
| --- | --- |
| New MQ-T07..14 nodes |52 pass: frozen/metadata1, delegation6, statistics6, records15, graph9, adapter8, real synthetic app1, persisted/fake listing6. No skips/xfails. |
| Current owning suites |Chat1390, Commands/cohort599, CLI155 pass. Chat has one existing Legacy Memory LLM deprecation warning. |
| Required fast lanes |D2-fast616 and D3-fast117 pass; the latter is the directive's source-test lane, not D3 artifact proof. |
| Canonical source run |651 (new52+neutral/cohort599) pass, with primary module roots/hashes before pytest, at session finish and after. Instrumentation has one anyio assertion-rewrite warning. |
| Private current controls |Unchanged52 passes; all20 mutants have named CALL assertion witnesses, stable canonical origins/hashes and no setup/import credit. |
| Frozen source observations |MEMQ68 exact+2 declared kind refusals+6 repair-superseded twice, from separate exports. DIAG68+4 approved cache refusals, SESSION25 and pilot196 match. Guard18/comparer14 and current pre-import source extra/byte refusals pass. |
| Supplemental records |All4 case outputs/events match exactly. Scenario logic is unchanged; the private control explicitly updates only three historical proof labels to the actual candidate/changed-source status. No false unchanged-product claim is used. |
| Static and format |Full named neutral/Chat/option R Ruff gate passes; mypy15 source files passes with explicit private cache. Seven changed Python format check reports4 existing failed files/3 formatted. Pinned no-new-debt gate passes with old debt unwaived. |
| Metadata/admin |Offline clean-current-export lock214, board validate36, dashboard check, documentation lifecycle925 and diff checks pass. No metadata/dependency/config/lock change. |
| Source retention |Original Chat ASTs reverse after only approved additions/wrappers/six tuple replacements; public helper bytes unchanged; exact package fixture SHA0403471b… . D1 source/tests/API stay unchanged; its README update is permitted documentation. |

The20 mutants cover early graph projection, warning dedupe/order, zero-as-missing,
missing utilization suffix, record/entity cap, double formatting, ignored result,
legacy engine substitution, decayed reads, grouping/count/order/cancellation,
missing kind refusal, case-folded nodes, nodes relationships and double/unawaited
query. Actual witness nodes, roots/hashes, commands and raw outputs are preserved
as94 exact embedded/raw pairs in [evidence.json](evidence.json).
Supplied builder/reviewer directories are read-only; reconstruct every output,
cache, basetemp and explicit mypy --cache-dir in fresh reviewer scratch.

## Limits and debt

The original six synthetic getattr-listing rows are superseded, not reported
unchanged. Six new real/fake listing cases cover persisted single/multi-chunk
ingest, re-ingest, promotion, description grouping/order, malformed/partial reads,
decayed/source read tripwires and cancellation. They use fresh disposable stores
and deterministic local embeddings; no provider/network or real user store.

An existing ingestion limitation surfaced: omitting description passes None to
Chroma, which rejects that metadata. The unchanged ingest method is proven by
the complete AST audit and paired clean pre-D2/candidate exports reproducing the
exact same TypeError and message; no repair or waiver is included. Real listing tests use
explicit ingest descriptions and a directly persisted record with the optional
description key absent. Fake None-description behavior remains covered. A child
CancelledError from gather may be reconstructed; capability/port cancellation
identity is separately tested, and no cancellation is swallowed.

Initial assertion/setup/KeyError attempts are disclosed and earn no passing
credit. Root Ruff534, root test_display conflict6929 and four existing Chat
format failures remain failed/unwaived. Future candidate builds, installed MEMQ
proof and human UAT are not claimed. The [UAT plan](../../../../uat/memq-user-acceptance-plan.md)
remains in the established folder, all20 cases NOT RUN. Its correction-cycle1 instructions now explicitly require an ingestion description as the workaround for unchanged baseline debt.

**Next gate:** Reconcile fresh Sol/Astra/Claude MEMQ D2 documentation correction review, then D3 artifacts and installed proof under the existing approval. Round1 runtime checks passed; MEMQ-D2-ASTRA-001 correction awaits independent verification. UAT NOT RUN; no acceptance or delivery.

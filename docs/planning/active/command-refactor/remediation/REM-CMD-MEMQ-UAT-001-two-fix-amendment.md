# REM-CMD-MEMQ-UAT-001 — quoted entity names and absent ingest descriptions

Status: **PROPOSED — awaiting Chuck Russell’s approval of this exact bounded
amendment. Product implementation has not started.** Prepared 2026-11-09.
This proposal adds no authority until approved. UAT remains stopped. It is one
repair unit, with one candidate and one implementation council; no separate
readiness council or new D0–D3 construction sequence is proposed.

## Authority and baseline

Initiative: `friday-command-refactor`, started/local, branch
`feature/command-retirement`. Planning base: `a0594eea1cfc6394851537445ed2be16a46fe3b4`;
reviewed MEMQ candidate `bab167579a0c6fcae8765f263ec754f1d4700d93` and installed
source `e4c0b9a2c5e80569829cc56af9addc8b3e358714` remain historical VERIFIED evidence.
The [contract](../memory-query-command-contract.md) and
[directive](../directives/CD-CMD-MEMQ-001-memory-queries.md) otherwise remain in
force. Approval of this document would supersede only MQ-05’s literal outer-quote
behavior in the Chat host and the directive’s prohibition on the specific
optional-description metadata repair below. It grants no acceptance or delivery.

The supplied UAT transcript confirms that unquoted `Peano Arithmetic (PA)`
works while the quoted form does not. The ingestion attachment shows returned
embeddings followed by Chroma rejecting `description: None`. Fresh installed
reproductions use a private graph and Chroma store: quoted lookups fail, and
omitted-description single/batch writes fail; explicit descriptions succeed.
[FU-009](../../../backlog/friday-chat-framework-followups/upgrade-log.md#fu-009-omit-absent-ingestion-description-metadata)
tracks the ingestion defect. The original MEMQ contract deliberately preserved
both behaviors; these are explicit new compatibility decisions, not claims
that the reviewed candidate violated its approved contract.

## Fix Q — optional outer quotes for `/entities` names

Normalize the already-joined name only inside `ChatMemoryQueryPort.graph_snapshot`,
before the existing entity/relationship reads. A small private helper in that
module may be added. Remove exactly one matching outer pair of ASCII single
or double quotes only when the interior contains non-whitespace text. Preserve
that interior as provided by the existing whitespace parser. Do not repeat
stripping or interpret escapes, substitutions or shell syntax.

- `/entities Chuck` and `/entities "Chuck"` query the same name.
- `/entities Peano Arithmetic (PA)`, `/entities "Peano Arithmetic (PA)"`
  and `/entities 'Peano Arithmetic (PA)'` query the same complete label.
- Preserve internal apostrophes/quotation marks, backslashes, Unicode and
  parentheses. Unbalanced/mismatched quote pairs pass through unchanged.
- Empty/whitespace-only quoted inputs pass through unchanged; they must not
  become an unfiltered listing request.
- Exact lowercase unquoted first argument `nodes` remains the special mode.
  `NODES` remains a name. Quoted `"nodes"` is an ordinary lookup for the label
  `nodes`, with relationships permitted; it does not become listing mode.
- Normalize once and use the same name for both reads. Preserve await order,
  caps, output formatting, errors/cancellation and read-only behavior.

This intentionally changes how literal labels whose first and last characters
are matching quote marks are selected; no new escaping mechanism is added.
Exact label matching remains: `Peano Arithmetic` is not an alias for the stored
label `Peano Arithmetic (PA)`. The shared command parser and neutral handlers
continue receiving/preserving their original raw argument tuples.

## Fix I — omit an absent optional ingestion description

Inside `FrameworkMemoryAdapter._ingest_document` only, omit the `description`
metadata key when its value is `None`, in both the single-document and batch
branches. Preserve an explicitly provided empty string or non-empty description
verbatim. Do not stringify None or manufacture a description.

Retain source/type/chunk_index/chunk_count and all controller-managed metadata,
chunking, embeddings, protection, storage/promotion and listing grouping rules.
Leave the `/ingest` command parser/handler unchanged. Real Chroma must accept
single- and multi-chunk ingestion without a description and subsequent listing
must render the missing description as empty, as already specified. Re-ingestion
and explicit-description behavior remain unchanged. No store migration or
modification of existing records is authorized.

## Exact implementation allowlist

| Path | Allowed change |
| --- | --- |
| `packages/friday-chat/src/friday_chat/commands/memory_queries.py` | Fix Q private helper and normalization in graph_snapshot only. |
| `packages/friday-chat/src/friday_chat/adapters.py` | Fix I metadata construction in _ingest_document only. |
| `packages/friday-chat/tests_chat/test_memq_uat_repair.py` (new) | Focused command, real-graph and real-Chroma regressions and negative controls. |
| `packages/friday-chat/tests_chat/test_command_memory_queries.py` | Amend only the exact frozen-case comparison for entities:quoted as specified below. All other old assertions/test bodies unchanged. |
| `docs/planning/active/command-refactor/validation/memory-queries/uat-repair/` (new) | Frozen request, pins, bounded compatibility comparison, installed checks, raw evidence, independent reports and final handoff. |
| `packages/friday-chat/README.md` | Document these two behaviors only. |
| This amendment; packet README/authority/next-phase/tactical/execution-log; board/dashboard | Exact approval, repair progress and evidence; preserve append-only history. |
| MEMQ UAT plan and existing D3 handoff | Correct only quoted-name expectations, ingestion workaround/status, repaired build identity and targeted retest instructions. Preserve and reconcile the maintainer’s existing uncommitted UAT edits. |
| FU-009 in the Chat framework follow-up log | Record this repair and validation; leave other follow-ups unchanged. |

No neutral package source/test/API/union/export changes. No shared parser,
framework package, dependency, lock, config, schema/migration, provider setup,
source validation, fuzzy/partial matching, uppercase-NODES alias, new command,
maintenance, telemetry or exception-handling overhaul. Old approval, directive,
contract, baseline JSON and all accepted evidence remain byte-exact; this
amendment records the two exceptions without rewriting that history.

## Acceptance and regression criteria

1. **Q-01:** Registry dispatch on a fresh real graph proves quoted/unquoted
   Chuck and Peano Arithmetic (PA) selections equal, using known fixture labels.
   Cover double/single outer quotes, parentheses, Unicode and internal apostrophes.
2. **Q-02:** Assert names delivered to entity and relationship reads, exactly
   once/in order. Cover nodes, NODES, quoted nodes, malformed/mismatched/empty
   quotes, backslashes and a missing exact-label suffix. Ensure failed or empty
   selections never broaden to all-node output. Preserve cancellation/errors.
3. **Q-03:** Prove global parser argument tuples and representative other-command
   quoting remain unchanged. No command-wide shell parser is introduced.
4. **I-01:** Through the actual `/ingest` command and real FrameworkMemoryAdapter
   on disposable Chroma, single/multi files with omitted descriptions succeed,
   produce stored chunk counts and appear under `/list-ingested`.
5. **I-02:** Exact metadata assertions distinguish absent, explicitly empty and
   non-empty descriptions in both branches. Prove chunk/protection metadata,
   explicit descriptions, re-ingest counts and listing groups are preserved.
   Deterministic local embeddings are permitted; no LM Studio/provider access.
6. **R-01:** Keep the immutable 76-row fixture hash unchanged. In the sole
   `entities:quoted` row, compare the full old row after replacing exactly its
   two lookup-name event strings with the stripped name. All other row fields,
   ordering and output remain equal. Report **67 exact +1 explicitly changed
   quote row +2 approved kind refusals +6 option-R superseded rows**. No broad
   skip, loose comparator or regenerated baseline is permitted. The new focused
   tests establish real selection behavior independently of the old stub row.
7. **R-02:** Mutating away quote normalization, normalizing only one graph read,
   reclassifying quoted nodes, or leaving None in either ingestion branch must
   fail named call-phase assertions. Setup/import/product exceptions alone earn
   no mutation credit. An unchanged control must pass.
8. **R-03:** Run the owning Chat suite (including the new tests), Commands/cohort,
   CLI, changed-path lint/types, new-file formatting and the pinned no-new-format-
   debt check. Root/format debt remains failed/unwaived. Run board/dashboard/docs
   and diff checks. Use the existing offline Python3.13.10 environment, external
   caches/basetemps and passive canonical module-origin checks.
9. **R-04:** Build/replay the repaired candidate with the pinned offline inputs;
   verify the Chat closure and unchanged neutral surface. Run the existing
   installed pilot/MEMQ probes against matching new artifacts, then new installed
   Q/I command checks in normal and -O modes with real disposable graph/Chroma.
   Prove module origins inside the installed prefix. Preserve the old probe;
   new evidence must identify the repaired source/probe hashes and report which
   checks ran fresh versus which unchanged receipts were hash-inspected.
10. **R-05:** Freeze one repair candidate. Obtain a fresh read-only Sol/Astra/Claude
    implementation review under the approved roster: repair delta first, then
    bounded MEMQ aggregate interaction. No separate directive-readiness council,
    nested delegation or unrequested new workflow. Reuse verified unchanged
    evidence by explicit hash inspection where permitted; never carry a prior
    verdict onto changed bytes. Retest MQ-UAT-08 and10–14 plus impacted read-only
    checks after controller reconciliation. Preserve earlier UAT observations;
    do not claim all20 cases passed or record acceptance automatically.

All review/build/output writes use new private external scratch. Preserve the
three current dirty files (including the maintainer’s UAT edits), ignored exports,
personal stores, external locator, supplied build/evidence directories and all
prior raw reports. No cleanup, provider request, push, merge or release.

## Reporting and stop conditions

Record exact base/candidate, approval and source hashes; commands/results and
module origins; single/batch stored metadata/counts; compatibility-row accounting;
failed attempts with no passing credit; preserved identities; independent result;
new installed launch command; and the targeted human retest checklist.

Stop before implementation until this exact amendment is approved. During the
repair, stop for a conflict requiring another source/package/behavior change,
protected-state drift, missing offline inputs, or a new unexplained regression.
After two unsuccessful bounded correction cycles, return remaining findings to
Chuck Russell. No automatic scope expansion. Stop after verified repair for
human UAT and the maintainer’s acceptance decision.

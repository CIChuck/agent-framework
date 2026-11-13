# Opus seat: INGEST product directive, additional pass 1/3 (global round 3)

## Opening boundary
- **Request file:** SHA256 `39e8c399…3f94f3c39` matched before I read it.
- **Helper:** I read `review_tools.py` (`2e20c4e5…`) in full before running it. It writes only to reviewer scratch.
- **Boundary check:** passed, exit 0. Logical index `96a44982…c8c` was measured before status. HEAD is `af4e12bd`, branch `feature/cmd-ingest-001`, nothing staged, status shows only the two dirty Chat YAML files and `.friday-old/`. The check covered 18,790 tracked files, 26 symlinks, 8 preserved entries and 47 pins.

## Verdict: **CHANGES_REQUESTED**
There are 3 mandatory findings (1 medium, 2 low).
- **Coverage:** 8.6/10.
- **Overall:** 8.9/10.
- Both are below the 9.5 target. Construction activation is **NOT APPROVED**, and every activation prerequisite (Q/A1–A5, RD-01–07) remains open.

## Mandatory findings

**F1 (medium): DI-22's earliest-complete stage is set too early.**
- **Requirement:** DI-22 requires a "role spy matrix for every inventoried caller", explicitly including source/derived storage, with the whole batch validated before the first write. The map defines "earliest complete evidence" as the first point where the *complete original* scenario is available.
- **Evidence:**
  - `phase-evidence-map.json` sets DI-22 to stage I2, with references only to I1-C2 and I2-C2.
  - I3-C2 traces DI-16/17/19/23/24/30/31 but not DI-22, and I3-C3 does not trace it either.
  - At base, `large_file_processor.py:880-954` stores raw chunks, then the file synthesis, then chunk summaries, each separately. There is no source/derived preflight.
  - That caller is only rebuilt at I3-C2, which is also where the smart_read/large-file/tool-ingester paths are listed. `/ingest` common-entry storage only exists from I3-C3.
- **Risk:** this is the same defect class as the DI-24/33 correction. No I3 exit is required to produce role evidence for the callers I3 creates or restructures, so AG would find the gap instead of an I3 witness.
- **Fix (bounded):**
  - Add I3-C2 and I3-C3 to DI-22's scoped references, and DI-22 to those exits' traces.
  - Set its earliest-complete stage to I3.
  - State that I2 covers existing callers only.
  - Update the MD join table to match.
- **Proof:** re-run the bidirectional join check. There are no other document effects.

**F2 (low): the frozen fixture inventory misses some tracked test-tree files.**
- **Requirement:** the directive says it freezes "tracked test/fixture bytes", and the summary scope says "Tracked package/integration fixtures and conftest hashes".
- **Evidence:** at base there are 63 tracked non-Python files under test trees, but only 59 are inventoried. The missing ones are:
  - `packages/friday-chat/tests_chat/fixtures_session/session-baseline.json`. It is read by `test_command_session_views.py:47` and `test_command_diagnostics.py:63`, and it contains a quoted-argument case for an unrelated command. That makes it an oracle for the "parser preserved for unrelated commands" requirement and the retained SESSION/DIAG regressions.
  - `tests/integration/llm/config.yaml` and `tests/integration/llm/README.md`.
  - `tests/integration/.DS_Store`.
- **Fix:** add these files to the inventory (or record `.DS_Store` as an excluded artifact). Alternatively, narrow the scope statement to the actual selection rule and list the exclusions. Then regenerate the gzip and summary digests.

**F3 (low): the pinned branch handoff has stale routing.**
- **Evidence:** `branch-handoff.md` still says "**Next gate:** Corrected conditional product directive is in fresh round2 review". The directive, readiness decision, TOOLS-DOC and current controls all say additional pass 1/3, global round 3.
- **Risk:** this is a direct PD-16 disagreement, and AGENTS.md says disagreeing documents must be reconciled. It grants no authority.
- **Fix:** update that single routing line.

## Advisories (not mandatory)
- **A1:** The I2-C1 JSON exit text still says "CLI is source-unchanged if forwarding suffices". It is logically consistent, but `container.py` is not a primary seam, and the four-origin test duty appears only in the MD prose and the FC-10 row.
- **A2:** I1-C3 adds direct store admission while existing Chat/Runtime callers (`di.py:250,295`, `ChromaVectorStore.__init__` opening `PersistentClient`) are only wired at I2. A2 should state the I1 intermediate-compatibility approach (additive or mapped temporary exception) so the PD-Q05 blocking rule doesn't strand I1.
- **A3:** I1 changes LLM/Memory extras, so a `uv.lock` delta starts at I1. `uv.lock` is currently a primary seam only at I3-C5, so A2 should assign it to I1 as well.

## Correction delta (PD-Q01–07)
| ID | Result |
| --- | --- |
| Q01 | **Closed.** A1, RD-01/RD-05, the qualification plan (4 slots, all `qualified:false`, `actual_serving` required) and the map all keep actual B/N-DIM/N-SPACE/N-CAP qualification before I1. They forbid deterministic-only completion and keep candidate N operations at I2/AG. This is consistent with the annex's B/N/R requirement and impact v0.6. |
| Q02 | **Closed.** The raw receipt blob is unchanged from base to candidate, and its hash `36682354…` equals the projection's `source_sha256`. The projection contains only digests and byte counts. `boundary.json` is hashes/metadata only. |
| Q03 | **Closed.** The "primary seams, not exhaustive" wording is in the directive §4, the MD and the JSON `path_list_semantics`. Pruner/synthesizer/fact-checker admission is named for I2-C2. |
| Q04 | **Closed for DI-24/33**, which now join both ways. All 19 annex witnesses are mapped one-for-one with specific per-FC I2 and I3 text. F1 is a residual of the same class for DI-22. |
| Q05 | **Closed.** The blocking rule is in directive §7, the MD and the JSON `intermediate_regression_rule`. |
| Q06 | **Closed.** I independently enumerated 30 non-test support modules at base, 30/30 are listed, with no hash mismatches and zero node credit. |
| Q07 | **Substantively closed.** The source confirms `to_runtime_config()` forwards the resolved `chroma_path` (`container.py:70,126`). Settlement is required before I1, and I2-C1 must test the four origins. See A1 for the residual wording. |

## PD-R01–03
- **R01: met, except F1.**
  - The phase DAG Q→I1→I2→I3→AG→UAT is acyclic and forward-only.
  - All 12 exits join both ways, with no unknown references.
  - The DI-17/23/28/29/32/33 splits and the per-slice versus AG treatment of DI-35/36 are coherent.
  - DI-12's UAT is explicitly later.
  - I found no exit that requires later implementation.
- **R02: met.** Every RD-01–07 Q column uses upstream/unchanged-code/proposal evidence. A2 is a design binding, and Gate-A 9.5 plus the final installed positives are retained.
- **R03: met.**
  - All 36 DI definitions match the REM table byte-for-byte, and the SHA256 digests match.
  - The 12 proof groups are disjoint and cover all 36.
  - The 3 seed entries' file and definition hashes match the inventory, and the "eight-byte" seed is exactly `%PDF-1.4`.
  - DI-12's three-seat code council before UAT is retained.
  - The package arithmetic holds: 8 owners plus Agent plus 8 indirect packages = 17.

## PD-01–16
| ID | Result |
| --- | --- |
| 01 | Pass. The three-pass cap, approvals pending, no effects. |
| 02 | Pass with F1 and A2. Bounded and traceable, no circular activation. |
| 03 | Pass. Ownership matches the REM and impact v0.6. No new Tools↔Memory edge, and legacy edges are disclosed. |
| 04 | Pass. Matches REM A/B and the measured settings. |
| 05 | Pass. Matches REM C exactly (raw tail, the two options, `--` terminator, `/read` refusal, line rules). |
| 06 | Pass. Matches REM D (independent precedence, final-input budget, no second chunking pass, plain CSV has no inferred header). |
| 07 | Pass. Consistent with the actual `embed_query`/`embed_documents`/`_embed_batch_with_retry` bodies (no order or shape validation yet). |
| 08 | Pass. The six annex exceptions are listed individually, FC-03/09 are bounded, and there is no backup or migration project. |
| 09 | Pass with F1. FC-01–14 and B01–08 are traced, and the 19 witnesses are mapped. |
| 10 | Pass. Worker, lease and quiescence ownership are clear, and the source seams exist (`assembler.py:420`, Agent `base.py:500`). |
| 11 | **Fail (F2).** Otherwise the inventory is exact: 237 modules, 3,073 AST nodes re-derived with matching `ast.dump` digests and line numbers, and both gzip/uncompressed digests match. |
| 12 | Pass. Matches G2, the architecture plan and the guide handoff. |
| 13 | Pass. Transcript/Finance selectors explicit, Finance live module excluded. |
| 14 | Pass. All three measured archives stream-verify: 8,148/8,148, 367/367 and 194/194 members, with hashes and sizes equal to the indexes. Fact checks hold: 81 chunks per mode, 162+10 vectors, server usage 0, 20 documents/31,544 words/46 pages/6 sheets/96 slides, no large-corpus Docling run. |
| 15 | Pass. The REM allowlist intersection plus mandatory A2/A3 assignment grants no broad edits. |
| 16 | **Fail (F3).** INGEST and TOOLS-DOC are otherwise consistently separate. |

## Scores
- **Coverage 8.6.** Fully read: the target, readiness decision, phase map (MD and JSON), qualification plan, projection, manifest, seed, inventories, criteria, brief, authorization, controls, annex, REM headers/A/C/D/F/paths/G, most of impact v0.6, the test-migration and architecture plans, TOOLS-DOC, and the approval/store/handoff/assessment records. Only partly read: REM B/E (§332–456, 632–1205), the three policy documents, the TOOLS-DOC proposal, guide handoff details and the results narratives beyond their fact checks. Source depth was targeted seams only.
- **Overall 8.9.** Rubric breakdown:

| Area | Score | Reason |
| --- | --- | --- |
| Scope/authority | 1.35 of 1.5 | F3 |
| Architecture/feasibility | 1.8 of 2.0 | A2, A3 |
| Extraction/chunking | 1.9 of 2.0 | — |
| Compatibility/data/effects | 2.6 of 3.0 | F1 |
| Tests/docs/evidence | 1.25 of 1.5 | F2 |
- No rounding up or averaging was applied.

## Commands and exits
- **Opening and closing boundary:** exit 0 and exit 0.
- **The seven admin checks**, all exit 0:

| Check | Result |
| --- | --- |
| board | 36 tasks validated |
| dashboard | current |
| docs | 1,143 Markdown files checked |
| metadata | 18 `pyproject.toml` files validated |
| range-whitespace | passed |
| owned-whitespace | passed |
| staged-whitespace | passed |
- **My own scripts**, all stdlib-only, run with `-I -B` and exit 0:
  - `joins.py`: DI digests, proof groups, DAG, exits and FC witnesses.
  - `helpers.py`: helper-module inventory.
  - `inv.py`: test inventory and AST nodes.
  - `archives.py`: archive members.
- **Also ran:** read-only `git cat-file`, `git diff`, `grep` and `sed`.
- **Closing re-check:** request, helper, boundary and controls hashes were unchanged.

## Fresh versus inspected evidence
- **Fresh:** every join, digest, inventory, AST, archive and helper check above, plus the source seams I read (CLI `container.py`, Runtime `config.py`/`di.py`, Core `profiles.py`, Memory `vector.py`/`assembler.py`/`recovery*`/`large_file_processor.py`/`tool_ingester.py`, Tools `smart_read.py`, LLM `embeddings.py`, Chat `registry.py`/`files.py`/MCP sites).
- **Inspected, not rerun:** the historical test runs behind the measured facts. Archive checks are hash checks, not replays.

## Limits
- No product imports, tests, installs, network access, model calls or store access.
- I did not read prior or peer reports, memory, or raw authority/navigation/log history. The diff stat showed peer report filenames only.
- Scratch outputs: `/private/tmp/claude-501/-Users-chuckrussell-Dev-gendev-agent-framework/1fa344f1-96fb-4755-9dca-1cd767dc92ee/scratchpad/r3-opus-pass1/` (summary at `/private/tmp/claude-501/-Users-chuckrussell-Dev-gendev-agent-framework/1fa344f1-96fb-4755-9dca-1cd767dc92ee/scratchpad/r3-opus-pass1/report.md`).

## Closing boundary
Passed and identical to the opening: HEAD, branch, logical index, status, staged files and 47 pins all match.

This seat stops here. It grants no Gate-A, construction, acceptance or delivery authority.

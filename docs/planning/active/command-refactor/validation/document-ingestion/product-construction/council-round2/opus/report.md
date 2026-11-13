# INGEST product directive — council round 2/2 — Opus seat report

Seat: claude-opus-5-5, high effort, fresh, read-only, no delegation.
Target: `docs/planning/active/command-refactor/directives/CD-CMD-INGEST-001-product.md`
SHA256 `be9b6611d725740bff401464c3b4be6e51bb18396d3b631009f92501bba1ad8c`.
Candidate `be3aed3a9ba5629c548e36437e7e01a7333210d1`; correction base `5f43d424e3b695c3fb85227f74830a7d1dc895cf`.
Scope: conditional document readiness and source feasibility only.

## RESULT: CHANGES_REQUESTED

One mandatory finding (INGEST-PD-R2-OPUS-001). Coverage 9.1/10, overall 8.75/10.
Both scores are below the 9.5 threshold. Construction activation is NOT APPROVED.
The activation prerequisites A1–A5, all of RD-01–07 Q, and the Gate-A 9.5 readiness
review are still open. Passing this document review would not have granted Gate A,
construction, effects, UAT, acceptance or delivery.

## Correction closure (delta first)

- R1-001: closed. Checks: the DAG Q→I1→I2→I3→AG→UAT is acyclic; there are 12 exits;
  every exit→DI trace is reciprocal; no exit's phase is later than its requirement's
  earliest stage; DI-23 is I1 contract plus I3 actual; DI-32 is I1 values plus I2
  actual; DI-17 is I1 supplied text plus I3; DI-29 is I1, I2 and I3; DI-35 is per
  slice plus AG; DI-12 is AG plus UAT. Advisories A-1 and A-2 remain.
- R1-002: NOT closed. RD-01–07 Q and post-build columns otherwise separate correctly,
  but the replacement-model (N) qualification was dropped from Q (finding 001).
- R1-003: closed. All 36 parent-definition digests match the REM rows. The 12 proof
  groups are disjoint and cover all 36 DIs. Seed tags are TM-01 DI-01/02/04/13/14/35
  and TM-02 DI-07/35. The old file and AST definition hashes match. The `%PDF-1.4`
  seed is 8 bytes. The DI-12 post-code three-seat council is retained.
- AD-01 to AD-09: all addressed. AD-03's CLI disposition stays conditional; see A-6.

## Mandatory finding

### INGEST-PD-R2-OPUS-001 — the Q column drops replacement-model (N) qualification

- **Authority:**
  - Annex B/N/R: N is "explicit selection of another qualified embedding model".
    It must cover a different dimension, the same dimension with a different
    artifact or preparation, and a smaller capacity.
  - Annex: "Exact real model/dependency/counter feasibility remains Gate A".
  - Approved assessment v0.6, "Details to settle before construction approval":
    "baseline and replacement-model positives as well as refusals".
  - REM DI-20 and DI-33.
- **Source:**
  - v0.1 readiness RD-01 at base `5f43d424` required "actual baseline and
    replacement-model positive operations" and said Nomic E2E "does not qualify
    … a replacement model".
  - The v0.2 RD-01 Q column qualifies only the "actual selected deployment" and
    "unchanged-baseline positive operations". It only *defines* candidate B/N/R
    nodes.
  - RD-05 Q covers the "exact served artifact" in the singular.
  - The phase map, its JSON and the directive never mention replacement
    qualification. Meanwhile, I2/RD-01 post-build "runs actual integrated existing
    consumer B/N/R".
- **Risk (medium):**
  - I2's N positives depend on qualified replacement identities: their artifact or
    declared identity, local counter assets, capacity and dimensions. No Q step
    produces these.
  - That leaves a hidden forward dependency: either a late I2 stop after I1 is built,
    or N satisfied by doubles. The second contradicts DI-20 (real readiness
    distinguished from doubles) and the "no mock-only final proof" rule.
  - The correction silently narrows an approved parent's pre-construction item, with
    no materiality row.
- **Bounded fix:**
  - Add to the RD-01/RD-05 Q column: qualify the exact replacement identities that N
    will use. Cover the different-dimension, same-dimension different
    artifact/preparation, and smaller-capacity cases.
  - Each identity is either a real served model under separately authorized effects,
    or an explicitly declared deterministic test identity with real provisioned
    counter assets, labelled as not serving qualification.
  - Bind those identities into the asset manifest and the FC/DI-33 B/N/R node plan.
    Where meaningful, record unchanged-baseline replacement positives.
  - Keep candidate N positives and refusals as I2/AG post-build. Add a
    materiality-table row reconciling assessment v0.6's wording.
- **Proof:**
  - Readiness RD-01/05 Q text, a phase-map Q row and JSON naming N identities.
  - A directive A1 reference to them.
- **Docs impact:** `readiness-decision.md` and `phase-evidence-map.md/json`, plus
  one A1 sentence in the directive.

## Advisories

- **A-1:** exit `implemented_paths` are presented as "the exact listed JSON paths", and the
  directive says the map defines each exit's owner/path. Yet 28 REM production paths have no
  slice assignment. Examples: pruner/synthesizer/fact_checker/backup/analyzer/__main__,
  collection_manager, memory_controller, graph models/adapters, graph_scorer, pipeline,
  reorganizer, provider_contracts, extraction_filter, consolidator, promotion, ingestion/mcp,
  Memory/Chat mutation, embedding_limits, Chat config/templates/exports and CLI files.
  DI-28 names pruner/synthesizer/fact-checker yet claims I2 completion through exits that do
  not list them. Source confirms the `[memory_dir, memory_dir/vector]` fall-through in
  `pruner.py` `_get_chroma_client`. RD-04/A2/A3 do require exact phase path lists, so this is
  not an authority grant. Relabel the lists as primary paths, or add a complete row→slice
  partition before the first activation.
- **A-2:** DI-24 and DI-33 are listed as "earliest complete: I3", but no I3 exit traces them.
  DI-24's only ref, I1-C2, disclaims closure, so both are first verified only at AG. Either add
  them to I3-C2/I3-C5 or mark them AG.
- **A-3:** the 14 FC Q/I1/I2/I3/AG dispositions are identical boilerplate. The named annex
  nodes, apart from FC-10/FC-14 used as I2 witnesses, are not assigned to a slice. Assign each
  named node in A3.
- **A-4:** state whether an unchanged-scope regression at an intermediate slice blocks its exit
  or needs an exact A3 disposition. An example is Chat tests while Memory admission lands in I1
  before Chat wiring lands in I2. "Must be reported" alone could let an I1 exit pass with broken
  maintained consumers.
- **A-5:** the inventory omits non-`test_*`, non-fixture helper modules in test directories:
  `tests/integration/mcp_fake_server.py`, `tests/integration/llm/*.py` and Moltbook test apps.
  Disclose them in `excludes`, or hash them.
- **A-6:** source shows CLI `FridayConfig.chroma_path` defaults to `.friday/chroma` and
  `to_runtime_config` forwards it as a value. FC-10 origin therefore likely requires a CLI
  sentinel adaptation. Resolve the CLI disposition early in A2.

## Criterion matrix

- PD-01 PASS
- PD-02 PASS with advisories A-2 and A-4; the N dependency affects sequencing (001)
- PD-03 PASS
- PD-04 PASS
- PD-05 PASS
- PD-06 PASS
- PD-07 FAIL (001)
- PD-08 PASS
- PD-09 PASS with advisory A-3
- PD-10 PASS with advisory A-4
- PD-11 PASS with advisory A-5
- PD-12 PASS
- PD-13 PASS
- PD-14 FAIL (001: replacement qualification not distinguished as an open Q fact)
- PD-15 PASS with advisory A-1
- PD-16 PASS
- PD-R01 PASS with advisories A-1 and A-2
- PD-R02 FAIL (001)
- PD-R03 PASS

## Scores (honest, no rounding up)

Overall rubric:

| Area | Score | Reason |
| --- | --- | --- |
| Scope/authority | 1.45/1.5 | |
| Architecture/feasibility | 1.65/2.0 | A-1, A-2, A-4 |
| Extraction/chunking | 1.90/2.0 | |
| Compatibility/data/effects | 2.35/3.0 | 001, A-3 |
| Tests/docs/evidence | 1.40/1.5 | A-5 |
| **Total** | **8.75** | |

Coverage 9.1. Deductions for targeted, not exhaustive, source depth:

- Not read in full: LLM embed bodies, recovery.py, assembler and smart_read.
- Policies and the test-migration plan were read only in their relevant sections.
- The TOOLS-DOC proposal was read only through the companion directive.

## Fresh versus inspected facts

**Fresh:**

- request and helper SHA256 matched before reading;
- opening and closing boundary passed: 45 pins, 18,754 tracked files, 26 symlinks,
  8 preserved entries, logical index `6e7f445e…`, unchanged dirty status;
- all 7 admin checks exited 0;
- 36 DI digest recomputations;
- proof-group, exit-join and DAG checks;
- inventory recomputation: gz `dd37f3d5…`, JSON `3c513e8f…`, 237 modules, 3,073 nodes
  with all AST definition hashes equal, 72 fixtures, 237 inventoried + 28 excluded = 265
  tracked `test_*.py`, per-package and root-integration totals equal;
- seed old-file and AST hashes;
- three archive SHA256 values and every member's hash/size against its index:
  behavior 8,148 members / 67,376,725 B, E2E 367, large-v2 194;
- archive or pinned facts consistent with the readiness claims: 37 cases/mode,
  21 documents, 324 matrix, 41+40 stored chunks/mode, 5 rank-1 results, 162+10 vectors,
  20+5 corpus, maxima 31,544 words / 46 pages / 6 sheets / 96 slides.

**Inspected only:** historical test/E2E/large-document executions and receipts. Nothing
was rerun, converted, imported, served or opened with a database or store client.

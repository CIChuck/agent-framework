# INGEST product directive — council round 1 — seat opus — formal report

- Seat: opus (claude-opus-5-5, high effort). Fresh, independent, read-only, single round.
- Request: `request.json` SHA256 `6047aec2f9a5fa117055c41617b971edf01dd926a822a59b8fea8824891b4095`. I verified this hash before reading the file.
- Helper: `review_tools.py` SHA256 `2e20c4e5568d8501e04c6c3a8e7e3277c8f67500f2d43d30851f7d864a2c7e46`. I read every byte before running it.
- Candidate `fb587e7a12f48ef0d6937e008045de1de2dd8cd2` on `feature/cmd-ingest-001`; base `8c36d8e26c618032c1ff536004a582c07ec56a5b`.
- Target: `docs/planning/active/command-refactor/directives/CD-CMD-INGEST-001-product.md`, SHA256 `da911b7e6f052ab27b0e37ee939e52a0555ca177c047f84b475c9fc72b5414c1` (399 lines).
- Scope: conditional document readiness and selected-source feasibility (PD-01–16). This is not implementation conformance and not construction activation.

## Verdict

**CHANGES_REQUESTED**

There are two mandatory findings (F-01, F-02).

- **COVERAGE: 9.4 / 10**
- **OVERALL: 8.6 / 10**

Both scores are below the 9.5 threshold. I scored independently and inferred nothing about any other seat.

**Construction activation remains NOT APPROVED** regardless of this document verdict. Activation prerequisites A1–A5 and RD-01–07 remain open. Even a VERIFIED document result would not grant construction readiness, effects, acceptance or delivery.

## Opening / closing preserved boundary

Both runs used the supplied helper (`boundary`) and the qualified base Python `-I -S -B`. The logical index was measured before status.

| Check | Opening | Closing |
| --- | --- | --- |
| passed / errors | true / [] | true / [] |
| HEAD | fb587e7a…2cd2 | fb587e7a…2cd2 |
| branch | feature/cmd-ingest-001 | same |
| logical_index_before_status | 61ca9594…cf4e | 61ca9594…cf4e |
| status | ` M packages/friday-chat/config.example.yaml`, ` M packages/friday-chat/models-config.example.yaml`, `?? .friday-old/` | identical |
| staged | empty | empty |
| tracked files / symlinks / preserved / pins | 18715 / 26 / 8 / 37 | 18715 / 26 / 8 / 37 |

Preservation:

- The supplied `request.json`, `review_tools.py`, `boundary.json` and `current-controls.json` re-hashed identical at close.
- The controller scratch listing is unchanged.
- I opened neither dirty YAML payload, nor `.friday-old`, nor any personal store or cache. The helper hashed or stat-checked them only.
- No product, test, Git, install, network, model, provider, store or service effects occurred.

## Independence disclosure

While listing the supplied scratch, I printed the first 400 bytes of `delegates.json` in a combined `cat … | head -c 400` command before I recognised it as a delegate inventory. Those bytes contain only a seat name ("sol"), a "fulfilled" status and an opaque task/thread ID. They contain no review content, findings, scores or reasoning.

I read nothing further from that file, and nothing from it informed this review. This is harmless inventory exposure, not peer-review reasoning exposure, so I am not treating it as a BLOCKED condition.

I used no memory, history, peer reports, builder private reasoning or raw authority/navigation/log files. Current controls came only from the pinned `current-controls.json`.

## Inputs read

**Read in full:**

- Target directive (399 lines).
- REM-CMD-INGEST-001 (1,420 lines).
- Embedding compatibility contract (583 lines).
- Package Impact Assessment v0.6 and its approval record.
- Test-migration plan, command-architecture plan and guide handoff.
- Companion TOOLS-DOC directive and TOOLS-DOC proposal.
- Readiness decision, authority manifest, preparation authorization and preparation checks.
- Council criteria, authorization and roster.
- Behavior, end-to-end and large-document results.
- `current-controls.json`.

**Parsed:**

- E2E `facts.json` (structure and values).
- The decompressed baseline inventory, statically.
- Baseline summary and migration seed.

**Targeted source and metadata:**

- Existence of every REM path-table source path.
- Commands `__all__` and dependencies.
- Chat `registry.execute`, `_parse_command_input`, `_SHARED_ADMISSION_COMMANDS`, `files.py` placeholder and `--lines` helper.
- `adapters.py` 2,048-character slicer, and the template's `persist_directory` and `rejection_log` entries.
- `pyproject.toml` dependencies and extras for Tools, Chat, Memory, LLM, Core and Runtime.
- Cross-package import edges.
- Runtime `_friday_tools_catalog`.
- Memory 8,192-dimension ceiling, embedding role call sites, v1 strict recovery models, and BackupManager probing.
- The readiness harness limit constants.

## Fresh vs inspected facts

**Fresh, executed this session:**

- SHA256 of request, helper and supplied files.
- Opening and closing boundary.
- Seven admin checks.
- Static inventory verification against baseline blobs (AST only, nothing imported):
  - The `.gz` and JSON hashes match the summary.
  - All 237 module hashes match.
  - All 3,073 node names match an independent AST walk.
  - All 72 fixture hashes match.
  - All three seed entries resolve, with matching file and definition hashes.
- Base→candidate filename diff: planning files only; no product source changed.
- Source and metadata greps and AST parsing listed above.

**Inspected, not re-executed:**

- All measured Docling, Nomic and Chroma behavior and E2E claims, plus corpus facts. I compared their result documents and facts.json against the directive's claims; I re-ran no conversion, inference or tests.
- Preparation-checks receipts.
- Independent-review statuses of the measured slices.

## PD-01–16 matrix

| PD | Result | Requirement / source evidence |
| --- | --- | --- |
| PD-01 | PASS | Explicit request and pending state are correct:<br>• "proceed" is recorded as preparation only (directive L8–12; `preparation-authorization.json`).<br>• Policy precedence: L17–18.<br>• A4 requires Chuck's approval of the exact SHA.<br>• A5 bounds effects.<br>• The one-round budget comes from `council-round1/authorization.json`.<br>• §7 says there is no automatic loop.<br>Advisory A-06: header state is stale. |
| PD-02 | **FAIL** | **F-01.** The I1/I2 exit proofs (L69–70) require DI evidence that only I2/I3 deliverables can produce, so the slice sequence is a circular gate. Aggregate interaction is otherwise preserved (L60–65). |
| PD-03 | PASS | L78–85 match the REM ownership table. Commands has `dependencies = []` and `__all__` length 54. Tools declares no Memory dependency, and Memory pins LLM, so the FC-12 extra route is feasible. The existing edges match REM disclosures: smart_read/inspection/lifecycle/maintenance → Memory; `large_file_processor` → Tools `code_chunker`; Core `profiles` and `interfaces/transcript` → Memory. Advisory A-03: CLI is still conditional. |
| PD-04 | PASS | §3.1 matches REM B and the measured evidence: furniture export, `always_emit_headings`, notes/comments, read-only audit, complete-success admission, assets, and Office pipelines independent of PDF assets. RD-02 (hidden rows/columns) is honestly gated, with no false exclusion claim (L127–129). |
| PD-05 | PASS | §3.2 incorporates REM C exactly: raw tail after resolving the default handler, custom handlers and aliases, API54, exact options, lookalikes, `--` terminator, `/read` refusal, `--lines` refusal, and no `shlex`. Feasible: `registry.execute` holds the raw `user_input` before `_parse_command_input` splits it (registry.py L165–190, L1196–1201). |
| PD-06 | PASS | §3.3 matches REM D:<br>• `document`/512 defaults.<br>• Independent precedence: override → YAML → built-in.<br>• Final-input budget.<br>• Three strategies.<br>• No overlap knob.<br>• Plain CSV/TSV has no header.<br>• Source plan vs derived unsplit records.<br>• No second chunking.<br>• `smart_file` keys are not aliases. The slicer is confirmed at adapters.py L385. |
| PD-07 | PASS | §3.4 L205–218 cover:<br>• Pool/non-pool shapes and call interfaces.<br>• Optional fields from qualified readiness.<br>• Preparation exactly once.<br>• Local synchronous counter.<br>• Smallest limit wins.<br>• Index/cardinality/finite checks.<br>• No silent model change.<br>Replacement-model positives are gated in RD-01. Advisory A-02 covers the B02 hosted-default risk. |
| PD-08 | PASS | L220–228 and L243–252 cover:<br>• Explicit fresh creation; unset and default paths do not create stores.<br>• Template literal origin, which resolves PIA OPUS-R4-A05; the template literal is confirmed at L236 and the rejection log inside `vector/` at L71.<br>• FC-03 backup safety without a repair project.<br>• Non-colliding evidence names.<br>• Strict v1/v2 recovery and fingerprint timing.<br>Source confirms v1 is `Literal[1]` and BackupManager uses `[memory_dir, memory_dir/vector]` probing. |
| PD-09 | PASS (advisory) | "Apply all FC-01–14" (L230) plus explicit MCP/logging/task/graph/backup/recovery/multi-agent safeguards. DI-34 is in the proof groups, and RD-01 requires the full trace matrix. Advisory A-01: the annex's intentional-exception list is not consolidated. |
| PD-10 | PASS (advisory) | §3.5 covers:<br>• A worker with no provider or storage capability.<br>• Admission held until quiescence (the `ingest` command is already in `_SHARED_ADMISSION_COMMANDS`).<br>• Stale-success prevention.<br>• No OS-sandbox claim.<br>§3.3 covers the cache/destination binding. Advisory A-04: the worker owner is not named. |
| PD-11 | **PARTIAL → F-02** | Inventory: verified accurate (237/3,073/72, hashes, classification, default retain). Seed: hashes and nodes are correct, but the DI attributions are wrong. Summary: per-package rows sum to 226/3,012 and omit the 11 root modules (A-05). Final-phase exception rules (L297–304) are correct. |
| PD-12 | PASS | §6 covers:<br>• The canonical architecture document.<br>• The three registries.<br>• CLI placeholder modules.<br>• Exact guides from the handoff, the eight READMEs and the templates.<br>• The requirement → section → source → example matrix.<br>• Independent content review; structural checks are not acceptance.<br>This matches the architecture plan and guide handoff. |
| PD-13 | **PARTIAL → F-02** | Content is credible:<br>• Source and installed lanes, normal and `-O`.<br>• Registry → real Chroma → separate-process reopen.<br>• Zero-ingestion negatives.<br>• Minimal profiles.<br>• Certifi version and origin.<br>• Offline/live classification.<br>• Finance live exclusion with a witness.<br>• Protected state.<br>However, the §5 proof-group DI mapping is materially wrong. |
| PD-14 | PASS | The directive and readiness claims match the pinned evidence:<br>• Stack: Docling 2.150.0, Core 2.106.0, RapidOCR 3.10.0, Certifi 2026.10.23, dateutil 2.9.0.post0 (facts.json).<br>• Stored chunks: 41 + 40 per mode, 768 dims, loaded context 2048, server usage 0.<br>• Behavior matrix: 37 cases, 324-case matrix.<br>• Limits: identical to the harness constants (fixtures.py L796–1044, behavior.py L849/872).<br>RD-01–07 separate proven behavior from open facts, and component scores are not presented as the 9.5 gate. |
| PD-15 | PASS (with F-01 note) | §4:<br>• Intersects the REM path table with slice scope.<br>• Requires a machine-readable exact list in A2/A3.<br>• An unexpanded row grants nothing.<br>• No speculative edits outside the eight owners.<br>• Protected state is preserved.<br>§7 has the stop controls. Advisory A-07: the "other nine" arithmetic is wrong. The A1 RD wording ambiguity is covered in the F-01 correction. |
| PD-16 | PASS | INGEST and TOOLS-DOC are separate:<br>• INGEST L73–76.<br>• Companion activation, its "changed contract bytes require a new INGEST aggregate review", and its separate completion claim.<br>Human acceptance, rollout, model selection and delivery are separately authorized (L398–399). Qwen is not the default (L55–56). There is a disposable UAT checklist (L397). |

## Mandatory findings

### F-01 — Slice exit gates depend on later-slice deliverables (circular activation trap) — MANDATORY, medium-high

**Requirement.** Criteria PD-02 requires feasible, bounded I1/I2/I3 sequencing "without a circular activation trap". The criteria also say "A gate must not hide a contradiction, circular dependency or missing required behavior". REM F (L1217–1220) requires three bounded slices, and the directive (L60–62) requires each slice to be frozen and verified "before integrating its dependants".

**Source evidence.** Directive L67–71 lists "Required proof before the next slice":

- **I1** (owners: Core, LLM, Memory contracts) must prove DI-17/18/21–24/27–29/32/33. Per REM L1280–1316, several of those cannot be produced inside I1:
  - **DI-23** requires a "Public headless Memory factory → Core entry → smart_read text small/large/force_chunked and warm caches … stored raw texts equal common plan chunks exactly". The directive assigns "Memory shared plan and entry" and "existing smart_read **text** storage/cache handoffs" to **I3** (L71).
  - **DI-17** requires real token counts over headings, repeated table headers, sheets and slides, with "no … second chunking pass". Chunking strategies are I3 deliverables.
  - **DI-32** requires "Actual Chat bound Memory-v2 snapshot → aggregate-v2 writer/read/participant reparse → same-namespace restore". The Chat `reorganization/contracts.py`, `artifacts.py` and `coordinator.py` changes are consumer integration (I2 owners include Chat; I1 does not). I1's own text says "strict v1/v2 handoff", which is the Chat handoff.
  - **DI-28** requires "Maintained Chat aggregate snapshot/rollback … execute" (I2).
  - **DI-29** requires "Actual Chat/Runtime pool/non-pool startup" (I2).
  - **DI-33** requires "extraction → graph and insight/summary storage → recall, compaction/lifecycle, maintenance synthesis/re-embedding" through consumers (I2).
- **I2** must prove DI-35, the test-migration acceptance across the whole changed suite. That needs I3's document test rewrites (for example TM-01/TM-02, which the seed labels "INGEST/I3").

**Risk.** As written, I1 cannot exit without I2/I3 code. I2 and I3 cannot start until I1 is verified. A builder must either:

- deadlock;
- ignore the gate; or
- silently reinterpret "DI-xx" as "the contract-level portion of DI-xx".

The directive never defines that reinterpretation, which is exactly the hidden-gate defect PD-02 prohibits.

A related ambiguity sits in A1 (L47). A1 makes completing RD-01–07 a pre-generation gate. RD-01's "require actual baseline and replacement-model positive operations plus refusals" across the FC-01–14 matrix, and RD-07's "Complete the architecture/guide evidence matrix", can be read as needing new guard refusals and DI-36 verified-example evidence. Neither can exist before construction, while §6 L361 permits the architecture document only once the candidate exists.

**Bounded correction** (document-only):

1. Replace the I1/I2 "Required proof" cells with slice-scoped obligations. One approach is a per-slice DI/FC table in the A2/A3 appendix form, stating for each DI which slice proves which portion. For example:
   - I1 proves the DI-17/24 counter and limit contract on supplied text.
   - I1 proves DI-23 at the Core-entry/Memory-factory contract level with deterministic doubles.
   - I1 proves the DI-27/32 Memory-v2 model and loader only.
   - I2 proves the DI-28/29/32/33 consumer and Chat portions.
   - I3 and the aggregate prove every DI in full.
   Alternatively, move each DI to the slice that delivers it.
2. State that full DI-01–36 closure is an aggregate (post-I3) gate. Make DI-35 per-phase map acceptance at I1/I2 and whole-suite acceptance at the aggregate.
3. In A1, or by a reference to the readiness decision, state that RD-01/RD-07 close on pre-construction qualification and planning facts:
   - deployment identity, counter and capacity qualification;
   - baseline-code positives on fresh stores;
   - the planned trace and documentation matrix.
   The new-guard B/N/R witnesses and DI-36 verified examples are construction-phase obligations.

**Proof.** A fresh review can confirm the fix by checking that every DI/FC listed as a slice exit proof is producible from that slice's owner deliverables plus earlier slices. The REM DI text (L1280–1319), the I1–I3 owner/deliverable cells and the REM path table give the mechanical join. The review should also confirm that A1/RD wording no longer requires post-construction evidence before generation.

**Docs impact.** Directive §2 table (L67–71) and A1 row (L47). Possibly the readiness decision RD-01/RD-07 wording. No parent change is needed.

### F-02 — Requirement-to-evidence traceability errors in §5 and the migration seed — MANDATORY, medium-low

**Requirement.**

- PD-11: the seed must be "accurate".
- PD-13: tests and evidence must be credible.
- A4 asks Chuck to approve this exact SHA as the binding construction directive (AGENTS.md: the directive binds "exact scope … tests, verification").
- REM DI-01–36 define each DI's content (REM L1282–1319).
- REM DI-12 requires post-freeze, separately authorized fresh Sol/Astra/Opus review before human UAT.

**Source evidence.**

1. **Directive §5 proof-group table (L306–313) attaches DI IDs to the wrong evidence descriptions.** The union is complete (DI-01–36), but:
   - "Parsing/configuration — raw-tail quotes/description/options, independently resolved defaults, custom handlers, API54" lists **DI-03** (scanned-PDF OCR), **DI-04** (corrupt/encrypted/partial conversion), **DI-10** (regression/lint/lock/Certifi gates) and **DI-13** (XLSX structure).
   - The actual parsing DIs **DI-05** (quoting/options) and **DI-06** (document `--lines` refusal) are placed under "Extraction/chunking".
   - **DI-12** (three-seat independent review + human UAT) and **DI-30** (destination-bound storage receipts) also sit under "Extraction/chunking — genuine native/OCR documents …".
   - DI-18 appears in two groups.
2. **The directive does not say how DI-12 is satisfied.** §7 (L384–387) says "a council is a separate maintainer-requested workflow" and "Any later council uses the then-authorized roster". Read with the misplaced DI-12, this can be taken as making REM DI-12's required post-freeze three-seat review optional. That would relax a parent verification requirement rather than merely gate its authorization.
3. **The seed (`test-migration-seed.json`) misattributes requirements.**
   - TM-01 (`test_read_dispatches_supported_extensions`; four-format genuine `/read` extraction and the corrupt-document refusal) lists DI-01/02/**08**/35. DI-08 is headless imports and the installed profile. The entry omits DI-13/DI-14 (XLSX/PPTX) and DI-04 (corrupt refusal), all of which its own required assertions exercise.
   - TM-02 (`test_ingest_records_source_metadata_and_list_ingested`) lists DI-**06**/**08**/35. DI-06 is document `--lines` refusal and is unrelated. The governing requirement is **DI-07** ("absent/explicit descriptions … `/list-ingested` alone is not proof"), which is missing.

**Risk.** A builder or validator binding witnesses by proof group or by seed could:

- attach parsing evidence to XLSX/OCR/corrupt-input DIs;
- treat DI-12 as satisfied by extraction tests, or as optional;
- carry incorrect DI tags into the A3 case-level map, which by REM G1 becomes the named fixture/oracle exception.

This undermines DI-35's traceability and the approval of exact bytes.

**Bounded correction** (document-only):

- Re-key §5 to the REM DI definitions. For example:
  - Parsing/config: DI-05/06/16 (+18 config).
  - Extraction: DI-01–04/07/09/11/13–15/17/25/26/31.
  - Embeddings/namespaces/recovery: DI-18/20–24/27–30/32/33.
  - Integration: DI-34.
  - Migration: DI-35.
  - Docs: DI-36.
  - Release/review: DI-08/10/12.
- State explicitly that DI-12's three-seat post-freeze review remains a required verification, subject to its separate authorization, or record an explicit maintainer amendment.
- Correct the TM-01/TM-02 requirement lists. The seed is proposed and not approved, so this is a planning-file edit only.

**Proof.** A mechanical cross-check of each proof-group DI against the REM DI table text, and of each seed's `required_assertions` against its `requirements`.

**Docs impact.** Directive §5 table and §7 sentence; `test-migration-seed.json` entries TM-01 and TM-02. No parent change is needed.

## Advisories (non-mandatory)

- **A-01 — compatibility-exception list (PD-09).** The annex says the six intentional compatibility exceptions "must be individually visible in the final directive" with an operator remedy (annex L41–51):
  - fresh-store admission;
  - preparation/role correction, including Nomic prefixes on the unchanged model;
  - invalid/overflow/result refusal;
  - MCP existing-reason mapping;
  - FC-03 backup identity admission;
  - ephemeral isolation.
  They appear piecemeal across §3.4 but not as a labelled list. Ingest/role correction (ChromaVectorStore query via `embed_documents`, synthesizer `embed_query`) in particular is not stated as an intentional exception. Add a short enumerated list.
- **A-02 — B02 hosted-default risk (PD-07).** The annex (L114–118) requires the risk that the B02 hosted `text-embedding-3-small` default fails immutable-identity qualification to be "report[ed] … before Gate A and check[ed] first". Neither the directive nor RD-01 names it. Surface it as an RD-01 ordering item.
- **A-03 — CLI conditionality (PD-03/15).** The PIA lists "Resolve P-08's conditional edits" as a detail to settle. The directive names CLI as one of eight implementation owners without saying the edits are conditional. A2's exact file list should record CLI as source-unchanged or as a named edit.
- **A-04 — worker owner (PD-10).** §3.5 does not name the worker owner. The PIA says "Tools/LLM capability, Chat request ownership", and headless callers also need off-loop conversion. Freeze the worker owner and the headless contract in A2.
- **A-05 — inventory summary (PD-11).** Per-package rows sum to 226 modules / 3,012 nodes against stated totals of 237 / 3,073. The 11 `tests/integration` modules (61 nodes) appear only in the totals. The inventory also silently excludes `tests/lab` (3), `tests/unit/security` (6) and `tests/readiness/ingest/tests` (14). State that scope and add a root-integration row.
- **A-06 — stale state statements (PD-01/16).** The header "validation state: pending" and "for his review before any council is invoked" (L6, L11–12) are stale against current controls (`in_review`; council authorized). Update them on the next revision; no correction is possible this round.
- **A-07 — package count (PD-15).** "Agent and the other nine indirect package rows" (L275) should read "eight". P-09–P-17 are nine packages including Agent, as the list on L276–277 confirms.
- **A-08 — assessment change control.** The PIA's change-control step 2 says "Refine this assessment with its measured … findings" and "Keep one authoritative copy". The directive instead preserves v0.6 and uses a "separately bound addendum" (L28–29), with measured differences carried in the readiness decision. The substance holds: no reuse of old approval, and fresh satisfaction is required. Make the choice explicit, and say whether the measured differences (Certifi patch, dateutil, RD-02, template origin) are material.

## Scores

**Overall rubric** (criteria-specified weights):

| Area | Max | Score | Deductions |
| --- | --- | --- | --- |
| Scope / authority | 1.5 | 1.4 | Stale header (A-06), "nine" arithmetic (A-07), addendum vs refined-assessment form (A-08). |
| Shared architecture / feasibility | 2.0 | 1.5 | F-01 circular slice gates (−0.4); unnamed worker owner (A-04, −0.05); CLI conditionality (A-03, −0.05). |
| Extraction / chunking | 2.0 | 1.9 | Faithful to measured evidence. RD-02 is honestly gated, but whole-workbook refusal leaves a parent contract open (−0.1). |
| Compatibility / data / effects | 3.0 | 2.75 | Exception list not consolidated (A-01, −0.15); B02 risk not surfaced (A-02, −0.1). |
| Tests / documentation / evidence | 1.5 | 1.05 | F-02 DI mapping, DI-12 treatment and seed attribution (−0.35); summary/scope disclosure (A-05, −0.1). |

**OVERALL = 8.6.** That is 1.4 + 1.5 + 1.9 + 2.75 + 1.05 = 8.60. Not rounded up.

**COVERAGE = 9.4.** All 16 criteria were assessed against full governing text, the static inventory and targeted source. Deductions:

- Compressed raw evidence archives (behavior/E2E/corpus tarballs) not opened; claims were checked against result documents and facts only (−0.2).
- Unpinned referenced records not read: `ingest-existing-store-policy.md`, branch-handoff and assessment.md (−0.2).
- Source feasibility checked at existence and anchor level for the ~60 allowlisted paths, not a full per-row audit (−0.2).

The gate requires VERIFIED, no mandatory findings and both scores ≥ 9.5. This seat does not meet it.

## Commands ledger (exact, with exits)

All commands ran from the repository or my scratch. Git commands ran with `GIT_OPTIONAL_LOCKS=0`; Python ran as `<qualified python> -I -S -B` (`PYTHONDONTWRITEBYTECODE` set by the helper for its own children).

| # | Command | Exit | Fresh / inspected |
| --- | --- | --- | --- |
| 1 | `shasum -a 256 request.json` (before reading) | 0 | fresh: hash matched |
| 2 | `shasum -a 256` of helper and supplied files; `cat request.json`; `cat review_tools.py` | 0 | fresh |
| 3 | `python3.13 -I -S -B review_tools.py boundary --request … --scratch <S> --label opening` | 0 | fresh: passed |
| 4 | `cat current-controls.json`; `head -c 400 delegates.json` (see disclosure); `cat` criteria/authorization/roster | 0 | inspected |
| 5 | Read target, REM, annex, PIA, approval, test plan, architecture, guide, companion, proposal, readiness, manifest, prep authorization/checks, measured results | 0 | inspected |
| 6 | `python3.13 -I -S -B -c <facts.json walker>` | 0 | fresh parse |
| 7 | `grep` of harness limit constants in `tests/readiness/ingest/{fixtures,behavior,e2e,manifests}.py` | 0 | fresh |
| 8 | `git diff --name-only 8c36d8e2 fb587e7a`; `git log --oneline` | 0 | fresh: planning-only diff |
| 9 | `python3.13 -I -S -B scripts/inv_check.py <repo> <base>` | 0 | fresh |
| 10 | `python3.13 -I -S -B scripts/inv_verify.py <repo> <base>` (git show blobs; AST; no imports) | 0 | fresh: 0 mismatches |
| 11 | `git ls-tree -r --name-only <base> tests/` + `grep testpaths pyproject.toml` | 2 | fresh: listing succeeded; exit 2 came only from `grep` on the absent `pytest.ini`/`setup.cfg` |
| 12 | Path-existence loop over REM path-table sources | 0 | fresh |
| 13 | Commands `__all__` AST, dependencies; Chat registry/files/adapters/template greps | 0 | fresh |
| 14 | `pyproject.toml` dependencies/extras; Tools extras grep; import-edge greps; Runtime/Memory/LLM anchors | 0 (one zsh `--include` glob warning; other output valid) | fresh |
| 15 | Inventory classification/summary sums | 0 | fresh |
| 16 | `python3.13 -I -S -B review_tools.py admin --request … --scratch <S>` | 0 | fresh |
| 16a | board validate | 0 | "Development board validation passed: 36 tasks" |
| 16b | dashboard `render --check` | 0 | "Planning dashboard is current" |
| 16c | documentation lifecycle | 0 | "1130 Markdown files checked" |
| 16d | package metadata | 0 | "Validated 18 pyproject.toml files … OK" |
| 16e | range whitespace `git diff --check base..candidate -- docs/planning` | 0 | clean |
| 16f | owned whitespace `git diff --check -- docs/planning` | 0 | clean |
| 16g | staged whitespace `git diff --cached --check` | 0 | clean |
| 17 | `review_tools.py boundary … --label closing`; re-hash supplied files | 0 | fresh: passed, identical |

`<S>` = `/private/tmp/claude-501/-Users-chuckrussell-Dev-gendev-agent-framework/f268fd3b-04ac-41ff-87b7-f500dc85ba1b/scratchpad/opus-council-r1` (fresh, physical, reviewer-owned, outside the repo and the supplied scratch). Helper caches and tmp dirs were set inside `<S>`.

Not run, per request: full `git diff --check` (known protected-YAML debt), root Ruff/collection, product tests, installs, network, models, providers and stores.

## Limits

- This is a document-readiness and source-feasibility review only. I made no implementation-conformance claim.
- Measured behavior and E2E claims were inspected, not reproduced.
- Seed and inventory checks are static. Node names are compared by AST, and definition hashes are trusted from the inventory except where they match the seed.
- Known baseline debt stays failed and unwaived:
  - root Ruff;
  - the `test_display` collection collision;
  - registry formatting;
  - protected `models-config.example.yaml` whitespace.
- One round only. No remediation, reissue or source/document edits were made.

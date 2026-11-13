# INGEST activation council — global round 7/9 (extension 2, pass 1/3) — Opus seat

- Seat: opus (claude-opus-5-5, high effort). Fresh, read-only, single seat. No nested agents.
- Candidate: `9ddaf6f87f12486ee0bea82dc1561046f2353d5a` on `feature/cmd-ingest-001`.
- Request SHA256 was checked before the request was read, and it matched: `ada377dd…72af`.
- **Verdict: VERIFIED**
- **assessment_complete: true; areas_assessed: 8/8**
- **Overall: 9.52 / 10.** This is the weighted sum 9.525, cut down to two decimals rather than rounded.
- **Mandatory findings: 0**

## Boundary and input checks

- **Entry check (before reading anything substantive):**
  - Logical index was the SHA256 of `git ls-files -s -z`, taken before `git status`: `fa0be09a…0b9b`. It matched.
  - HEAD, branch, porcelain status and empty staging all matched.
  - Run with `GIT_OPTIONAL_LOCKS=0` and bytecode off (`-I -B`).
- **Exit check:** identical results. All eight preserved records matched on mode, size, mtime, ctime and birthtime, plus SHA256 where one is declared. For `.friday`, `.friday-old`, `.venv` and `exports` only metadata and hashes were checked; their contents were not read.
- **Pins:** all 27 pins matched. That covers 16 required inputs, 10 optional references and the controller checks file. `current-controls.json` matched `65f07b3c…`.
- **Not done:** no product imports, tests, builds, installs, network, model, provider or store calls. Finance `test_integration_massive.py` was not opened. No user YAML or credentials were read. Nothing was written to the checkout or to the input directories.
- **Executed:** stdlib git and hash checks only, plus a stdlib recheck of `digest-vectors.json`. All 5 canonical vectors and the raw-content vector reproduce their stated canonical bytes and SHA256. The receipt's `plan_sha256` equals the plan vector's hash.
- **Read in full:** extension2, review instructions, authorization, round7 correction requirements, README, shared-contracts (all 855 lines), readiness, validation plan, approval binding, the three decision records and the requirement reconciliation.
- **Focused views:** the file map (all 91 rows; owners and exits for the key lifecycle rows) and the case map (all 51 planned witnesses; helpers, modules, exclusions).
- **Targeted reads:** source for `DIContainer.shutdown`, `FrameworkAsyncClientLifecycle`, the Chat embedding builder, the `SmartFileReadTool`/`LargeFileProcessor` constructors and Chat `_instantiate_tool`. Directive §3.3 and the REM rows that cover smart_read.
- **Not used:** controller-check content (it is identity metadata only), previous reports, memory.

## H1–H3 neutral corrections

**H1 (counter-factory composition and same-entry late attach): satisfied.**
- The signature `create_ingestion_entry(..., counter_factory: CounterFactory, ...)` is required with no default (shared-contracts §2). Missing or `None` is refused at construction.
- The "Counter-factory construction" subsection binds counter, embedder and factory to **one** `ResolvedEmbeddingCapabilities`. It also states that this needs no document settings or Docling.
- `test_same_entry_ingests_text_then_document_after_late_attach` (I3-C4) demands, through the identical entry, in this order:
  - text ingest with the document binding absent;
  - publishing the binding, then resolving and attaching the converter;
  - a genuine PDF/Office ingest with stored-chunk readback;
  - entry-then-converter drain.
- The installed-probe helper row makes that same transition mandatory in normal and `-O` lanes, with require-style checks. It states explicitly that separate positives do not satisfy it.
- Runtime `test_di.py` and Chat `test_lifecycle_drains_entry_with_optional_late_converter` repeat the one-lifecycle transition and exclude ownership-only spies.

**H2 (source/session, reuse, snapshot, slot): satisfied.**
- **Converted-kind invariant:** `source_kind ∈ {pdf,docx,xlsx,pptx}` if and only if `conversion_profile_sha256` is non-null.
- **Session match:** the session's source must equal the submitted source on every immutable field. A text source with a session, or a closed or already-planned session, is refused before plan, embed or store. Witness: `test_converted_source_requires_exact_matching_session` at I3-C2, including parent and child wrong-space negatives.
- **Get-or-create and loser cleanup:** the loser closes its unowned entry and leaves shared clients open. It reuses the winner only when destination and space match and the holder is not closing. A mapped Chat witness covers simultaneous creation.
- **C3 vs C4 split:** C3 builds minimal holder, get-or-create and normal close; C4 proves races, cancellation and drain. The file map and validation plan agree on this.
- **Worker slot:** held until `session.aclose` has finished an OS-confirmed reap and cleanup. Being `planned` alone does not free it. The C4 headless witness checks the release point.
- **Environment snapshot:** one is taken at each request entry. Embedding capabilities stay fixed for the runtime build, so late document configuration cannot redirect the counter or embedder.

**H3 (scope and authority): satisfied.**
- extension2 overrides only the round caps, for global rounds 7–9.
- `approval-binding.json` keeps gates A1–A5 incomplete, `product_generation_allowed: false`, and `construction_approved`/`effects_approved` false.

## A1–A8 matrix

The weights total 10.00, so the overall score is the sum of the contributions.

| ID | Wt | Score | Contribution | Evidence |
|---|---:|---:|---:|---|
| A1 | 1.50 | 9.6 | 1.440 | The three maintainer decisions are applied directly: parity campaign removed, XLSX workbooks rejected, shared worker. Readiness separates reused evidence from implementation acceptance. Gate A1–A5 is kept distinct from Review A1–A8. Worker proof is set at I3-C4, not before coding. The only issue is one stale caption (Advisory 1). |
| A2 | 1.75 | 9.4 | 1.645 | Exact frozen values and invariants. The protocols have one coherent direction: caller opens the session, entry calls `session.plan(counter_factory=…)`, then validates the whole plan and batch before `write_prepared`. Strict manifest discovery with the record hash retained in the factory. Canonical JSON and vectors are verified. Gaps are listed in Advisories 2–4. |
| A3 | 1.75 | 9.6 | 1.680 | Concrete subprocess and IPC design: `exec -I -B -m`, framed protocol, fd-1 redirection, trusted factory frame only after a valid `plan`. One active and one queued session; slot release at reap. Monotonic deadlines, TERM/KILL/reap, psutil RSS. Close order is the same in DI and Chat. The `DIContainer.shutdown` and frozen `FrameworkAsyncClientLifecycle` seams match the source. Advisory 5 covers `-O` propagation. |
| A4 | 1.50 | 9.5 | 1.425 | Additive keyword-only parameters only; I1 leaves legacy paths unchanged; I2 switches callers in a coordinated step and makes defaults positive through configured records. Fresh-store, marker, v1/v2 and the configured-identity limits are stated honestly. Advisory 6 covers Chat's retained capabilities. |
| A5 | 1.25 | 9.4 | 1.175 | Exact files with exit-level purposes; 49 mapped cases plus 51 witnesses. Helper and installed-probe classification. Explicit selectors outside root discovery, and the Finance exclusion. Gaps are in Advisories 2 and 7. |
| A6 | 0.75 | 9.6 | 0.720 | Error code set, workbook refusal before conversion through a cooperative bounded preflight, coverage and no-drop rules, refusal on context overflow, receipt only after confirmed readback, truthful partial results, cache bound to the destination. |
| A7 | 0.75 | 9.6 | 0.720 | Ownership split: Tools, Memory, Core, LLM, and composition roots. Dependencies are declared before use (I1-C2, I3-C1, I3-C3) and verified installed at C5. Headless text profile does not need the document stack. TOOLS-DOC routing stays separate. |
| A8 | 0.75 | 9.6 | 0.720 | I1, I2 and I3-C1…C5 build on each other without circular dependencies. Approval and A5 are bound per phase. AG review comes before human UAT. Advisory 8 covers retries. |
| **Total** | 10.00 | | **9.525** | Reported as 9.52, cut down rather than rounded. |

## Mandatory findings

None. Every gap below fails closed through stated guards, or is already pinned by parent requirements that the package says still control. None would lead a builder into unsafe or contradictory behavior.

## Advisories (optional)

1. **Stale extension caption.** `requirement-reconciliation.md` still says "the current extension controls global rounds 4–6". A later paragraph in the same file corrects this to rounds 7–9. Replace the stale sentence.

2. **smart_read injection point is unnamed.** The I3-C2 witness requires an injected entry built with a same-capabilities factory, routed through smart_read into a Core entry. REM line 141 requires storage without an entry to fail, and REM line 1231 requires the entry to be injected.
   - Shared-contracts does not give the exact keyword argument or where it goes: `SmartFileReadTool`, `LargeFileProcessor` or the `MemoryController` handoff.
   - It also does not state the no-entry refusal code.
   - Fix: pin something like `ingestion_entry: IngestionEntry | None = None` on the chosen classes, plus `readiness` refusal when storage is requested without an entry.

3. **Text `SourceDocument` construction has no named owner.** For text, web and tool sources, nothing says who sets `source_id`, `units` and `blocks`. Nothing says whether `blocks=()` is allowed and the Memory non-Docling planner segments the content.
   - Fix: name one Memory or Core helper for this, to avoid per-caller drift.

4. **No construction-time factory check.** A factory from the wrong capability record is only caught when the child creates its counter or when the parent validates the plan. Both happen before any effects, so this is safe but late.
   - Fix: have the entry factory call `counter_factory.create()` once at construction and compare its space with the counter's. The read is cheap and local.

5. **Worker optimization flag unstated.** The worker launch command (`sys.executable -I -B`) does not pass the `-O` flag. In the installed `-O` lane the child therefore runs unoptimized. That is stricter, not weaker, but the document should say whether this is intended.

6. **Chat's retained capabilities have no named location.** Say where Chat keeps the runtime-build `ResolvedEmbeddingCapabilities` for lazy entry creation (a runtime field or the embedding wrapper). Otherwise a builder might resolve them again from a fresh environment.

7. **Missing negative witness and probe wording.**
   - Add an explicit witness that a missing or `None` `counter_factory` is refused at construction, including under `-O`.
   - Align the validation-plan wording "probe must execute `test_same_entry…`" with the helper row, which describes require-style checks in a script rather than a pytest node whose plain `assert`s would be stripped under `-O`.

8. **Retry after a consumed session is undefined.** For documents, a plan call on an already-planned session is refused. Define what an explicit retry after an embedding or storage failure means: a new session, while keeping the attempt's IDs.

## Limits

- This is a design and document assessment only.
- No future code, tests, assets, installs or worker thresholds were run or confirmed.
- Source reads were targeted interface checks, not a code audit.
- Controller structural checks were not semantically relied on.
- This verdict grants no construction, effects, acceptance, push or delivery authority.
- This seat is finished; no later pass follows.

# INGEST activation council — global round 6/6 (additional pass 3/3), Opus seat

- Seat: claude-opus-5-5, fresh read-only, high effort. Final authorized seat; stops after this report.
- Candidate: `7cf8956012a9c66d15f959436c6e129cde8a86c5` on `feature/cmd-ingest-001`.
- Target: `.../activation/README.md` (sha256 `da16c57b…0ede5`).

## Result

| Field | Value |
| --- | --- |
| verdict | **CHANGES_REQUESTED** |
| assessment_complete | true |
| areas_assessed | 8/8 |
| overall | **9.4 / 10** (weighted sum 9.415, truncated; not rounded up) |
| mandatory findings | 1 (M1) |
| gate (>=9.5, zero mandatory) | not met |

## Identity and boundary evidence

- request.json SHA256 computed with Python stdlib **before reading**: `19c218ef08b8dd4d0bb409e9ab24348218441cc42293c86741871385c11c4dfd` (matches; re-verified at exit). current-controls.json matched `f24d6cf4…a6f1e`.
- Entry and exit: logical index (`git ls-files -s -z` SHA256) computed **before** status = `57a7b11e…89401`; HEAD, branch, porcelain status and empty staging all equal the declared values. GIT_OPTIONAL_LOCKS=0, `python -I -B`, PYTHONDONTWRITEBYTECODE=1.
- All eight preserved records matched declared mode/size/mtime/ctime/birthtime (and sha256 where declared). Only metadata and hashes were taken. Nothing was read from user YAML, `.friday*`, `exports` or `.venv`.
- All 16 required inputs, 10 optional references and controller-checks matched their declared SHA256. The target blob is present in the candidate tree. Controller checks were treated as identity metadata only and were not read as semantic evidence.
- Extension-authorization was read first. It overrides only the original three-round cap.

## What was inspected and what was executed

Inspected in full:
- README;
- shared-contracts (all five sections);
- requirement-reconciliation and readiness-disposition;
- validation-plan and approval-binding;
- the three decision records;
- review-instructions, authorization, extension-authorization and the round-6 correction requirements.

Inspected through focused views:
- slice-file-map: every row's owner, mode and exits, plus the full purposes for the seam files (DI, Chat adapters/runtime/files/registry, Tools/Memory ingestion, pyprojects, uv.lock);
- test-case-map: structure, TM-A049, lifecycle/settings/session witnesses, modules, helpers and exclusions;
- digest-vectors: re-canonicalized all five vectors. Canonical bytes, hex and SHA256 are self-consistent.

Targeted source reads (read-only, no imports):
- Chat `FrameworkAsyncClientLifecycle` is `@dataclass(frozen=True)` with no-arg construction, and the app closes it through `runtime.async_clients.close()`.
- `DIContainer.shutdown` only stops MCP today. `RuntimeKernel` calls `_di.shutdown()`.
- `SmartFileReader` is in Chat `commands/files.py`.
- Tools already declares `psutil>=7.2.1`. Chat already depends on friday-tools, and Memory on tiktoken.

These seams match the design's assumptions.

Executed: hash and metadata checks plus pure JSON canonicalization only. There were no product imports, tests, builds, installs, network, model, provider or store operations, and no harness replay. Finance `test_integration_massive.py` was not opened. No prior or peer reports, memory or history were used.

## Neutral corrections G1–G3

**G1 — partially met.** The following are well specified:
- Optional `document_converter` on both Runtime and Chat `bind_ingestion`.
- Entry-only ownership with no settings lookup.
- `bind_document_converter` for read-only/late attachment.
- Identical-object idempotence, and atomic refusal of different or closing binds that never relinquish prior ownership. A clear five-row state table is common to both owners.
- Shutdown order entry → converter → MCP/LLM, with or without a converter.
- Memory requiring a matching session for converted sources, with no Memory→Tools import.

The gap is a cross-object interaction (M1): the entry's own document-planning dependency is optional and immutable once bound.

**G2 — met for its listed items.**
- `test_text_ingestion_needs_no_document_binding` (C3) and TM-A049's fixture-only adaptation ("no converter/settings fixture") give text /ingest a positive that does not depend on document fixtures.
- Chat and Runtime C4 matrices cover entry-only, late-attach, mismatch and drain.
- Dependencies are declared before use: Tools pyproject + lock at I3-C1, Chat edge + lock at I3-C3, LLM/Memory counter at I1-C2, with each phase interpreter bound by its own Gate A5.
- Asset errors are distinct: present-with-wrong-size and wrong hash are `identity`; absent is `missing_asset`.
- The snapshot is copied in 64 KiB yielding steps, with cancellation cleanup inside the heartbeat window.
- `.pptx` is added to the reader extensions.
- The cap wording is current.

**G3** — the full A1–A8 review below.

## A1–A8 matrix

| ID | Weight | Score | Contribution | Evidence summary |
| --- | ---: | ---: | ---: | --- |
| A1 | 1.50 | 9.6 | 1.440 | The three maintainer decisions are applied exactly: parity campaign removed, with no later replacement; XLSX whole-workbook refusal; shared worker. approval-binding is honestly `not_approved`, with all Gate A1–A5 incomplete and `product_generation_allowed:false`. The stale "no new council follows" clause is explicitly reconciled. Gate A vs Review A labels are disambiguated. |
| A2 | 1.75 | 9.2 | 1.610 | Values and protocols are precise (frozen/slotted, strict ints, sorted metadata, canonical JSON, verified digest vectors). Settings and embedding resolvers are independent with exact precedence. Plan/receipt identity is specified. Deducted for M1 (an optional injected dependency whose absence silently disables late document ingestion) and for the underdetermined "converted source / matching session" predicate (ADV-1). |
| A3 | 1.75 | 9.4 | 1.645 | Tools-owned process. Exact `create_subprocess_exec` argv, fd-1 redirection, framed IPC state table, one active plus one queued with a third request busy, TERM→KILL→reap, `worker_not_quiescent`, the psutil RSS sampler, and the shielded repeated-cancel close. The headless DI/Chat/runtime=None owners are coherent and match the actual frozen-lifecycle and DI seams. Deducted because late-attach is specified only as ownership, not as a functional document capability (M1). The slot release point after `planned` is unstated (ADV-4). |
| A4 | 1.50 | 9.5 | 1.425 | Additive keyword-only `capabilities` and `open_request`; old call shapes are retained; I1 legacy is unchanged and I2 makes a coordinated switch. Strict exact-route manifest without fallback. Fresh namespace marker and fsync protocol. Strict v1/v2 recovery combinations. Configured identity limits (alias swap) are disclosed honestly. |
| A5 | 1.25 | 9.2 | 1.150 | Exact per-path owners, exits and purposes. 49 mapped cases with frozen old identities and a retain default. 49 planned witnesses. Modules are classified and exclusions explicit, and the installed normal/-O probe is specified. Deducted for two gaps: no positive witness for text-then-document with the same bound entry (M1), and no named negative control for a converted source without, or with a mismatched, session (ADV-1). The bind_ingestion purposes for Chat adapters.py sit at C4 while the C3 witness already needs entry-only ownership (ADV-3). |
| A6 | 0.75 | 9.6 | 0.720 | Exact input envelope; bounded XLSX preflight with no DTD expansion; stable `unsupported_workbook_visibility` with no partial success. No silent clamp or dropped tail. Whole-batch validation happens before the first write. PreparedWriteResult confirms only after readback; a receipt is issued only on complete stored success. Cache and destination binding are covered. |
| A7 | 0.75 | 9.5 | 0.7125 | Ownership is clear (Tools converter/worker, Memory policy, Core protocols, LLM counter/broker). No Tools→LLM import: the factory is injected. Optional/default/headless extras are staged and verified at C5. The TOOLS-DOC boundary is held (TM-03 and routing stay separate). |
| A8 | 0.75 | 9.5 | 0.7125 | I1 foundations → I2 coordinated switch → I3 C1–C5 sequencing is buildable. Worker proof is at C4, not a pre-coding gate. Per-slice approval and independent validation are required. Gate A4/A5 owners and artifacts are named, and the final aggregate review precedes UAT. Intermediate compatibility is preserved. |
| **Total** | 10.00 | — | **9.415** | Overall reported as **9.4**. |

## Mandatory finding

### M1 — Late converter attachment does not guarantee that the already-bound entry can plan converted documents

**Evidence**
- In shared-contracts §2, `create_ingestion_entry(..., counter_factory: CounterFactory | None = None)` notes that "converted-document planning requires the supplied pure counter factory", and `OwnedDocumentSession.plan` requires it.
- shared-contracts §4 (ownership table and Chat lifecycle text) says that binding a different entry while one is bound is a readiness error, and that entry-only binding needs "no settings… merely to bind an entry".
- README (closing paragraph) and requirement-reconciliation say a converter "may be attached later for document requests".
- Nothing requires composition roots (Chat `runtime.py`/`adapters.py` at I3-C3, Runtime/headless recipe) to construct every entry with `counter_factory` from the same `ResolvedEmbeddingCapabilities`. That factory is independent of document settings.
- Only lifecycle/ownership is asserted by `test_lifecycle_drains_entry_with_optional_late_converter` and the `test_di` matrix. The installed probe keeps text and document positives in **separate** lifecycles.

**Failure scenario**
1. A user runs `/ingest notes.md`. The adapter binds E, built without `counter_factory`, which is plausible given the "no document dependency for text" guidance.
2. The user runs `/ingest report.pdf`. Converter C attaches successfully, but `E.ingest(..., document_session=S)` refuses with a readiness error.
3. E cannot be replaced, so document ingestion is unavailable for the rest of the process. No witness detects this.

**Violated requirements:** G1 (valid late-attach semantics), A2 (injected dependencies), A5 (positive acceptance mapping).

**Bounded fix**
- In shared-contracts §4, state that every Runtime/Chat/headless composition root creating a bindable entry passes `counter_factory` from the same resolved embedding capabilities used for `counter`/`embedder`, whether or not a converter exists. This needs no document settings.
- Alternatively, make the parameter required for any entry that may later receive a document session.
- Optionally, have `create_ingestion_entry` validate the factory's space against `counter.space`.
- Add the assertion to the existing C4 witnesses.

**Future acceptance:** Chat `test_lifecycle_drains_entry_with_optional_late_converter` and Runtime `test_di.py::test_shutdown_drains_shared_document_worker` (or the installed probe) must show, in one lifecycle:
1. a text /ingest with an entry-only bind;
2. a later converter attach;
3. a genuine document /ingest through the **same** entry that stores a complete plan.

## Advisories (non-blocking)

- **ADV-1 — Converted-source/session predicate is not exact.** Define when a source counts as converted: `source_kind ∈ {pdf,docx,xlsx,pptx}` ⇔ `conversion_profile_sha256` is not None, as a `SourceDocument` invariant. Define "matching" as equality of `session.source` with `source` (including `source_id`, `raw_sha256` and `content_sha256`). Add a Memory/headless negative witness: a converted source with no session, or a mismatched session, refuses readiness before embedding. A text source plus a supplied session should also refuse. The plan-identity checks are a partial backstop.
- **ADV-2 — Reusing the Chat entry.** Spell out get-or-create semantics: reuse the owned entry on later /ingest, create it only when the holder slot is empty, and have the loser close its unowned entry. Otherwise a second per-request entry hits the different-object refusal.
- **ADV-3 — Exit labels.** Chat `adapters.py` places the "optional-converter bind_ingestion" and holder purposes at I3-C4, but the C3 text-ingest witness already needs entry-only ownership. Mark C3 as implementing minimal bind/ownership and C4 as completing the race/drain proof.
- **ADV-4 — Worker slot release.** State whether the one-active slot is released at `planned` or held until session close, which would cover parent embedding/storage. This affects backpressure and C4 expectations.
- **ADV-5 — Environment snapshot timing.** For runtime-backed Chat, state when the "captured explicit environment snapshot" is taken (runtime build vs. request entry), matching the runtime=None request-entry rule.

## Limits

This is a design/document review. It does not assess product-code conformance, completed vendor evaluation or a whole-framework source audit. Repeated generated map rows were inspected through focused views, not exhaustively. A4 consumer-compatibility claims were evaluated as design and not traced through every one of the roughly 40 Memory consumer files. This verdict grants no construction, effects, acceptance, push or delivery authority. No seventh council follows: the root hands back to the maintainer.

# SOL independent activation-package review — round 1

Candidate: `b04ab83afda313630eaaaa4e1dab09b71d9ce59c`  
Branch: `feature/cmd-ingest-001`  
Seat: SOL  
assessment_complete: **true**  
areas_assessed: **8/8**  
Verdict: **CHANGES_REQUESTED**  
Mandatory findings: **3**  
Overall design score: **8.25/10**

This is a completed document/design assessment. The package provides substantial implementation detail, but its exact headless dependency contract has a missing link, its active maps retain a removed qualification obligation, and worker readiness timing is not actionable without clarification. These are bounded planning corrections. Missing future implementations, unexecuted acceptance tests and unsigned final construction approval are not findings.

All references below are relative to `docs/planning/active/command-refactor/validation/document-ingestion/product-construction/activation/` unless stated otherwise. The score is the sum of the weighted contributions below; there is no cross-seat averaging, coverage grade or rounding to the council threshold.

## A1–A8 assessment

| Area | Weight | Weighted contribution | Assessment and evidence |
| --- | ---: | ---: | --- |
| A1 — decisions, scope and approval | 1.50 | 1.10 | All three decision records and `approval-binding.json` correctly preserve the removed pre-coding model campaign, workbook refusal, shared ownership and unactivated construction. Historical RD-01/RD-05 rows are explicitly superseded and are not independently treated as active requirements. However, current implementation-map assertions still request actual-serving parity qualification; F1 addresses that operative contradiction. |
| A2 — exact contracts and data flow | 1.75 | 1.30 | `shared-contracts.md` §§1–3 supplies immutable values, strict validation, Unicode spans, prepared input/vector identities, canonical serialization and injected local counting. Five digest examples distinguish preparation drift and bind plan/receipt data. The public Memory factory cannot obtain a `PreparedBatch` using its declared dependencies: F2. |
| A3 — shared process and lifecycle | 1.75 | 1.50 | §4 and `shared-worker-decision.md` give Tools one service implementation, Core lifecycle/events, Memory policy and external LLM requests. One active/one queued, early busy refusal, queued cancellation, termination/escalation/reaping and headless shutdown witnesses are concrete. The pre-activation measurement requirement conflicts with product-worker availability: F3. |
| A4 — consumer/configuration/store compatibility | 1.50 | 1.40 | I1 preserves old preparation/cache/call shapes; I2 coordinates guarded consumers. Omitted config fields remain parseable. Origin preservation, explicit fresh namespaces, pending-marker refusal, ephemeral isolation, role envelopes and strict v1 inspection/v2 active recovery are specified. No refusal-only compatibility credit is offered. F1 affects the capability prerequisite interpretation but does not justify weakening these runtime safeguards. |
| A5 — source/test/helper/document assignments | 1.25 | 1.10 | The 91 selected file entries identify owners, slices, exits and purpose. The 49 case exceptions retain valid assertions, with narrow mock/admission changes and genuine replacement document positives. Forty planned witnesses include headless and real app acceptance. Helpers, synthetic fixtures, offline exclusions and substantive guides are assigned. F1 contaminates specific I3 acceptance rows; it is not a reason to reject the overall mapping approach. |
| A6 — format/chunking/effects/cache | 0.75 | 0.70 | Shared contracts plus relevant REM sections specify meaningful content, complete coverage, exact capacity refusal, source-backed context, no lost tail, no second split and truthful partial/unconfirmed results. The Office decision rejects included-sheet hidden dimensions before conversion, retaining excluded-sheet behavior. Destination/incarnation/collection-specific cache receipt requirements remain in the linked REM. |
| A7 — packages/assets/profiles/TOOLS-DOC | 0.75 | 0.65 | Core/Commands remain neutral; LLM owns provisioned counters; Tools owns Docling and structural audit; Memory imports neither frontend nor Tools for the public entry. Strict manifest-root resolution, lazy conversion, separate counter/document extras, headless profiles and the Certifi floor are retained. TOOLS-DOC routing and its test exception remain separate. Final graph/profile bindings are honestly future work. |
| A8 — sequencing and handoff | 0.75 | 0.50 | I1 additive foundations, I2 coordinated existing consumers, I3 common ingestion and AG before human UAT form a useful sequence. Exact per-slice approval/effects and environment bindings are required. F3 leaves the remaining worker gate temporally ambiguous; F1 leaves removed qualification language on the proposed execution path. |
| **Total** | **10.00** | **8.25** | **Eight areas assessed; three mandatory corrections.** |

## Mandatory findings

### SOL-R1-01 — operative I3 acceptance reinstates parity qualification

**Sources:** `model-qualification-decision.md`, paragraphs 2–3; `slice-file-map.json:924`, `:957`, `:985`, `:1346`; `test-case-map.json:1357` and `:1375`; `shared-contracts.md` §3, lines 163–172; `validation-plan.md`, installed-probe paragraph.

The decision removes the separate identity/tokenizer-parity campaign and explicitly forbids a new mandatory campaign after coding. Nevertheless, the I3-C2 assignments and both headless common-plan witnesses instruct the builder to “Apply DI24 offline asset-root and actual-serving parity qualifications to the final common document plan and counter.” This is an operative future acceptance instruction, beyond the expressly historical RD-01/RD-05 rows. The validation plan also anticipates an actual-serving window supplying Q parity/identity facts, while the strict capability record requires parity and serving-identity evidence fields and declares null evidence unqualified. Together these leave a builder without a clear distinction between retained runtime safeguards and the removed campaign.

**Requirement:** Common brief decisions 2 and 5; A1 current decisions and removal of contradictory prerequisites. The issue is not that identity, local asset validation or normal positive compatibility tests exist. Those remain required.

**Bounded fix:** Reconcile the active map assertions, validation paragraph and capability-record admission semantics with the decision. Explicitly specify which existing records/evidence are reused and how retained input-limit, identity, role, vector and store safeguards operate without commissioning the removed campaign. Mark historical prerequisite wording as historical where necessary; a fresh campaign must not be an implicit dependency of a non-null evidence field. Do not reopen Docling selection or erase ordinary implementation tests.

**Future acceptance implication:** I1/I2/I3 must still prove exact local counting/preparation, overflow rejection, valid positive consumer flows and store-space isolation. A reviewer must be able to identify their approved inputs and witnesses without demanding a separately completed actual-serving parity campaign.

### SOL-R1-02 — the exact headless factory lacks an embedding dependency

**Sources:** `shared-contracts.md` §2, lines 82–90, especially the exact `create_ingestion_entry` signature at line 87; §3 full-plan/batch-before-write rule; linked REM, shared-entry ownership paragraphs around lines 155–170.

The factory receives destination, `PreparedVectorStore`, `TokenCounter`, defaults and optional pure counter factory. `TokenCounter` only prepares/validates input locally. `PreparedVectorStore` exposes only `write_prepared(..., batch: PreparedBatch)`. The separate LLM `embed_prepared` method creates that batch, but no declared factory argument or Core protocol makes that operation available to Memory. Thus a conforming headless caller supplying only the stated protocols cannot complete planning → embedding → storage. Accessing a concrete store's private embedding client, importing LLM by name or using a global would introduce an undocumented dependency and defeat the exact injected contract.

**Requirement:** A2 exact data flow and injected dependencies; shared-worker decision keeps actual LLM requests outside the converter; REM assigns full-batch embedding and persistence orchestration to the common entry.

**Bounded fix:** Declare a narrow neutral prepared-embedding protocol and inject it into the Memory factory, or specify an equally explicit composition contract that supplies the operation. Identify validation, timeout/cancellation and ownership responsibilities and bind the corresponding Core/Memory/composition/test assignments. Keep the local counter distinct from the provider operation and keep the worker free of clients/stores.

**Future acceptance implication:** A headless positive test must compose the public factory using only declared dependencies, show once-only preparation, validate the entire returned batch before its first write and propagate embedding refusal with zero storage. No Chat imports or hidden concrete-store attributes may be needed.

### SOL-R1-03 — worker feasibility gate precedes availability of its assigned implementation

**Sources:** `shared-contracts.md` §4, lines 247–249; `readiness-disposition.md`, RD-03 row and “Proposed numeric interpretation”; `README.md`, slice boundaries and activation status; file-map Tools worker assignments I3-C1/I3-C4; `approval-binding.json`, A1/A2.

The exact proposed product process/session choice is subject to measured RD-03 feasibility “before activation.” RD-03 calls for spawn/IPC/local-counter, cold/warm resources, cancellation, 300-second deadline and two-second termination-grace proof. Yet the owned worker is explicitly new product code assigned to I3, while each slice needs the prior readiness/approval binding. The package does not distinguish an already available reusable measurement from a narrowly authorized prototype or from acceptance after creation. Existing Docling results are correctly acknowledged as insufficient to establish this worker's behavior. That leaves a circular or ambiguous gate, rather than an actionable remaining readiness disposition.

**Requirement:** Common brief decision 5 and A8: feasible, noncircular timing with actionable owner/artifact; completed product worker code must not be required before authorizing its creation.

**Bounded fix:** Separate reusable upstream resource/admission facts from product lifecycle acceptance. State which concrete artifact Tools supplies at which gate, allowing the assigned worker implementation to exist before its lifecycle tests run and before subsequent activation/acceptance depends on them. If a pre-coding experiment is truly needed, identify its specific unresolved risk, bounded artifact and authority and explain why normal I3 tests cannot answer it. Do not invent a general readiness project.

**Future acceptance implication:** Preserve all resource, responsiveness, repeated-cancel, queued-cancel, backpressure, timeout, escalation, OS-confirmed reap and no-late-effects tests. Tie them to the exact created worker and installed profile before claiming implementation readiness.

## Separate advisories

Make operative next-step text directly reflect the current decisions: the README's final hosted-identity-first instruction and readiness disposition's final B02-first paragraph are easy to misread despite the explicit override. This editorial cleanup supports F1 but does not independently invalidate historical provenance.

Retain the explicit app.py scope-reconciliation stop. The inspected app awaits registry execution before publishing output and reaches coordinator cleanup in `finally`; the proposed handler/adapters can therefore be evaluated at real seams. That inspection establishes plausibility, not cancellation correctness. Likewise, Runtime shutdown and the client-close adapter are existing extension points, not already implemented worker drains.

## Input identity, preservation and limits

The request was hashed before reading: SHA256 `5c23e6db6eb72299cf8821ce4b53413468fd663bce9e14dce45cbc1690ceaf50`. All 13 required input hashes matched, including the exact brief `784d0f97fe2faf5699ed583ed3f751471995b6362f8f5d890c576c5a923c2894`. All required prose/binding/decision inputs were read. Complete file identities/assignments, grouped repeated case semantics, concrete new witnesses, helper/module/fixture dispositions and five vector values were inspected; ordinary output truncation was recovered through bounded views.

The safe current controls and supplied controller-checks hashes matched. Their reported administration/preservation outcomes were inspected once, not rerun or treated as semantic proof. Optional reads were limited to relevant REM content/cache/format requirements and phase sequencing. Source reads were limited to app publication/finally handling, Runtime shutdown and FrameworkAsyncClientLifecycle.close to answer concrete lifecycle feasibility questions.

Entry and exit checks used `GIT_OPTIONAL_LOCKS=0`, bytecode disabled and logical `git ls-files -s -z` hashing before status. HEAD/branch matched the frozen request; logical index was `ef217e835738dc266e88c4380d9720f75fa79590865d5e87f2bc53f38e6c618a`; staging remained empty and status exactly matched the two declared modified examples plus untracked `.friday-old/`. All eight declared preservation entries matched metadata and permitted hashes at both boundaries. Independent records are `entry.json` and `exit.json` beside this report.

No product imports/tests/builds/installs/network/model/store calls, inventory rebuilds or dependency/archive audits were performed. No memory, peer/prior reports, raw authority/history, controller reasoning or delegate inventory was used. Finance's excluded integration module and protected state contents were not read or parsed; only declared preservation hashes/metadata were checked. Writes were confined to this seat's new external scratch. There were no delegates, repairs or additional passes. This verdict grants no construction, effects, UAT, acceptance or delivery authority. This seat stops after this report.

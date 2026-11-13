# SOL independent design review — INGEST activation, global round 7/9

Verdict: **VERIFIED**. assessment_complete=true; areas_assessed=8/8; mandatory_findings=0; overall_score=**9.54/10**. This seat meets the design gate. No separate coverage score is assigned. This report concerns frozen candidate `9ddaf6f87f12486ee0bea82dc1561046f2353d5a`, branch `feature/cmd-ingest-001`, second extension pass 1/3.

## Authority, inputs and method

The first operation computed the request SHA256 using Python standard-library hashlib, before reading it: `ada377ddd0835d4cd5e128a2a9313e922a22f984792124972d748216e92972af`, as required. I read the request, then the latest extension authorization and unchanged common brief before substantive review. An initial attempt to open the authorization at checkout-root `council/` failed without reading any file; I corrected it to the exact activation-relative path declared in the request. The latest extension authorizes rounds 7–9 after round 6, changing caps only. The original brief's draft preface and historical limits do not override that authorization.

All sixteen required input pins matched at entry and exit. I read the overview, contracts, dispositions, validation plan, approval binding, three decision records, reconciliation, common brief, authorization and neutral corrections. I inspected the complete slice assignments, case exceptions, future witnesses, helper/module/fixture dispositions and digest examples through focused views, recovering truncated output with bounded reads. Repeated generated identity fields were not treated as semantic evidence. Controller and current-control files were hash-checked only; neither supplied correctness proof.

New physical scratch is this report's containing directory, outside the checkout and supplied input directories. Entry and exit records show the logical index obtained before status, optional locks disabled, identical HEAD/branch/status/staging, all required pins and all eight preserved metadata/hash records. Logical index SHA256 is `fa0be09a85c95d9185bc1edc3fe8d83371ab1836b04d56bbb1598792c7a30b9b`. The only dirty paths remain the two declared example YAML files and untracked `.friday-old/`; staging is empty.

## Neutral corrections assessed first

**H1 — satisfied as design and assigned acceptance.** Shared contracts section 2 makes counter_factory required for every new Memory entry. Every composition root must derive factory, parent counter and embedder from one ResolvedEmbeddingCapabilities; document settings are irrelevant to factory construction. Missing/None refuses construction. The retained capability-record hash travels with the pure factory and is verified against the exact bounded bytes later parsed, including child creation. Space and complete-plan/batch checks remain independent safeguards.

The functional witness is explicit, rather than inferred from registration. Section 2, validation-plan's final paragraph, the integration node `test_same_entry_ingests_text_then_document_after_late_attach`, Runtime/Chat lifecycle nodes and installed helper require text storage, late document binding/converter attachment, then genuine document storage through identical E and lifecycle, with actual plan/provenance readback and ordered shutdown. Installed normal and optimized execution must repeat it. The transition uses an already document-capable installation; only configuration arrives late. Separate text-only profiles still prove independence from the document stack. These are unexecuted future obligations, correctly assigned after construction.

**H2 — satisfied.** SourceDocument declares converted-kind iff non-null conversion-profile identity. Memory requires full immutable session.source equality, rejects missing/mismatched sessions and text-plus-session before planning/embed/store, and does not revive closed or consumed sessions. A named I3-C2 negative witness covers these rules. Chat get-or-create reuses the admitted entry, atomically adopts a winner, closes an unowned loser without closing shared clients and refuses foreign/closing ownership. C3 implements minimal holder, binding, reuse and normal cleanup; C4 proves contention and repeated cancellation. Request-entry document environment snapshots permit first late configuration, while existing converter settings and service-lifetime embedding capabilities remain immutable. Section 4 retains the active worker slot through planned state until session close, confirmed reap and cleanup; queue release is explicitly observed at C4.

**H3 — satisfied.** I completed the unchanged eight-area review below under extension2, preserving scope, weights, roster and per-seat gate. No earlier or peer verdict was consulted.

## Weighted eight-area assessment

Contribution equals area score/10 multiplied by the stated overall weight; weights total 10. The overall is the exact sum, without upward rounding or cross-seat averaging.

| Area | Weight | Score /10 | Contribution | Evidence and outcome |
|---|---:|---:|---:|---|
| A1 | 1.50 | 9.6 | 1.4400 | README, current decisions, reconciliation and binding consistently retain proposed/unapproved status. Removed parity campaign is not restored; workbook refusal and staged worker proof control historical clauses. Satisfied. |
| A2 | 1.75 | 9.6 | 1.6800 | Contracts §§1–3 specify immutable fields, strict optimized-mode validation, source/profile/session/plan/vector/receipt identity and explicit injected factory/broker/store. Digest examples cover space, preparation drift, Unicode, plan and receipt meaning. Satisfied. |
| A3 | 1.75 | 9.5 | 1.6625 | Contracts §4 fixes process/IPC ownership, bounded queue, deadlines, cooperative copy/audit, diagnostics, cancellation, reap and unhealthy-state exclusion. Public DI and direct headless composition avoid kernel private access; actual shared and app witnesses are assigned. Satisfied. |
| A4 | 1.50 | 9.5 | 1.4250 | Contracts §§2,3,5 preserve old call shapes and I1 positives, require coordinated I2 resolution, positive supported defaults, fresh namespaces, strict v2 active recovery and isolated ephemeral clients. Case map includes successful CRUD and existing-consumer operations, beyond refusal controls. Satisfied. |
| A5 | 1.25 | 9.5 | 1.1875 | Exact slice/file owners, 49 narrow exceptions, retained default, no retirements, opt-in helper rules, classified selectors and named public/installed witnesses provide actionable coverage. Authored architecture/guides and independent content review remain required. Satisfied. |
| A6 | 0.75 | 9.5 | 0.7125 | Source-backed spans, exact counting, whole-plan validation, typed failures and readback-confirmed receipts prevent false completion. Retained REM cache rules bind destination/incarnation/collection/record provenance and separate extraction reuse from storage proof. Satisfied. |
| A7 | 0.75 | 9.6 | 0.7200 | Narrow LLM counter and Tools document dependencies/assets have owners and declaration-before-use timing. Default Chat, optional Tools, headless, origin and Certifi acceptance remain explicit. TOOLS-DOC routing is separate. Satisfied. |
| A8 | 0.75 | 9.5 | 0.7125 | I1 additive foundation, I2 coordinated callers/recovery, I3 conversion/common plan/adoption/lifecycle/install sequence is buildable. A1–A5 activation gates remain open; aggregate review precedes human UAT and delivery. Satisfied. |
| Total | 10.00 | | **9.5400** | Eight areas complete. |

## Buildability and mandatory findings

**No mandatory findings.** The required corrections now describe both a viable composition and the future tests that can falsify it. Exact dependencies exist before their first assigned use; C3 is not asked to adopt text ingestion before basic ownership exists; C4 proves the fuller lifecycle. The package does not require a finished worker to authorize building it.

Targeted source inspection supports the chosen seams: adapters.py currently has the frozen no-argument FrameworkAsyncClientLifecycle and close method; DIContainer has service slots and shutdown; files.py contains the placeholder document dispatch being replaced. app.py serially awaits registry execution before output and reaches coordinator cleanup in finally. Those seams plausibly support the selected adapter/runtime edits without app.py expansion. Their existence is not proof that future cancellation code works: actual application cancellation, post-child/pre-return races, repeated cancellation, failed reap and installed launch must still pass. If the permitted seams cannot deliver those results, scope reconciliation is expressly required rather than silent expansion.

Future acceptance remains substantial: real local counting assets, genuine format fixtures, complete source and derived preflight, disposable Chroma readback/reopen, source/session negatives, retained positive consumer behavior, normal/-O installed origins, headless lifecycle/resource limits and independent implementation/document review. These are assigned implementation obligations, not missing preconstruction experiments.

## Separate advisories

1. In requirement-reconciliation.md, the paragraph beginning “For current exact implementation choices” still says the current extension controls rounds 4–6. Its later final paragraph and extension2 clearly supersede that wording. Clean up that stale sentence at the next authorized planning update; it does not create an operative cap ambiguity in this frozen package.
2. Slice-map adapters.py rows repeat some holder/registration work under C4 after the later explicit C3 minimum. Consolidate those descriptions when preparing exact phase approval so builders can readily distinguish C3 implementation from C4 proof. The current precedence and final assignment are sufficient; no extra scope or deferred ownership is needed.

## Limits and disposition

Only document reads, targeted source reads and standard-library/Git identity checks ran. No product import, test, build, install, old harness, network, provider, model or store operation ran. No memory/history, peer reports, private reasoning, raw authority/navigation inventories or nested agents were used. The excluded Finance integration file was never read, parsed or executed. Preserved files received only authorized metadata/hash checks; protected directories were not traversed. No checkout or supplied-input write occurred.

This is one completed independent SOL design seat. It supplies no construction, effects, human acceptance, push, merge, delivery, replacement-seat, later-pass or tenth-council authority. Work stops with this report and its boundary evidence.

# ASTRA independent design review — INGEST activation, round 7

Verdict: **VERIFIED**. `assessment_complete=true`; `areas_assessed=8/8`; mandatory findings: **0**; overall design score: **9.55/10**. This is SECOND extension pass 1/3, global round 7/9, on candidate `9ddaf6f87f12486ee0bea82dc1561046f2353d5a`, branch `feature/cmd-ingest-001`.

The package provides a coherent, bounded basis for preparing the exact construction approval. It does not itself activate construction. The score is the sum of the eight weighted contributions below, assigned after assessing all eight areas. It is not averaged with another seat, rounded up to the gate, or accompanied by a separate coverage score.

## Authority and initial correction assessment

The first operation computed the supplied request's SHA256 with Python standard library and matched `ada377ddd0835d4cd5e128a2a9313e922a22f984792124972d748216e92972af` before reading its contents. The request and latest `council/extension2-authorization.json` were read before the common brief and other required inputs. The extension explicitly renews rounds 7–9 after round 6 and preserves scope, roster, weights and quality gate. The original brief's historical draft preface and earlier caps do not defeat that explicit authority. No earlier extension report, peer conclusion, private reasoning or memory supplied this judgment.

**H1 — satisfied as a design and assigned acceptance requirement.** Shared-contracts section 2, “Counter-factory construction and functional late attachment,” requires the factory for every entry, including text-first composition. A single resolved embedding capability supplies factory, parent counter and embedder; the child-created counter must match the expected space. The required argument is not conditional on document settings, and missing/None cannot produce an entry that later lacks planning capability. This is matched by the Memory factory signature, selected Memory implementation assignments, and headless/text composition witnesses.

The correction also reaches actual functionality. The named `test_same_entry_ingests_text_then_document_after_late_attach` requires successful text ingestion with no document binding, publication of that binding before the next request, late converter attachment, genuine PDF or Office ingestion through the identical entry, complete stored-chunk/provenance readback, and ordered shutdown. Both Chat and Runtime lifecycle witnesses carry this requirement; the installed helper explicitly repeats it in normal and optimized modes. Separate lifecycles and ownership-only spies are expressly insufficient. Using an already document-capable installation with late settings avoids an impossible mid-lifecycle dependency installation. This is future acceptance, not claimed execution.

**H2 — satisfied.** Section 1 makes converted kind and non-null conversion profile an iff invariant. Section 2 requires complete immutable `session.source == source` equality, rejects missing/foreign sessions and nonconverted sources with sessions before planning/embedding/storage, and refuses consumed sessions. The named Memory negative witness covers these conditions. Section 4 specifies get-or-create reuse, atomic winner adoption, loser entry cleanup without closing shared clients/stores, and refusal after closing or a foreign binding. Minimal Chat ownership and ordinary cleanup belong to C3; contention/cancellation proof belongs to C4. The active converter slot persists through planned state until session close, OS-confirmed reap and cleanup. The worker witness observes that release point. Document environment snapshots are request-local until first converter binding, then immutable; embedding capabilities retain their service-lifetime snapshot. The binding-refusal witness checks both runtime-backed and runtime-absent paths.

**H3 — satisfied.** The complete original A1–A8 design scope was assessed after H1/H2. The new authority changes the round budget only. No replacement, extra seat, later pass, construction or effects were initiated.

## Weighted eight-area matrix

Contributions are points earned against each area's stated maximum; they sum exactly to 9.55.

| Area | Weight | Contribution | Assessment and principal evidence |
| --- | ---: | ---: | --- |
| A1 | 1.50 | 1.44 | Current decisions, reconciliation, readiness dispositions and approval-binding agree on removed serving/parity campaign, XLSX refusal and post-build worker proof. All activation gates remain incomplete. One stale intermediate budget sentence is an advisory below. |
| A2 | 1.75 | 1.67 | Shared-contracts sections 1–3 and 5 specify immutable values, strict loaders, source/profile/plan/prepared identities, injected counter/broker/store interfaces, required factory and complete-batch validation. Digest examples cover space, preparation drift, Unicode, plan and receipt. |
| A3 | 1.75 | 1.66 | Section 4 assigns the subprocess and IPC to Tools, policy to Memory and neutral protocols to Core. Explicit queue, deadlines, signal/reap, unhealthy-state exclusion and retained cleanup rules have headless, Runtime and actual Chat acceptance assignments. |
| A4 | 1.50 | 1.44 | Sections 2, 3 and 5 preserve configured call shapes, stage legacy behavior through I1, switch consumers together in I2, require positive defaults, enforce namespace origin/space/incarnation, and separate strict v1 inspection from v2 active recovery. |
| A5 | 1.25 | 1.19 | Complete selected slice assignments and concrete case-map meanings were inspected. Retain-by-default, narrow exceptions, helper restrictions, offline classifications, named installed probes and substantive guide work are explicit. Missing future nodes cannot earn proof. |
| A6 | 0.75 | 0.72 | Format decisions, source spans, meaningful-content admission, exact capacity checks, readback receipts and parent cache rules preserve truthful outcomes. Workbook refusal precedes conversion; incomplete/unknown effects cannot produce a success receipt. |
| A7 | 0.75 | 0.72 | Narrow counter and document dependencies precede first use; assets stay externally bound. Headless text remains independent of the document stack. TOOLS-DOC routing, Core/Commands dependency boundaries and default Chat adoption remain distinct. |
| A8 | 0.75 | 0.71 | I1 foundations, I2 coordinated compatibility/recovery, and I3 conversion/common-plan/adoption/lifecycle/installed exits are buildable. Exact impact/approval/effects binding, aggregate implementation review and human UAT remain explicit later duties. |
| Total | 10.00 | **9.55** | Complete bounded design assessment; zero mandatory findings. |

## Aggregate buildability and compatibility

The architecture has a usable dependency direction: Tools owns the retained converted document and process; Memory invokes the owned session with an injected pure factory; LLM embeds in the parent; the admitted store receives a fully checked batch. Read-only conversion does not need Memory or embedding initialization. Text ingestion does need configured embedding capabilities, but neither conversion settings nor Docling. The public headless recipe obtains the destination from an admitted store instead of reaching into RuntimeKernel internals.

Targeted source inspection confirmed that `FrameworkAsyncClientLifecycle` is currently a frozen dataclass with a no-argument builder and `close()` delegating to LLM cleanup. The proposed custom constructor with one mutable typed holder is implementable within the selected adapter file while preserving that call shape. Runtime's existing public `DIContainer` and shutdown method provide the identified ownership seam. These observations support the design assignments; they do not establish that the proposed lifecycle already exists or works.

The compatibility plan requires operational positives, not only refusals. TM-A001–010 retain embedding result/cache/batch/telemetry assertions while fixing synthetic dimensions and indices. TM-A011–047 retain store behavior using admitted disposable destinations. TM-A048 replaces fake-extension document positives with real extraction and preserves text dispatch. TM-A049 preserves source/description/listing and text ingestion without converter setup. The B/N/R and FC witnesses address existing consumers, ephemeral isolation, truthful background effects and strict recovery. No test counts or prior verdicts were treated as proof.

For format and cache questions, targeted REM sections establish complete admitted content, meaningful OCR text, saved-formula limitations, original unit provenance and no diagnostic substitution. The current Office decision overrides only hidden-row/column filtering: affected included sheets cause whole-workbook refusal, while hidden-sheet exclusion remains. Parent cache requirements additionally demand current destination/incarnation/collection and record/provenance validation before storage can be skipped. Context-only or mtime-only hits cannot satisfy new storage, and derived records stay unsplit with whole-batch preflight. Current case assignments carry these requirements without activating previously unwired routes.

## Mandatory findings and future acceptance

**None.** No mandatory bounded repair is requested. This conclusion does not waive the unexecuted acceptance obligations. Builders must still prove same-entry late attachment, exact session admission, contention and cleanup, complete format/chunk provenance, no late publication/storage, positive existing consumers, strict recovery and actual normal/optimized installed profiles. Those duties have owners and feasible post-build exits. The final canonical impact revision, local manifests, exact case exceptions and isolated execution/effects must be bound before their applicable phases. Completed worker evidence is not required before authorizing its construction, and no serving/parity campaign is reinstated.

## Separate optional advisories

1. In `requirement-reconciliation.md`, the middle paragraph still calls rounds 4–6 the “current extension”; its final paragraph correctly names the second extension and rounds 7–9. Consolidate that sentence when next editing the packet. The latest authorization and final controlling statement are unambiguous, so this is editorial and does not block the design.
2. When implementing C4, include parent-side decoding and validation of large IPC results in responsiveness observations. A bounded 128 MiB frame can still be expensive to materialize. The existing end-to-end heartbeat and resource criteria already provide the acceptance boundary; this advice does not require a new experiment or prerequisite.

## Evidence and limits

All required input pins matched at entry and exit. Logical index was obtained before status with optional locks disabled; HEAD, branch, status and staging matched the request. All eight declared preserved metadata/hash records matched, including both dirty YAML files and export files by hash only. Entry and exit records are identical. Required controller files were hashed only and never used as semantic proof. Additional targeted parent reference hashes also matched their supplied pins.

Read-only Python/Git/text operations were used. No product import, test, build, install, old harness, admin replay, provider, model, network or store operation ran. No excluded Finance file or protected state/configuration contents were inspected. Truncated displays were recovered through focused reads; repeated mapping rows were reviewed by their actual assignment/assertion meaning. No repository or supplied-input writes occurred. Durable outputs reside only in the new physical scratch directory containing this report and minimal entry/exit/boundary JSON evidence.

This single-seat review is complete and stops here. VERIFIED grants no construction, effects, human acceptance, delivery, merge or tenth-council authority.

# ASTRA focused council seat — round 2

Verdict: **VERIFIED**. `assessment_complete=true`; **8/8** areas assessed. Mandatory findings: **0**. Coverage: **10.0/10**. Overall: **9.60/10**, the exact sum of the rubric contributions below, without rounding up. This seat meets the requested document-review threshold.

Candidate: `0144c53908afb6f8288425c58c7a3bbff651faef`, branch `feature/cmd-ingest-001`. Target: `docs/planning/active/command-refactor/directives/CD-CMD-INGEST-001-product.md`, SHA256 `3b998de0ec87d2a2a581a5b5734cf2703a5ca950a1876707e854557cadce4db1`.

The directive provides a comprehensive, coherent, conditionally buildable Friday implementation plan. Its staged contracts and acceptance duties distinguish shared capabilities, actual public integration, compatibility and subsequent human acceptance. This conclusion is an independent assessment of the current documents and bounded source reads, not adoption of prior verdicts or proof that future runtime behavior already works.

## C1–C5 assessment first

**C1 — read-only lifecycle: satisfied as a construction-plan requirement.** Sections 3.2 and 3.5 explicitly require an awaitable Chat document adapter over Tools-owned off-event-loop work, with no Memory lease, embedding profile, entry or chunk planner solely for display. They preserve synchronous legacy text/table use. Cancellation before launch, during work and after completion before rendering invalidates output; cleanup joins work even when its caller is cancelled. Exit/shutdown drains owned handles. Section 5 and the phase map's additional I3-C3/C4 witnesses separately cover responsiveness, cancellation and actual shutdown with absent/unready Memory and zero admission/provider/store calls. A2 must freeze the actual tracking, adapter and drain hooks before generation. This is actionable staged design, not an unsupported assertion that current code already supplies it.

Source corroboration matters here: registry.py:669–682 calls synchronous `SmartFileReader.read` directly inside the async handler. The application awaits registry execution, then separately writes the result (app.py:490–507); its finally path reaches coordinator cleanup and runtime async-client close (app.py:540–550, 611–647). These are real integration boundaries. Per-request join and lifecycle drain are technically feasible at the named seams; final exact bindings and application-level witnesses remain essential. No native hard-kill guarantee is inferred.

**C2 — shared headless planning: satisfied.** Section 3.3 now states the invocation direction: Memory invokes an injected Tools document planner through Core protocols; LLM supplies counting/preparation; vendor structures remain Tools-internal. Section 5 and I3-C2 require a genuine headless document composition into actual disposable storage, exact shared-plan chunks/receipt, and no Chat import. Text-only headless evidence cannot substitute.

**C3 — dispatch: satisfied.** Section 3.2 preserves the raw tail before `_parse_command_input`, resolves aliases and the actual registered handler, and selects file parsing by default-handler identity. Source registry.py:165–195 and 1196–1201 confirms both the whitespace-loss point and the existing resolution seam. Custom overrides, unrelated commands and aliases retain explicit compatibility duties.

**C4 — capacity: satisfied.** Section 3.3 requires refusal rather than clamping for explicit, YAML and built-in budgets above effective prepared-input capacity. It includes default 512 under N-CAP, known-capacity preflight before conversion and complete final batch preflight before provider/storage calls. Section 3.4 adds once-only preparation and whole-response validation.

**C5 — assets/defaults: satisfied.** Sections 2, 3.1 and 3.3 assign LLM counter/profile support and exact asset shipping or provisioned-root identities, hashes, licenses and headless availability to A2. Tools consumes injected capabilities; no global-cache or first-use download assumption is permitted. Memory built-ins/per-call options serve headless document policy; RuntimeConfig gains no document YAML subtree. Existing MCP settings and unsplit semantics remain separate. Processor character settings cannot override or re-split common source plans.

## Fresh full F1–F8 assessment

| Area | Outcome and evidence | Award / weight |
| --- | --- | ---: |
| F1 | Complete extraction → planning → embedding → storage ownership in §§2–3.5. Core owns neutral values/protocols; Tools conversion/document adaptation; Memory policy, plan validation and persistence; LLM exact preparation/counting. Actual headless document proof and injected call direction prevent Chat-only or vendor-coupled completion claims. | 1.90 / 2.00 |
| F2 | §3.2 names actual registry/default-handler integration, raw-tail quoting, opaque descriptions, exact options, aliases/custom handlers and legacy lines behavior. §5 requires genuine registry-to-Chroma evidence. Existing placeholder readers and quote-loss source seams match the proposed changes. | 0.95 / 1.00 |
| F3 | §3.3 applies document/512 defaults and independent overrides across supported source types; assigns document/recursive/fixed strategies and forbids second splitting. §§3.1/3.4 specify qualified counters, final prepared-input limits, roles and model configuration preservation. | 1.45 / 1.50 |
| F4 | §3.4 incorporates FC-01–14 with explicit six exceptions/remedies, fresh/matching/ephemeral namespace policy, recovery versions, positive B/N coverage and source/derived distinctions. The phase map and annex distinguish maintained, public injectable and absent routes, including unsplit MCP, unscored maintained recall, background extraction, multi-agent visibility and store-only inspection. | 1.90 / 2.00 |
| F5 | §§3.1/3.3/3.5 require complete-success extraction, truthful partial storage, source/attempt/profile/plan binding, destination-specific receipts, admission through quiescence and separate read-only cancellation. No transaction or immediate native-kill promise conceals partial effects. | 0.95 / 1.00 |
| F6 | §4 and P01–P17 cover eight bounded implementation owners and nine indirect package dispositions. Counter-only headless profiles, default Chat document dependencies, lock/Certifi effects and optional Tools behavior have owners. The full companion directive independently owns factory/smart_read document routing and selections. | 0.75 / 0.75 |
| F7 | §5 requires actual command/storage/reopen, genuine formats, separate headless document and read lifecycle cases, operational B/N/R, installed normal/optimized profiles and meaningful negative controls. A3 maps old/new cases, helpers and oracles before rewriting. §6 demands authored architecture/guides with verified examples and technical review. | 0.95 / 1.00 |
| F8 | §§1–2/7 and the phase map provide Q → I1 → I2 → I3 → AG → UAT with owners, prerequisites and scoped exits. Additive I1 staging preserves old preparation/vectors until I2 binding; unwaived regressions block every exit. Exact appendices, authority, stop conditions and separate final council/UAT are explicit. | 0.75 / 0.75 |

The total is **9.60**. The small deductions reflect integration and verification complexity concentrated in future contract detail, not unidentified mandatory omissions. Coverage is **10.0** because all eight requested focused assessment areas were completed; it is not a measure of runtime confidence or exhaustive source coverage.

## Mandatory gaps

**None.** No requirement/evidence/bounded-fix/acceptance-implication finding is raised. In particular, the absence of future product protocols or executed candidate tests is not a defect in this conditional directive: actionable owners, required decisions, pre-generation timing and post-build witnesses are specified.

## Advisories and practical limits

1. **Bind read lifecycle at the real application boundaries.** A2 should show how ownership survives cancellation and how result eligibility is checked at the command/render boundary, then identify the existing shutdown callback that drains it. The actual app writes output after registry return and performs shutdown through a separate coordinator path. The required I3 tests should exercise those paths, not only a worker helper. This implements the existing requirement; it is not a demand for product code during this review or an automatic expansion of the allowlist.
2. **Make the A2 planner contract demonstrably composable.** Specify who owns retained document structure, its lifetime, neutral source/plan identity, synchronous counting calls and which bounded worker executes repeated counting. Sections 3.3/3.5 already assign these responsibilities; an approved concrete appendix must preserve them without introducing cross-package imports or a second conversion.
3. **Keep cache acceptance destination-sensitive.** Current smart_read.py:279–320 returns early on cache hits; its large-file processor is lazily constructed with existing character configuration at lines 209–231. These actual seams justify the directive's required small/large/force_chunked, opt-in-transition and destination-bound receipt witnesses. A conversion hit alone must never count as completed storage.
4. **Do not interpret this result as Q closure.** Readiness RD-01–07 still govern unresolved deployment identity/parity, hidden-unit exclusion versus whole-workbook refusal, resource envelopes, dependency assets and exact appendices. The directive explicitly stops activation for unknown qualification. Completed Docling evaluation was accepted as established input; it was not repeated or extrapolated to candidate integration support.

## Source and boundary evidence

First action hashed request.json before reading it: SHA256 `eb0d88149a5b8bf3413b81ff9a2303e9baeb55063e14398c1af303fca7df09fe`, matching the supplied value. Verified all nine required input hashes and safe current-controls hash. Read the neutral correction brief before assessing the full directive and context. Read the required phase map, full companion, P01–P17/test/documentation responsibilities and readiness distinctions. Ordinary combined-output truncation was recovered through bounded reads.

Optional references were limited to REM exact implementation paths/related requirements and the compatibility annex's B/N/R, consumer and proof matrix sections; both matched their request hashes. Targeted source inspection covered Chat registry, file helpers, runtime lifecycle declarations/composition, actual app command/render/shutdown paths and Tools smart_read cache/processor seams. No body-by-body framework audit was performed. Source identities and read ranges are recorded separately.

Entry and exit used `GIT_OPTIONAL_LOCKS=0`, with logical index from `git ls-files -s -z` before status; Python utility calls disabled bytecode. HEAD/branch, logical index, status, staging and all eight declared preserved metadata records matched the request and each other. Logical index SHA256: `5dca109fa1fc88aa868e5efd2d9c761a810e994cb24840c181cffea33dab4f5b`. Dirty example YAML and export files were hashed only; protected directories were stat-only. No protected contents were inspected.

No memory, prior/peer reports, transcripts, raw authority history, credential, excluded Finance file or private reasoning was accessed. No repository/supplied-input writes, imports of product code, tests, builds, installs, administrative suites, network/provider/model/store calls, inventory rebuilds, delegation or repair occurred. Only new physical external reviewer scratch was written.

This **document verdict grants no construction, effects, UAT, acceptance or delivery authority**. This single ASTRA seat is complete; the controller owns any remaining bounded workflow.

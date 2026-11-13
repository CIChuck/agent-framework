# SOL focused council assessment — round 2

Verdict: **VERIFIED**

assessment_complete: **true**; areas_assessed: **8/8**; mandatory_findings: **0**.
Coverage: **10.0/10**. Overall: **9.60/10**, computed directly from the contributions below, without rounding up or averaging with other seats.

Candidate: `0144c53908afb6f8288425c58c7a3bbff651faef`, branch `feature/cmd-ingest-001`.
Target: `docs/planning/active/command-refactor/directives/CD-CMD-INGEST-001-product.md`, SHA256 `3b998de0ec87d2a2a581a5b5734cf2703a5ca950a1876707e854557cadce4db1`.
This is an independent assessment of a proposed implementation directive, not product conformance or completed runtime validation.

## Current C1–C5 requirements assessed first

**C1:** §§3.2/3.5 now define an awaitable Chat document-read adapter over a Tools worker, independently of Memory admission/profile/entry and chunk planning. Before-start cancellation prevents launch; during-work and completed-before-render cancellation invalidate output; per-request cleanup joins even under caller cancellation; exit/shutdown drains before returning. The phase map adds three separate actual read witnesses for responsiveness, cancellation and shutdown, alongside ingestion's distinct lease-bearing lifecycle. The existing registry performs a synchronous SmartFileReader call inside its async read handler (`registry.py:669`); consequently these are necessary implementation duties, not descriptions of an already asynchronous path. A2 must freeze the adapter and real drain hooks before generation. This is actionable staging rather than missing product code.

**C2:** §3.3 makes Memory invoke an injected Tools planner through Core preparation/counting protocols; vendor structures remain in Tools. §5 and I3-C2 require a genuine document-to-disposable-store headless witness, exact one-plan source records and receipt, and no Chat import. Text-only headless coverage is explicitly insufficient. The composition and acceptance directions are coherent.

**C3:** §3.2 names the real loss point, `CommandRegistry.execute` / `_parse_command_input`, and requires preserving raw tail before whitespace splitting. Selection depends on the resolved registered default handler's identity. Existing aliases resolve before dispatch (`registry.py:177–190`); the specified custom/alias preservation is feasible without replacing unrelated parsing.

**C4:** §3.3 refuses excessive explicit, YAML and built-in budgets, including default 512 under N-CAP. It requires known-capacity checks before conversion and complete final embedding-batch preflight before provider/storage effects. It does not silently reduce the chosen budget.

**C5:** §§3.1/3.3 assign counter/schema support to LLM and exact capability/tokenizer shipping or provisioned-root identity, hashes, licenses and headless availability to readiness/A2. They prohibit global-cache/first-use resolution, give headless callers Memory defaults and typed options, preserve existing MCP configuration, and prevent character settings from overriding/re-splitting common source plans. These requirements have owners and pre-generation timing.

## Fresh full F1–F8 assessment

| Area | Outcome and material evidence | Weighted contribution |
| --- | --- | ---: |
| F1 — flow/contracts/reuse | Satisfied. §§2, 3.1, 3.3 and 3.5 allocate conversion, neutral data, injected document planning, non-document strategies, preparation, complete validation and storage. Headless document proof closes the composition boundary; no new Tools↔Memory import is needed. | 1.90 / 2.00 |
| F2 — real file-command integration | Satisfied. §3.2 identifies actual default handlers and raw-tail handoff, opaque descriptions/options, line behavior, retained synchronous text/table APIs and truthful stored counts. §5 requires real registry-to-Chroma evidence, not helper-only routing. | 1.00 / 1.00 |
| F3 — policy/model limits | Satisfied. §§3.3–3.4 cover all-source document/512 defaults, independent precedence, three strategies, final prepared-input accounting, once-only roles, exact local counting and no second split. Smaller effective limits win; explicit contradictions and overflow refuse. | 1.45 / 1.50 |
| F4 — consumers/identity/upgrade | Satisfied. §3.4 preserves configuration/call shapes while enumerating six deliberate exceptions, fresh coherent namespace policy, query/document identities, strict recovery versions, public scorer/backup/MCP/task/multi-agent obligations and unwaived defects. Phase-map FC rows assign existing and later common-entry proof. | 1.90 / 2.00 |
| F5 — errors/lifecycle/bindings | Satisfied. §§3.1, 3.3 and 3.5 require complete extraction, typed refusals, whole-batch preflight, honest partial storage, destination/incarnation-bound receipts and worker quiescence. Read display and persistent ingestion have separate ownership/admission requirements. | 0.95 / 1.00 |
| F6 — packages/dependencies/unit boundary | Satisfied. §2, §4 and impact P-01–17 name eight implementation owners and nine indirect dispositions. Narrow counters, default-Chat document extras, bare-Tools behavior, shared lock/Certifi impact and conditional CLI origin changes have explicit responsibilities. Companion adoption remains separately activated. | 0.70 / 0.75 |
| F7 — meaningful acceptance/docs | Satisfied. §§5–6 require genuine formats/scanned input, stored content/provenance inspection, separate-process reopen, headless composition, failure/worker witnesses, normal/optimized installed profiles, substantive migration review and authored architecture/guide examples. Setup failures cannot count as negative controls. | 1.00 / 1.00 |
| F8 — sequencing/gates/handoff | Satisfied. §§1–2/7 and the phase map separate Q, I1, I2, I3, AG and UAT. Additive I1 preserves old preparations until coordinated I2 binding. Exact A2/A3 owner/file/case assignments precede generation/rewrites; missing assignments or unchanged-scope regression block the applicable exit. | 0.70 / 0.75 |
| Total | Eight areas complete; zero mandatory findings. | **9.60 / 10.00** |

## Mandatory gaps

**None identified.** No requirement/evidence/bounded-fix/acceptance finding is necessary on the current planning candidate. This does not certify that the future implementation will satisfy its gates.

The plan treats known feasibility uncertainties as blocking qualification decisions rather than hiding them: hosted immutable identity, hidden-row/column exclusion, real counter parity, production resource coverage and exact dependency/assets remain explicit Q duties. Readiness evidence is established input, while its limitations are preserved. Requiring these to be resolved before implementation is coherent; demanding their execution during this read-only document seat would exceed the assignment.

## Advisories and limits

1. **Make A2's output-publication and shutdown binding concrete.** Source shows command output is written by `app.py:500–506`, shutdown runs through `_shutdown_through_coordinator` and maintenance hooks, and `FrameworkAsyncClientLifecycle.close` currently closes LLM clients only (`adapters.py:144–150`). The proposed worker registry/drain is new work. A2 should show how the permitted registry/files/runtime/adapters seams participate in actual app shutdown and protect the completion-to-render interval. A helper's close method alone cannot satisfy the already-required actual shutdown witness. If exact scope cannot support the design, existing stop/scope reconciliation rules apply. This is an implementation-design checkpoint already required by §§3.2/3.5/4, not an additional council prerequisite.

2. **Preserve additive staging deliberately.** Existing LLM query caching and batch APIs and Chat's actual character slicing are real integration seams. `adapters.py:376–407` currently chunks and stores directly; `embeddings.py:249–325` batches documents and caches queries. I1's unchanged preparation/vector witnesses and I2's coordinated consumer switch are important safeguards. The specified gates are adequate, but staged implementation must not equate new contract tests with compatibility of these old callers.

3. **Keep composition and asset matrices explicit.** Existing smart_read has lazy large-file processing and separate small/large/cache paths. The directive correctly assigns their storage/cache adaptations to INGEST and document routing/selection to TOOLS-DOC. Exact future matrices should retain that distinction. Likewise CLI forwards resolved defaults into Runtime (`container.py:109–136`); the directive correctly requires an origin-preserving decision rather than assuming forwarding establishes explicit selection.

Overall deductions reflect the substantial remaining gated design/integration work and dependence on exact future bindings, not incomplete review coverage. Coverage scores this focused assessment's completeness. It does not measure every source method, runtime reliability, extraction quality, model relevance or all-platform support.

## Source, identities and read-only boundary

The request was hashed **before reading** and matched `eb0d88149a5b8bf3413b81ff9a2303e9baeb55063e14398c1af303fca7df09fe`. All nine required inputs matched their supplied identities at entry and exit. The correction brief was read before the target assessment; all required target/context/criteria/authorization, phase-map, companion, package-impact and readiness scopes were read. Ordinary output truncation was recovered by bounded reads of the package-impact rows and obligations. The optional REM was consulted only for concrete source-path ownership and its proposed implementation boundaries; its hash matched the request.

Targeted direct source scopes are recorded in `evidence.json`: Chat registry/files/runtime/adapters/app, Tools smart_read, CLI container, Core factory signature search and LLM embeddings. Failed guessed path lookups yielded only missing-path errors and were corrected; no product imports or execution resulted. No correctness credit is taken from controller structural checks, provenance labels, previous verdicts or peer material.

Entry and exit used bytecode-off Python and `GIT_OPTIONAL_LOCKS=0`; logical `git ls-files -s -z` SHA256 was obtained before status both times: `5dca109fa1fc88aa868e5efd2d9c761a810e994cb24840c181cffea33dab4f5b`. HEAD/branch matched the frozen candidate; staging was empty; status retained exactly the two dirty Chat example YAML paths and untracked `.friday-old/`. All eight declared metadata records and declared file hashes matched both the request and each other. Protected contents were not inspected; only authorized metadata/hash checks were performed.

No repository/supplied-input writes, full tracked-file rehash, admin suites, inventory reconstruction, tests/builds/imports/installations, network/model/store access, credential access, excluded Finance file, state-directory contents, memory/history/peer reviews, delegation or repairs occurred. Only fresh physical reviewer-owned external scratch was written. Lightweight evidence consists of `entry.json`, `exit.json`, `evidence.json` and `assessment.json` beside this report.

This single seat stops here. **VERIFIED grants no construction, effects, UAT, acceptance or delivery authority.** The controller owns any remaining authorized workflow.

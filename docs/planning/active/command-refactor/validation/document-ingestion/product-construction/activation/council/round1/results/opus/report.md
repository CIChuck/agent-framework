# INGEST activation-package council — round 1, OPUS seat

- Seat: opus (claude-opus-5-5), fresh read-only context, single pass.
- Candidate: `b04ab83afda313630eaaaa4e1dab09b71d9ce59c` on `feature/cmd-ingest-001`.
- Request SHA256 verified before reading: `5c23e6db…af50` (match). Brief SHA256 `784d0f97…2894` (match).
- **assessment_complete = true; areas_assessed = 8/8**
- **Verdict: CHANGES_REQUESTED**
- **Overall: 7.4 / 10** (weighted sum 7.4375, truncated, not rounded up)
- Mandatory findings: 4. Advisories: 7.

## Overall judgement

The package is unusually precise. The neutral Core values and protocols, error codes, canonical hashing (all five digest vectors recompute exactly under the stated canonicalization), namespace and v2 recovery rules, XLSX refusal, chunk policy and the 49-case and 40-witness test map would give a builder a clear basis for most work. The maintainer decisions to keep Docling, reject workbooks with hidden rows or columns, and use a shared worker are mostly carried through faithfully.

The removal of the model qualification has not been carried through, though. Each of its three updated documents carries a banner calling RD-01/RD-05 "superseded background". Yet the README's next action, the readiness checkpoint, the validation plan and an I3 acceptance witness still require hosted-identity and actual-serving parity evidence. The capability-record contract also makes every guarded embedding path depend on that evidence once I2 runs. In addition, the worker "RD-03 qualification" is set before activation for a worker that does not exist until I3. The Runtime half of the shared-worker ownership also has no signature. These issues would misdirect a builder or controller, so the package is not ready for VERIFIED.

## A1–A8 assessment

| ID | Weight | Score | Contribution | Evidence |
|---|---:|---:|---:|---|
| A1 Decisions, scope, readiness honesty, stale prerequisites | 1.50 | 6.0 | 0.900 | Decision records and approval-binding gates state the removals correctly and honestly (`product_generation_allowed: false`). But removed parity/identity work is still operative in the README "Activation status and next decision", readiness RD-01/RD-05 and "What can proceed now", validation-plan l.31, and the I3-C2 witnesses (M1). RD-03 is a pre-activation gate (M3). |
| A2 Neutral values/protocols, data flow, identity | 1.75 | 7.5 | 1.3125 | §1–2 field, invariant and signature tables are exact. Injection avoids Tools→LLM and Memory→Tools imports. Plan/receipt/space hashing is consistent and the vectors verify. But the `EmbeddingSpaceIdentity` "independently qualified" rule and the capability record's `parity_evidence_sha256` / `serving_identity_evidence_sha256` with "Null evidence is unqualified" re-bind the removed campaign (M2). |
| A3 Shared process, concurrency, cancel/timeout/shutdown, headless reuse | 1.75 | 7.5 | 1.3125 | Strong design: one active plus one queued request, `worker_busy` before I/O/spawn, queued cancel never starts, 300 s deadline / 2 s grace / kill / join, `worker_not_quiescent`, typed progress, no frontend imports, a renderer-free consumer, and app.py publication-boundary reasoning with a stop rule. Gaps: the Runtime construction/injection seam is unspecified (M4), and the acceptance timing for resource feasibility is circular (M3). |
| A4 Consumer compatibility, config/call shapes, safeguards, fresh store, recovery | 1.50 | 6.5 | 0.975 | Legacy signatures and v1 models are retained. Optional config keys are additive, I1 legacy paths stay unchanged, admission comes before any client effects, and the strict v1/v2 combinations are well bounded. But I2 removes the unguarded branch, and a missing or unqualified record then refuses before provider I/O. Without the removed parity/serving evidence, existing default consumers either refuse or need the removed campaign (M2). |
| A5 Slice/file/test/helper assignments, coverage, installed acceptance, docs | 1.25 | 8.5 | 1.0625 | The file map's 91 exact paths with owner, slice and exit match their stated existence. Unlisted tests are retained by default; fixtures are synthetic, opt-in and enumerated. The offline/non-default/excluded selectors are explicit, the installed probe runs in normal and `-O` modes, and docs work requires real authoring. Deductions: the I3-C2 parity assertion (M1), and several witnesses share boilerplate assertions (advisory). |
| A6 Format refusal, chunking/capacity, errors, partial effects, no false success | 0.75 | 9.0 | 0.675 | XLSX refusal comes before conversion, with a stable code, sideband counts and no hidden values. Budgets refuse rather than clamp. There is no overlap, coverage is exact, and an indivisible unit is refused. A receipt is issued only after readback; partial/unconfirmed IDs are kept separate. Errors are safe. |
| A7 Packages, dependencies, assets, profiles, TOOLS-DOC boundary | 0.75 | 8.5 | 0.6375 | Package owners are clear and the extras are narrow (`tokenizers==0.23.3`). Assets come from a manifest under an explicit root with no fetch or global cache. Read-only work does not need the counter. The Certifi floor and TOOLS-DOC/TM-03 separation are kept. The hosted counter is "only if separately qualified", which is acceptable once M2 is reconciled. |
| A8 I1/I2/I3 sequencing, intermediate compatibility, approvals, handoff | 0.75 | 7.5 | 0.5625 | The I1 additive → I2 coordinated switch → I3 sequence is buildable. Per-slice approval and independent validation, AG and then UAT are stated. Deductions: the README next step points at the removed campaign, and the RD-03 gate has no feasible owner or timing (M1, M3). |
| **Total** | **10.00** | | **7.4375** | |

## Mandatory findings

### M1 — Removed parity/identity qualification is still operative in current next-step and acceptance text

- **Evidence:**
  - README "Activation status and next decision": "A1 still needs … actual qualified asset/serving records and its required independent readiness gate" and "the next bounded preparation is to resolve the explicitly named Q facts, starting with hosted identity feasibility". "Scope" also says "A post-qualification revision".
  - readiness-disposition: RD-01 is "Open: actual identities and B/N qualification … Check B02 hosted immutable identity first", and RD-05 is "Open: immutable serving identity and boundary parity". "What can proceed now" says: "The first independent readiness checkpoint is B02's immutable hosted identity, followed by the actual B/N identity/counter binding."
  - validation-plan: "A separately approved actual-serving window supplies Q parity/identity facts." This file has no override banner.
  - test-case-map and slice-file-map, I3-C2 witnesses `test_headless_common_plan_and_destination_bound_receipts` and `…uses_injected_tools_planner`: "Apply DI24 offline asset-root and actual-serving parity qualifications".
- **Violated requirement:** Preserved decision 2 and model-qualification-decision.md: the campaign is not to be reintroduced under another gate or moved after coding. Brief A1 also requires removal of stale or contradictory prerequisites. A banner calling clauses "background" does not neutralize next-action and acceptance clauses, and the validation plan and maps carry no banner.
- **Bounded fix:**
  - Rewrite or strike those clauses.
  - Set RD-01/RD-05 dispositions to "removed by maintainer decision; runtime guards and ordinary compatibility tests retained".
  - Replace the README next step with the actual remaining preparation (asset/record provisioning, M3/M4 items, A4/A5 binding).
  - Replace the I3-C2 parity wording with offline exact counting plus runtime overflow/response validation.
  - Add one explicit reconciliation of the directive's DI-24 "actual boundary parity" (directive l.457) to that retained scope.
- **Future acceptance:** No I1–I3/AG exit may require actual-serving parity or hosted immutable-identity evidence. I3-C2 passes on offline counting and runtime guards.

### M2 — Capability-record and identity semantics make I2 depend on the removed evidence

- **Evidence:** shared-contracts §1 `EmbeddingSpaceIdentity`: "Model/artifact identity must be independently qualified". §3 requires the record fields `parity_evidence_sha256` and `serving_identity_evidence_sha256`, and states "Null evidence is unqualified" and "Its exact serving behavior must be qualified". §2 says I2 "removes the internal unguarded branch: missing resolved capability then refuses before provider/cache effects … Never invent a record from a mutable model name."
- **Violated requirement:** Decision 2 (no substitute gate) and A4 existing-consumer compatibility. As written, after I2 every maintained embedding consumer, including the current default Nomic configuration, either needs serving-identity/parity evidence (the removed campaign) or refuses all embedding. It is unclear which.
- **Bounded fix:** Define the admissible record after the decision:
  - Which fields are required and which are optional or informational (for example, evidence hashes nullable without being disqualifying).
  - What `artifact_identity` means for a hosted model without immutable serving evidence (for example, a declared configured identity, where any change is a new space).
  - That runtime pre-provider counting, response index/dimension/finite checks and namespace space admission are the enforcement.
  - Who provisions the record for existing configured models, and in which slice.
- **Future acceptance:** I2-C1/C2 show existing default and pool configurations operating positively from a provisioned record without parity evidence. Overflow, foreign and changed-space cases still refuse.

### M3 — RD-03 worker qualification is set before activation for a worker first built in I3

- **Evidence:** readiness-disposition l.29 says it "still requires resource/spawn/timeout qualification in RD-03". The RD-03 row is "Open … Qualify the proposed worker … cold/warm resource limits, spawn/IPC … 300-second deadline and two-second terminate grace". The numeric section says "qualify this exact interpretation before activation" and leaves memory/startup/IPC ceilings as an "evidence field, not an invented value". shared-contracts §4 says it is "subject to RD-03's measured feasibility before activation" and "require[s] RD-03 proof". The file map creates the worker at I3-C1/C4.
- **Violated requirement:** Decision 5: timing must be feasible and non-circular, completed worker code may not be required before its creation is authorized, and any pre-coding experiment must name a specific unresolved risk. A gate needs an owner, an artifact and feasible timing.
- **Bounded fix:** Rebind RD-03 as I3-C4 implementation acceptance, with explicit pass criteria (deadline, grace, kill/join, busy/queue, quiescence, no late output) plus measured startup/RSS/IPC values recorded against a maintainer-chosen or stated envelope. Alternatively, name one bounded pre-coding spike with its specific unresolved risk, owner and artifact. Remove "before activation" wording elsewhere.
- **Future acceptance:** The I3-C4 headless worker witness carries those thresholds. Activation does not wait on a product worker that does not yet exist.

### M4 — The Runtime half of shared-worker ownership has no construction or injection contract

- **Evidence:**
  - shared-worker-decision: "Runtime/composition roots own shared service lifetime … DIContainer.shutdown drains its owned converter/session service".
  - file map, `friday_runtime/di.py` I3-C4: "Own and drain the same injected … service".
  - shared-contracts §3: Runtime gains no document YAML. §2 claims "Signatures are exact".
  - Source check: `DIContainer.__init__(config, memory_profile)` has no service slot, and `shutdown()` only stops `mcp_provider`. Chat composes its own service and does not use DIContainer; it drains via `FrameworkAsyncClientLifecycle`.
- **Violated requirement:** Brief A3 (shared process ownership and headless CLI/Runtime reuse) and "unclear owners". A builder must invent:
  - how a `DocumentConverter` (with `assets_root` / `profile_id` / manifest) reaches DIContainer or RuntimeKernel;
  - whether Runtime constructs it or only adopts it;
  - drain ordering relative to MCP stop;
  - whether Runtime exposes an `IngestionEntry`.
- **Bounded fix:** Add an exact keyword-only injection or registration signature, the ownership-transfer rule (caller constructs; once injected, Runtime closes it idempotently), the drain order, the no-asset-config statement, and the headless composition path for CLI/Runtime consumers.
- **Future acceptance:** `tests_runtime/test_di.py::test_shutdown_drains_shared_document_worker` binds to that signature.

## Advisories (non-blocking)

1. The Office decision requires read-only `/read` to report `unsupported_workbook_visibility` without claiming an ingestion attempt. No witness names that read-only path explicitly.
2. State the oracle role of `hidden-units.xlsx` under the new policy (hidden-sheet-only success control or refusal case) to avoid a conflicting I3-C1 oracle.
3. In §4, "spawned process" alongside "launch with subprocess `env`, not parent `os.environ` mutation" should name the mechanism, for example asyncio subprocess plus defined IPC framing. multiprocessing `spawn` cannot take a per-child env without mutating the parent's environment.
4. slice-file-map uses `mode: "edit"` for seven paths with `exists_at_preparation: false`. A `new` mode would be clearer.
5. The activation-gate labels A1–A5 collide with council areas A1–A8 and with "A2 = shared contracts". Disambiguate.
6. Several witnesses (for example, the three I3-C3 Chat read witnesses) share one generic assertion string. Per-node specific assertions would make validation sharper.
7. The README/readiness banners could list exactly which superseded clauses they cover rather than "RD-01/RD-05 descriptions below".

## Source/boundary checks and limits

- **Entry and exit (identical):** logical index (`git ls-files -s -z`) SHA256 `ef217e83…618a` was taken before status. HEAD `b04ab83a…`, branch `feature/cmd-ingest-001`, status exactly the expected three lines, nothing staged. All 8 preserved entries matched mode, size, mtime, ctime and birthtime, plus SHA256 where declared. All 13 required inputs, 10 optional references and controller-checks hashes matched. `GIT_OPTIONAL_LOCKS=0` and `PYTHONDONTWRITEBYTECODE=1` were set.
- **Read in full:** request, brief, authorization.json, current-controls.json, README, shared-contracts, readiness-disposition, validation-plan, approval-binding, and the three decision records.
- **Inspected:** slice-file-map (all source/doc rows in a focused view; existence cross-checked), test-case-map (metadata, modules, helpers, fixtures, all 40 planned witnesses, one sample mapped case — not all 49 bodies individually) and digest-vectors (all 5 recomputed with stdlib only).
- **Targeted source reads:** `friday_runtime/di.py` (DIContainer init/shutdown), `friday_chat/adapters.py` (FrameworkAsyncClientLifecycle) and a grep of `friday_llm/embeddings.py` signatures. Directive: one grep for DI-24/parity.
- **Not done:** no product imports, tests, builds, installs, network, model or store calls. No AST or inventory rebuild, harness replay, or reading of prior or peer reports, memory, or dirty YAML/state/.friday*/exports/.venv contents (hash/metadata only). Finance `test_integration_massive.py` was not opened. Nothing was written to the checkout. No delegates.
- **Limits:** Mapped-case bodies were not each re-verified against inventory definitions. Parent directive/REM clauses were consulted only for DI-24.
- **Scratch:** `/private/tmp/claude-501/-Users-chuckrussell-Dev-gendev-agent-framework/ddcbb487-0b30-46ab-bf20-db19bfc441b8/scratchpad/opus-seat-r1/` (external to the checkout).

This document review grants no construction, effects, UAT, acceptance or delivery authority. This seat stops here.

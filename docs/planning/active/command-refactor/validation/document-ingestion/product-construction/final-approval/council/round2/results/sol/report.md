# SOL final INGEST document council — round 2/2

Reviewer: fresh SOL read-only seat, gpt-6.1-sol, high effort; 2026-11-13.
Candidate: `b4eecbe804b862f606995c4c4e5197c9b9d37150`, branch `feature/cmd-ingest-001`, workdir `/Users/chuckrussell/Dev/gendev/agent-framework`. Declared base: `b0d166256015b090b4a5082389b1b4f47835d1a2`.

**Aggregate: CHANGES_REQUESTED. assessment_complete=true; areas assessed=8/8; mandatory findings=1; overall=9.5725/10.** The numerical target is met, but the mandatory consistency finding prevents VERIFIED. This is a document readiness judgment, not implementation conformance or maintainer acceptance.

## Correction assessment first

**C1 — satisfied.** README lines 81–91, impact lines 206–216, approval-request phase_dependency_checks and execution-profile dependency_policy consistently distinguish the actual Certifi baseline from the planned upgrade. Targeted standard-library parsing of uv.lock confirms 2025.11.12; root/package metadata contains no direct Certifi declaration. I1/I2 record the installed locked version, module and CA origin, or explicit absence in dependency-free profiles, without enforcing the later floor prematurely. Tools/Docling introduces selected 2026.10.23 and floor >=2026.10.19 at I3-C1. Enforcement continues after every applicable private install, including final normal/optimized headless and Chat lanes containing Certifi. Profiles lacking it record absence without installing it just to satisfy a check. HTTPS consumers inherit the shared change while TLS verification remains required. These are clearly future execution duties, not falsely claimed installed results.

**C2 — satisfied.** README lines 76–80 and impact lines 197–205 expose tokenizers 0.22.1→0.23.3 as a shared-lock consequence at I1-C2. Targeted lock parsing confirms current tokenizers 0.22.1 and both Chroma and LiteLLM dependency edges. The profile repeats the paired unchanged-legacy requirement and stop on incompatible intended resolution. The case map explicitly assigns `test_i1_legacy_inputs_vectors_and_cache_are_unchanged` to I1-C2 and separately preserves legacy preparation, vectors, roles and cache behavior in its qualified-boundary witness. This is adequate assignment of future positive evidence; no product replay is necessary for this document decision.

**C3 — satisfied in its substantive corrections, with the separate A4 consistency defect below.** README lines 127–131 prominently require the embedding manifest/API binding and local counters for recall, extraction and ingestion even with fresh stores. Lines 36–42 explain phase activation beneath the already-started initiative without recycling its old authority. The presentation receipt names content commit `115e4cecdb659d2af043c11e73964aca0a590d78` and the exact approval-request digest. Read-only `git show <named-commit>:<path>` reproduced all four hashes and matched current files. The request points to the receipt without embedding its hash; the pinned review request supplies that external binding, avoiding a self-hash cycle. Later metadata does not invalidate unchanged document bytes. No construction authority was inferred.

## Per-document disposition

- **Final approval README v2: CHANGES_REQUESTED as an approval assembly.** Its prose is clear and appropriately bounded, but it delegates the exact gate to an inconsistent current approval-request JSON. Finding SOL-FD-001 applies to that linked assembly, not to a missing runtime implementation.
- **Canonical package impact v0.8: VERIFIED within this document review.** All 17 rows, eight implementation owners, nine source-unchanged consumers, dependency consequences, operator prerequisites, migration duties and delivery boundaries are sufficiently explicit. This does not approve construction.
- **approval-request.json: CHANGES_REQUESTED**, for SOL-FD-001 only. **execution-profile.json: VERIFIED as a proposed profile**, with no effects performed or activated.

## Complete weighted matrix

Contributions are rating × weight /10. Weights total 10. The sum below is exact; there is no seat averaging, upward rounding or separate numerical coverage score.

| Area | Weight | Rating /10 | Contribution | Assessment |
| --- | ---: | ---: | ---: | --- |
| FD1 | 1.50 | 9.8 | 1.4700 | Coherent current decisions; separate TOOLS-DOC; no revived parity/vendor campaign or new frontend. |
| FD2 | 1.75 | 9.8 | 1.7150 | Complete package/operator impact, correct baseline and planned dependency deltas, explicit positive compatibility duties. |
| FD3 | 1.25 | 9.8 | 1.2250 | Neutral shared ownership, independent read, same-entry functional late attachment and owned shutdown are accurately conveyed. |
| FD4 | 1.50 | 9.7 | 1.4550 | Two independent bindings, retained selection/pools, optional fields, fresh-layout policy and configured-identity limits are clear. |
| FD5 | 1.50 | 9.0 | 1.3500 | Phase order and effects are actionable, but A4's wrong impact version contradicts the approval target. |
| FD6 | 1.00 | 9.0 | 0.9000 | Exact content binding and phase paths match; current gate metadata still contains SOL-FD-001. |
| FD7 | 1.00 | 9.8 | 0.9800 | Traceable case preservation, offline exclusions, substantive authored documentation and independent code review are assigned. |
| FD8 | 0.50 | 9.5 | 0.4775 | Human request and practical upgrade consequences are understandable; the linked gate label needs reconciliation. |
| Total | 10.00 | | **9.5725** | **CHANGES_REQUESTED** |

FD1–FD4 evidence includes the impact's ownership tables and cross-package effects, current requirement reconciliation, shared-contracts signatures and resolver rules. Core holds neutral contracts; Tools owns conversion/processes; Memory owns ingestion/storage policy; LLM owns preparation/counting/embedding guards. Chat and Runtime reuse those services. `/read` needs no embedding setup or Memory lease. The factory requires its counter factory from the outset; actual text ingestion followed by document ingestion through the identical entry is expressly required. Worker resource/cancellation/reap criteria belong to I3-C4 after construction. None becomes an absent pre-coding prerequisite.

FD4 also preserves ordinary model YAML/pool/resilience choices while requiring explicit provisioning. Exact manifest resolution does not guess paths or silently fall back. Missing bindings refuse affected operations. Fresh vector/graph/configured-WAL targets must be absent; identity-free stores are not stamped or migrated. Runtime root effects on transcripts/artifacts and old-release recovery are disclosed. Configured identity cannot attest an undeclared server alias change. Those limitations are described honestly.

For FD5–FD7 I checked the JSON phase paths against the selected map: all three sets match exactly. The map contains 91 paths; the case map contains 49 old-case exceptions, 51 planned witnesses, 18 classified modules and zero retirements, matching the assembly. Default retention and helper restrictions prevent blanket rewrites. The Finance live integration path is excluded; offline Finance and Transcript selectors are explicit. Synthetic fixture oracles, registry/store readback, installed normal/optimized acceptance, substantive guide/architecture/README authorship and independent content review are future gates. Counts and link checks are not treated as behavioral proof. The proposed private profile binds stable exports, artifacts, local assets, selectors, origins and owned paths before effects, with offline tests and only named local fixture servers.

## Mandatory finding

**SOL-FD-001 — medium; approval gate names the wrong current impact revision.**

Location: `final-approval/approval-request.json:283`, `gate_disposition.A4.requires`: “Chuck approves this request SHA256 at its presented commit and impact v0.7.” The same JSON's request at line 9 says v0.8 and current_package_impact identifies version 0.8 with its correct digest. Both primary documents present v0.8. A4 is an operative future approval condition, not a historical caption. The common brief's FD5/FD6 requirements demand a noncircular, actionable, internally consistent approval assembly. Those requirements remain violated even though the correct target is recoverable from the hashes.

Risk is limited to approval interpretation and recording: an operator must choose between the stated A4 version and the explicitly pinned current version. This is not evidence of an incorrect hash, unsafe executed effect or flawed ingestion design. It still requires reconciliation before the assembly is declared ready for exact approval.

Bounded fix: change A4's required impact revision to v0.8, or reference the current_package_impact version and digest unambiguously. Refresh the affected request digest and presentation receipt against the resulting content commit, plus controlling pins as required. Preserve the substantive C1–C3 content and unchanged technical scope. No product/test/guide implementation or new council is requested by this finding.

Future proof: verify the corrected A4 target agrees with current_package_impact and the two documents, and verify all four presented document hashes at the newly named content revision before recording approval. Existing hashes cannot attest changed request bytes. This report authorizes neither those edits nor a third round; it reports the bounded correction needed for a later maintainer decision.

## Advice, checks and limits

Optional advice: future phase receipts should make Certifi absence and installed version/module/CA origin separate explicit fields so reviewers can distinguish “not installed” from a missing check. The current prose already requires this distinction; no additional schema or harness is a prerequisite.

First operation used Python standard-library SHA256 on the external request before parsing it, obtaining required `aef9c61c5183c75900feb9323f0a9bc4103657d413a65c97be899a6c9c79d048`. Entry/exit evidence records logical index before status, exact HEAD/branch/status/empty staging, required input pins and all eight preserved metadata/hash records. Optional input pins and controller checks were hashed; controller contents and historical/peer verdict bodies were not read. Policy and required target text were inspected, including allowed historical references; earlier verdicts supplied no correctness proof.

Methods were Python standard-library reads/hashes/JSON/TOML, read-only Git, and scoped text reads/searches. Git optional locks and bytecode were disabled for boundary operations. Truncated combined target output was recovered with bounded reads. No product imports, tests, builds, installs, network, model/provider/store operations, Finance live-test reads/parsing, dirty YAML parsing, history search, nested agents or repository writes occurred. Preserved files were hash-only and preserved directories stat-only, without traversal. No vendor/platform feasibility or product performance claim is made. The scope was document completeness, consistency and decision readiness. This seat stops after this final pass; no repair, replacement, further round, acceptance or delivery authority follows.

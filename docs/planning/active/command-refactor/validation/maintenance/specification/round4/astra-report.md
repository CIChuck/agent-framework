# MAINT-001 round 4 independent specification/directive readiness review

**VERIFIED — 9.6/10. Mandatory findings: none.**

Reviewer: GPT-6 Astra, high reasoning effort. Date: 2026-11-10. This is this reviewer's independent seat, not an aggregate council result. The score assesses specification and construction-directive readiness only. No implementation conformance, construction activation, human acceptance, or delivery authority is granted by this result.

Candidate: `2b0850bfe6cfc6a91d744fa4440a40eaadaf3a60`; branch: `feature/command-retirement`; workdir: `/Users/chuckrussell/Dev/gendev/agent-framework`.
Revision base: `294437ebddcfada2ef072f872c4e5ba08d2156d2`. Aggregate base: `1093aff80cb17ff9c946b4a8a127fd2163f9f151`.

The request was SHA256-verified BEFORE reading it: `21ad93bc05b054f3a96f97bb434afa8f13eafd4442d9d942f59214db93a23ddf`, at `/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-round4-request-m4u9sbpw/review-request.json`.

Private scratch: `/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-r4-astra-review-986o3bc0`.

The explicit shared-checkout exception was used. No checkout/worktree was created. All generated artifacts were written exclusively in this fresh scratch. No delegation, repair, repository writes, staging, commits, providers, network, tests, builds, or personal-store operations occurred. Protected files were read as bytes solely for mandatory hash checks; their contents were not displayed. Peer reports/evidence and excluded authority/README/log/next/tactical documents were not opened. Historical review references embedded in the required full directive were not used as correctness evidence. No prior memory-derived verdict was used.

The safe three-path delta and new vector/conditional-approval contents were reviewed first, followed by the complete specification/directive, allowed governance instructions, preparation hash/baseline maps, and relevant source. Only names were inspected for broader delta preservation checks; no whole-packet content diff was displayed.

## Mandatory findings and bounded mitigation

None. No corrective construction or document change is required by this review. Runtime proof remains due at the separately specified implementation gates; its current absence is not a document-readiness failure.

## Optional improvement

1. **A4-A01 — add a future non-empty created-selection literal vector.** Directive lines 74–79 preserve ordered selection references, while lines 244–251 sort the separate effective-reference list. The two current vectors satisfy the requested Unicode/unsorted-pending and exact-empty-created cases. A third vector could make the distinction between ordered `selection.references` and sorted effective `references` especially easy to audit, using intentionally different orders. This is optional because the present canonicalization rule is concrete and behavioral coverage is already mandatory. Do not regenerate current expectations or change this frozen candidate merely to pursue a score.

## Criteria matrix

References below: **S** = `docs/planning/active/command-refactor/maintenance-reorganization-specification.md`; **D** = `docs/planning/active/command-refactor/directives/CD-CMD-MAINT-001-reorganization-order.md`; **A** = `docs/planning/active/command-refactor/approval/maintenance-reorganization-conditional.md`; **V** = `docs/planning/active/command-refactor/validation/maintenance/selection-digest-vectors.json`. PASS means document readiness, never implemented behavior.

| Criterion | Result | Independent evidence and assessment |
|---|---|---|
| MC-01 | PASS | A:8–37 binds exact hashes and conditional activation; D:18–50,719–728 bounds scope. Current approval expressly governs historical proposal labels. Review does not activate implementation; controller must record exact candidate/reports/integrity and activation. |
| MC-02 | PASS | S:64–94; D:153–228,320–391 place order, skips, assessments, lifecycle and postconditions in Memory. Chat delegates one execute call and retains cross-store transaction safety. Existing Chat policy seams are directly named for removal. |
| MC-03 | PASS | D:52–151,163–253,279–318,328–354 define strict models, operation lifecycle, command selection binding, receipts, provider contracts and generic boundary. Memory-to-Chat/Commands dependency is forbidden. Existing strict Memory models and LLM dependency support the proposed extraction. |
| MC-04 | PASS | S:33–62,154–177; D:94–146,320–326. Pending retains uncertain/old-meta/non-source coverage; synthesis replans afterward; second pass consumes only the registered created batch. Empty and migration-only success are explicit. Existing Memory selector at mutation.py:749–769 and migration/apply paths support these seams. |
| MC-05 | PASS | D:393–416 and named test at 572 distinguish provider-free preview, static verification configuration, conditional future-output checks, and real three-role assessment. D:328–339 preserves strict decoding and diagnostics. Current Chat decoder at mutation.py:243–309 and assessment at 785–959 are separable without changing policy. |
| MC-06 | PASS | S:179–203; D:215–228,289–318,356–391,477–512. Per-stage default/injected drain, callback aborts, outer rollback, final shared postconditions and recovery failure precedence are specified. Existing coordinator snapshot-before-mutation and rollback paths provide the retained envelope. |
| MC-07 | PASS | S:125–152; D:94–102,418–445,454–512 require final persisted judge counts, unavailable failed/legacy counts, content-safe immutable sidecars, unchanged journal/bundle v1 and audited fixture relocation. AtomicJsonStore.write_model already supports require_absent and constrained atomic writes. |
| MC-08 | PASS | D:514–558 exact product/test allowlist covers observed extraction seams, registry, lifecycle methods, fake runtime reports, artifacts and public maintenance exports. Memory already depends on its LLM/core packages; no hidden dependency/config/lock change is indicated. Future unexpected seams explicitly require stopping. |
| MC-09 | PASS | S:228–240; D:560–703 specify named real-flow tests, one-call Chat spy, complete no-Chat headless execution, negative controls requiring call-phase assertion witnesses, source/origin checks, private offline commands, clean builds/replay, installed normal/optimized proof, and later human UAT. These are assessed obligations, not executed receipts. |
| MC-10 | PASS | S M-01..05/MT-01..09 and D D1/D1b/D2 agree on technical behavior and ownership. A explicitly supersedes historical authorization labels. Concrete signatures, file boundaries, compatibility strategy, failure paths and stop conditions are sufficient for bounded construction. |
| MC-R01 | PASS | D:289–318 and test obligation 575 require a single owned worker, shielding/draining under repeated cancellation, worker-error precedence, no next stage, cleanup only after settlement, both default/injected paths, graph/lifecycle suspension after a write, and outer restoration. Current coordinator helper and repeated-cancel test are feasibility evidence only. |
| MC-R02 | PASS | D:175–199,230–253,279–287,462–492,576 bind operation/ordinal/stage/actual plan/selection, define nullability, canonicalization and before/planned/after transport, preserve planned scope on post-plan failure, reject substituted receipts, and copy Memory facts into durable evidence. Exact-empty and migration-only obligations are named; sidecar failures cannot prevent restoration. |
| MC-R03 | PASS | Both base-to-candidate name-only comparisons contain planning paths exclusively. All 812 preparation product-map hashes match current bytes; protected dirty work remains unchanged. Current A governs activation; historical preparation authority/status fields were not used. |
| MC-F01 | PASS | D:244–275,532,569; V:7–53. Independent reference computation matches both literal canonical byte strings and SHA256 values, cross-checked with shasum. Exact package-local fixture copy is allowlisted; production expectations cannot be regenerated. Headless/installed probes use the same vectors through installed modules with hash-verified external fixture input; runtime tests avoid planning dependencies. |
| MC-F02 | PASS | A:22–37 and D:719–728 require both named fresh reviewers VERIFIED, each independently >=9.5, no mandatory findings, no averaging/rounding/substitution/provisional scores or threshold-chasing loops. Failing or missing seats stop advancement. This report cannot establish the other seat's result. |

## Source feasibility evidence

`packages/friday-memory/src/friday_memory/maintenance/mutation.py`: strict base/reference/plan models at 44–178; existing pending selector and side-effect-free planner at 749–923; freshness re-plan, actual additions, migration writes and failure result at 1095–1276; shared persisted postconditions at 1278–1444. Generated outputs already carry maintenance provenance and unverified status. Existing final-verdict mapping across command receipts supports preserving both verification passes instead of overwriting earlier commands.

`packages/friday-chat/src/friday_chat/reorganization/mutation.py`: provider decoder at 243–309, preflight at 623–708, and synthesis/three-role/reembedding construction at 785–959 locate the bounded extraction. The judge response supplies persisted verification updates. Provider transport/configuration can stay in Chat while schema/coverage/assessment logic moves.

`packages/friday-chat/src/friday_chat/reorganization/coordinator.py`: 700–920 demonstrates verified snapshots and journal mutation boundary before its current per-step loop and final postconditions; 1868–1893 implements the existing shield/drain helper. The proposed single pipeline call fits inside that envelope. Existing repeated-cancellation coverage at `tests_chat/test_reorganization_coordinator.py:690–723` was read, not run, and does not itself prove the new default headless boundary.

`packages/friday-chat/src/friday_chat/adapters.py:767–833` contains the two bounded promotion/decay methods; `runtime.py` contains the corresponding report annotations/fakes. `reorganization/durability.py:198–240` exposes the atomic, require-absent writer needed by new sidecars without changing the recovery schema. `commands/registry.py:1246–1325` has localized duplicate/conflict/full-only parsing suitable for explicit `--full`.

Existing migration-only test at `packages/friday-memory/tests_memory/test_maintenance/test_mutation_participant.py:323–361` and disposable recovery setup at `tests/integration/reorganization/test_reorganization_recovery.py:453–510` demonstrate available fixture seams. No test outcome is inferred from their presence. Package metadata confirms Memory already depends on core and LLM; no runtime fixture packaging is needed.

## Executed versus inspected

Executed only read-only Git identity/status/name-delta commands, filesystem reads/hashes/metadata checks, and standalone standard-library JSON/hash reference calculations. All Git subprocesses inherited `GIT_OPTIONAL_LOCKS=0`.

- Request hash verified first with `shasum -a 256`.
- `audit.py opening` and `audit.py closing`: exact `git ls-files -s -z` stdout SHA256 computed BEFORE `git status --porcelain`, then HEAD/branch/staging, protected manifest, request pins and preserved metadata checked.
- Protected manifest SHA256: `82a5d911938ac92cc9a95ec7cefe379d3f3a03c53e5ee1d799bcfc26d0d688c1`.
- Preparation maps: all 812 baseline product hashes and 14 pins matched. Excluded pinned document contents were hashed, not displayed or interpreted.
- Revision delta: 11 changed paths, all planning. Aggregate delta: 23 changed paths, all planning.
- `pending-unicode`: 371 canonical bytes; SHA256 `082bc35dabb55d3e8101ce346e3039f109bd5f115c1f2e2286e4b36cc84175d9`.
- `created-exact-empty`: 368 canonical bytes; SHA256 `5502c0e7fd37ef3077ca2d9518b6f254dc7be04f8fd33844a8a20969314035b0`.
- Both canonical byte strings matched literals and both hashlib digests matched independent shasum. Reference sensitivity calculations distinguished changed operation/stage/plan/ordinal, key order and newline; pending additionally distinguished Unicode escaping, effective-reference order and changed reference. These are reference-data computations, not production mutation tests or proof that future validators reject invalid inputs.

Inspected only: source/test seams, policy/doc contracts, future validation argv and test obligations. No runtime imports, pytest, lint/type runs, build/install, network/offline harness execution, live provider, personal-store inspection, prior receipt reproduction or human UAT occurred. Tool caches from product tooling were not created. The final file-discovery command returned exit 1 because no additional AGENTS.md files matched beneath packages/tests/scripts; it was not a product-check failure.

## Opening and closing integrity

Both boundaries matched the request with zero discrepancies:

- HEAD `2b0850bfe6cfc6a91d744fa4440a40eaadaf3a60`; branch `feature/command-retirement`.
- Logical index SHA256 `960baa24a25bd8fbc9761f9e38ba9f99ea8355b9d2d09caa8a542aef36412fa3`, computed from exact NUL-delimited index listing before status at each boundary.
- Status unchanged: modified `packages/friday-chat/config.example.yaml`, modified `packages/friday-chat/models-config.example.yaml`, untracked `.friday-old/`.
- Staged diff empty.
- All 17,446 protected-file content hashes and all 12 request pins matched.
- All six preserved metadata records matched, including mode, size, mtime_ns, ctime_ns and SHA256 where supplied.

Receipts: `opening-integrity.json`, `closing-integrity.json`, `preparation-checks.json`, `vector-checks.json`, `vector-sensitivity.json`, and the two `delta-*.json` name inventories in this scratch. The audit script is retained for reproducibility. No repository-side preservation discrepancy was observed.

## Score rationale and limits

**9.6/10** independently reflects complete bounded ownership, explicit safety/receipt contracts, concrete file and proof boundaries, correct independent fixed vectors, and an unambiguous two-seat conditional gate. The remaining design risk is implementation complexity across cancellation, observer persistence and application recovery; it is explicitly bounded and assigned meaningful future proof. The optional additional vector would improve audit convenience but is not a missing requirement. This score is neither an average nor a carried-forward score and was not rounded to satisfy the gate.

The review establishes document readiness at this frozen candidate only. It does not demonstrate runtime correctness, artifact reproducibility, provider readiness, UAT success or acceptance. Controller advancement still requires the independently passing Sol seat and exact recorded activation under the current conditional approval. No automatic follow-up council or implementation work was started.

# MAINT-001 round4 independent document-readiness review

**Outcome: VERIFIED. Independent score: 9.6/10. Mandatory findings: none.**

Reviewer: GPT-6.1 Sol / high. Date: 2026-11-10. This is the Sol seat's fresh independent read-only specification and construction-directive readiness review. It is not implemented-product conformance, an aggregate council verdict, construction activation, human acceptance or delivery approval. No other reviewer was consulted or delegated to.

Candidate: `2b0850bfe6cfc6a91d744fa4440a40eaadaf3a60`; branch `feature/command-retirement`; workdir `/Users/chuckrussell/Dev/gendev/agent-framework`. Revision delta base: `294437ebddcfada2ef072f872c4e5ba08d2156d2`. Aggregate documentation base: `1093aff80cb17ff9c946b4a8a127fd2163f9f151`.

## Inputs, independence and conduct

The first command verified request SHA256 `21ad93bc05b054f3a96f97bb434afa8f13eafd4442d9d942f59214db93a23ddf` at `/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/maint-round4-request-m4u9sbpw/review-request.json`. The request was then read and followed. The opening boundary preceded review content. The safe three-path delta was displayed first, including the new vectors and conditional approval; full specification/directive and relevant baseline source followed. No whole-packet content diff, linked prior review, peer output, authority/README/log/next/tactical content was read as review evidence. Embedded historical references in the permitted directive were not used to infer correctness or scores. V4 preparation was inspected only for its key names and baseline file map, with its whole contents hash-verified. No prior-memory lookup or builder transcript supplied correctness evidence.

The explicit shared-checkout exception was used: no checkout/worktree was created. All generated material is in this reviewer's newly created external scratch directory containing this report. No runtime import, test, build, provider, network or personal-store operation was performed. Required protected-file hashing read bytes without displaying contents. AGENTS and the three repository policies were inspected; the council skill was read as a pinned input, with its orchestration instructions bounded by this review-seat assignment and explicit no-delegation rule.

## Findings and optional improvements

Numbered mandatory findings: **none**. No remediation is required by this review.

1. **Optional A-01 — add a nonempty created-scope literal vector in a separately authorized future amendment.** Directive lines 244–276 and the fixture already specify and correctly demonstrate Unicode/unsorted pending selection and exact-empty created selection. A third literal vector with a nonempty created reference tuple would make the distinction between preserved selection-reference ordering and sorted actual selected references easier to maintain. Current behavioral obligations already cover changed/foreign/duplicate references, selection binding and headless/installed use; this addition is not necessary for current readiness and is not a request to change the frozen candidate.

The score reflects a complete, tightly bounded design with concrete failure and proof obligations. The remaining 0.4 accounts for extraction/integration complexity that must be resolved through construction evidence and the opportunity for broader literal-vector coverage. It does not conceal a mandatory defect. The threshold was not used as a scoring target.

## Complete criterion matrix

Paths below are relative to `docs/planning/active/command-refactor/` unless stated otherwise. S = `maintenance-reorganization-specification.md`; D = `directives/CD-CMD-MAINT-001-reorganization-order.md`; C = `approval/maintenance-reorganization-conditional.md`. PASS means document readiness only.

| Criterion | Outcome | Independent evidence and assessment |
| --- | --- | --- |
| MC-01 | PASS | D:18–50, 715–728 and C:14–37 bind exact inputs, scope and controller activation. The current conditional approval controls older proposal labels. Review does not itself activate construction. |
| MC-02 | PASS | S:64–94; D:153–228, 320–391. Memory owns mode/skip/order, assessments, scoped planning, lifecycle and postconditions. Chat has one execute-pipeline call and retains the cross-store recovery envelope. Headless complete-flow and Chat one-call proofs are named. |
| MC-03 | PASS | D:54–151, 165–253, 279–287, 328–354. Strict shared models, normalized pending/created selection, operation-local one-use synthesis receipts, typed lifecycle/errors and shared decoding are explicit. No Chat/commands dependency in Memory is permitted. |
| MC-04 | PASS | S:33–62, 154–171; D:94–146, 320–326. Order is reembed/dedupe/prune/pending verification/fresh synthesis/exact generated verification/lifecycle/postconditions. Existing old-meta/non-source pending coverage remains. Empty/migration-only creation is explicitly distinct from missing evidence. Standalone and skip behavior are bounded. |
| MC-05 | PASS | D:393–416 and S:173–177. Preview has no probe/completion/embed calls or operation/recovery creation. Conditional verification configuration checks cover possible future outputs; empty selections do not assess. Synthesizer/embedding readiness stays distinct. Shared strict decoder relocation preserves validation. |
| MC-06 | PASS | S:179–203; D:215–228, 289–318, 356–391. Per-stage and final-postcondition shielding/draining precede operation cleanup. Failures and hooks abort; outer Chat restores the whole run. Shared postconditions are consumed without repeated apply. Worker failure and cancellation precedence are explicit. |
| MC-07 | PASS | D:87–102, 418–512. Counts derive from persisted final judge updates; unsuccessful/deferred/skipped results cannot invent zeros. Receipts are durable content-safe sidecars. Journal/bundle v1 remains unchanged; malformed sidecars cannot obstruct restoration. Old-source synthetic fixture generation and audited test-only relocation are concrete. |
| MC-08 | PASS | D:514–558 and inspected baseline seams listed below. Exact source/test paths accommodate the Memory engine/provider extraction, Chat adapter/coordinator/error mapping, safe artifact writer and lifecycle delegation. Existing Memory dependencies support the moved code. No hidden package, config or lock change was identified as necessary. Stop-on-outside-seam rule remains. |
| MC-09 | PASS | S:228–243; D:560–703. Named tests cover full headless domain flow, one-call Chat, cancellation/rollback, exact scope and receipts, parser behavior and old-journal recovery. Negative controls require intended call-phase assertion failures and unchanged controls. Offline/private-cache commands, clean build/replay, installed normal/optimized origins and later human UAT are specified. These are obligations, not reproduced passes. |
| MC-10 | PASS | S:64–123, 199–226; D:52–512; C:8–37. Concrete signatures, receipt canonicalization/lifecycle, result mapping, compatibility and failure behavior are mutually implementable. Current conditional approval resolves historical review-only/proposal wording and historical preparation state. No technical conflict requiring amendment was found. |
| MC-R01 | PASS | D:289–318 and named test at D:575. Default direct-await is explicitly forbidden. One owned shielded worker drains through repeated caller cancellation; worker failure remains primary; no next stage starts; worker-origin cancellation aborts. Both default and injected paths must prove suspended-write drain, cleanup and outer restoration. This closes the supplied requirement at design level. |
| MC-R02 | PASS | D:175–199, 230–287, 462–492, 576. Non-null planned verification identity/digest exists before assessments/writes, including exact-empty; before/planned/after correlation survives private-state cleanup. Actual applied plan/selection must match, not merely string shape. Chat copies Memory evidence; substituted/omitted scope and sidecar failure have explicit rejection/rollback obligations. This closes the supplied requirement at design level. |
| MC-R03 | PASS | Name-only revision and aggregate comparisons contain 11 and 23 changed paths respectively, all under docs/. All 812 V4 baseline-map files and 17,446 protected files match. No runtime implementation is being claimed. Current conditional approval governs historical captures. |
| MC-F01 | PASS | D:244–276, 532, 569; vector fixture and private reference-checks.json. Both literal canonical strings and hashes reproduce independently. Unsorted Unicode pending input and created exact-empty selection are represented. Fixture bytes are pinned, package-local copy is allowlisted, production-derived expectations forbidden. Headless/installed execution and intended mutation witnesses are mandatory without package/dependency changes. |
| MC-F02 | PASS | C:23–37; D:719–728. Both fresh named reviewers must individually return VERIFIED and >=9.5/10 without mandatory findings. Averaging, rounding, provisional/missing scores, substitutions and automatic threshold-chasing loops are forbidden. Controller records exact candidate/reports/integrity and activation before edits. This report supplies only the Sol seat. |

## Baseline-source feasibility inspected

- `packages/friday-memory/src/friday_memory/maintenance/mutation.py`: strict models (44–85), canonical plan hashing (372–381), pending selector (749–769), planning (771 onward), fresh-plan-before-apply and typed writes (1095–1276), and final synthesis/verification postconditions (1278–1444). The pending selector includes uncertain and old meta; successful synthesis additions are explicitly available in the command while migration changes share its changed count. This supports exact-reference extraction rather than count inference. The final postconditions already account for later verification status when checking generated additions.
- `packages/friday-chat/src/friday_chat/reorganization/mutation.py`: strict provider contracts and response decoder (roughly 50–348), explicit registry/composition, existing run-local command list (roughly 516 onward), provider-role/preflight authority (609 onward), command building/three-role chain (785–959). These are identifiable relocations; transport/config construction can remain in Chat while shared response/schema/coverage validation moves to Memory.
- `packages/friday-chat/src/friday_chat/reorganization/coordinator.py`: mutation protocol (251 onward), transaction stage loop and final live verification (roughly 810–915), and `_atomic` (1868–1893). Existing application rollback and snapshots can surround one pipeline invocation. The directive correctly requires proof of default shared behavior rather than assuming the old Chat helper establishes headless safety.
- `packages/friday-chat/src/friday_chat/adapters.py:767` and corresponding runtime lifecycle signatures/fakes identify the bounded promotion adapter and error-type changes. Artifact-store code uses the existing confined atomic writer with absent-file enforcement. Registry mode parser already centralizes mode conflicts/duplicates, making the explicit-full spelling local.
- Memory maintenance exports and package dependency declarations were inspected for feasibility. Existing dependencies cover the shared functionality; no new dependency or top-level export is essential because the public maintenance surface is allowlisted. Existing test node names establish applicable regression seams; they were not executed.

## Checks actually run versus obligations only inspected

**Run:** standard `shasum -a 256` on the request before reading; Python standard-library JSON/SHA computations; exact Git logical-index hash before status at both boundaries; HEAD/branch/status/staged checks; all pinned/protected content hashes; preserved mode/size/mtime_ns/ctime_ns and requested file hashes; V4 baseline file-map comparisons; safe path-restricted delta and aggregate/revision name-only checks; source/document reads and bounded searches. No Git command omitted `GIT_OPTIONAL_LOCKS=0` from its environment.

For vectors, reference code parsed the fixture, sorted actual references by `(collection,memory_id)`, then used `json.dumps(sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('utf-8')`. It compared bytes directly with each literal canonical string, wrote canonical bytes only to this scratch, and checked each hash with both hashlib and shasum:

| Vector | Canonical bytes | Independently reproduced SHA256 |
| --- | --- | --- |
| pending-unicode | 371 | `082bc35dabb55d3e8101ce346e3039f109bd5f115c1f2e2286e4b36cc84175d9` |
| created-exact-empty | 368 | `5502c0e7fd37ef3077ca2d9518b6f254dc7be04f8fd33844a8a20969314035b0` |

Reference-only perturbations confirmed trailing newline and operation identity changes alter both hashes; disabling Unicode escaping changes the Unicode vector. The all-ASCII empty vector correctly remains unchanged by ensure_ascii=False. These are data checks, not runtime negative-control/product-test witnesses. See `reference-checks.json`.

**Inspected, not run:** every proposed pytest suite, cancellation/observer/rollback test, runtime mutation control, baseline v1 fixture generation, installed probe, optimized Python check, static/tooling command, clean archive build/replay, offline dependency closure and future human UAT. No passing construction evidence is owed by this design review, and none is claimed. Offline input availability and actual construction conformance remain later gates.

## Opening and closing integrity

Both boundaries matched the requested candidate and branch. Exact SHA256 of `git ls-files -s -z` stdout, computed before status each time:

`960baa24a25bd8fbc9761f9e38ba9f99ea8355b9d2d09caa8a542aef36412fa3`

Status at both boundaries:

```text
 M packages/friday-chat/config.example.yaml
 M packages/friday-chat/models-config.example.yaml
?? .friday-old/
```

Staged diff was empty at both boundaries. All 12 request pins matched. Protected manifest SHA256 matched `82a5d911938ac92cc9a95ec7cefe379d3f3a03c53e5ee1d799bcfc26d0d688c1`; all 17,446 listed file hashes matched at opening and closing, zero mismatches. All six preserved metadata records matched at both boundaries, including both dirty YAML hashes and `.friday-old`, exports and the two export files. Contents were not displayed. Request SHA256 remained exact at closing. All 812 V4 baseline-map entries matched current bytes.

Machine-readable receipts: `opening-partial.json`, `opening-protected.json`, `reference-checks.json`, `closing-integrity.json`. Closing capture time: `2026-11-10T16:11:21.956161+00:00`. Subsequent work only wrote this private report.

Shared-checkout hashing establishes observed start/end equality, not an exclusive filesystem lock. No drift was observed. Runtime correctness, real provider behavior and human usability remain deliberately unassessed. The controller must assess the other named fresh seat and all conditional activation requirements; this result alone grants no construction, human acceptance or delivery authority.

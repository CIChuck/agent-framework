# INGEST-C2 independent implementation validation

**CHANGES_REQUESTED**

One medium-severity mandatory finding remains. The current C2 checker accepts malformed wheel tag declarations containing an empty ABI or platform component. Both independent assertion failures reproduce in normal and optimized execution. Retained C0/C1 controls, all supplied C2 selector assertions, required static checks and repository administration pass within their bounded scope.

Advisory component score: **8.8/10**. This is a judgment of the bounded offline component and retained controls only. It neither overrides the finding nor advances the full-harness 9.5 gate. Full HR readiness, actual A0-A4, human acceptance and delivery remain open.

## Identity, scope and authority

- Reviewer: fresh native Codex validation agent, independent of implementation; exact model/version was not surfaced by this task interface. Date: 2026-11-12T15:04:42.569107+00:00.
- Review mode: C2 CD-01-08 dependency-selection delta FIRST, followed by FULL bounded retained C0/C1/C2 aggregate. No memory, old/peer review reports, inherited verdicts, nested agents, repairs or repository mutations.
- Repository: `/Users/chuckrussell/Dev/gendev/agent-framework`; branch `feature/cmd-ingest-001`.
- Base `73fbda9b7f4e90da9912be442e1eb05b494a13b5`; frozen candidate `120def192117d6ed53fe10fa2ec3728c0e56ea7b`; source increment `f931db992746619aec6bc2a834c731555047dab8`.
- Diff `73fbda9b7f4e90da9912be442e1eb05b494a13b5..120def192117d6ed53fe10fa2ec3728c0e56ea7b`. Request SHA256 was verified before reading it: `06787f8adda6242076fbd0175287f22f3124e8aaa9be6c7ad6e58f904837252b`.
- Supplied boundary SHA256: `c871b19210a85daac6381683f63d8fc01e9c4ecb459dca05895afcd4d76297fb`.
- Reviewer-owned committed-blob export: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/export/tests/readiness/ingest`. Exact 29-file manifest: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/harness-manifest.json`, SHA256 `c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a`. Its complete file/blob/hash/mode rows equal the pinned source manifest; its enclosing commit/tree identify this candidate.
- Applied AGENTS.md, engineering/lifecycle/independent-validation policies and Friday development board skill. Explicit construction approval is hash-matched to its current routing digest and exact directive. C1 continuation grants the bounded test-only remaining construction; the parser approval grants only its private offline tool role.
- Current routing was selectively parsed into `current-routing.json`; raw authority history was not examined. Board/dashboard/current packet routing agrees on validation/in_review, started/local, no actual effects activation.

All request authority pins were verified at both boundaries:

| Authority | SHA256 |
| --- | --- |
| `AGENTS.md` | `9c2840ea92bf5f25acd5c85d36a18d2c7d9677c0768d1e811aef5efde6fc936b` |
| `docs/reference/policies/repository-engineering-policy.md` | `17b830b8990f74d1b0a25a46fc2cf2f62249f4e0d668f45b96cfe03a6cc76aff` |
| `docs/reference/policies/development-task-lifecycle.md` | `2c0241fd353145a4704699e69000dd8c4bd8404cb616e224fe77dee03165d844` |
| `docs/reference/policies/independent-validation-policy.md` | `4d951418e0f0c96a4c87d4b8a07cb4025dd94738da50893d19a6d2b7a7f82f4a` |
| `docs/planning/board.yaml` | `5f97b2a727ec3d00cf765e1678fa1cd125c277e2908929328004de4a2f442938` |
| `docs/planning/active/command-refactor/authority.json` | `6afa8e0e2c1b78f944f21a41ddc347d02e25997b72555c5503081d9c886e2c2a` |
| `docs/planning/active/command-refactor/directives/CD-CMD-INGEST-GATE-A-001-readiness-harness.md` | `bb5453f9078a2c7ec4d45762d522ab75d52c35dfcf15685b1b6c8f1a53a50803` |
| `docs/planning/active/command-refactor/validation/document-ingestion/gate-a/construction/c1/continuation.json` | `8c82270067c26255f92b0432ffa9165884cb4adeff95d116999dbcfb18ca78ee` |
| `docs/planning/active/command-refactor/validation/document-ingestion/gate-a/construction/c2/implementation-scope.md` | `b1a71e754c60d33c972743c76ac632b28c36307285fc34ce6f9ed7db607c6b0a` |
| `docs/planning/active/command-refactor/validation/document-ingestion/gate-a/construction/c2/harness-manifest.json` | `d70c8dfb1f4058e13476299f0a0812567e1915ce1f6b617549325da201c20d02` |
| `docs/planning/active/command-refactor/validation/document-ingestion/gate-a/construction/c1/private-resolver-tool-profile.json` | `f81bc1edc54635a51dcb720fe6cc82e990affd85b73fc75c5b69be91698bffe6` |
| `docs/planning/active/command-refactor/validation/document-ingestion/gate-a/execution-contract.md` | `ac09cc3115640f788fba8f3c29e0b981e18e43ae29846e5fe9585a3099f24a69` |
| `docs/planning/active/command-refactor/validation/document-ingestion/gate-a/isolation-requirements.md` | `a50069c9ede478c2387ed819e15cc949223e14bd0635ee9dcc5aa14b0bb60264` |
| `docs/planning/active/command-refactor/validation/document-ingestion/gate-a/readiness-plan.md` | `94c37e845c0acc4c8f79568c57060dd65df01b20def54abf78c1cf177bba6cd2` |
| `docs/planning/active/command-refactor/validation/document-ingestion/gate-a/effects-envelope.json` | `4b6273c2a629affd02e388574a0b1715334456c921611e55e069122f7b0b4315` |
| `docs/planning/active/command-refactor/validation/document-ingestion/gate-a/construction/c0/private-typecheck-approval.json` | `df2e14f1381ee277f0e9894fb517f04ce2ad2d0ea004579d04ec44a45f66d711` |
| `docs/planning/active/command-refactor/validation/document-ingestion/gate-a/construction/c0/private-typecheck-profile.json` | `329f572b587c5998a4b8e96e6cfda8605a69f2bce6cbe4637fa191394300a568` |
| `docs/planning/active/command-refactor/validation/document-ingestion/gate-a/construction/c1/private-resolver-tool-approval.json` | `5f39686d4acba01a1d77602d8dfa71654abed2bfa3fa67cd86a290ed0ff164eb` |

## Mandatory finding

1. **INGEST-C2-VAL-001 — Medium — malformed wheel tag components accepted**

   Affected source: `tests/readiness/ingest/manifests.py:185` and its wheel-tag comparison near line 237; coverage: `tests/readiness/ingest/tests/test_manifests.py:86`.

   Violated authority: C2 implementation-scope CD-02 requires explicit schema/tag selection and CD-04 requires malformed declarations and wrong wheel/platform declarations to refuse. The scope prose says the checker validates Python/platform tags. `packaging.tags.parse_tag` splits the three components and constructs Tag objects; it does not reject empty components. `parse_wheel_filename` similarly returns these tags. Comparing two equally malformed tags therefore succeeds.

   Actual call-phase evidence: the reviewer-authored assertions `malformed empty ABI tag refused` and `malformed empty platform tag refused` fail with `Refusal not raised` in BOTH modes, after successful bootstrap, guard installation, exact private parser origin verification, and the 5-positive/31-refusal selector. The other 15 independent assertions pass. These failures are application semantic assertion failures, not setup/import/collection failures.

   Minimal accepted declarations use otherwise valid schema/environment/requirements/host/digest/size fields and respectively:

   | Explicit target tag | Wheel filename | Actual result | Required |
   | --- | --- | --- | --- |
   | `py3--any` | `a-1.0-py3--any.whl` | `CONSISTENT_CANDIDATE_DECLARATIONS` | `Refusal` |
   | `py3-none-` | `a-1.0-py3-none-.whl` | `CONSISTENT_CANDIDATE_DECLARATIONS` | `Refusal` |

   Full exact input/output witnesses are in `tag-witnesses.json`; executable independent assertions are in `independent_selection.py`, loaded from `selection_worker.py` under the guard. `witness_worker.py` corroborates accepted output without changing the source. Both selected-byte totals are 70, distribution count is 1, and all four qualification flags remain false. No artifact fetch or execution occurs.

   Risk: malformed metadata can be mislabeled a consistent candidate and become input to a later adapter. The present false execution/qualification flags limit immediate impact, but do not satisfy the mandatory rejection requirement.

   Required mitigation: explicitly validate each interpreter/ABI/platform tag component and every compressed-tag member as a nonempty syntactically admissible identifier before treating it as a target or selected wheel tag. Keep the approved parser for standards semantics; do not assume its parse helpers perform complete validation. Apply consistent validation to explicit targets and wheel-derived tags. This report does not prescribe an ambient-platform lookup or real resolver call.

   Required verification: add actual guarded normal/-O assertion cases for empty interpreter/ABI/platform components and empty members of compressed tag groups, retain valid universal/native/compressed-tag positives, rerun the 55 minimal tests, explicit selector, focused static checks and the full bounded aggregate on a new frozen candidate. Required documentation impact: keep the README/scope validation claims and new evidence consistent; do not claim real A0-A4 qualification. No root configuration or third-party source change is needed.

## CD-01-08 criteria matrix

| Criterion | Result | Fresh evidence and practical limits |
| --- | --- | --- |
| CD-01 | PASS | Request/boundary and all pins verified; exact 3-path source delta; all 29 committed files exported; C0/C1 construction trees byte-unchanged across range; opening/closing equality for tracked hashes, symlinks, logical index, branch/HEAD/status and 9 metadata entries. |
| CD-02 | FAIL | Exact top-level/environment field sets and bounded declarations; malformed outer controls refuse before optional parser import in minimal tests. Complete tag validation fails finding INGEST-C2-VAL-001. |
| CD-03 | PASS within bounded declaration semantics | Real copied/hash-verified packaging24.2: all 5 selector positives pass each mode; independent cycles, late extras, additive base/extra, canonical names, exact total bound and inactive marker flows pass. This is explicit target metadata, not observed machine capability. |
| CD-04 | FAIL | All 31 selector refusal assertions pass each mode. Independent missing/unreachable closure, repeated/transitive constraints, unknown extras, root references, Python and byte violations refuse. Empty tag ABI/platform declarations are accepted in both modes. |
| CD-05 | PASS | Source bounds roots64/wheels512/tags2048, per-wheel requirements256, declared/expanded graph8192, requirement4096, extras32/64 and total bytes4GiB. Independent exact/over byte bound checks and all four false qualification flags pass. No resolver/download/install, bytes/license/runtime permission is inferred. |
| CD-06 | PASS | AST comparison retains all 54 prior test definitions unchanged; 55 minimal tests pass normal/-O. Explicit guarded selector passes 5 positive/31 refusal each mode with packaging24.2 from reviewer-owned verified target. Minimal API schema test leaves optional parser import state unchanged. |
| CD-07 | PASS | Exact root config copy; copied1177 typing files and23 parser files hash-verified before/after; Ruff check0, format0 (25 files), mypy0 (25 sources). Parser supplied only as the single explicit private PEP561 package path; no ambient site, source edits, suppressions or root-rule changes. |
| CD-08 | Review completed; candidate gate FAIL | Fresh read-only delta then full bounded aggregate performed, private outputs/caches only, administration0, owned/cached/range whitespace0, all evidence hash pairs checked, final preservation equal. Finding prevents VERIFIED; real A0-A4/readiness/9.5 remain unqualified. |

## Retained full bounded C0/C1/C2 aggregate

The complete current harness source and tests were assessed, without carrying earlier conclusions forward. Both 55-test runs execute positive and negative startup, path/config/environment, canonical controls, ledger/promotion/budget, committed object export, Python guard/detection, fake window/transport, fixture and reporting tests. Actual stage implementations and profile qualification are intentionally outside this component.

| Full HR criterion | Bounded evidence assessed now | Full readiness disposition |
| --- | --- | --- |
| HR-01 | Exact source scope, committed export, own unit roots, opening/closing protected state equality. | OPEN for whole harness/product. |
| HR-02 | No-file preflight; absent-root init; frozen copy; manual fixture, reports and each gated stage interface, both modes. | Actual full/selected/offline A0-A4 adapters remain OPEN. |
| HR-03 | Archive path/duplicate/member/expanded limits; guarded Python read/probe/write/thread/dir_fd/descriptor/socket negatives; positive owned controls; metadata detection. | Real native/profile containment remains OPEN, no OS claim. |
| HR-04 | Control/artifact digest/schema/host/closure and stale bindings exercised; current tag refusal gap recorded above. | OPEN; malformed tag finding mandatory. Bytes/licenses/upstream origins unqualified. |
| HR-05 | Fake loaded-state/window identity/expiry/safe-policy and final-admission controls; zero unauthorized fake handoffs asserted. | Actual preloaded service/window qualification OPEN. |
| HR-06 | Thirty deterministic genuine format candidates and literal structural/oracle tests; manual publications hash/size/read-only verified. | Real-reader/OCR compatibility and supplied-copy acceptance OPEN. |
| HR-07 | Fake full prepared-input/vector/token limits and no synthetic-count overclaim. | Three actual chunk strategies/512 semantics/provenance OPEN. |
| HR-08 | Ledger cumulative reservation/reopen, owned lease, sticky stop, callback expiry/stop and conservative retained charges. | Actual time/process/download/conversion budgets OPEN. |
| HR-09 | INCOMPLETE reports preserve ledger-only evidence, false current-byte/converter/full-readiness facts and attested/observed/containment distinctions. | Full stage aggregation OPEN. |
| HR-10 | Qualified base CPython -I -S -B, normal/-O; stdlib minimal core; explicit private guarded parser/static tools. | Actual runtime/upstream profile imports OPEN. |
| HR-11 | Explicit minimal and parser selectors; private root-rule lint/format/mypy; no root pytest credit or .venv fallback. | Whole harness/profile gate OPEN pending mandatory finding and remaining implementation. |
| HR-12 | Stable candidate/input/tool origins; fresh exact receipts and protected-state equality. | This candidate receives CHANGES_REQUESTED; no UAT/acceptance/delivery. |
| HR-13 | Dirty/extra/pyc refusal, verified-buffer path swap, armed private startup canary unsafe-control witness, guarded child positive/refusal in both modes. | Real tool-child trace/startup inventories OPEN; no inherited -O/guard assertion. |
| HR-14 | Ledger extension, stale tip/order/tamper/writer/receipt tests and blocked all behavior. | Real stage promotion/window-prefix lifecycle OPEN. |
| HR-15 | Fake credential/proxy/Python settings stripped; startup-site classification; private guard paths and fake transport request accounting. | Real LiteLLM/HTTP/system-channel qualification OPEN. |
| HR-16 | Native fake-repository committed-blob positive excludes dirty/untracked content; object hashes checked; review committed export exact; production logical index unchanged. | Actual application selected-source adapter admission OPEN. |
| HR-17 | Simulated metadata mutation fails detection; missing/truncated coverage refuses; explicit guarded worker tests pass; real protected state unchanged. | Real upstream default-channel coverage OPEN. |
| HR-18 | Fake chosen native status profile/load identity/no fallback and per-attempt controls tested. | Actual chosen service API/model safe policy and before/after checks OPEN. |

## Commands, exits and evidence classes

Fresh executed receipts: `commands.json` (34 commands), `checks.json` (12 commands), `tag-witnesses.json` (2 commands). Every row retains exact argv/cwd/environment/stdout/stderr/exit; the full argv/exit appendix below is independently generated from those receipts. The only nonzero unexpected semantic results are the two independent tag assertions inside each selection worker. The worker deliberately exits1 if any independent assertion fails; the review orchestrator expects that reproduced exit and continues the aggregate. A successful orchestrator exit never turns those assertion failures into PASS.

| Fresh lane | Exit/result |
| --- | --- |
| 55 minimal tests normal and -O | 0 each, 55 tests each |
| Guarded selection normal and -O | 1 each: supplied selector5/31 pass; independent15 pass/2 fail |
| Explicit accepted-tag witness normal and -O | 0 each; two malformed declarations accepted each |
| Manual preflight/init/prepare-fixtures/stop | 0 each mode; 30 candidates each publication |
| Repeat fixture generation and stopped effects | expected2 each mode, actual control Refusal |
| all plus each A0-A4; prepare-model; incomplete/after-stop reports | expected3 each mode; blocked/incomplete, no actual activation |
| Ruff / format / mypy | 0 /0 /0; 25 Python sources |
| Board / dashboard / docs / metadata | 0 /0 /0 /0;36 tasks,1094 Markdown files,18 metadata files |
| Owned / cached / range whitespace | 0 /0 /0 |
| Preserved dirty YAML whitespace | 2, known baseline/unwaived: models-config.example.yaml130,142 |
| C0/C1 evidence range comparison | 0, unchanged |

The separate required administration lane used the existing documented `uv run --offline --frozen --no-sync --no-python-downloads --no-env-file python -B ...` maintenance commands, bytecode off, GIT_OPTIONAL_LOCKS=0 and reviewer-owned UV/XDG/config/credential/temp paths. It imported no Friday application modules and performed no sync/install. The harness, parser and static lanes used the pinned base interpreter and reviewer-owned targets, never the working .venv. The admin exception is not runtime/profile qualification.

Mypy guarded logs contain two denied optional probes for base-interpreter bin/Modules/Setup and Setup.local; they are caught optional discovery paths, with no payload read or write and no unguarded retry. The final mypy result is 25-source success with the sole explicit private PEP561 package path. No guard refusal is credited as a product negative unless the test assertion actually reaches the intended call.

Inspected-only receipts: `aggregate-evidence-audit.json` verifies 41 current C0/C1/C2 compressed/raw hash pairs. Historical review reports were not opened, and no preexisting test verdict was adopted. Tool inspection/inventory digests were checked and1177 typing/23 parser files copied by exact inventory, then rechecked. These byte/metadata inspections do not reproduce historic downloads or prove application artifacts/licensing/installed profiles.

Review preparation note: an initial reviewer snapshot implementation expected existing .friday_test and then used a mismatched absent-key spelling. Those reviewer-owned setup attempts failed before producing the opening result; the script was corrected outside the repository and the complete opening snapshot then matched. They earn no product rejection or guard credit.

## Final integrity and limitations

- Both boundaries: HEAD `120def192117d6ed53fe10fa2ec3728c0e56ea7b`, branch `feature/cmd-ingest-001`, logical index SHA256 `8a219b29265910325bb2e0b72377abee0b03e41817933dfca9b551ae45e5cf03`. Logical index was obtained with GIT_OPTIONAL_LOCKS=0 before status at each boundary.
- All18340 tracked regular-file hashes,26 symlink targets,all request pins and9 protected entries match. Protected entries: the two dirty YAML files, .friday, .friday-old, .venv, exports, its two selected files and absent .friday_test. Dirty YAML payloads were not read; hashing/metadata and explicit whitespace diagnostics were the authorized exceptions. No .friday tree was traversed.
- Status remains two dirty example YAML files plus untracked .friday-old/. No repository .friday_test was created. No cleanup/restoration/staging/commit/board write was performed.
- All1207 supplied input/interpreter/tool paths hashed in input-closing.json are unchanged; all29 exported source members and all1177+23 copied tools still match. Request and supplied boundary digests still match.
- No real metadata/resolver/download/install/conversion/tokenizer/model/store/provider/network call, application import or production write was performed. Offline parser selection is a pure declaration check. The native/extension boundary remains detective/residual; this is not an OS sandbox or complete filesystem guarantee.
- Report rendering, malformed-tag accepted output and test passes confer no artifact/license/installed/runtime permission. Actual A0-A4, all full HR readiness obligations and9.5 advancement remain OPEN. No maintainer acceptance, publication or delivery is granted.

## Exact command appendix

Supplemental validation entry commands (exit0 after the reviewer preparation correction):

`python3 -I -S -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/setup_review.py`

`python3 -I -S -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/run_review.py`

`python3 -I -S -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/run_checks.py`

`python3 -I -S -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/snapshot.py opening`

`python3 -I -S -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/snapshot.py closing`

`python3 -I -S -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/finalize_integrity.py`

The tag-witness subprocess argv is recorded below. Evidence byte audits and final copied/supplied integrity checks use the standard-library code retained in the reviewer artifact sources and their JSON results. Final report generation writes only reviewer scratch.

### selection-normal

Exit: `1`; expected by driver: `1`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/selection_worker.py
```

### selection-optimized

Exit: `1`; expected by driver: `1`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/selection_worker.py
```

### selftest-normal

Exit: `0`; expected by driver: `0`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/export/tests/readiness/ingest/bootstrap.py selftest --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --scratch /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/selftest-normal
```

### normal-preflight

Exit: `0`; expected by driver: `0`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/export/tests/readiness/ingest/bootstrap.py preflight --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/control-normal.json --config-sha256 f2c5d497814ceea7562abbfe4a9de298ac215e6716ab3b7e42e7c340a8d89403
```

### normal-init

Exit: `0`; expected by driver: `0`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/export/tests/readiness/ingest/bootstrap.py init --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/control-normal.json --config-sha256 f2c5d497814ceea7562abbfe4a9de298ac215e6716ab3b7e42e7c340a8d89403
```

### normal-prepare-fixtures

Exit: `0`; expected by driver: `0`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/harness/run.py prepare-fixtures --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/config/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/config/control.json --config-sha256 a83bac0adda83cdfd2d84695b788f439373e748e727dc7ce187e613649039627
```

### normal-repeat-refused

Exit: `2`; expected by driver: `2`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/harness/run.py prepare-fixtures --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/config/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/config/control.json --config-sha256 a83bac0adda83cdfd2d84695b788f439373e748e727dc7ce187e613649039627
```

### normal-stage-all

Exit: `3`; expected by driver: `3`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/harness/run.py run --stage all --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/config/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/config/control.json --config-sha256 a83bac0adda83cdfd2d84695b788f439373e748e727dc7ce187e613649039627
```

### normal-stage-A0

Exit: `3`; expected by driver: `3`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/harness/run.py run --stage A0 --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/config/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/config/control.json --config-sha256 a83bac0adda83cdfd2d84695b788f439373e748e727dc7ce187e613649039627
```

### normal-stage-A1

Exit: `3`; expected by driver: `3`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/harness/run.py run --stage A1 --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/config/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/config/control.json --config-sha256 a83bac0adda83cdfd2d84695b788f439373e748e727dc7ce187e613649039627
```

### normal-stage-A2

Exit: `3`; expected by driver: `3`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/harness/run.py run --stage A2 --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/config/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/config/control.json --config-sha256 a83bac0adda83cdfd2d84695b788f439373e748e727dc7ce187e613649039627
```

### normal-stage-A3

Exit: `3`; expected by driver: `3`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/harness/run.py run --stage A3 --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/config/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/config/control.json --config-sha256 a83bac0adda83cdfd2d84695b788f439373e748e727dc7ce187e613649039627
```

### normal-stage-A4

Exit: `3`; expected by driver: `3`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/harness/run.py run --stage A4 --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/config/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/config/control.json --config-sha256 a83bac0adda83cdfd2d84695b788f439373e748e727dc7ce187e613649039627
```

### normal-report-incomplete

Exit: `3`; expected by driver: `3`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/harness/run.py report --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/config/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/config/control.json --config-sha256 a83bac0adda83cdfd2d84695b788f439373e748e727dc7ce187e613649039627
```

### normal-prepare-model-blocked

Exit: `3`; expected by driver: `3`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/harness/run.py prepare-model --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/config/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/config/control.json --config-sha256 a83bac0adda83cdfd2d84695b788f439373e748e727dc7ce187e613649039627
```

### normal-stop

Exit: `0`; expected by driver: `0`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/harness/run.py stop --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/config/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/config/control.json --config-sha256 a83bac0adda83cdfd2d84695b788f439373e748e727dc7ce187e613649039627
```

### normal-stopped-effects-refused

Exit: `2`; expected by driver: `2`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/harness/run.py prepare-fixtures --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/config/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/config/control.json --config-sha256 a83bac0adda83cdfd2d84695b788f439373e748e727dc7ce187e613649039627
```

### normal-report-after-stop

Exit: `3`; expected by driver: `3`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/harness/run.py report --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/config/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-normal/.friday_test/runs/review-c2-normal/config/control.json --config-sha256 a83bac0adda83cdfd2d84695b788f439373e748e727dc7ce187e613649039627
```

### selftest-optimized

Exit: `0`; expected by driver: `0`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/export/tests/readiness/ingest/bootstrap.py selftest --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --scratch /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/selftest-optimized
```

### optimized-preflight

Exit: `0`; expected by driver: `0`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/export/tests/readiness/ingest/bootstrap.py preflight --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/control-optimized.json --config-sha256 eaa695ffd200e844cade1bca0e585fc5563c522c0bf397c72ea54720c0953bc2
```

### optimized-init

Exit: `0`; expected by driver: `0`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/export/tests/readiness/ingest/bootstrap.py init --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/control-optimized.json --config-sha256 eaa695ffd200e844cade1bca0e585fc5563c522c0bf397c72ea54720c0953bc2
```

### optimized-prepare-fixtures

Exit: `0`; expected by driver: `0`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/harness/run.py prepare-fixtures --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/config/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/config/control.json --config-sha256 50c7dfdce571bdde44f4e10e98efbae52e6ac6301ff2fc8fba5e93c997668ba0
```

### optimized-repeat-refused

Exit: `2`; expected by driver: `2`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/harness/run.py prepare-fixtures --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/config/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/config/control.json --config-sha256 50c7dfdce571bdde44f4e10e98efbae52e6ac6301ff2fc8fba5e93c997668ba0
```

### optimized-stage-all

Exit: `3`; expected by driver: `3`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/harness/run.py run --stage all --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/config/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/config/control.json --config-sha256 50c7dfdce571bdde44f4e10e98efbae52e6ac6301ff2fc8fba5e93c997668ba0
```

### optimized-stage-A0

Exit: `3`; expected by driver: `3`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/harness/run.py run --stage A0 --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/config/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/config/control.json --config-sha256 50c7dfdce571bdde44f4e10e98efbae52e6ac6301ff2fc8fba5e93c997668ba0
```

### optimized-stage-A1

Exit: `3`; expected by driver: `3`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/harness/run.py run --stage A1 --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/config/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/config/control.json --config-sha256 50c7dfdce571bdde44f4e10e98efbae52e6ac6301ff2fc8fba5e93c997668ba0
```

### optimized-stage-A2

Exit: `3`; expected by driver: `3`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/harness/run.py run --stage A2 --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/config/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/config/control.json --config-sha256 50c7dfdce571bdde44f4e10e98efbae52e6ac6301ff2fc8fba5e93c997668ba0
```

### optimized-stage-A3

Exit: `3`; expected by driver: `3`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/harness/run.py run --stage A3 --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/config/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/config/control.json --config-sha256 50c7dfdce571bdde44f4e10e98efbae52e6ac6301ff2fc8fba5e93c997668ba0
```

### optimized-stage-A4

Exit: `3`; expected by driver: `3`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/harness/run.py run --stage A4 --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/config/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/config/control.json --config-sha256 50c7dfdce571bdde44f4e10e98efbae52e6ac6301ff2fc8fba5e93c997668ba0
```

### optimized-report-incomplete

Exit: `3`; expected by driver: `3`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/harness/run.py report --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/config/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/config/control.json --config-sha256 50c7dfdce571bdde44f4e10e98efbae52e6ac6301ff2fc8fba5e93c997668ba0
```

### optimized-prepare-model-blocked

Exit: `3`; expected by driver: `3`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/harness/run.py prepare-model --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/config/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/config/control.json --config-sha256 50c7dfdce571bdde44f4e10e98efbae52e6ac6301ff2fc8fba5e93c997668ba0
```

### optimized-stop

Exit: `0`; expected by driver: `0`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/harness/run.py stop --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/config/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/config/control.json --config-sha256 50c7dfdce571bdde44f4e10e98efbae52e6ac6301ff2fc8fba5e93c997668ba0
```

### optimized-stopped-effects-refused

Exit: `2`; expected by driver: `2`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/harness/run.py prepare-fixtures --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/config/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/config/control.json --config-sha256 50c7dfdce571bdde44f4e10e98efbae52e6ac6301ff2fc8fba5e93c997668ba0
```

### optimized-report-after-stop

Exit: `3`; expected by driver: `3`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/harness/run.py report --harness-manifest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/config/harness-manifest.json --harness-manifest-sha256 c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/unit-project-optimized/.friday_test/runs/review-c2-optimized/config/control.json --config-sha256 50c7dfdce571bdde44f4e10e98efbae52e6ac6301ff2fc8fba5e93c997668ba0
```

### ruff-check

Exit: `0`; expected by driver: `0`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/export`

```text
/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/validation-tools/ruff check --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/validation-tools/pyproject.toml --cache-dir /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/validation-tools/ruff-cache /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/export/tests/readiness/ingest
```

### ruff-format

Exit: `0`; expected by driver: `0`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/export`

```text
/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/validation-tools/ruff format --check --config /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/validation-tools/pyproject.toml --cache-dir /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/validation-tools/ruff-format-cache /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/export/tests/readiness/ingest
```

### mypy

Exit: `0`; expected by driver: `0`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/export`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/run_private_mypy.py /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/validation-tools/mypy-target /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/export/tests/readiness/ingest /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/harness-manifest.json c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a 70e03f2215282e2d4aa6fd0a58161ce0b9858981a114caba49f4826f5833599c --config-file /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/validation-tools/pyproject.toml --no-site-packages --explicit-package-bases --cache-dir /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/validation-tools/mypy-cache/fresh-pep561 /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/export/tests/readiness/ingest
```

### board

Exit: `0`; expected by driver: `0`

Cwd: `/Users/chuckrussell/Dev/gendev/agent-framework`

```text
/opt/homebrew/bin/uv run --offline --frozen --no-sync --no-python-downloads --no-env-file python -B scripts/friday-dev-board.py validate
```

### dashboard

Exit: `0`; expected by driver: `0`

Cwd: `/Users/chuckrussell/Dev/gendev/agent-framework`

```text
/opt/homebrew/bin/uv run --offline --frozen --no-sync --no-python-downloads --no-env-file python -B scripts/friday-dev-board.py render --check
```

### docs

Exit: `0`; expected by driver: `0`

Cwd: `/Users/chuckrussell/Dev/gendev/agent-framework`

```text
/opt/homebrew/bin/uv run --offline --frozen --no-sync --no-python-downloads --no-env-file python -B scripts/check-documentation-lifecycle.py
```

### metadata

Exit: `0`; expected by driver: `0`

Cwd: `/Users/chuckrussell/Dev/gendev/agent-framework`

```text
/opt/homebrew/bin/uv run --offline --frozen --no-sync --no-python-downloads --no-env-file python -B scripts/check-package-metadata.py
```

### owned-whitespace

Exit: `0`; expected by driver: `0`

Cwd: `/Users/chuckrussell/Dev/gendev/agent-framework`

```text
/usr/bin/git diff --check -- .gitignore docs/planning tests/readiness/ingest
```

### cached-whitespace

Exit: `0`; expected by driver: `0`

Cwd: `/Users/chuckrussell/Dev/gendev/agent-framework`

```text
/usr/bin/git diff --cached --check
```

### range-whitespace

Exit: `0`; expected by driver: `0`

Cwd: `/Users/chuckrussell/Dev/gendev/agent-framework`

```text
/usr/bin/git diff --check 73fbda9b7f4e90da9912be442e1eb05b494a13b5 120def192117d6ed53fe10fa2ec3728c0e56ea7b
```

### dirty-baseline-whitespace

Exit: `2`; expected by driver: `2`

Cwd: `/Users/chuckrussell/Dev/gendev/agent-framework`

```text
/usr/bin/git diff --check -- packages/friday-chat/config.example.yaml packages/friday-chat/models-config.example.yaml
```

### c0-c1-evidence-unchanged

Exit: `0`; expected by driver: `0`

Cwd: `/Users/chuckrussell/Dev/gendev/agent-framework`

```text
/usr/bin/git diff --exit-code 73fbda9b7f4e90da9912be442e1eb05b494a13b5 120def192117d6ed53fe10fa2ec3728c0e56ea7b -- docs/planning/active/command-refactor/validation/document-ingestion/gate-a/construction/c0 docs/planning/active/command-refactor/validation/document-ingestion/gate-a/construction/c1
```

### malformed-tag-witness-normal

Exit: `0`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/witness_worker.py
```

### malformed-tag-witness-optimized

Exit: `0`

Cwd: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80`

```text
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-validator-rua3yd80/witness_worker.py
```

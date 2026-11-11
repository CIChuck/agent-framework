# Independent Astra document-readiness review — round 6 of 6

**VERIFIED** — no mandatory findings. Coverage **9.8/10**; overall **9.7/10**.

Reviewer: GPT-6 Astra, high reasoning effort, independent read-only seat. Date: 2026-11-11. Unit: INGEST-PACKAGE-IMPACT-001. This is one seat's conclusion, not the aggregate council verdict. No replacement review, further round, delegation or repair was performed.

## Frozen inputs and independence

Workdir `/Users/chuckrussell/Dev/gendev/agent-framework`; branch `feature/cmd-ingest-001`; candidate `ae813002a8537b35feb2d9492338b65fa13bff4b`; delta base `b7c7b1393d6f18db3d26cc518adce2d8458f315a`; administrative whitespace base `8390f3688d00985b1cac0443da8105f33fb1a6b7`.

The first tool command hashed the supplied request before reading it: SHA256 `a20f7116d5b4a682f58532e6c671dbe04d4b32f0939f063973b75698c01a2406`, matching the brief. All request document pins, helper pins, safe-controls pin and protected-manifest pin were independently recomputed and matched before substantive review. Helpers were read before use. Relevant AGENTS, repository engineering/lifecycle/independent-validation policies and the two pinned repository skills were read. Explicit review restrictions control over general workflow suggestions; no council children were launched.

No memory, session/rollout history, parent activity, peer report or peer verdict was read. Historical labels inside the supplied current technical documents were treated solely as labels. No accidental peer-verdict exposure occurred. Raw authority/navigation/board were hash-checked, with current fields inspected only through pinned `current-controls.json`. The execution-log check compared bytes without displaying historical content. No Finance credential literal was printed: Finance inspection used AST names/calls and string-redacted AST source. No credential was verified or used.

All generated files and wrapper caches are under reviewer-owned external scratch:
`/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/astra-round6-independent-qlayd3lx`.
No supplied cache/output root was used for writes. No application/test imports, pytest, dependency installation/resolution/download, network, provider/model or store operation was run. No checkout edits, Git mutations, staging, repair or delivery occurred.

## Delta first: PC-10 and PC-11

Inspected the exact delta for only the five request.review_diff_paths. The architecture and guide plans have no delta in that range; the assessment, REM and migration plan contain the correction.

PC-10 PASS: REM's test allowlist row and migration P-14 explicitly select `packages/friday-finance/tests/test_basics.py`. The migration plan's explicit execution section gives that same selector, identifies `test_integration_massive.py` as live-provider coverage, preserves its obligations and denies executed/offline coverage credit while unrun. Explicit authorization must name service, effects and credential handling. Every non-default module and root integration witness requires offline/live classification and exact directive selectors. Current Finance AST shows nine basic tests covering registry, governor and client configuration, versus ten integration tests invoking provider data methods/tool execution. The client constructor configures SDK/modules; provider query execution is a separate method. No live execution was needed to establish this distinction.

Root `pyproject.toml` testpaths are `packages/*/tests_*` and `experiments/*/tests`; they omit both actual `tests/` directories and root integration. Transcript has four current test modules (correlation, MCP provenance, models, SQLite snapshot), whose inspected imports/call inventory supports their offline classification. Optimization has no baseline `test_*.py` suite. These paths and limitations agree across the revised plans. The future Transcript directory selector does not authorize other live modules if that suite changes: the directive must classify each module.

PC-11 PASS: assessment v0.6, REM opening and closing, criteria and safe current controls consistently state five completed rounds and one fresh full round6/6, self-contained pinned inputs, no memory/history search, no reset/replacement/seventh round or construction. The original test/documentation decision remains controlling. Its older budget is a timestamped authorization record, not the current budget. Unchanged annex/companion historical cycle labels do not override the explicit round6 authorization.

## Full PI-01–18 matrix

Paths below are relative to the workdir. `PIA`, `REM`, `Migration`, `Architecture`, `Guide`, `Annex` and `Companion` denote respectively the five reviewed plans, `embedding-compatibility-contract.md`, and `proposals/tools-document-adoption.md` under `docs/planning/active/command-refactor/`.

| Criterion | Outcome | Independently assessed evidence and conclusion |
| --- | --- | --- |
| PI-01 | PASS | PIA P-01–17 matches all 17 `packages/*/pyproject.toml` members under root workspace pattern. Eight implementation owners include conditional CLI; nine remaining rows distinguish unchanged production source from test/import/transitive impacts. Tools→Finance, Optimization→Memory, MCP full→Agent and inherited headless edges match metadata. |
| PI-02 | PASS | PIA implementation rows map to REM ownership and exact proposed implementation paths. Test-only allowances include actual Transcript/Finance paths and conditional new Optimization witnesses. Conditional CLI edits and unchanged multi-agent/metadata algorithms do not grant unnamed source ownership. |
| PI-03 | PASS | REM ownership and PIA P-01–08 retain Core contracts, Commands parsing, Tools conversion, Memory policy/admission, LLM preparation/limits, Chat/Runtime composition. Core `profiles.py:56` currently lazily constructs Memory adapters; the plan discloses that legacy edge rather than claiming total existing dependency neutrality. |
| PI-04 | PASS | PIA delivery boundaries and P-02, REM active routes/B, Companion delivery sequence and TD-01–10 separate converter installation/INGEST text storage from factory/smart_read document adoption. Current Tools factory imports legacy PDF/DOCX/XLSX readers. No installation-only completion claim. |
| PI-05 | PASS | Current Chat directly depends on plain Tools; Tools extras are documents/spreadsheets/all-formats, with no current Docling extra. PIA dependency effects and REM A correctly describe future default Chat growth, optional Tools support, Certifi floor and narrow LLM counter extra inherited through Memory. Exact artifacts remain readiness outputs. |
| PI-06 | PASS | Annex B01–B08/FC-10, REM E and PIA preserve pool/non-pool selection, independent extraction/maintenance roles and omitted-field qualification. Chat `adapters.py:1734` selects pool default and retains hosted non-pool fallback; docs explicitly disclose hosted qualification uncertainty. B/N positives remain distinct from R refusals, with no silent Qwen swap. |
| PI-07 | PASS | REM identity/upgrade/recovery sections and PIA data effects cover same-dimension changes, explicit absent vector/graph/WAL layout, no legacy stamping, preserved files and /read. Strict bundle1/memory1/transcript1 offline versus bundle2/memory2/transcript1 active matrix retains Transcript v1 and Chat path fingerprint. No migration or maintenance redesign is granted. |
| PI-08 | PASS | REM D, active-route table and PIA configuration effects specify document/512 defaults, independent overrides and document/recursive/fixed policies; source chunks versus unsplit summaries/snapshots are explicit. Chat `adapters.py:385,2793` currently uses character slicing, and smart_read composition at `:2364` supplies LLM/config rather than automatically injecting Memory. Future changes are accurately bounded. |
| PI-09 | PASS | PIA P-09–12 and cross-package section, Annex FC-02/06/13 cover actual Agent/background, Memory-owned multi-agent, MCP receipt/telemetry and metadata error projection. Runtime `di.py:308` assembles Memory multi-agent classes. Current MCP ingester `:107–189` exposes ownership/reuse/storage-failure seams justifying narrow guard adaptation. No transport/schema expansion. |
| PI-10 | PASS | PIA P-04/06/07/08 explicitly exposes Memory's broadest impact, startup admission, owned logging/task teardown, Runtime profile isolation and truthful counts. Current Runtime `di.py:245–305` eagerly creates graph parents, vector and lifecycle stores; Core profiles use SimpleVectorStore for ephemeral/testing. Planned causal wiring corrections are disclosed, with independent transcript effects and no CLI launcher. |
| PI-11 | PASS | Annex causal boundary and FC-03/13 plus PIA backup/MCP readiness row preserve public backup/default behavior and pending snapshot IDs; protect live marker and distinguish logical-v2 recovery. Current BackupManager public method AST and MCP reuse path support the named seams. Tools inspection `:134` calls vector.search while no-query `:141` uses get_all; FU-013 is explicitly unwaived and earns no query credit. FU-014 completeness debt is also unwaived. |
| PI-12 | PASS | REM DI-01–36, Annex proof matrix, Migration execution section and PIA consistently require future real format/model/installed normal/optimized/B/N/R evidence. Current Chat file tests contain fake PDF/DOCX/XLSX inputs; they are correctly classified for replacement, not evidence of actual conversion. Administrative successes below do not establish runtime compatibility. |
| PI-13 | PASS | PIA readiness table and REM A/E bind exact releases, assets/licenses/resource limits, counter/served identity, dimensions, signatures and final paths. B02 hosted qualification and 8192 ceiling are explicit stops; selected-source feasibility does not claim qualified backend execution. |
| PI-14 | PASS | PIA approval/change control and REM closing require Chuck's explicit satisfaction with exact post-readiness version/commit/hash, remaining conditions, separate Gate-A activation and final directive approval. Safe controls report all relevant approval fields not granted; earlier conditional REM hash is explicitly distinguished. |
| PI-15 | PASS | All rows describe purpose, type of change, retained behavior and required proofs. Memory's greater scope and CLI conditionality are visible. No invented estimate or claim of completed package upgrades. Long cross-references impose some reading burden, reflected in the overall rubric. |
| PI-16 | PASS | Opening/closing identity checks both pass; all pins, logical index, expected status and 17,750 protected file identities remain stable. Safe current controls agree on scope/version/budget. Log prefix check passes without history display; board render and lifecycle checks pass. Historical technical labels grant no current runtime verdict. |
| PI-17 | PASS | Migration dispositions, per-package rows and case-map gate agree with REM G1/DI-35. Exact incorporated case-level exceptions reconcile the unchanged annex body rule; unmapped edits, public signatures and named FC nodes remain protected absent approved equivalents. Every valid requirement needs executed coverage; retirement requires a reason. PC-10 selectors preserve the live/unrun distinction. Full case inventory and rewritten tests are appropriately future construction outputs. |
| PI-18 | PASS | Architecture canonical deliverable/DI-36 and Guide named chapter/package coverage require actual authored rewrites, diagrams, source/schema/metadata map, verified examples and fresh content review. REM G2 agrees. Chat `app.py:12,344,492` uses its own registry; selected families import shared Commands. CLI `commands.py:74` is a distinct public registry; CLI repl/main/server modules are placeholders and metadata has no launcher. Current guide index states alpha3, correctly identified for future reconciliation. |

## Findings and advisories

Mandatory numbered findings: **none**. There is no bounded corrective document change to request for this frozen candidate.

Advisory A-01 (low, optional): preserve the compact maintainer-facing package table as the readiness evidence grows. The already-required final trace table should provide direct per-consumer navigation to the exact directive node/selector and oracle. This is a readability suggestion, not an additional gate or a missing current artifact.

Residual risks already controlled by the plans: hosted-baseline identity/counting may not qualify; Docling release/Office mapping/OCR/resource feasibility is unmeasured; dynamic optional tool imports require actual installed discovery proof; broad Memory integration must remain within approved exact files. These risks do not invalidate planning readiness and do not receive executed-test credit.

## Independent rubric totals

| Coverage category | Score / maximum | Basis |
| --- | --- | --- |
| All-package inventory and source/dependency/test classification | 3.0 / 3.0 | All metadata members and corrected test discovery/classification checked. |
| Material behavior/configuration/data effects | 2.0 / 2.0 | Explicit changes and preserved behavior, namespace and recovery consequences. |
| Shared ownership/dependency/deployment consequences | 2.0 / 2.0 | Consistent neutral seams, counter/Docling split and separate adoption. |
| Traceable boundaries/compatibility/required proofs | 1.8 / 2.0 | Complete planning obligations; tracing is dispersed across large normative documents and selected-source feasibility is not an exhaustive runtime audit. |
| Unresolved readiness and approval completeness | 1.0 / 1.0 | Concrete readiness outputs and exact approval stops. |
| **Total** | **9.8 / 10** | Independent assessment; no averaging. |

| Overall category | Score / maximum | Basis |
| --- | --- | --- |
| Accuracy against current scope/source | 2.9 / 3.0 | Strong direct metadata and selected-source corroboration; dynamic caller completeness remains future audit. |
| Architecture/bounded delivery | 2.0 / 2.0 | Owners and causal boundaries explicit. |
| Data/configuration/dependency safety | 2.0 / 2.0 | Explicit origin, qualification, no overwrite/migration and offline/live separation. |
| Evidence/future distinctions/reproducibility | 1.5 / 1.5 | Frozen identities, pinned checks, honest future-work distinction. |
| Maintainer readability/approval/change control | 1.3 / 1.5 | Clear package table and gates; lengthy cross-document requirements require careful navigation. |
| **Total** | **9.7 / 10** | No mandatory finding is waived by scoring. |

## Reproduced checks, commands and limits

All Git/admin commands used the pinned wrapper with this seat's scratch. Custom subprocesses inherited `GIT_OPTIONAL_LOCKS=0` and `PYTHONDONTWRITEBYTECODE=1`. The wrapper allocated UV/XDG/tmp/mypy paths only beneath this scratch. No product test command in a plan was executed.

The exact wrapper prefix for the ARGV entries below was:

```text
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/read_only_command.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/astra-round6-independent-qlayd3lx --
```


```text
git diff b7c7b1393d6f18db3d26cc518adce2d8458f315a..ae813002a8537b35feb2d9492338b65fa13bff4b -- docs/planning/active/command-refactor/package-impact-assessment.md docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md docs/planning/active/command-refactor/test-migration-plan.md docs/planning/active/command-refactor/command-architecture-update-plan.md docs/planning/active/command-refactor/guide-update-handoff.md
```

Exit 0. Receipt: `/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/astra-round6-independent-qlayd3lx/command-1794425542571844000.json`.
Five-path correction diff inspected before aggregate review.

```text
uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate
```

Exit 0. Receipt: `/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/astra-round6-independent-qlayd3lx/command-1794425592934659000.json`.
Development board validation passed: 36 tasks

```text
uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py render --check
```

Exit 0. Receipt: `/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/astra-round6-independent-qlayd3lx/command-1794425593097103000.json`.
Planning dashboard is current

```text
uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-documentation-lifecycle.py
```

Exit 0. Receipt: `/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/astra-round6-independent-qlayd3lx/command-1794425593755708000.json`.
Documentation lifecycle validation passed: 1045 Markdown files checked

```text
uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-package-metadata.py
```

Exit 0. Receipt: `/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/astra-round6-independent-qlayd3lx/command-1794425593814159000.json`.
Validated 18 pyproject.toml files: version, license, authors, README, URLs, wheel package selection, and internal pins OK

```text
git diff --check 8390f3688d00985b1cac0443da8105f33fb1a6b7..ae813002a8537b35feb2d9492338b65fa13bff4b -- docs/planning
```

Exit 0. Receipt: `/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/astra-round6-independent-qlayd3lx/command-1794425593858547000.json`.


```text
git show b7c7b1393d6f18db3d26cc518adce2d8458f315a:docs/planning/active/command-refactor/execution-log.md
```

Exit 0. Receipt: `/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/astra-round6-independent-qlayd3lx/command-1794425653070092000.json`.
Historical log content deliberately not reproduced; exact prefix comparison only.

First command (exit 0):

```text
shasum -a 256 /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/round6/inputs/review-request.json
```

Opening and closing commands (each exit 0; LABEL respectively opening.json and closing.json):

```text
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/verify_identity.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-package-impact-hal86zs4/round6/inputs/review-request.json /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/astra-round6-independent-qlayd3lx LABEL
```

Both identity receipts: PASS; logical index before status `34a3b48276800231abf5478d9da5e4f67773f56b72a9f73ff20b0ebf8d2bb7ca`; candidate `ae813002a8537b35feb2d9492338b65fa13bff4b`; 17,750 protected files and six preserved metadata entries; no errors. The helper verified branch, HEAD, empty staging, every input pin and exact expected status:

```text
 M packages/friday-chat/config.example.yaml
 M packages/friday-chat/models-config.example.yaml
?? .friday-old/
```

The protected state was hash/metadata inspected only, never opened for semantic inspection. Append-only receipt: old log 231112 bytes, current log 232757 bytes, exact prefix preserved; old prefix SHA256 `c5cb73ee7702e20b52b2dc355b80f5d6c2a7990d73cd9d5705af03e3aef89817`.

Additional read-only evidence was produced by Python standard-library JSON/SHA256/TOML/AST inspection and targeted cat/sed/rg reads. A targeted rg invocation included a nonexistent guessed `commands/shared_bridge.py` path and emitted a missing-file diagnostic. It was resolved by searching the actual Chat commands directory, which identified session_views.py, diagnostics.py, memory_queries.py and pilot.py shared imports. No missing-path output was treated as evidence of product failure or proof of missing delegation.

Reproduced: hashes, identities, byte-prefix preservation and the five administrative checks. Inspected only: source, test declarations/selected bodies, dependency metadata, current normative documents and safe control snapshot. No supplied test receipt or historical council result was credited as newly reproduced proof. No runtime conformance or exhaustive dynamic call graph is claimed. Root Ruff534, test_display collection collision and legacy formatting/MAINT oracle debt remain unwaived and were not rerun. There is no whole-repository-green claim.

This report establishes current document readiness and selected-source feasibility only. It does not record maintainer package-impact satisfaction, Gate-A activation, construction approval, implementation acceptance, model qualification or delivery authority. The single authorized round ends here for this seat; no replacement or seventh round follows.

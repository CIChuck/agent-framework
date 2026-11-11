# VERIFIED — Astra independent directive review

Unit: CD-CMD-INGEST-GATE-A-001. Corrective pass 1/4; harness-global round 2.
Reviewer: Astra, gpt-6-astra, high effort, fresh task-only review context, 2026-11-11.

This is VERIFIED for the proposed isolated readiness-harness construction directive and its bounded planning aggregate. It is not implementation verification. Mandatory findings: **0**. Coverage: **10.0/10**. Overall: **9.6/10**. No construction, effects activation, model window, acceptance or delivery authority is granted.

## Candidate, authority and independence

Repository: `/Users/chuckrussell/Dev/gendev/agent-framework`.
Branch: `feature/cmd-ingest-001`.
Candidate: `23253a72ba265334e254c6a0bbad53f70cd85313`.
Base: `35df1fa35162fdd70216ed47e5675a74c748139b`.
Aggregate range: `35df1fa35162fdd70216ed47e5675a74c748139b..23253a72ba265334e254c6a0bbad53f70cd85313`.
Prior normative directive source: `f81453695007cacfa072fe295b8da7aa478438ba`.
Mode: proposed remediation delta RC-01–06 first, followed by full bounded current directive/readiness aggregate HRC-01–16 and HR-01–18. Relevant approved parent obligations were checked without reopening the whole product design or requiring later implementation proof.

The request was hashed BEFORE reading it: SHA256 `d5c04007476e093519d795a3224d638ce7d4576dabd09f0a009fc200d9d92953`. Helper SHA256 `7a7f2ef72d4b1e6592e6ba65d2762641865031a81e7bfdfc573b9ec5d56a11e5` matched; its source was read before execution. Both initial shasum checks exited 0. The complete 27-entry authority manifest is in `request.json`, independently verified at both boundaries; current controls and protected-manifest pins also passed the helper. Directive SHA256: `9925170d3ca55c7429bb5a08132f175aa9690f6a80757a3bda52a58944854d3f`.

Applied the supplied repository council and independent-code-validator skills solely to this seat. User instruction overrides their generic delegation workflow: no delegates, repairs, reissues or further passes were started. No memory lookup, prior thread/history search, builder transcript, council-round1 report/evidence or directive_council_history was opened. The supplied correction map was a location index only. Safe current-controls includes historical review labels/status statements; pinned parents also contain older review labels and links. These were encountered as navigation/provenance, not used as current correctness evidence. No historical review archive was followed. Generic environment guidance was provided by the harness but was not used to derive this verdict.

The shared checkout exception is explicit. This is a pinned mixed checkout, not a clean detached review worktree. The two dirty Chat example YAML contents were not opened. Protected status path names were visible in the supplied manifest; underlying .friday*/store contents were not opened. Reviewer-owned private external scratch: `/tmp/astra-ingest-review-QtIDzDTs` (canonical macOS alias may be `/private/tmp/astra-ingest-review-QtIDzDTs`), created by mktemp outside both checkout and supplied controller/input trees. Only that scratch received reviewer writes.

Additional commit-object pin inspection found 25 authority files identical in candidate and worktree. The two skill authorities are explicitly pinned **working authority**, not identical committed candidate inputs: council SKILL.md is absent at candidate (git show exit 128), and independent-code-validator SKILL.md has different committed bytes. Their requested working-byte SHA256 values match exactly at opening and closing. This does not contradict the self-contained request: it supplies exact authority hashes separately from candidate identity. No committed skill substitute was used. `pin-verification.json` and `pin-commands.json` preserve this distinction; the empty-output SHA recorded for council is not a successful object digest.

## Findings and residual observations

No violated mandatory requirement or concrete document correction is identified.

1. **ASTRA-A01 — advisory; native profile qualification remains substantial work.** E:43–71,193–227, D:99–108 and HR-15/17 correctly require actual config/credential/proxy/discovery neutralization and separate native detection. A Python hook cannot guarantee arbitrary native behavior. Risk: a later implementation may mistake empty environment variables or a green Python refusal test for native containment. Mitigation already required: exact tool profiles, bounded declared metadata observations, blocked unknown channels and fail-on-change. Future proof: poisoned private settings, positive guarded children, intentional fake native-cache writes detected as failure, and missing/truncated coverage refusal. No extra current document fix or production experiment required.
2. **ASTRA-A02 — advisory; operator facts remain an explicit activation dependency.** E:229–292, P:301–330 and I:114–145. A read-only listing alone does not establish immutable artifact identity, safe JIT/TTL/eviction policy or log separation. Risk: later activation could overclaim observation from an alias or downloaded listing. Mitigation already required: exact preloaded instance/profile, labelled operator attestation, version-qualified selected status route, no unsafe/unknown policy, and blocking unsupported qualification. Future proof: private valid and invalid simulated transport flows, then separately authorized real qualification. No new server, settings change or extra endpoint is requested.

## Citation key

All relative paths below are under the exact repository above; line numbers refer to frozen current bytes.

- **D**: `docs/planning/active/command-refactor/directives/CD-CMD-INGEST-GATE-A-001-readiness-harness.md`.
- **E**: `docs/planning/active/command-refactor/validation/document-ingestion/gate-a/execution-contract.md`.
- **P**: same Gate-A directory, `readiness-plan.md`.
- **I**: same Gate-A directory, `isolation-requirements.md`.
- **J**: same Gate-A directory, `effects-envelope.json` (JSON field citations).
- **C**: same Gate-A directory, `correction-loop/pass1/criteria.md`.
- **A**: same Gate-A directory, `correction-loop/authorization.md`.
- **R**: `docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md`.
- **B**: `docs/planning/active/command-refactor/embedding-compatibility-contract.md`.
- **W**: same Gate-A directory, `consumer-readiness-matrix.md`.
- **S**: same Gate-A directory, `source-observations.json`.
- **Controls**: pinned supplied `current-controls.json`, copied into reviewer evidence.

## Correction matrix — independently assessed first

PASS below means a coherent implementable design obligation, not a completed runtime test.

| Criterion | Result | Independent assessment and evidence |
| --- | --- | --- |
| RC-01 | PASS | E:10–41, D:89–93,150–167,192. External interpreter/stdlib/launcher trust precedes execution. -I alone is insufficient; -S suppresses site initialization and -B makes bytecode behavior explicit. Explicit file loading resolves the sibling-path issue without re-enabling site or .pth. Python 3.13 -S prefix behavior is explicitly addressed by distribution manifests. Positive startup and armed unsafe controls prevent setup failure receiving guard credit. All entrypoints/workers and optimized lanes are covered. |
| RC-02 | PASS | E:133–191, D:109–118,169–174,193; J.promotion_policy/time_accounting. Init is immutable; later facts extend a single-writer strict hash-chained ledger with explicitly authorized receipts. A0/A1/A2 candidates exist before promotion, prepare-model precedes batch promotion and window receipt. Receipt anchors a promoted prefix rather than an ever-changing tip; ordinary execution descendants preserve it and scope promotions invalidate it. all exits on missing gates; cumulative budgets and uncertain attempts survive resumes. No cyclic up-front digest or human-wait process is required. |
| RC-03 | PASS | E:45–71, D:99–103,194; J.tool_isolation. Exact target/cwd/config roots, uv no-config and no dotenv, no pip executable, no inherited credential/proxy/keyring/netrc fallback, direct HTTP without system proxies, explicit TLS origin and validation-tool boundaries. Unknown or unsupported suppression blocks the profile. Fake settings prove effective origins, without modifying real HOME. This is feasible as qualified profiles, not an assertion every ambient tool is safe today. |
| RC-04 | PASS | E:75–129, D:94–103,195; J.source_export. Minimal private bare control directory separates object reads from production config/index/ref discovery. Declared read-only alternate objects and explicit object-ID operations can export regular blob bytes without smudge/filter/checkout. Commit/tree/type/length/hash and output hashes are checked; absent objects cannot fetch. Metadata rehearsal is a separately bound overlay with code equality. Logical-index evidence comes from a stable private index copy, with split-index qualification or stop. This does not require production Git mutation. Actual export qualification remains future private-fixture proof. |
| RC-05 | PASS | E:195–227, I:174–193, D:104–108,196. Prevention, bounded detection and uncovered native channels are distinct. Explicit metadata-only roots include absent defaults; truncation fails. Outside writes invalidate isolation and stop work, without cleanup or retrospective prevention claims. Malicious OS/operator and universal filesystem protection are not claimed. |
| RC-06 | PASS | E:229–292, D:130–136,197; J.model_window_policy. Exactly one version-qualified GET native status profile; V0 instance limits remain attested. A pre-existing safely loaded instance and no JIT/idle unload/eviction are prerequisites, not management API tasks. Requests are only selected status plus embeddings, all charged to 64 requests. Before/after state checks supplement continuous attested conditions rather than pretending to close a race. Sticky stop is checked before requests outside the writer lease; in-flight limits are honestly disclosed. |

The exact prior normative directive delta is retained as `directive-delta.diff`. Current E is the added detailed contract, read in full. Plan/envelope/isolation changes were compared directly with the prior normative source; no prior reviewer disposition was used as closure proof.

## Full bounded aggregate matrix

| Criterion | Result | Evidence and rationale | HR trace |
| --- | --- | --- | --- |
| HRC-01 | PASS | D:3–45,74–85; A; Controls board/current_scope. Design-only review, construction, stage activation, model window and acceptance remain distinct. Nine business inputs stay pinned. Older parent status prose does not override current explicit controls. | 12 |
| HRC-02 | PASS | D:47–70; I:24–45; opening/closing changed-path validation. Test-only named code scope plus sole root ignore rule; no product or environment edits. Actual candidate delta is planning-only. | 01 |
| HRC-03 | PASS | E:8–71; D:89–103,162–167. Trust roots, no site, explicit imports/guards, private tool/worker targets and no working-venv fallback are coherent; unknown tool capabilities stop dependent work. | 03,10,13,15 |
| HRC-04 | PASS | I:75–103; P:87–105; E:101–129,204–227. Physical ancestor/alias/symlink checks, regular-blob export, new immutable publication directories, bounded manifests and honest native limits. Hash-bound asset/input reuse never authorizes overwrite. | 01,03,04,16,17 |
| HRC-05 | PASS | D:143–174; E:133–191,294–303. No-effects preflight versus absent-root init; owned explicit reopen; full/selected/offline/report operations; nonzero awaiting/incomplete status and no report-render readiness inference. | 02,09,14 |
| HRC-06 | PASS | P:41–60,175–257; J candidate_requirements/security_floor/stages; S seed status. Exact URLs/hashes/licenses/platform and promoted transitive manifest precede installation; Certifi floor checked after all installs in target normal/-O lanes. Seeds are observations only. No unlisted extras/builds/mirrors. R:200–330 is preserved. | 04,10,12 |
| HRC-07 | PASS | I:107–145; E:229–292; J.model_window_policy. Production shutdown/restart/log separation are operator prerequisites; exact receipt, expiry, sticky revocation, per-request checks and budgets. No harness service authority. | 05,08,18 |
| HRC-08 | PASS | P:109–137,296–330; E:229–262. Served assets are endpoint-only exception; Docling/OCR/tokenizer assets and application state remain private. Missing version/model/counter/status facts block A3, without inventing capabilities or blocking independent offline work. | 05,07,18 |
| HRC-09 | PASS | P:259–280; I:147–159; D:124–129. At least 30 genuine fixtures, independent late-content/order/formula/notes/hidden-content/refusal oracles; supplied documents explicit copies only. R section B remains the acceptance contract; diagnostics cannot count as content. | 06 |
| HRC-10 | PASS | P:282–294,312–330; R:526–664; D:127–129. Three strategies, 512/default override boundaries, full contextualized model input, no truncation/estimated enforcement; preliminary counts/synthetic vectors cannot establish real model qualification. | 07 |
| HRC-11 | PASS | D:14–19,137–141; P:195–198,324–352; W; B compatibility and proof matrix; Tools companion delivery sequence. No Memory/Chroma writes, no feature extraction, no new URL/automatic-tool route. Later B/N/R consumer proofs, test migration and substantive guides remain obligations. | 01,09,12 |
| HRC-12 | PASS | P:139–156; J.budgets/document_probe_limits; E:181–191,264–285. Finite requests/bytes/disk/RSS/thread/time/admission and child quiescence; only owned work may be stopped. Time is cumulative active execution, with unchanged numeric ceilings. No runtime effects authorized here. | 03,08,18 |
| HRC-13 | PASS | D:150–167,178–205; E:36–41,68–71,222–227,287–292. Minimal core and explicit dependency profiles; private positive/negative controls in normal/-O; setup failures and skips earn no semantic proof. Root pyproject.toml:134 confirms tests/ is excluded from default testpaths. | 04,06,07,10,11,13–18 |
| HRC-14 | PASS | D:137–141,188–191; E:294–303; I:188–193; P:332–348. Explicit execution/inspection, attestation/observation, prevention/detection, candidate/promotion/qualification and scope distinctions; source/private-target origins and protected-state evidence required. | 09,12,17 |
| HRC-15 | PASS | Controls; A; pinned pass1 roster; helper admin results. Current state is design_only/remediation/in_review for this bounded pass, with exact three named seats and four-pass cap. No implementation/effects/window facts inferred; broad historical navigation was not opened. | 12 |
| HRC-16 | PASS | D:207–220; P:354–370; E:62–66,153–179,229–292. Clear remaining approvals/facts, stop-on-unknown/scope-drift and separate fresh implementation validation. No later product/store proof demanded now. | 04,05,08,12,14,18 |

## Complete HR trace

All rows are **design PASS; future execution not claimed**. Requirement text is D:180–197 respectively.

| Requirement | Current controlling evidence | Future proof to retain |
| --- | --- | --- |
| HR-01 | D:47–70; I:24–103 | Scope inventory and protected-state equality. |
| HR-02 | D:94–98,143–174; E:75–78 | Successful manual modes; zero-effect preflight including startup. |
| HR-03 | E:17–71,193–227; I:75–96 | Before-effect refusals for intercepted operations and separately labelled native evidence. |
| HR-04 | E:101–108,139–163; P:192–202,246–257 | Missing/tampered/extra/unknown/stale controls reaching semantic assertions. |
| HR-05 | E:237–292 | Invalid windows and unsafe loaded state cause no unauthorized calls; valid preloaded flow succeeds. |
| HR-06 | P:259–280; I:147–159 | Independent genuine content and preservation oracles, not extension-only files. |
| HR-07 | P:282–294,312–330; R:D/E | Three strategies, prepared-input boundaries, model parity and honest preliminary labels. |
| HR-08 | E:181–191,264–285; J.budgets | Resumes/crashes cannot reset counters; owned shutdown and per-request stop/expiry. |
| HR-09 | E:294–303; I:188–193 | Human/JSON reports preserve all evidence distinctions and incomplete states. |
| HR-10 | E:10–41; D:162–167 | Stdlib core positive; private profile worker positive; no live environment fallback. |
| HR-11 | D:150–167,199–205; pyproject.toml:134 | Explicit normal/-O selectors and private validation tools/caches. |
| HR-12 | D:191,207–220; P:334–352 | Stable candidate, exact origins/receipts and independent implementation review. |
| HR-13 | E:36–41 | Armed unsafe private canaries plus safe positive startup across all entries/workers. |
| HR-14 | E:133–191 | Valid promotion/resume, tamper/order/concurrency/stale rejection, execution-prefix receipt continuity. |
| HR-15 | E:43–71 | Poisoned fake config/proxy/credential/parent roots; effective tool origin proof. |
| HR-16 | E:73–129 | Exact committed blobs, excluded dirty traps, unchanged production Git state. |
| HR-17 | E:193–227 | Fake native write detection, explicit worker guard positive, unknown/truncated snapshot refusal. |
| HR-18 | E:229–292 | One selected version-qualified status API, exact loaded request ID, safe policy and counted before/after observations. |

## Source-feasibility checks and limits

Targeted source inspection confirms why full assembly must be avoided: `packages/friday-runtime/src/friday_runtime/di.py:244–302` creates graph directories, vector adapters, transcript storage and collection managers. D:137–141 and P:312–319 prohibit using that assembly for the readiness probe. Existing `packages/friday-llm/src/friday_llm/embeddings.py:326–410` contains internal retries around LiteLLM requests: budget enforcement therefore must cover attempted transport calls, not just outer method invocations, as E:187–188 and E:264–271 require. This is an implementation acceptance concern already covered by the draft, not authority to edit the service. `pyproject.toml:134` confirms explicit test selectors are necessary. Workspace build metadata names hatchling (root:147–148, Tools:88–89, Commands:19–20); private build-tool manifests and guarded Python workers are necessary under E:17–34/P:206–210, with no production tool borrowing.

Private Git object view is feasible by static mechanism analysis: independent bare control metadata plus declared object alternates supports object-ID reads without checkout discovery. Exporting raw regular blobs avoids worktree transformations. Split-index dependencies are explicitly either qualified or refused. No actual view, fixture repo or build was created in this seat, and no supported-target Git/tool/server capability is claimed experimentally established. No internet or endpoint verification was performed, as prohibited for this review. Source observations and referenced upstream facts remain inspected planning inputs, with exact installed versions/APIs to qualify at activation.

## Executed commands and evidence

All eight permitted administrative commands exited **0**. Exact argv, cwd, timestamps, stdout/stderr file paths and exit codes are recorded in `commands.json`. This was a fresh helper execution, not replay of a supplied receipt. Its environment used reviewer-owned UV/XDG/mypy/temp/bytecode cache paths, removed inherited Python environment overrides specified in the helper, and set GIT_OPTIONAL_LOCKS=0.

| Check | Exact argv (cwd repository) | Exit |
| --- | --- | --- |
| Board | uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate | 0 |
| Dashboard | uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py render --check | 0 |
| Documentation | uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-documentation-lifecycle.py | 0 |
| Metadata | uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-package-metadata.py | 0 |
| Worktree whitespace | git diff --check -- docs/planning | 0 |
| Staged whitespace | git diff --cached --check | 0 |
| Unit whitespace | git diff --check 35df1fa35162fdd70216ed47e5675a74c748139b..23253a72ba265334e254c6a0bbad53f70cd85313 -- docs/planning | 0 |
| Preparation whitespace | git diff --check f81453695007cacfa072fe295b8da7aa478438ba..23253a72ba265334e254c6a0bbad53f70cd85313 -- docs/planning | 0 |

Helper invocations (all exit 0):

```text
python3 -I -S -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-harness-loop-p1-1l9b_pck/inputs/review_tools.py boundary --request /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-harness-loop-p1-1l9b_pck/inputs/request.json --scratch /tmp/astra-ingest-review-QtIDzDTs --label opening
python3 -I -S -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-harness-loop-p1-1l9b_pck/inputs/review_tools.py admin --request /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-harness-loop-p1-1l9b_pck/inputs/request.json --scratch /tmp/astra-ingest-review-QtIDzDTs
python3 -I -S -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-harness-loop-p1-1l9b_pck/inputs/review_tools.py boundary --request /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-harness-loop-p1-1l9b_pck/inputs/request.json --scratch /tmp/astra-ingest-review-QtIDzDTs --label closing
```

Helper boundary Git argv in execution order at each boundary: `git ls-files -s -z`, `git status --short --untracked-files=all`, `git rev-parse HEAD`, `git branch --show-current`, `git diff --cached --name-only`, `git diff --name-only 35df1fa35162fdd70216ed47e5675a74c748139b..23253a72ba265334e254c6a0bbad53f70cd85313`. All exited 0; logical index was calculated BEFORE status.

Additional read-only Git: `git diff --stat` and `git diff --unified=0` against the stated prior/candidate range, restricted to D/P/I/J/E (stat) or D and P/I/J (content); all exit 0 and GIT_OPTIONAL_LOCKS=0. The D diff is saved. Exact 27 additional `git show <candidate>:<authority path>` argv/exits are in `pin-commands.json`; one exit 128 as disclosed, all other exits 0. Read-only cat/nl/sed/rg/wc inspections supplied the cited document/source observations; they ran successfully and no product code was imported or executed. Scratch creation command was `mktemp -d /tmp/astra-ingest-review-XXXXXXXX` (exit 0). Report/evidence generation used isolated stdlib Python and shell writes to reviewer scratch only.

Fresh admin output: board 36 tasks; dashboard current; documentation lifecycle 1066 Markdown files; metadata 18 pyproject.toml files; all whitespace checks clean. These structural checks do not establish technical runtime correctness.

## Opening/closing integrity and skipped lanes

Opening at `2026-11-11T23:09:05.716973+00:00`, closing at `2026-11-11T23:12:18.619636+00:00`: **PASS**, no failures. Both record candidate above and logical index SHA256 `2ac4171989e649cbdcfe9ed53211dd32ff0685503eccec3c050fcf23a4cda073`; 17,861 tracked-file hashes, 27 authority pins, 9 preserved metadata records match. Status, branch, HEAD, empty staging and exact planning-only changed paths match. The helper includes the declared absent-path protection; no .friday_test environment was created. Raw authority was hash-checked without opening its history. Evidence: `integrity-opening.json`, `integrity-closing.json`.

No tests, dependency installs/syncs, builds, services, endpoint/model/provider calls, store operations, source edits, Git writes, worktrees, cleanup or nested agents. Current harness does not exist; future positive/negative normal/-O proofs were assessed as requirements, not run or demanded at this document gate. No later product/store/consumer integration proof was demanded. Historical Ruff534, root test_display collection conflict and registry formatting debt remain failed/unwaived, were not rerun and receive no fresh passing credit.

## Scores and next gate

Coverage uses the prescribed dimensions: all 16 HRC criteria assessed (5.0/5.0) and every HR-01–18 traced with its future proof (5.0/5.0): **10.0/10**. All six RC closure questions were also independently assessed. This is review coverage, not executed implementation coverage.

Overall prescribed rubric: scope/authority **2.0/2**; isolation/effects enforceability **2.85/3** (native version qualification and attested server preconditions remain materially demanding); clarity/feasibility **1.90/2** (dense multi-document operation); verification/evidence **1.90/2** (strong positive/refusal obligations, practical proof quality still an implementation responsibility); manual operator usability **0.95/1** (explicit staged workflow but numerous receipts/profiles). Total **9.60/10**. These deductions describe residual design complexity, not missing current runtime evidence or mandatory defects. No score was adjusted to waive a finding.

Return this seat result to the controller for the current council aggregation. This seat does not authorize or launch another review, construction, activation, model window, acceptance or delivery. Remaining actual interpreter/tool/model facts and exact approvals must be supplied at their specified later gates.

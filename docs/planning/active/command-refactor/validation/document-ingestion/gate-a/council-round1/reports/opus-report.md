# CD-CMD-INGEST-GATE-A-001 — Council round 1, Opus seat report

**Formal outcome: CHANGES_REQUESTED**

Five mandatory findings (1 Major, 4 Medium) and seven advisories. Coverage score 8.6/10; overall score 8.3/10. Both are below the 9.5 target. The scores were not adjusted to reach the target, and the target does not waive any finding. This report grants no construction, effects, window, acceptance or delivery authority.

## 1. Identity, independence and frozen inputs

| Item | Value |
| --- | --- |
| Seat | Opus — Claude Opus 5.5 (`claude-opus-5-5`), Claude Code harness under T3 Code |
| Context | Fresh task-only context. No builder transcript, no memory search, no history search, no peer report opened. No current peer verdict supplied. |
| Relevant exposure | The auto-loaded user memory index (general Friday framework notes) was present in context. It is unrelated to this unit and was not used as evidence. Current-controls navigation text mentions the earlier round6 council as VERIFIED. That is a historical label only, not peer evidence for this unit. |
| Request | `/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-harness-council-r1-3kkwwzkk/inputs/request.json`. SHA256 `651d8edfa6d1afb952418ee393b5f1369eadce2ef6b73eeb63eeb61c37320a44`, verified before reading and again at close. |
| current-controls.json | `6692e709d1167c48723fa853461d02d6538101cd4c9db5f95a730fb21b1d6508` (matches the request) |
| protected-manifest.json | `d1fc0015ea83ef13ae62c8f96b881f072b524d62471f89030dddde01dfb32256` (matches) |
| review_tools.py | `7a7f2ef72d4b1e6592e6ba65d2762641865031a81e7bfdfc573b9ec5d56a11e5` (matches). Source read in full before running. It only runs read-only `git ls-files/status/rev-parse/branch/diff` with `GIT_OPTIONAL_LOCKS=0`, writes only to the scratch, and runs admin commands offline/frozen/no-sync with private UV/XDG/mypy/pycache/TMP. |
| Candidate | `f81453695007cacfa072fe295b8da7aa478438ba` on `feature/cmd-ingest-001` |
| Construction source | `494eed4f1c15d79d29cf0acc5e2203d7c7ebe5ef`. The directive blob `b4c9b0dd55d926f91c42bcf0ab5c81890fa62cf1` is identical at the source and at the candidate. |
| Directive SHA256 | `e44d4e4b28736d66a1de1e66314cb6da25343430dec0933be4ac9f1645ec91ad` (verified by the boundary helper's 24 authority pins) |
| Diff | `72c5d736..f8145369`, 18 paths, all under `docs/planning/` (the helper's check passed) |
| Scratch (own, external) | `/private/tmp/claude-501/-Users-chuckrussell-Dev-gendev-agent-framework/b636ec71-b4d2-4b21-9c9f-a41503241b90/scratchpad/igh-r1-opus-1794433942` |

## 2. Commands and exits

| # | Command (cwd) | Exit | Result |
| --- | --- | --- | --- |
| 1 | `shasum -a 256` of the request and the inputs | 0 | All four hashes match the pins |
| 2 | `python3 -B …/review_tools.py boundary --request … --scratch <own> --label opening` | 0 | PASS. HEAD/branch/index/staging/status unchanged; 17,773 protected files; 24 authority pins; 9 preserved records; logical index `2873bdac…0d46`. Evidence: `integrity-opening.json` |
| 3 | `python3 -B …/review_tools.py admin --request … --scratch <own>` | 0 | board validate 0 (36 tasks); dashboard `render --check` 0 (current); documentation lifecycle 0 (1058 Markdown files); package metadata 0 (18 manifests); whitespace worktree/staged/unit/preparation all 0. Ledger: `commands.json`, plus `*.stdout`/`*.stderr` |
| 4 | Static read-only `git diff/grep/ls-files/rev-parse/status` (`GIT_OPTIONAL_LOCKS=0`, run after the opening boundary), `grep` and `sed` on documents and scripts | 0 | Evidence: `static-evidence.txt` |
| 5 | `python3 -B …/review_tools.py boundary … --label closing` | see §9 | Evidence: `integrity-closing.json` |

Before running command 3, I read `scripts/friday-dev-board.py` `_command_render`. Its check mode only reads; it does not write.

**Not executed:** root or package tests, root Ruff, mypy, live Finance tests, builds, dependency resolution, installs, conversions, inference, and any network/LM Studio/provider/store call. I did not inspect the dirty YAML contents, `.friday/` or `.friday-old/`; only the names of the dirty files were listed. Known baseline debt (root Ruff 534, the `test_display` collection conflict, registry formatting) was not re-run. It remains FAILED/UNWAIVED historical debt, and nothing here is a whole-repo green claim.

## 3. What was read

- AGENTS.md.
- The independent-validation policy: authority chain and Construction Directive Gate, lines 36–110.
- The council skill and the independent-validator skill. Repository-engineering and lifecycle policies were consulted through AGENTS.md, which states the operative rules. They were hash-verified by the boundary helper but not re-read line by line.
- The complete directive (244 lines), complete criteria HRC-01–16, the authorization and the roster.
- Pinned Gate-A parents in full: readiness-plan v0.3, isolation-requirements v0.2, effects-envelope.json, consumer-readiness-matrix and planning-checks.json. Source-observations.json was summarised programmatically (keys and seed package/asset records).
- All 18 changed paths: full diffs of the board, dashboard, branch-handoff, current-verified-report, execution-log additions and authority.json; navigation text through current-controls.json. Execution-log append-only check: 0 deleted lines.
- Source-feasibility probes, each tied to a concrete claim:
  - `pyproject.toml` testpaths (HR-11).
  - `.gitignore` entries (the `/.friday_test/` claim).
  - Committed `packages/*/src` greps for dotenv/home/cwd discovery (ambient-config claim).
  - `config_templates` names (B01 versus the dirty files).
- I did not restart the parent product-design audit (REM, assessment, compatibility annex and related documents are pinned and treated as approved inputs).

## 4. Findings

### IGH-R1-OPUS-001 — Major, mandatory
**The manual stage-promotion, init-binding and window-receipt lifecycle is incoherent for `full`/`all` and multi-stage runs.**

**Violated:**
- HRC-05: manual full/selected operation, owned continuation, complete vs. incomplete.
- HRC-06: effects promotion.
- HRC-07: receipt binding.
- Directive §Required behavior 2 and 4, §Manual interface lines 182–185.
- Plan §Stage promotion lines 151–156 and §Activation checklist lines 333–338.

**Evidence:**
- `init` "binds source/config/manifest hashes" (directive line 97). Later commands may reopen the run "only if its binding still matches" (lines 99–101).
- The plan requires that "each transition still requires a recorded, complete manifest before its effects", reviewed by the Codex controller (plan 151–156). A1/A2 "require exact promoted artifact/license manifests" (plan 335–336). Those manifests are A0/A1 outputs of the run.
- The A3 receipt must contain "Run ID and effective config, dependency, asset and input manifest hashes" (directive 150).
- The interface nevertheless advertises a single `run … --stage all --window-receipt <receipt>` (line 184). The plan budget is "Two hours overall" (plan 138).

**Risk:**
- For a fresh run, the operator cannot write a valid receipt before invocation, because the manifests it must bind do not exist yet.
- A mid-run promotion changes what init bound. That trips the "binding still matches" refusal, unless the binding is a ledger the directive does not define.
- `all` would have to pause for human review (and blow the 2-hour wall budget), or silently skip promotion.
- The builder must invent the promotion record format, its storage and its effect on run binding. That is the kind of authority invention HRC-16 forbids. Manual operators get either an unusable `all` or a gate that can be bypassed.

**Narrow mitigation:**
- Define an append-only, hash-chained run binding ledger. `init` records source/config/seed. Each stage writes a candidate manifest. A separate explicit promotion record (reviewer identity, manifest SHA256, time) is supplied to the run as a test-owned input and appended to the ledger.
- Later stages verify the ledger chain. They do not compare against a static init snapshot.
- `--stage all` runs consecutive stages whose promotion/receipt prerequisites already exist, then stops with an explicit `awaiting-promotion` or `awaiting-window` state. It never pauses interactively and never auto-promotes.
- The receipt is prepared after A2 promotion and binds the promoted manifest hashes from the ledger.
- State that the wall-clock budgets apply per stage invocation, not across human waits.

**Proof (future construction):**
- CLI/ledger tests for:
  - `all` stopping at each missing promotion;
  - a resumed run after promotion that is accepted;
  - a tampered or out-of-order ledger that is refused;
  - a receipt binding pre-promotion hashes that is refused.
- README walkthrough of the multi-invocation flow.

### IGH-R1-OPUS-002 — Medium, mandatory
**Ambient tool configuration and credentials can reach test processes through the un-repurposed HOME, macOS system proxy settings and upward discovery from the in-project `.friday_test/`.**

**Violated:**
- HRC-03: configuration/environment isolation.
- HRC-06: no unknown mirror.
- Isolation-requirements lines 81–83 ("do not inherit application configuration, provider credentials, Python paths or proxy settings").
- Directive item 3 ("minimal environment allowlist without repurposing HOME") and item 5 ("no … unknown mirror").

**Evidence:**
- The directive deliberately keeps HOME (line 106) and controls only environment variables.
- Tools the harness must run read HOME/system files that are not environment variables:
  - uv user/system `uv.toml` (index or mirror redirection);
  - pip config;
  - `~/.netrc` (index credentials honoured by uv, pip and requests);
  - git global/system config (needed for any source export, see -003).
- Python `urllib`/requests on macOS read **system** proxy settings via `_scproxy` even with a clean environment.
- `.friday_test/` is nested inside the checkout (envelope `paths.test_workspace`). Any tool that walks upward from a run directory (git repository discovery, uv project/workspace discovery outside the export root, Ruff/pytest config discovery) resolves to the production `pyproject.toml` or `.git`.
- My grep found no `load_dotenv`/`find_dotenv` and no `Path.home()`/`Path.cwd()` discovery in committed `packages/*/src` (`static-evidence.txt`). The application import path is therefore not the exposure; the tool layer is.

**Risk:**
- A0/A1 could resolve or transfer through a user-configured mirror or with user credentials. The allowed-host claim would rest only on configuration the harness did not control.
- A child could discover and operate against the production repository or workspace configuration.
- The isolation claim would be certified by intent.

**Narrow mitigation:** add a required "ambient configuration neutralization" clause:
- Every tool invocation uses its documented no-config/isolated flags, or points its config and credential variables at run-owned empty files. Examples, to be confirmed by the builder against the pinned tool versions: uv `--no-config`; pip isolated mode with `PIP_CONFIG_FILE` set to an empty run file; `NETRC` set to an empty run file; requests/httpx `trust_env=False` or explicit `NO_PROXY` handling; `GIT_CONFIG_NOSYSTEM=1` and `GIT_CONFIG_GLOBAL` set to an empty run file.
- Every child invocation passes an explicit project/working directory. Repository/workspace discovery is bounded (for example `GIT_CEILING_DIRECTORIES` and explicit `--project`/`--directory`).
- Record each tool's effective configuration origins in the report.
- Treat any unneutralizable channel as a stop.

**Proof (future construction):**
- Offline unit tests asserting the constructed child environment and argv for every tool profile. Use a fixture HOME-like directory passed only to the test, never the real HOME.
- A report section listing the effective configuration origins.
- A negative test showing that a discovered parent `pyproject.toml` or `.git` is refused.

### IGH-R1-OPUS-003 — Medium, mandatory
**The source-export mechanism is unspecified: Git non-mutation and exclusion of dirty or untracked state are not bound.**

**Violated:**
- HRC-03: isolation before effects, no live-checkout fallback.
- HRC-02 boundary: zero production checkout change.
- Directive line 97 ("copies the harness and source export") and line 163 ("Do not read the dirty production YAML").
- Plan line 161 ("Freeze a clean export of the current source").

**Evidence:**
- Neither the directive nor the parents define how the export is produced, from which commit, or which Git operations are permitted (grep: `static-evidence.txt`).
- The checkout has two dirty tracked package files: `packages/friday-chat/config.example.yaml` and `packages/friday-chat/models-config.example.yaml`. Only the names were observed.
- Untracked `.friday-old/` exists, and ignored `.friday/` and `.env` exist by policy.
- `.git` is not in the forbidden-edit list (lines 68–72), although the council's own protected state treats the logical index as protected.

**Risk:**
- A working-tree copy would read and ship the dirty YAML (and possibly ignored state) into the export.
- Git operations such as `worktree add`, `stash`, `checkout`, or `status`/`diff` without `GIT_OPTIONAL_LOCKS=0` (which rewrites the index) mutate production `.git`.
- The exported "source" would not correspond to any reviewable commit.

**Narrow mitigation:** specify that the export is:
- created from an exact, recorded commit/tree ID via read-only object access (for example `git archive <commit>`);
- run with `GIT_OPTIONAL_LOCKS=0` and neutralized Git configuration (see -002);
- free of worktree/stash/checkout/reset/index-writing commands.

Dirty, untracked and ignored paths are excluded and reported by name only. Add `.git/` (index, refs, worktrees, config) to the forbidden mutations. Treat the harness copy the same way: either from the committed candidate, or recorded as an uncommitted-bytes binding.

**Proof (future construction):**
- An export test asserting a byte-identical tree against `git ls-tree` for the recorded commit.
- Absence of dirty-file working-tree bytes (compare blob IDs, never content).
- An unchanged `.git/index` SHA256 and refs before and after `init`.

### IGH-R1-OPUS-004 — Medium, mandatory
**The protected-state and detective scope omits global caches and HOME tool directories. "Refuse before effects" is unattainable for non-Python children and native code, and the directive does not separate prevention from detection.**

**Violated:**
- HRC-03 (no global-cache fallback) and HRC-04 (accurate containment limits, not intent).
- HRC-12 (measurable controls).
- HR-01 and HR-03.
- Isolation-requirements lines 158–169.

**Evidence:**
- HR-03 requires guards that "refuse … global-cache fallback and unowned subprocesses before effects".
- Python audit hooks see only events in instrumented Python interpreters. They do not see:
  - uv, which is a native binary;
  - native libraries' own I/O or networking;
  - children that do not load the guard.
- HOME is intentionally not repurposed (directive 106), so library defaults resolve into user cache directories (Hugging Face, Docling, uv, pip, torch) unless every variable is set and honoured.
- HR-01 "production protected-state checks" and isolation-req "opening/closing protected-state checks" define no scope beyond production. Global/user caches are not enumerated, so a native fallback write would pass undetected.

**Risk:**
- The harness could report "isolated" while writing into shared user caches that production also uses.
- That is a change to the production environment the maintainer excluded, certified from intent.

**Narrow mitigation:**
- Split the HR-03 claim into prevented events (Python-visible, refused before effect) and detected events (non-Python/native, verified by before/after evidence that fails the run).
- Enumerate a protected-state scope: the checkout and `.git`; `.venv`; `.friday/`; `.friday-old/`; `.env`; plus a metadata-only (path/size/mtime, no content) snapshot of the specific default cache roots of every manifest tool and library. The LM Studio model directory is listed as read-never.
- Any change attributable to the run fails isolation credit.
- Child Python processes load the guard explicitly (for example a run-owned `sitecustomize` in the target), and that is proved in a test.

**Proof (future construction):**
- A negative witness in which a child writes to a simulated default cache root (inside a test-owned fake root), and the detective check fails the run.
- A report table classifying each control as prevent or detect, with its limits.

### IGH-R1-OPUS-005 — Medium, mandatory
**A shared-LM-Studio inference request can itself load, swap or evict models (JIT loading, idle TTL, auto-evict). The directive prohibits model load/unload but specifies no precondition, receipt field or observation that prevents a request-triggered load.**

**Violated:**
- HRC-07: exact model/request scope, no service-management rights.
- HRC-08: no unsupported server capability assumed.
- Directive lines 167–169 ("No … model load/unload") and 148–158 (receipt contents).

**Evidence:**
- The receipt binds endpoint, model identity, artifact, counter, dimensions, operator stop/restart, logs, expiry, budgets and permitted paths (lines 150–158). It does not bind the served model's **loaded state** or the server's on-demand-load and eviction behaviour.
- As far as this reviewer knows from LM Studio's public documentation (**not verified against the running service; no endpoint was called**), LM Studio's OpenAI-compatible server can load a requested-but-unloaded model just in time and can auto-unload or evict models. With JIT enabled, its model listing can show downloaded rather than loaded models.

**Risk:**
- A permitted `/v1/embeddings` call could cause a model load or eviction. That is a service state change the harness is forbidden to cause.
- A "present in listing" observation could be mistaken for "served and loaded".

**Narrow mitigation:**
- Add receipt fields for the operator-attested loaded instance identifier and for the server's on-demand-load, TTL and eviction settings. These are attested, never configured by the harness.
- Add one exactly named read-only status path to the permitted list, with its semantics stated as attested or observed.
- Require the harness to refuse a batch when the model is not observed or attested as already loaded, or when on-demand loading or eviction could be triggered.
- An unexpected latency, identity or loaded-state change between batches stops A3.
- Label all of these as attestation versus observation.

**Proof (future construction):**
- Simulated-server tests in which a not-loaded or on-demand-load-enabled receipt yields zero embedding calls.
- A loaded-state change between batches stops further batches.
- The request log shows only the permitted read-only status and embedding paths.

### Advisories (non-mandatory; none substitutes for a requirement)
- **A-1:** `-I` implies `-E -P -s` on Python 3.11+. `run.py` therefore does not get its own directory on `sys.path`, and `PYTHON*` environment variables (for example `PYTHONPYCACHEPREFIX`) are ignored. Specify explicit sibling loading for `run.py`/`bootstrap.py` (directive line 222 covers tests only). Children must receive `-B`/`-X` flags, not `PYTHON*` variables, when also run with `-I`.
- **A-2:** The construction-time "focused Ruff/format/type checks" (line 224) should explicitly use private caches (`--no-cache` or a cache directory under scratch), so `.ruff_cache`/`.mypy_cache` are not written into the checkout.
- **A-3:** Add "operator-attested vs observed" explicitly to the HR-09 evidence row. It is present in the body (line 161) but missing from the acceptance matrix.
- **A-4:** Name the locations for the operator's pre-init config and receipt (for example under `.friday_test/`, never inside the tracked tree). Name the revocation/stop channel and how it is re-hashed per batch.
- **A-5:** authority.json `harness_construction_directive.council_authority: "not_granted_by_current_preparation_request"` and directive line 43 read as stale next to `directive_council.status`. This is accurate only literally; clarify at reconciliation without altering frozen bytes.
- **A-6:** Clarify whether `<test-python>` is a stdlib orchestrator that spawns each A1 profile target as a child, or a profile interpreter. A1 installs several profiles, and HR-10 requires the core harness to stay Docling-free.
- **A-7:** A3's "omitted-new-field B01–B08 … pool/… cache selection" (plan 288–290) must be qualified through explicit run-owned clients and configuration, never through DI/Runtime assembly that could open default store or cache paths. State this as a stop condition.

## 5. HRC-01–16 matrix

| ID | Result | Citation / reason |
| --- | --- | --- |
| HRC-01 | PASS | Directive 3–5, 9–14, 39–43, 74–80; separate construction/effect/window permissions; authority.json `construction_approval: not_granted`, `window_confirmed: false`; validation policy 68–83. |
| HRC-02 | PASS (note -003) | Allowlist 45–66 is entirely `tests/readiness/ingest/` plus the root-anchored `/.friday_test/` ignore and planning records; forbidden list 68–72; `.gitignore` currently has no `.friday_test` entry (static-evidence). Runtime `.git` mutation risk is treated under HRC-03/-003. |
| HRC-03 | **PARTIAL — fails** | Strong env/import/bytecode/venv rules (items 1–3; plan 69–76), but -002 (HOME/system/upward discovery), -003 (export/Git) and -004 (global caches). |
| HRC-04 | **PARTIAL — fails** | Path/alias/archive/publication rules are implementable (item 3; isolation 68–77). Containment honesty is stated (107–109), but the prevent/detect split and detective scope are missing (-004). |
| HRC-05 | **PARTIAL — fails** | Preflight no-effects, fresh init, owned reopen and scoped-vs-full reporting are well specified (items 1–2, 188–192). The `all`/promotion/receipt lifecycle is incoherent (-001). |
| HRC-06 | **PARTIAL — fails** | Exact manifests, Certifi floor after all steps, no extras or production metadata (79–86, 115–121; plan 37–51, 159–205). The promotion ledger is undefined (-001), and mirror/credential neutralization is missing (-002). |
| HRC-07 | **PARTIAL — fails** | Operator stop/restart/log-separation receipt, expiry/revocation, per-batch check, no service management (141–171). A request-triggered load is not gated (-005). |
| HRC-08 | **PARTIAL — fails** | The served-model exception is distinguished from test-owned Docling/OCR/tokenizer assets (isolation 119–123; plan 103–106); unknown facts block only A3 (115). The implicit no-JIT-load server-behaviour assumption remains (-005). |
| HRC-09 | PASS | Item 6, HR-06; plan 238–257 (30+ genuine fixtures, independent expectations, read-only supplied copies); isolation 131–143. |
| HRC-10 | PASS | Item 7, HR-07; plan 259–270, 291–302 (preliminary vs model-qualified counting, synthetic vectors protocol-only). |
| HRC-11 | PASS | Lines 19–20, 134, 236–237; plan 154–156; envelope `excluded_effects`; consumer matrix is a worklist only. |
| HRC-12 | PASS (advisory) | Item 8; envelope budgets; "never kill or restart LM Studio or production". Note: process-tree RSS sampling on macOS needs a manifest-declared or recorded tool; detective scope is under -004. |
| HRC-13 | PASS (A-1) | HR-03/10/11, lines 211–227; root `testpaths = ["packages/*/tests_*", "experiments/*/tests"]` (pyproject 134) excludes `tests/`; normal and `-O` lanes; minimal vs profile selectors. |
| HRC-14 | PASS (A-3) | HR-09/HR-12, line 161, plan 305–312, isolation 166–169. |
| HRC-15 | PASS (A-5) | current-controls, board, authority, authorization and roster agree: one read-only round, `design_only`, no construction/effects/window. Execution log has 0 deleted lines; prior gate tails replaced only in mutable next-gate fields; admin checks exit 0. |
| HRC-16 | PASS | Lines 229–244 (independent validator, stop conditions, no push/install/restart); human decisions route to Chuck (plan 153–156). |

## 6. HR-01–12 trace

| HR | Directive basis | Criteria | Status |
| --- | --- | --- | --- |
| HR-01 | Lines 45–72, 63 | HRC-02/03 | Traceable. The protected-state scope needs -003/-004. |
| HR-02 | Items 1–2, 173–192 | HRC-05 | Traceable. Full/selected flow needs -001. |
| HR-03 | Item 3 | HRC-03/04/13 | Traceable. Overclaims prevention for native/child channels (-004); ambient config (-002). |
| HR-04 | Items 2, 5 | HRC-06 | Traceable. The changed-binding semantics depend on -001. |
| HR-05 | 141–171 | HRC-07/08 | Traceable. Needs the loaded-state/JIT gate (-005). |
| HR-06 | Item 6 | HRC-09 | Adequate. |
| HR-07 | Item 7 | HRC-10 | Adequate. |
| HR-08 | Item 8 | HRC-12 | Adequate (A-4 for the stop channel). |
| HR-09 | 191–192 | HRC-14 | Adequate (A-3). |
| HR-10 | 219–221 | HRC-13 | Adequate (A-6). |
| HR-11 | 208, 211–217 | HRC-13 | Adequate. Root discovery exclusion confirmed in source. |
| HR-12 | 209, 231–237 | HRC-14/16 | Adequate. |

## 7. Scores

**Coverage: 8.6 / 10.**
- All 16 criteria and all 12 HR rows are addressed and traceable.
- Nine criteria pass outright.
- Six are partial because of five gaps: lifecycle (-001), ambient configuration (-002), export (-003), detective scope (-004) and server behaviour (-005).
- No criterion is unaddressed.

**Overall: 8.3 / 10.**

| Component | Weight | Score | Reason |
| --- | --- | --- | --- |
| Scope/authority | 2 | 1.9 | Precise allowlist and authority chain; A-5 wording. |
| Isolation/effects enforceability | 3 | 2.3 | Strong intent and env/import rules; -002, -003 and -004 leave real channels open; -005 for the shared service. |
| Clarity/feasibility | 2 | 1.6 | Implementable components; the `all`/promotion/receipt lifecycle is not (-001); A-1/A-6. |
| Verification/evidence | 2 | 1.8 | Meaningful normal/`-O`, negative and simulated-window tests; the prevent/detect evidence split is missing. |
| Manual operator usability | 1 | 0.7 | The advertised `all` command cannot work as written for a fresh run; config/receipt locations unnamed. |

The 9.5 target is not met. No finding was softened to approach it.

## 8. Residual limitations

- This is a document-readiness review. Future harness code, installs, fixtures, model facts and stage results are obligations, not evidence.
- LM Studio behaviour claims in -005 come from public-documentation knowledge, not observation. Mitigation is phrased as attestation/observation gating so it holds regardless.
- Tool-flag names in the -002 mitigation are examples for the builder to confirm against the pinned tool versions.
- Source-observations.json was summarised, not read line by line. The parent product contracts (assessment, REM, annex, test/architecture/guide plans) were trusted as approved and not re-audited.
- The repository-engineering and lifecycle policies were hash-verified and applied through AGENTS.md's operative rules, not re-read in full.
- One round only. No remediation, replacement or authority is implied.

## 9. Preserved state and closing

The opening boundary PASSED. Closing boundary result and request re-hash: see the appended closing section below.

### Closing (appended after report preparation)

- The closing boundary (`--label closing`) exited 0 with **PASS** at `2026-11-11T21:59:27Z`. The logical index `2873bdac566cf50f8c9acf1994aaaf02a23b58a31cc4c06cdb1e828b35ed0d46` is identical to the opening value. Unchanged: HEAD `f8145369`, the branch, empty staging, status, 17,773 protected files, 24 authority pins and 9 preserved records. Evidence: `integrity-closing.json`.
- The request was re-hashed at close: `651d8edfa6d1afb952418ee393b5f1369eadce2ef6b73eeb63eeb61c37320a44` (unchanged).
- No writes occurred in the checkout, `.venv`, `.git`, `.friday_test` or the supplied inputs. All reviewer evidence is in this scratch only.

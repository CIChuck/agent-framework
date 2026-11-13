# CD-CMD-INGEST-GATE-A-001 — Opus seat, corrective pass 2/4 (harness-global round 3)

## 1. Outcome

**VERIFIED** (design/source-feasibility scope only). No mandatory finding.
Five non-mandatory findings: two low, three advisory.

- Coverage score: **9.6 / 10**
- Overall score: **9.5 / 10**

This does not grant construction, effects/stage activation, a model window,
acceptance, push, merge or delivery authority. A VERIFIED result is not
maintainer acceptance.

## 2. Candidate and diff identity

| Item | Value |
| --- | --- |
| Repo | /Users/chuckrussell/Dev/gendev/agent-framework, branch `feature/cmd-ingest-001` |
| Frozen candidate | `474479df6baf1ffab89ffab81ae3b84bb7a98ed7` (HEAD at opening and closing) |
| Prior normative candidate / base | `23253a72ba265334e254c6a0bbad53f70cd85313` |
| Unit diff | `23253a72..474479df`: 95 paths, all under `docs/planning/` (the helper checked this) |
| Preparation delta | `35df1fa3..474479df`, whitespace-checked |
| Logical index (before status) | `a7ba1c933bce5289582901fae06b6e99aa3b6e05fcf8423cc4875132b6bdc43f`, same at opening and closing |
| Request SHA256 | `fa5117b2…2da00` matched before reading and again at close |
| Helper SHA256 | `7a7f2ef7…11e5` matched before reading; source read before running |
| current-controls / protected-manifest | `f39027a3…cc91` / `d559c254…f8a0`, matched at close |

## 3. Authority manifest and review mode

- Mode: remediation delta first (P2-01..03, RC-01..06), then the full bounded
  HRC-01..16 aggregate with an HR-01..18 trace. This is a design/source-feasibility
  review. It is not implementation verification.
- 27 authority pins were verified by the helper at opening and closing (AGENTS.md,
  4 policies, 2 pinned working skills, directive v0.3 `bb5453f9…`, authorization,
  loop-state, pass2 criteria/roster/corrections, 9 business inputs, plan v0.5
  `94c37e84…`, envelope v0.5 `4b6273c2…`, isolation v0.4 `a50069c9…`, contract v0.2
  `ac09cc31…`, source-observations and the consumer matrix). I also read both pinned
  skills (council, independent-code-validator). The working bytes equal the pins,
  so no committed-version substitution happened.
- I recomputed the directive's 15-row parent table: **all 15 match**. None of the
  nine business inputs has a commit in `23253a72..474479df`.
- Board (`474479df:docs/planning/board.yaml`): `work_state: started`,
  `implementation_authority: design_only`, branch `feature/cmd-ingest-001`. This
  agrees with current-controls (construction/effects not granted; council
  pass2/4, global round 3).

## 4. Independence and context provenance

- Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), high effort. Fresh task-only
  context created 2026-11-11 for this request. I have no builder transcript, no
  current peer verdicts and no memory/history search, and I spawned no nested
  agents.
- I did **not** open council-round1, `correction-loop/pass1/results/*` reports or
  evidence, or directive_council_history. I hashed raw authority through the helper
  and did not display it.
- Exposure I am disclosing:
  - Names only: the request's changed-path list names pass1 result files.
  - Labels only: criteria and corrections.json carry the labels "Opus pass1 F1–F3",
    and README navigation carries a round1 link label. I did not use either as
    correctness evidence.
  - I read one single-line hunk of `package-impact/current-verified-report.md` to
    confirm that only the controller status line changed ("pass1/4" → "pass2/4").
  - I did not see the content of SOL-001 or ASTRA-001. I assessed RC-01 from its
    own question text and the current bytes only.
- One host-tool side effect: a long grep output was auto-persisted by the Claude
  Code harness to
  `~/.claude/projects/-Users-chuckrussell-Dev-gendev-agent-framework/4c1349c8-…/tool-results/b0fnrdl5z.txt`.
  It contains only installed LiteLLM source text. It was not a reviewer-directed
  write and is not in the checkout or the supplied roots.

## 5. Findings (none mandatory)

### OPUS-P2-001 — low — the approved-manifest digest is not an explicit bootstrap input; the post-init entry trust root is implicit

- Files: contract §1.1 (lines 45–71); directive manual interface (lines 156–167, 170–172).
- Requirement: contract §1.1 says the manifest is "independently approved/bound by
  its digest" and "a self-written manifest derived from dirty files is not
  approval". P2-01 asks for one externally approved bootstrap that verifies the full
  committed selection.
- Evidence: the `preflight`/`init` shapes take only `--harness-manifest
  <approved-manifest>`. Unlike `promote … --sha256 <digest>`, they carry no expected
  digest, and nothing names where the bootstrap obtains the approved digest. After
  init, launches execute `<run-root>/harness/run.py` directly. Its bytes are read by
  the interpreter, not by the verify-then-compile loader. "A later launch
  revalidates its approved bootstrap identity" is therefore a self-check on a
  read-only export, but the text does not label it that way.
- Risk: an implementer may accept whatever manifest file sits at the path. A
  regenerated manifest built from dirty files would then pass byte verification
  against itself. This is accidental-error risk. The threat model already excludes
  a malicious operator.
- Bounded fix: add `--harness-manifest-sha256 <digest>` to preflight/init. Or state
  that the operator verifies the manifest digest externally, exactly as for the
  bootstrap, or that the approved control config binds it. Label the post-init
  `run.py` as the frozen exported entry: read-only export plus ledger-bound
  self-check, which detects accidental change and does not self-authenticate.
- Future proof (C0): a manifest whose digest is not the approved one is refused
  before any sibling is executed, even when every file matches that manifest. A
  run-root `run.py` byte change is refused on the next launch.

### OPUS-P2-002 — low — tool-spawned backend/uv ancestor discovery in the nested export is neither enumerated nor detectable as a read

- Files: contract §1.2 (78–114), §2 (118–124, 141–144), §5 residual row; plan A1 (207–216).
- Requirement: contract §2 says "Tools must not discover the parent production
  workspace merely because `.friday_test/` is nested inside it". RC-04 requires no
  dirty/untracked/ignored input. P2-02 asks for pre-inspected build targets.
- Evidence:
  - The export sits at `<project>/.friday_test/runs/<id>/source-export/`.
  - All 18 committed `pyproject.toml` files use `hatchling.build` (checked with
    `git show HEAD:…`). There is no hatch-vcs and no dynamic version.
  - Inspected from knowledge, not from installed text: Hatchling's VCS-ignore
    lookup walks ancestor directories for `.gitignore`/`.hgignore`, and uv
    project/workspace discovery walks upward. Hatchling is not installed in `.venv`
    or locked, so I could not verify the installed text and did not read caches.
  - Contract §1.2 evidence for tool children is argv/environment trace plus
    startup-site inventory. §5 detection is write metadata. A read of a production
    ancestor file, such as the working-tree `.gitignore`, by a uv-spawned backend
    is neither prevented nor detected, and §1.2 does not list it as a residual for
    that class.
  - The guarded-backend shape would deny the probe under §2.1, which is
    fail-closed.
- Risk: dirty production working-tree content (for example an edited
  `.gitignore`) could silently change wheel contents under the tool-spawned
  shape. Practical impact is low today, because the committed root `.gitignore`
  is clean and the backend would apply the same patterns production uses.
- Bounded fix: in A1 build qualification, require a per-backend/uv
  ancestor-discovery inventory (VCS-ignore files, project/workspace `pyproject`,
  `.python-version`, VCS markers). Include the committed root `.gitignore` and
  root `pyproject.toml` blobs in the export selection so upward walks stop inside
  the export. State that tool-child reads are residual unless the guarded backend
  is used.
- Future proof: a fake parent project with a poisoned `.gitignore` that excludes
  a module, plus a poisoned workspace `pyproject`, must leave the wheel RECORD
  byte-identical, or block the tool-spawned shape.

### OPUS-P2-003 — advisory — sticky `stop` has no defined clearance/resume semantics outside the A3 window

- Files: contract §4 (322–328), §6 (422–430); envelope `promotion_policy.stop`.
- Requirement: RC-02 asks for coherent all-stop/resume.
- Evidence: revocation is "sticky until a new explicitly confirmed window" and
  "reopening never clears revocation implicitly". `stop` also gates offline effects
  ("readers recheck before each request/effect"), but no explicit clearance path
  exists for offline stages (A0–A2). Whether a stopped run is terminal (new run
  ID) or resumable by explicit receipt is undefined.
- Risk: operator ambiguity only. It fails closed.
- Fix: state whether a manual stop is terminal for the run's effects, or name the
  explicit resume receipt and its scope. Keep the window-revocation clearance
  separate.
- Proof: C0 shows that stop → offline resume is refused or accepted exactly as
  specified.

### OPUS-P2-004 — advisory — "existing 64 MiB retained-control metadata ceiling" has no envelope field

- Files: contract §4 lines 260–264; envelope `budgets.metadata_bytes`; plan budgets row "Metadata".
- Requirement: preserve and trace numeric ceilings exactly.
- Evidence: the only 64 MiB value is `metadata_bytes: 67108864`. The plan
  describes it as a network metadata budget ("500 requests, 15 minutes; public
  allowlisted hosts"). No retained-control ceiling exists in the envelope. The
  sentence's own disclaimer ("not an extra network metadata allowance") confirms
  that it is a different concept reusing the number. No budget value changed in the
  delta; I checked the numeric lines of the envelope diff.
- Fix: reword it as "bounded by the 1 MiB per-record cap and
  `total_retained_disk_bytes`, with explicit finite record counts". Or bind a named
  field through a separately authorized envelope change. Do not call it existing.

### OPUS-P2-005 — advisory — navigation lag and status edits to a VERIFIED report

- loop-state `status: preparing_frozen_pass2` and the board text "is being frozen"
  lag the frozen dispatch.
- `package-impact/current-verified-report.md` gets a controller status-line edit
  every pass. The round6 verdict bytes are otherwise preserved.
- Neither affects authority. Prefer keeping per-pass status in navigation files.

## 6. Remediation delta matrix

| ID | Result | Evidence and limits |
| --- | --- | --- |
| P2-01 | **PASS** (OPUS-P2-001 low) | Contract §1.1 has a single stdlib bootstrap as the external root and a complete committed manifest (commit/tree, path/mode, blob ID, SHA256). It reads once and compiles/executes the same buffer with an explicit name mapping, and never re-opens through a path loader. It uses no pyc or sourceless modules ("-B prevents writes, not reads") and refuses dirty/extra/symlink/`__pycache__` before writes, without automatic cleanup. Init export requires code equality with the executed manifest, which closes the commit→blob loop that preflight cannot check without Git. After init, only the frozen run root is used. The C0 negatives (dirty, extra, matching-mtime pyc, post-hash swap) and positives (normal and `-O`) are named. Feasibility: under `-I` (which implies `-P`) the script directory is not on `sys.path`, so a verified-buffer meta-path loader is necessary and implementable in stdlib (`compile`/`exec`, `importlib` spec/module). `-O` is honoured by `compile(optimize=-1)`. Directive behaviours 1–2, HR-13 and envelope `startup_policy.pre_init`/`imports` agree. |
| P2-02 | **PASS** (OPUS-P2-002 low) | Contract §1.2 separates the tool-spawned class honestly: no claim of `-I/-S/-B`, guard or `-O` inheritance, and not allowed in preflight. It requires expected and actual child argv/env via a qualified trace or native evidence, and missing evidence blocks. Build targets are prepared and inventoried, with automatic build isolation disabled. If uv cannot control this, the fallback is a guarded harness-launched backend, or the profile is blocked. `.pth`/customize/egg-link files are inventoried and classified, and executable import lines block. Classification is detective/residual. Source check: the working `.venv` holds `_virtualenv.pth` (`import _virtualenv`), `coloredlogs.pth` and editable `.pth` files. The uv-managed base CPython 3.13.10 `site-packages` holds only `pip` and `README.txt`. The inventory rule therefore blocks a venv-shaped site-enabled child and admits a base-interpreter/`--target` shape, which shows the rule is meaningful and feasible. Flags used (`--no-config`, `--no-python-downloads`, `--python`) are real uv options; no invented flags. |
| P2-03 | **PASS** | Contract §2.1, directive behaviour 3 / HR-15, plan A1 and envelope `tool_isolation.import_channels`. Text-only check of installed `.venv` LiteLLM **1.100.1**, which matches `uv.lock` 1.100.1. `litellm/__init__.py:26-27`: `if os.getenv("LITELLM_MODE","DEV")=="DEV": _dotenv.load_dotenv(...)`. Line 538: `get_model_cost_map(url=...)` runs at import. `get_model_cost_map.py:441`: `LITELLM_LOCAL_MODEL_COST_MAP` with `.lower()=="true"` uses the local map only. Both named neutralizers are accurate for this version and correctly scoped to "this version only". `friday_llm/embeddings.py:19` imports `litellm` (confirmed). Further facts that make the transport-layer count necessary: `embeddings.py` has tenacity retries (`max_retries=5` default), and LiteLLM defaults to the aiohttp transport (`disable_aiohttp_transport=False`, line 505). Counting at the guarded send boundary with attempt IDs inside the unchanged 64-request cap, and blocking uninstrumented transports, is correct and implementable. The read/probe guard is feasible: CPython 3.13 has no audit event for `os.stat`, as the contract says, and denying with an `OSError` gives benign not-found semantics for `isfile`-style probes such as python-dotenv's ancestor walk and `mimetypes`. Native reads remain qualified/residual. Neither the C0 fake modules nor the A1 real-library proof needs a current import. |

| ID | Result | Evidence and limits |
| --- | --- | --- |
| RC-01 | PASS | Contract §1: trusted base, stdlib and launcher; `-I -S -B` (`-O` lanes) scoped to harness-launched processes; working `.venv` rejected by path and resolved context (a symlink to the shared base is not accepted; `.venv/bin/python` → base 3.13.10 symlink confirmed); no `sys.prefix`-derived sites under `-S`; explicit guard before dependencies. Canary proofs cover all harness entries and children in normal and `-O`. No production Python is edited. |
| RC-02 | PASS (OPUS-P2-003 advisory) | Contract §4: immutable init; single-writer lease; canonical hash-chained ledger; enumerated transitions; prepare-model offline before window; receipt anchors the promoted prefix, not the moving tip; `all` exits AWAITING_PROMOTION/PREPARATION/WINDOW; cumulative 7200 s active time with human waiting separate and no reset. No cyclic up-front hashes. |
| RC-03 | PASS | Contract §2 table and §2.1: uv/pip/Git/HTTP/validation/library profiles; owned UV/XDG/NETRC/credential roots; keyring off; macOS system proxy explicitly excluded; effective origins recorded; unknown channels block; fake HOME and fake parent poisoning; system channels need version-qualified evidence beyond fake HOME; real HOME untouched. |
| RC-04 | PASS (OPUS-P2-002 related) | Contract §3: run-owned bare object view with a declared read-only alternate and only `rev-parse`/`cat-file`/`ls-tree`; no filters, LFS or archive; blob/tree/commit verification; the Finance live-credential test is excluded; index boundary uses a stable copy with a private `GIT_INDEX_FILE`; split index is copied or the run stops; read-only export plus a derived metadata-only overlay with base/patch/result and code equality (directive lines 69–71; envelope `metadata_rehearsal`). |
| RC-05 | PASS | Contract §5 prevention/detection/residual table; bounded metadata only, with no payload, HOME scan or symlink traversal; a streaming digest with counts within finite limits; external writers invalidate and are never excused; no automatic restore; truncation or unknown coverage blocks. |
| RC-06 | PASS | Contract §6: already-loaded model; operator-attested JIT/TTL/eviction; exactly one version-qualified native status profile with no fallback probing; only the selected GET plus `POST /v1/embeddings`; attested versus observed labels; before/after checks per batch; status and embeddings share 64; no upgrade, new server or settings change; a pending activation-time settings decision keeps A3 blocked (envelope `pending_settings_decision`). |

## 7. Full aggregate HRC-01..16

| ID | Result | Citation |
| --- | --- | --- |
| HRC-01 | PASS | Directive lines 3–4, 8–12, 73–86; authorization.md; board `design_only`; current-controls `construction_approval: not_granted`, `effects_activation: not_granted`, `window_confirmed: false`. |
| HRC-02 | PASS | Directive edit table, lines 51–66: code only under `tests/readiness/ingest/`; `.gitignore` limited to root-anchored `/.friday_test/`. HEAD `.gitignore` has no `friday_test` entry yet, and `tests/readiness` is absent (`ls`), so nothing has been constructed. |
| HRC-03 | PASS (OPUS-P2-001, -002 low) | Contract §§1, 1.1, 1.2, 2, 2.1; isolation v0.4 lines 91–103; envelope `startup_policy`/`tool_isolation`. |
| HRC-04 | PASS | Isolation lines 78–89; plan lines 64–102; envelope `isolation.shared_*`; HR-03 archive negatives; document limits unchanged in envelope `document_probe_limits`. Containment limits are stated honestly (contract §5; plan line 101). |
| HRC-05 | PASS (OPUS-P2-003) | Directive behaviours 2 and 5, manual interface lines 156–189; contract §4 status semantics; isolation lines 168–175. |
| HRC-06 | PASS | Plan candidates (lines 43–60) and A0/A1 (178–236); envelope `candidate_requirements`, `security_floor` (≥2026.10.19, exact 2026.10.23); directive behaviour 7; binary-only; no extras or sdists. |
| HRC-07 | PASS | Contract §6; plan lines 110–140; isolation lines 114–152; envelope `model_window_policy`. |
| HRC-08 | PASS | Plan lines 112–118, 303–340; isolation lines 143–146; envelope `unbound_model_inputs` (all null, so A3 is blocked). |
| HRC-09 | PASS | Plan A2 (lines 269–288): 6+6+10+8 = 30 genuine fixtures; isolation lines 154–166; HR-06. |
| HRC-10 | PASS | Plan lines 290–301, 334–340; directive behaviour 8; HR-07. |
| HRC-11 | PASS | Directive lines 14–19 and behaviour 10; plan line 71; envelope `excluded_effects`; consumer matrix pinned unchanged. |
| HRC-12 | PASS | Plan budgets table; envelope budgets; contract §4 accounting; behaviour 6. RSS-tree sampling on macOS is implementable in stdlib via ctypes/libproc or with a qualified `ps`, but it is sampling-based. Plan lines 155–159 already disclaim the meaning of termination. |
| HRC-13 | PASS | Directive lines 172–179 and HR-11/13; root `testpaths = ["packages/*/tests_*", "experiments/*/tests"]` (HEAD `pyproject.toml`), so `tests/` is excluded as claimed. |
| HRC-14 | PASS | Contract §7; directive behaviour 10, HR-09/12; isolation lines 195–200. |
| HRC-15 | PASS (OPUS-P2-005) | current-controls, loop-state (passes_started 2, completed 1, current 2), roster (3 seats, high effort, gate), board and navigation all agree; round1 preserved by reference. |
| HRC-16 | PASS | Directive "Delivery and stops" (lines 225–239); plan activation checklist; envelope `activation` and `manifest_review`. |

## 8. HR-01..18 trace

| HR | Maps to | Notes |
| --- | --- | --- |
| HR-01 | HRC-02, 04, 15 | Edit table plus protected-state evidence (contract §5). |
| HR-02 | HRC-05 | No-effects preflight; staged invocations. |
| HR-03 | HRC-04, 12, RC-05 | Archive negatives now explicit; intercepted versus native. |
| HR-04 | HRC-06, RC-03 | Tamper/extra/unknown host/license/config origin; no setup-failure credit. |
| HR-05 | HRC-07, RC-06 | Simulated server negatives; zero unauthorized calls. |
| HR-06 | HRC-09 | Genuine fixtures and supplied copies. |
| HR-07 | HRC-10 | Three strategies, 512/override, preliminary versus real. |
| HR-08 | HRC-12, RC-02 | Cumulative budgets; stop gates new calls. |
| HR-09 | HRC-14 | Attested/observed and other separations. |
| HR-10 | HRC-03, RC-01 | Stdlib core; private worker interpreters. |
| HR-11 | HRC-13 | Isolated copy of the root rules; bare pytest fails closed. |
| HR-12 | HRC-14, 16 | Separate fresh implementation review. |
| HR-13 | P2-01, P2-02, RC-01 | Pre-init byte controls; tool-child detective class. |
| HR-14 | RC-02, HRC-05 | Ledger, awaiting exits, receipt anchoring. |
| HR-15 | P2-03, RC-03 | Dotenv/cost-map/proxy/transport accounting. |
| HR-16 | RC-04 | Blob export identity; dirty traps. |
| HR-17 | RC-05 | Simulated cache change detected; truncation refused. |
| HR-18 | RC-06 | One status API; counted requests; no management. |

All 18 rows are traceable, and each has a future proof assigned to C0 (offline)
or to the activated A1–A3 lanes.

## 9. Commands executed and exact results

Fresh evidence: these were run in this session.

1. `shasum -a 256 request.json review_tools.py` before reading. Exit 0, both matched.
2. `python3 -I -S -B <inputs>/review_tools.py boundary --request <inputs>/request.json --scratch <S> --label opening`. **Exit 0, PASS**: 17,941 files, 27 pins, 9 records, logical index `a7ba1c93…`.
3. `python3 -I -S -B <inputs>/review_tools.py admin --request … --scratch <S>`. **Exit 0**. The helper ran each check with `uv run --offline --frozen --no-sync --no-python-downloads python -B …` and private caches:
   - board validate: exit 0, "36 tasks"
   - render --check: exit 0, "current"
   - documentation lifecycle: exit 0, "1071 Markdown files"
   - package metadata: exit 0, "18 pyproject.toml"
   - the four whitespace checks (worktree, staged, unit, preparation): exit 0 each, empty output
4. `python3 -I -S -B … boundary … --label closing`. **Exit 0, PASS**, with identical identities. I rehashed the four inputs; all matched.
5. Read-only Git calls, each with `GIT_OPTIONAL_LOCKS=0` and none of them `status`: `git diff --word-diff`/`--stat`/`-U0`, `git show HEAD:<path>` and `474479df:board.yaml`, `git log --oneline` (business-input delta), `git grep`, `git ls-tree`. All exited 0.
6. Text inspection only, with no imports and no writes:
   - grep/sed of `.venv/.../litellm/__init__.py` and `litellm_core_utils/get_model_cost_map.py`, `default_encoding.py`;
   - name listing of `.venv` site-packages `.pth` files and the base uv CPython `site-packages`;
   - `cat _virtualenv.pth` (one line).

Interpreter used for the helper: `/opt/homebrew/bin/python3` (3.14.2) with `-I -S -B`.
The helper requires only stdlib.

Inspected, not executed: LM Studio API shapes and Hatchling/uv internals are
assessed from document citations and knowledge. Hatchling is not installed or
locked here, and no network was used.

## 10. Skipped checks and reasons

These were all skipped as outside this gate: product tests, Ruff/mypy, installs,
builds, uv resolution, imports of third-party packages, endpoint/model calls,
reading caches or personal `.env`/YAML, and Git experiments in fake repositories.
For example, private-view `ls-files` on a bare view and the alternate-object
behaviour are assessed as feasible, not demonstrated. They remain C0/A1
obligations.

## 11. Baseline failures versus regressions

The historical root Ruff 534 failures, the root `test_display` collection conflict
and the registry formatting failure were not rerun and are not waived. The
candidate changes only `docs/planning/`, so it can introduce no product regression.
The admin checks are green.

## 12. Score breakdown (honest; no score waives a finding)

Coverage **9.6**: every HRC, RC, P2 and HR row is assessed with citations. I
deducted for the unverified Hatchling/uv internals and for the bare-view
`ls-files` and LM Studio status shapes being knowledge-level only.

Overall **9.5**:

| Area | Score |
| --- | --- |
| Scope/authority | 2.0 / 2 |
| Isolation/effects enforceability | 2.8 / 3 (OPUS-P2-002 tool-child read channel; OPUS-P2-001 post-init entry self-check) |
| Clarity/feasibility | 1.85 / 2 (manifest digest input, 64 MiB wording) |
| Verification/evidence | 1.9 / 2 |
| Manual operator usability | 0.95 / 1 (stop/resume semantics; refusing a stale working-tree `__pycache__` needs a manual operator step) |

## 13. Residual risk and recommended next gate

Residuals:

- Tool-child reads are residual unless the guarded backend shape is used.
- RSS limits are sampling-based.
- Status shapes and JIT/TTL facts for the actual LM Studio server remain
  operator-attested activation inputs.

All three are honestly pending, not gaps at this document gate.

Next gate: reconcile the three Sol/Astra/Opus seats for pass 2. If every seat is
VERIFIED, the scores are at least 9.5 and there are no mandatory findings, the
controller may propose the directive for **separate** maintainer construction
approval. The low/advisory items above can be folded into construction-time
README/contract wording without a new pass, unless the maintainer prefers
otherwise. No construction, effects, window, acceptance or delivery follows from
this report.

# Opus seat — CD-CMD-INGEST-GATE-A-001 corrective pass 1/4 (harness-global round 2)

Seat: Opus, claude-opus-5-5, high effort. Read-only, fresh task-only context.
Candidate: `23253a72ba265334e254c6a0bbad53f70cd85313` (branch `feature/cmd-ingest-001`).
Mode: remediation delta (RC-01–06), then the full bounded aggregate (HRC-01–16, HR-01–18).
This report grants no construction, activation, window, acceptance or delivery authority.

## Formal outcome: **CHANGES_REQUESTED**

- Mandatory findings: **3** (F1, F2, F3). Advisory findings: 8 (A1–A8).
- Coverage score: **8.8 / 10**. Overall score: **8.7 / 10**. Both are below the 9.5 gate.
- The corrections are substantive and mostly sound. RC-02, RC-04, RC-05 and RC-06
  are closed at design level. RC-01 and RC-03 stay partial, for three concrete reasons:
  1. Pre-init code identity is not bound to committed bytes (F1).
  2. The universal `-I -S -B` rule cannot hold for Python processes that native tools spawn themselves (F2).
  3. The prescribed B01–B08 client path has a confirmed import-time `.env` upward-discovery channel and a remote-fetch channel that the documents do not operationalize (F3).

## 1. Integrity, pins and executed commands

| # | Exact argv (cwd `/tmp` for helper; repo for others) | Exit | Evidence |
| --- | --- | --- | --- |
| 1 | `shasum -a 256 <inputs>/request.json <inputs>/review_tools.py` (before reading) | 0 | request `d5c04007…2953` ✓, helper `7a7f2ef7…e5` ✓ |
| 2 | `python3 -I -S -B <inputs>/review_tools.py boundary --request <inputs>/request.json --scratch <S> --label opening` | 0 | `<S>/integrity-opening.json`: PASS, logical index `2ac41719…a073`, 27 pins, 17,861 files, 9 preserved records |
| 3 | `python3 -I -S -B <inputs>/review_tools.py admin --request <inputs>/request.json --scratch <S>` | 0 | `<S>/commands.json` + `*.stdout/*.stderr`. All 8 commands exited 0: board validate (36 tasks), dashboard current, documentation (1066 files), metadata (18 pyproject), whitespace worktree/staged/unit/preparation |
| 4 | Read-only `GIT_OPTIONAL_LOCKS=0 git show f8145369:<directive>`; `git diff --stat/--name-status f8145369 23253a72 -- <normative files>` | 0 | Delta comparison, names and stat only, plus prior normative directive bytes |
| 5 | `GIT_OPTIONAL_LOCKS=0 git diff --name-only f8145369 23253a72 -- <nine business inputs + source-observations + consumer matrix>` | 0 (empty) | Business inputs are byte-unchanged across the preparation delta. No non-planning path changed |
| 6 | `GIT_OPTIONAL_LOCKS=0 git ls-files/grep` targeted queries (test basenames, build backends, `litellm` imports, finance live-test path), `grep .gitignore`, `ls -ld .git .friday_test`, `pyproject` tool-config grep | 0 | See the source citations below |
| 7 | `grep -n "dotenv\|LITELLM_MODE\|LITELLM_LOCAL_MODEL_COST_MAP" .venv/lib/python3.13/site-packages/litellm/__init__.py`; `grep ^Version …/litellm-*.dist-info/METADATA` (read-only, existence or grep only) | 0 | litellm 1.100.1: lines 15, 26–27, 99, 413 |
| 8 | `ls .env` (existence only, never opened) | 1 → "no .env at root" | Root `.env` is currently absent |
| 9 | `python3 -I -S -B <inputs>/review_tools.py boundary --request … --scratch <S> --label closing` | 0 | `<S>/integrity-closing.json`: PASS, identical logical index, 27/17,861/9, no failures |

`<S>` = `/private/tmp/claude-501/-Users-chuckrussell-Dev-gendev-agent-framework/87d5f669-8954-47c3-8f96-389c9e2d699d/scratchpad/opus-review-p1-SW3t`
(a new reviewer-owned 0700 directory, outside the repo and outside the supplied directories).

How the scratch was handled:
- All helper caches and temp files stayed in `<S>`.
- No checkout, `.venv` or supplied-scratch writes were made.
- I made no Git writes, ran no tests, installs, network calls, model calls or endpoint calls, and started no nested agents.

Helper source review: I read the helper before running it.
- Boundary mode only runs read-only Git commands with `GIT_OPTIONAL_LOCKS=0`, and computes the logical index before status.
- Admin mode runs exactly the 8 permitted commands using private UV/XDG/mypy/pycache/TMP roots.

Authority pins: the helper verified the request's 27 pins. The directive's 15-row governing-input table matches those pins byte for byte, including directive `9925170d…3d3f`, criteria `61f7dcb2…5023`, authorization `d71afa78…a851`, roster `23fa0ada…700` and corrections `c992504a…94ff`.

## 2. Independence and exposure disclosure

- I started fresh, read the request first, and did not use memory or history search.
- I did not open the council-round1 reports or evidence, or `directive_council_history`.
- The `--name-status` listing exposed council-round1 *file names* only (evidence/astra/*, evidence/opus/*, archive-map, advisory-disposition). I did not read their contents, and they did not influence this report.
- `corrections.json` was used only as a location map.
- `current-controls.json` navigation text was read as supplied.
- I compared the prior normative directive bytes (f8145369) to check for dropped requirements. That comparison drives A6.

## 3. Remediation delta matrix (RC-01–06)

| ID | Verdict | Citations | Assessment |
| --- | --- | --- | --- |
| RC-01 | **PARTIAL** (F1, F2; A1) | contract §1 L8–41; directive L54, L89–93, L150–167, HR-10/13; envelope `startup_policy` L239–250; isolation L40, L93 | **Sound parts:**<br>- Trust root and threat-model limits are honest (L10–15).<br>- `-I` removes script-dir/user-site/PYTHON*; `-S` disables automatic site; explicit spec-from-file sibling loading is required under `-I`, and the contract requires it (L27–29).<br>- The prohibition on deriving `-S` site paths from `sys.prefix` is correct for 3.13. Under `-S`, `import site` does not call `main()`, so private roots via explicit `sys.path` are feasible.<br>- The canary/positive/unsafe-control design (L36–41) is meaningful.<br>**Gap F1:** preflight/init run from the live working-tree harness (directive L150–151), but sibling content is never bound to the committed harness. This contradicts isolation L40 ("execute from a frozen copy") and envelope `uncommitted_harness_fallback:false`.<br>**Gap F2:** "All Python invocations … use -I -S -B" (L17–18) and "Cover all … Python children" (L39–40) cannot hold for interpreters spawned by uv itself: interpreter queries in A0/A1, and PEP 517 hatchling builds in A1 (all 17 workspace packages use `hatchling.build`). |
| RC-02 | **PASS** (A4, A5) | contract §4 L131–191; directive L109–118, L169–174, HR-14; envelope `promotion_policy`, `time_accounting` | - Immutable init plus the hash-chained single-writer append-only ledger is coherent.<br>- Promotion binds the predecessor tip.<br>- The window receipt anchors the promoted prefix, not the execution tip (L171, L277), so there are no cyclic up-front hashes or tip-mismatch deadlock.<br>- `all` exits `AWAITING_*` instead of waiting (L174–179).<br>- Budgets are cumulative active time, with human wait reported separately. Crash accounting uses reserve-before-effect. No numeric ceiling changed (envelope L57–74 still holds the same numbers; `overall_active_seconds`=7200).<br>- The honest limit on what the hash chain proves (L150–151) is correct.<br>- Advisory: no `revoke`/`stop` interface command (A4); the end-of-run `all`/A3/A4 path is underspecified (A5). |
| RC-03 | **PARTIAL** (F3; A2) | contract §2 L43–71; directive L99–103, HR-15; envelope `tool_isolation` L273–281 | - The uv/Git/HTTP/validation-tool rows are concrete and correctly reject `--no-project`-only isolation.<br>- Git: `GIT_CONFIG_GLOBAL` overrides both `~/.gitconfig` and XDG; `GIT_CONFIG_NOSYSTEM` plus explicit `GIT_DIR` removes discovery.<br>- The uv `--no-config` design is feasible.<br>**Gap F3:** the prescribed A1 import checks and A3 B01–B08 "run-owned clients" path (plan L219–226, L312–316; consumer matrix C01) imports `friday_llm` → `litellm` at module level. That import runs `dotenv.load_dotenv()` by default (`LITELLM_MODE` defaults to DEV) and fetches a remote cost map. The dotenv load is an upward `.env` walk from the private target inside `.friday_test/`, into the production checkout and its ancestors. Library-level channels are left to a generic "unknown stops" rule with no inventory step, and the guard's read-side scope is unspecified.<br>A2: macOS system-proxy and other system-level channels cannot be proven by fake-HOME fixtures. |
| RC-04 | **PASS** (A7 wording) | contract §3 L73–129; directive L64–66, HR-16; envelope `source_export` L251–265; repo: `.git` is a directory, no `objects/info/alternates`, no `.gitattributes`/LFS | The design is feasible:<br>- Run-owned bare view with a declared read-only alternate, empty private config, `GIT_NO_REPLACE_OBJECTS`, and no remotes or promisor.<br>- Only `rev-parse`/`ls-tree`/`cat-file`. `cat-file blob` yields raw bytes without filters; there is no LFS in the repo.<br>- Independent blob SHA1/type/length/mode verification.<br>- The `.git` directory is not touched except for declared reads.<br>- Index collector: `ls-files -s -z --cached` with a private `GIT_INDEX_FILE` copy in a bare view needs no work tree for cached/stage listing (PLAUSIBLE, not executed here). Split-index stops fail-closed.<br>- The finance live-test exclusion path exists (`packages/friday-finance/tests/test_integration_massive.py`).<br>- Minor wording conflict with directive L69–70 (A7). |
| RC-05 | **PASS** (A3) | contract §5 L193–227; directive L104–108, HR-03/17; envelope `protected_state_policy` L282–289; isolation L174–186 | - The prevention / detection / residual classes are separated honestly.<br>- Python audit hooks are not called OS containment.<br>- Detected changes fail isolation, with no cleanup or restoration.<br>- Metadata scope is bounded, with no payload, HOME or model-directory scan, and truncation stops.<br>- Simulated roots are used for proof.<br>- A3: feasibility of enumerating large real default caches (for example a developer `~/.cache/uv`) within the bounds, and false positives from concurrent non-harness tools, should be addressed so the control does not just default to a block. |
| RC-06 | **PASS** (A8) | contract §6 L229–288; directive L130–136, HR-05/18; envelope `model_window_policy` L205–228 | - Existing endpoint, no new server or upgrade.<br>- Exactly one operator-selected native status profile: V1 `/api/v1/models` `loaded_instances[].id`, or V0 `/api/v0/models` `state=="loaded"` with instance facts labelled attested. No probing or fallback; `/v1/models` downloaded listing correctly rejected.<br>- Only the selected GET plus `POST /v1/embeddings`.<br>- Status calls share the 64-request ceiling. 64 requests with before/after checks still allow ≈21 batches against the unchanged 256-vector cap, which is feasible.<br>- Stop-file revocation re-read per request; in-flight limit stated.<br>- In-process stub transport for C0.<br>- A8: LM Studio's usual JIT-on configuration will likely block A3 under L241–245 unless a settings change is separately authorized. This is a pending human decision to surface now. Server version is operator-attested. |

## 4. Full aggregate (HRC-01–16)

| ID | Verdict | Citations / basis |
| --- | --- | --- |
| HRC-01 | PASS | Directive L3–4, L8–12, L72–85. Authorization L1–40. Board `design_only` per current-controls. Exact parent pins match. No self-approval, and review coverage is not inferred (L211–214). |
| HRC-02 | PASS | Directive L47–70: test-only allowlist plus the single anchored `/.friday_test/` ignore rule. Current `.gitignore` has only `.friday/` (does not match `.friday_test/`), and `.friday_test` is absent. Production package/lock/env/store edits are forbidden. Advisory A6 covers root lint/mypy scope. |
| HRC-03 | **PARTIAL** | Contract §§1–2. F1: pre-init identity. F2: tool-spawned interpreters. F3: library import-time config/network channels. The private cache/temp/bytecode design is otherwise sound. |
| HRC-04 | PASS | Isolation L75–86 (ownership/alias/symlink/overlap, never-overwrite publication). Plan L87–99 (manifest escapes/duplicates). Contract §5 limits are stated honestly. A6: archive-member negatives are no longer explicit in the HR table compared with v0.1 HR-03. |
| HRC-05 | PASS (A4, A5) | Directive L94–98, L143–174. Preflight makes no file, Git view or network. Init requires an absent root. Continuation is ledger-owned; incomplete and complete status are separated (contract L299–302). |
| HRC-06 | PASS | Directive behavior 7. Plan A0/A1 L175–226. Envelope candidate requirements and Certifi floor L13–22. Hatchling build tools must be inventoried (plan L210). No pip. Overlay is metadata-only. |
| HRC-07 | PASS | Contract §6. Isolation L107–145. Envelope L205–228. No service-management rights. Expiry/revocation/per-batch checks. |
| HRC-08 | PASS | Isolation L136–139. Plan L293–310. Unknown facts block only A3. No unsupported server capability is assumed (log separation is attested, no log-directory switch is invented). |
| HRC-09 | PASS | Plan L259–278: ≥30 genuine fixtures with independent expectations. Supplied copies are read-only. Directive behavior 8. |
| HRC-10 | PASS | Plan L280–291. Directive behavior 8 and HR-07. Preliminary versus synthetic versus real qualification are distinguished. |
| HRC-11 | PASS | Directive L17–19 and behavior 10. Plan L170–171 and L324–330. No Memory/Chroma writes. Later obligations are preserved. |
| HRC-12 | PASS | Directive behavior 6. Contract L181–191. Plan budgets L139–156. Only owned work is stopped. No restart, cleanup or effects during this review. |
| HRC-13 | **PARTIAL** | Directive L162–167 and HR-10/11/13. Root `testpaths` excludes `tests/` (pyproject L134), and there are no basename collisions in `tests/`. F2: the "all Python children normal/-O" proof obligation cannot be met for uv-spawned interpreters as written. |
| HRC-14 | PASS | Directive behavior 10 and HR-09. Contract §7. Attested/observed, prevented/detected, candidate/promoted/qualified and active/wall/wait are all separated. |
| HRC-15 | PASS | current-controls board/navigation, roster (3 seats, high), loop-state cap 4, and authorization all agree: one read-only pass, no construction or effects. Round1 is preserved as historical. `loop-state.status` "preparing_frozen_pass1" is a pre-freeze label; the frozen request binds the candidate. |
| HRC-16 | PASS (A8) | Directive L207–220 sets the stops, the smallest decision, and a separate fresh implementation validator. Remaining operator inputs are enumerated in envelope `unbound_model_inputs`. A8 adds the JIT-setting decision. |

## 5. HR-01–18 trace

| HR | Maps to | Status |
| --- | --- | --- |
| HR-01 | HRC-02, HRC-15 | Traced |
| HR-02 | HRC-05 | Traced; F1 affects pre-init executed-code identity |
| HR-03 | HRC-03, HRC-04, RC-05 | Traced; A6 (archive negatives implicit) |
| HR-04 | HRC-06 | Traced |
| HR-05 | HRC-07, RC-06 | Traced |
| HR-06 | HRC-09 | Traced |
| HR-07 | HRC-10 | Traced |
| HR-08 | HRC-12, RC-02 | Traced |
| HR-09 | HRC-14 | Traced |
| HR-10 | HRC-03, HRC-13, RC-01 | Traced; F2 |
| HR-11 | HRC-13 | Traced; A6 |
| HR-12 | HRC-14, HRC-16 | Traced |
| HR-13 | RC-01 | **Gap:** F1 (pre-init) and F2 (tool-spawned) proofs undefined or infeasible |
| HR-14 | RC-02 | Traced |
| HR-15 | RC-03 | **Gap:** F3 (library-level upward `.env` and remote fetch not in the proof); A2 (system channels not fixture-provable) |
| HR-16 | RC-04 | Traced |
| HR-17 | RC-05 | Traced; A3 |
| HR-18 | RC-06 | Traced; A8 |

## 6. Findings

### F1 — MANDATORY, Medium — pre-init harness code is not bound to the committed harness (RC-01, HRC-03, HR-13)

**Requirement.** These sources all require it:
- Contract L27–29: "Load sibling modules by explicit validated file locations".
- Isolation L40: execute "from a frozen copy in the test run root".
- Envelope L261: `uncommitted_harness_fallback: false`.
- Contract L117: "No uncommitted source fallback".

**Defect.** The required interface runs `preflight` and `init` from `tests/readiness/ingest/run.py` in the live working tree (directive L150–151). Init itself creates the Git view, exports, ledger and run root. Only "the approved launcher hash" is recorded (L11). "Validated" sibling locations are defined by path, ownership and run bindings (L22–23), but pre-init has no run binding, and nothing requires sibling *content* to match the committed harness. Path-based import also consults `__pycache__`, because `-B` stops writes but not reads. A validate-then-import sequence also leaves a TOCTOU window.

**Risk.** A dirty or stale sibling (`config.py`, `paths.py`, `export.py`, `ledger.py`) can perform init and its export verification, then bind a harness commit it did not run. That breaks evidence integrity and goes against the maintainer's isolation intent. Because init writes, the effect is not hypothetical.

**Bounded fix.** Add to contract §1 and directive behavior 2:
- Pre-init code is either a single operator-hash-verified launcher, or every pre-init sibling is verified against an operator-approved manifest of SHA256 and git-blob IDs bound to the activation's harness commit.
- Siblings are loaded by reading the bytes once, hashing them, and `compile()`/`exec` of exactly those bytes. Never use a path loader that can use `__pycache__`.
- A mismatch, an extra sibling, or a stale `.pyc` refuses before any write.
- After init exports the committed harness, init re-verifies the export against the executed pre-init bytes. All later operations, including the rest of init where possible, re-exec from `<run-root>/harness`.

**Future proof (C0).**
- A fake checkout with a modified sibling refuses before any file creation.
- A planted matching-mtime `.pyc` is never executed.
- A swapped-after-hash file is not loaded.
- Normal and `-O`.

### F2 — MANDATORY, Medium — the universal `-I -S -B` rule is infeasible for interpreters that native tools spawn (RC-01, HRC-03/13, HR-10/13)

**Requirement.** Contract L17–21 says "All Python invocations … use -I -S -B … No … .pth". L39–40 says "Cover all entry points and Python children, normal and -O".

**Defect.** In A0/A1, uv runs its own interpreter-discovery Python child to inspect the target interpreter. In A1, building the workspace wheels (all 17 packages declare `build-backend = "hatchling.build"`, confirmed by grep) runs a PEP 517 backend Python child inside a uv-created build environment. Site processing is enabled there, and argv and flags are chosen by uv, not the harness. Neither can satisfy `-I -S -B`, `-O`, explicit guard loading, or the canary proof.

There is also an expected `.pth` case. Torch declares a `setuptools` requirement on 3.12+, so setuptools' `distutils-precedence.pth` will likely appear in private profiles (PLAUSIBLE, resolution not executed). The contract has no rule for classifying it.

**Risk.** A0/A1 become either contract-violating or permanently blocked. A builder may silently narrow "all Python children" to harness-launched ones without an honest residual classification.

**Bounded fix.** In contract §§1–2/5, add a third class, **tool-spawned interpreters**:
- They are allowed only against run-owned interpreters and build environments that contain only manifest-promoted distributions.
- Record the uv version-qualified child argv and environment, from verbose or trace evidence.
- Strip PYTHON* and use only private caches/temp.
- Inventory every `.pth`, `sitecustomize`, `usercustomize` and `*.egg-link` in those environments and in worker roots before use. Classify each as inert or blocking, and record the classification. No user site.
- Classify the result as detective/residual (covered by §5 snapshots), not as prevention.
- Harness-launched entries and workers keep strict `-I -S -B` with the guard.
- Scope "Cover all … Python children" to harness-launched children.

**Future proof.**
- C0: a fake build environment with an armed unclassified `.pth`/`sitecustomize` is refused before the tool runs.
- A1: recorded uv child argv plus before/after snapshots.

### F3 — MANDATORY, Medium — library import-time config and network channels in the prescribed client path are not operationalized (RC-03, HRC-03, HR-15; touches RC-06 budgets)

**Requirement.**
- Contract L48–50: tools must not discover the parent workspace because `.friday_test/` is nested.
- L60: unknown library channel stops the profile.
- Isolation L91–92: do not inherit application configuration or provider credentials.
- Envelope `ambient_application_configuration_or_credentials_allowed:false`.

**Source facts (CONFIRMED).**
- `packages/friday-llm/src/friday_llm/embeddings.py:19` has `import litellm`, and `friday_llm/__init__.py:29` imports `embeddings`.
- The current lock's litellm 1.100.1 `__init__.py:15,26–27` has `import dotenv`; `if os.getenv("LITELLM_MODE","DEV")=="DEV": load_dotenv(...)`.
- With no path argument, python-dotenv's `find_dotenv()` walks upward from the *calling module's directory*. From `.friday_test/runs/<id>/target/.../litellm/`, it reaches the production checkout root and its ancestors.
- litellm also fetches a remote model cost map at import unless `LITELLM_LOCAL_MODEL_COST_MAP=True`. Repository tests already set this (`packages/friday-llm/tests_llm/conftest.py:13`).
- The A1 import/TLS checks (plan L219–226) and the A3 B01–B08 run-owned clients (plan L312–316, matrix C01) import this path.
- A root `.env` does not exist today (existence check only). The channel exists regardless, and `.env` is the documented local mechanism. Ancestors above the checkout were not probed.

**Defect.**
- An environment allowlist does not stop a post-start `load_dotenv` that injects into `os.environ`.
- The worker guard's read-side scope is unspecified, and §5 detection covers writes and metadata changes, not reads.
- No step requires inventorying import-time channels, so the generic "unknown channel" rule never fires.
- The same SDK path (OpenAI SDK/httpx under litellm) can retry by default and consult `urllib` proxies, including macOS system configuration (PLAUSIBLE). That could silently exceed or mis-count the shared 64-request budget unless counting happens at the transport level.

**Risk.** Production provider credentials or config can silently enter the A1/A3 worker. An unexpected network attempt can occur. Request accounting may undercount.

**Bounded fix.** In contract §2's third-party row and §5 prevention:
1. Worker guards refuse Python-level `open` and stat of any path outside declared run and read roots, including every ancestor `.env`.
2. A1 must inventory and record version-qualified import-time config, credential, dotenv and network side effects for every module a profile worker imports. That turns them into known channels.
3. The A1/A3 profile binds explicit neutralizers, for example `LITELLM_MODE=PRODUCTION`, `LITELLM_LOCAL_MODEL_COST_MAP=True`, telemetry/callbacks off, an explicit no-proxy client configuration, and SDK retries disabled or pre-reserved.
4. Request counting happens at the guarded transport or socket layer, so retries are counted against the same 64-request ceiling.
5. An uninventoried channel blocks the profile.

**Future proof.**
- A1 qualification with a private fake parent tree containing a sentinel `.env` above a fake nested test root, using the pinned real library: the sentinel never enters `os.environ`, and a guard refusal is logged for the DEV-mode negative control.
- An in-process stub transport shows retries counted or disabled.
- No real `.env` is read.

### Advisories (non-blocking)

- **A1 (RC-01).** Specify the `.pth` policy for worker private roots (inert-shim classification versus path-line needs versus blocking), as in F2's inventory.
- **A2 (RC-03).** HR-15's fake HOME cannot simulate system-level channels (macOS system proxy, `/etc` configs, Keychain). Require version-qualified source or documentation evidence, or an explicit flag, for native tools, and `ProxyHandler({})`-style explicit configuration for harness clients. Also name `--no-python-downloads`, explicit `--python`, and `.python-version` discovery suppression for uv.
- **A3 (RC-05).** Real default caches (for example a large `~/.cache/uv`) may exceed the finite enumeration bounds and force a block. Allow a streaming canonical-metadata digest with counts, so retained bytes stay small. Clarify that the "64 MiB metadata ceiling" (contract L140) is a retained-manifest bound, not the network metadata budget. Document attribution handling for concurrent non-harness tools (IDE, agents, other uv users) touching shared caches.
- **A4 (RC-02).** Add an explicit lease-free `revoke`/`stop` command with atomic rename to the manual interface, instead of hand-written `state/stop.json`.
- **A5 (RC-02/HRC-05).** State how `all` behaves after A2 promotion: whether `all` invokes or expects `prepare-model`, whether it accepts `--window-receipt`, and how A4 is reached. Make `prepare-model` or `report` print the exact ledger tip and hashes that the operator's window receipt must bind.
- **A6 (HRC-02/04/13).**
  - New files under `tests/` fall inside the root `ruff check .` and `mypy packages tests` gates (`disallow_untyped_defs`). Require conformance to an isolated copy of the root rules so root debt does not grow.
  - Harness tests imported by bare pytest or `.venv` must fail closed.
  - Restore an explicit archive-member/zip-bomb negative in HR-03/04 (it was explicit in v0.1 HR-03).
  - Note that the private validation-tool manifest activation is a construction-time prerequisite for HR-11.
- **A7 (RC-04).** Directive L69–70 ("may change its exported metadata") conflicts with contract L111–116 (export read-only, separate overlay). Align it to "derived overlay only".
- **A8 (RC-06/HRC-16).** LM Studio JIT loading is commonly enabled. Under contract L241–245 this blocks A3 unless a disable-JIT operator settings change is separately authorized. List this as a pending human decision, and label the server version (needed for profile qualification) as operator-attested.

## 7. Fresh versus inspected evidence and limits

**Fresh (executed this session):**
- Hashes, opening and closing boundary, 8 admin checks.
- Targeted Git greps and listings.
- Existence checks.
- Read-only grep of the locked litellm source.

**Inspected only, not executed:**
- uv interpreter-query and PEP 517 child behavior (from uv/PEP 517 design knowledge).
- `ls-files` in a bare view with `GIT_INDEX_FILE`.
- Torch's setuptools requirement.
- httpx/urllib macOS proxy behavior.
- LM Studio V0/V1 response shapes and JIT defaults.

Those are marked PLAUSIBLE. They are design-feasibility inferences, not runtime proof.

**Not done, by design:** no harness exists; no installs, resolution, tests, network or endpoint calls; no `.env`, dirty YAML, `.friday*`, store or cache contents opened; no `HOME`/ancestor probing.

The F3 core facts (import chain, DEV-default `load_dotenv`, cost-map env name) are CONFIRMED from current source. The upward walk is python-dotenv's documented `find_dotenv` behavior.

## 8. Scores (prescribed rubric, honest)

**Coverage: 8.8 / 10.**
- All 16 HRC rows and all 18 HR rows were assessed and traced.
- 14 rows PASS (several with advisories). HRC-03 and HRC-13 are PARTIAL.
- HR-13 and HR-15 have concrete traceability gaps.
- RC-01 and RC-03 are partial; RC-02, RC-04, RC-05 and RC-06 are closed at design level.

**Overall: 8.7 / 10.**

| Area | Score |
| --- | --- |
| Scope/authority | 1.95 / 2 |
| Isolation/effects enforceability | 2.35 / 3 (F1–F3) |
| Clarity/feasibility | 1.70 / 2 (F2 infeasible universal; A5/A7) |
| Verification/evidence | 1.85 / 2 |
| Manual usability | 0.85 / 1 (A4/A5/A8) |

The scores are not inflated toward the gate. All three mandatory fixes are bounded document edits with defined future proofs; none needs new authority, budget changes, production changes, or a second server.

## 9. Closing integrity

Opening and closing boundary both PASS, with an identical logical index (`2ac41719…a073`), HEAD `23253a72`, 17,861 protected files, 27 authority pins and 9 preserved records. The candidate was unchanged throughout the review.

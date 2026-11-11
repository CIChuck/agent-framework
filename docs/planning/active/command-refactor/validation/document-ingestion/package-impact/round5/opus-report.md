# INGEST-PACKAGE-IMPACT-001 — round 5/5 independent council review (Opus seat)

**Verdict: CHANGES_REQUESTED**

- Mode: fresh, independent, read-only review of the document and source feasibility. No delegation, repairs or shared writes. No prior or peer verdicts, reports or builder transcripts were read.
- Candidate: `b7c7b1393d6f18db3d26cc518adce2d8458f315a` on `feature/cmd-ingest-001`
- Correction delta reviewed: `56a495b7..b7c7b139`, limited to `request.review_diff_paths`
- Request SHA256 `befa6d78faefa4f438684ecd110950cbbc6163b5e51a84485067c813b403542e`. It was verified before the request was read.
- Mandatory findings: **1** (Medium)
- Coverage rubric: **9.5 / 10**
- Overall rubric: **9.4 / 10**
- Gate (VERIFIED, zero mandatory findings, both scores ≥ 9.5): **not met by this seat**

This report covers document readiness and source feasibility only. It grants no maintainer satisfaction, Gate-A activation, construction, implementation, acceptance or delivery authority. This is the last authorized round, so no further round is implied.

## Integrity

| Check | Result |
| --- | --- |
| Request hash before reading | match (`befa6d78…`) |
| Helper `read_only_command.py` | match `3acff26f…` |
| Helper `verify_identity.py` | match `c4d9bf96…` |
| `current-controls.json` | match `eea6949d…` |
| `protected-manifest.json` | match `58f72409…` (17,740 members) |
| Opening identity (`verify_identity.py`, own scratch) | PASS: logical index `0db5c6d9…`, HEAD equals the candidate, branch, status, empty staging, 28 pins, 17,740 protected files and 6 preserved metadata entries. Exit 0. |
| Closing identity | PASS: identical result, exit 0 |

The opening and closing outputs are byte-identical: SHA256 `87d6c955…0960` for both JSON files.

## Commands and exits

All Git and administrative calls ran through the pinned `read_only_command.py OWN_SCRATCH -- ARGV` wrapper. Own scratch: `/private/tmp/claude-501/…/scratchpad/r5-review`. The wrapper sets `UV_CACHE_DIR`, `XDG_CACHE_HOME` and `TMPDIR` inside that scratch, with `GIT_OPTIONAL_LOCKS=0` and `PYTHONDONTWRITEBYTECODE=1`.

| # | argv | Exit | Output |
| --- | --- | --- | --- |
| 1 | `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate` | 0 | Development board validation passed: 36 tasks |
| 2 | `… scripts/friday-dev-board.py render --check` | 0 | Planning dashboard is current |
| 3 | `… scripts/check-documentation-lifecycle.py` | 0 | 1041 Markdown files checked |
| 4 | `… scripts/check-package-metadata.py` | 0 | Validated 18 pyproject.toml files (root plus 17) |
| 5 | `git diff --check 8390f368..b7c7b139 -- docs/planning` | 0 | (none) |
| aux | `git diff --stat` and `git diff 56a495b7..b7c7b139 --` the five review paths | 0 | 3 files changed: assessment, REM, test plan. The architecture and guide plans are unchanged. |
| aux | `git diff --name-only f591989e..b7c7b139 -- packages pyproject.toml uv.lock tests docs/guides docs/architecture` | 0 | empty, which reproduces "production source/declarations unchanged" |
| aux | `git diff --name-only 56a495b7..b7c7b139` | 0 | names only; history and report contents not opened |
| aux | `git ls-files` (tui/optimization; transcript/finance tests) | 0 | — |
| aux | `git show 56a495b7:…/execution-log.md` → own scratch, then a byte-prefix comparison | 0 | append-only prefix **True** (229,621 → 231,112 bytes). Contents were not displayed. |

A first attempt to run commands 1–5 used unsplit zsh variables. The shell rejected it with exit 127, so nothing ran. The commands were then re-run with explicit argv, and those runs are the results above.

The raw `authority.json` and `execution-log.md` were hashed only (`ec661cf3…`, `c5cb73ee…`). Both match their pins, and their contents were not displayed.

## Reproduced vs inspected evidence

**Reproduced:**
- the five administrative checks
- the identity checks
- the delta diff and stat
- the claim that source is unchanged since `f591989e`
- the append-only prefix
- 56/56 relative links resolving in the five documents
- existence of every named test, source, guide and README anchor (31 paths)
- the 17 member `pyproject.toml` files: `friday-tui` has no pyproject and is untracked, so it is not a member
- Commands `__all__` has 54 entries and `dependencies = []` (AST and tomllib)

**Inspected as text or AST only:**
- Package dependency declarations: Tools → Finance; Memory → LLM; Optimization → Memory; MCP `full` → Agent/Tools; Runtime → MCP; CLI and Chat scripts.
- The registries, which are three distinct classes:
  - `friday_cli.commands.CommandRegistry` and `arg`, re-exported by CLI
  - `friday_chat.commands.registry.CommandRegistry`
  - `friday_commands.registry.CommandRegistry`

  Chat imports only `friday_cli` display components.
- CLI `repl.py`, `main.py` and `server/api.py`: 5-line docstring placeholders.
- The Chat 2048-character slicer in `adapters.py` and `runtime.py`.
- `persist_directory`, `chroma_path` and `runtime_data_root`.
- The packaged template literal `.friday/vector`.
- Runtime multi-agent assembly in `di.py`.
- The legacy edges: Core `profiles.py` → Memory (lazy); Memory `large_file_processor` → Tools `code_chunker`; Tools memory wrappers → Memory.
- `friday_tools.sandbox.FilesystemSandbox`.
- Optimization source is a 17-line stub with no imports.
- Transcript and Finance `tests/` contents.
- Root `testpaths`.

Nothing was executed: no product or test code, imports, builds, installs, resolution, network, provider, model or store operations.

## Correction-delta review

**PC-08 (test paths and selectors).**
- Transcript and Finance paths are correct: `packages/friday-transcript/tests/` and `packages/friday-finance/tests/` exist.
- Root `testpaths = ["packages/*/tests_*", "experiments/*/tests"]` omits both, so the plan correctly requires explicit future selectors and denies root-collection credit.
- Optimization has no test directory. The plan, the REM row and the P-13 row consistently require a new witness only if justified, with its exact path and selector bound in the directive. No phantom suite and no automatic parallel tree.
- The REM allowlist row and the migration-plan paragraph and table agree.
- **One defect.** The Finance explicit-selector requirement directs future construction validation to run the whole directory "including retained cases". That directory contains an unguarded live-network module (Finding 1).

**PC-09 (routing and budget).** These all coherently state v0.5, four completed rounds and exactly one extension, round 5 of 5, with no reset, replacement or sixth round, and a stop for guidance if the gate is unmet:
- assessment header, Basis, revision note, change-control paragraph and step 4
- REM header and closing Next decision
- current-controls `current_scope`, `next_gate` and `current_authorization`
- council fields: round 5, completed 4, max 5, remaining 1, `budget_reset: false`
- board `next_gate`
- packet README, next-phase, tactical-plan, Gate-A handoff and branch handoff

Historical records keep their original labels. The `test-doc-revision-authorization.json` budget (max 4, next 3) is unedited and is marked historical in controls. The original `iteration-authorization.json` is unchanged and pinned. No defect.

## PI-01–18 matrix

| ID | Result | Evidence and notes |
| --- | --- | --- |
| PI-01 | Met | 17 rows, each once: 8 implementation (CLI conditional) plus 9 source-unchanged compatibility packages. Membership comes from `members = ["packages/*"]` with 17 pyprojects. Test and dependency impact is kept separate from the absence of source edits. |
| PI-02 | Met | Every proposed edit maps to REM path-table rows and annex or companion IDs. P-10–17 are test-only conditional, and no new owner appears. |
| PI-03 | Met | Ownership statements match declared dependencies. Legacy lazy edges are verified and disclosed without being broadened. Headless reuse goes through Core injection. |
| PI-04 | Met | The P-02 INGEST/companion split, the Basis bullets and the readiness row "Tools completion boundary" make it explicit that a combined unit requires a scope revision. |
| PI-05 | Met | The default Chat stack, Tools extra, Certifi floor, LLM `embedding-limits` extra and inheritance (Runtime, CLI, Agent, MCP `full`, Optimization) are covered. Versions and assets are left as Gate-A outputs. Commands is stdlib-only, verified. |
| PI-06 | Met | Pool and non-pool selection is retained. Missing-field readiness, possible hosted-baseline non-qualification and illustrative Qwen are covered. Baseline and replacement positives are required alongside refusals. |
| PI-07 | Met | Store identity, same-dimension refusal, explicit fresh paths (vector, graph, WAL), preserved legacy files, `/read` availability, graph and recovery v2, and the old-release upgrade note. No reset or migration. |
| PI-08 | Met | `document`/512 defaults, three overrides and precedence. Source, derived and cache handoffs; unsplit MCP and derived records. No URL route or double chunking. The slicer claim is verified in source. |
| PI-09 | Met | Agent (FC-06), the Memory-owned multi-agent stack, metadata (FC-13), Telemetry existing-reason mapping and MCP Chat/Memory ownership. No transport or schema expansion. |
| PI-10 | Met | P-04, P-06 and P-07 cover admission before side effects, task and sink ownership, profile isolation, truthful counts and explicit origin. CLI edits are conditional and add no launcher; CLI has no `scripts`, verified. |
| PI-11 | Met | MCP and backups are causal consumers. Live-marker protection is required and FU-013/014 stay unwaived with no credit. |
| PI-12 | **Partly met — Finding 1** | References are generally accurate and future evidence is distinguished from completed work. However, the newly prescribed Finance selector would run unauthorized live-provider tests. |
| PI-13 | Met | The readiness table lists versions, backends, model and counter, licenses, assets, numeric limits, signatures and final path coverage. Missing qualification is a stop. |
| PI-14 | Met | Approval steps 1–4: Chuck's explicit satisfaction against the exact post-Gate-A version, commit and SHA256 as a required referenced appendix. Material changes return for review, and conditional approval of the REM (`e1c90753…`) is not carried forward. |
| PI-15 | Met | Each row gives change type, planned upgrade, purpose, retained behavior and evidence. No invented effort metrics. Dense but readable. |
| PI-16 | Met | Identities, links, current-state consistency, append-only log and preservation are reproduced. The current council is separated from the historical `f43368c5`/`1a040de3` verdicts. |
| PI-17 | **Met with Finding 1 interaction** | Explicit dispositions, a frozen inventory and old-to-new map before the first rewrite, the annex preservation reconciliation (incorporated case-level exceptions; unmapped bodies, public signatures, classes and named FC nodes protected), executed coverage for every valid requirement, and no skips or churn. The Finance selector needs live/offline classification. |
| PI-18 | Met | The canonical `docs/architecture/command-execution.md` and named guide, README and template rewrites are specified. The three registries are disambiguated by qualified name, owner and caller (verified), and the CLI placeholders are classified accurately (verified). DI-36 acceptance goes beyond link checks: source map, verified examples and independent review. |

## Mandatory findings

### Finding 1 — Medium — Finance explicit selector mandates unauthorized live-provider tests

**Controlling requirements:**
- `independent-validation-policy.md`, *External And Live Validation*: live-provider validation "requires explicit authority identifying the permitted service and effects". The *Candidate Freeze* section also requires the request to state the permitted credentials and live-provider tests.
- AGENTS.md: validation does not authorize any external side effect.
- PI-12: accurate verification references.
- PI-17: no weakening of production safety, and no silent skips.
- The REM and test plan's own offline / no-provider discipline.

**Affected text:**
- `test-migration-plan.md`, "Explicit execution of non-default suites": "Construction validation must therefore run them explicitly, including retained cases …", followed by `uv run --no-sync pytest packages/friday-finance/tests -q`.
- The P-14 row: "Retain existing behavior tests in `packages/friday-finance/tests/`".
- REM path row: "Transcript and Finance require explicit suite selectors … the migration plan specifies the future run commands."

**Source evidence (text inspection only):** `packages/friday-finance/tests/test_integration_massive.py`
- Line 5 says the tests "use a real API key and hit the live Massive API".
- Line 20 holds a hard-coded credential literal. The value is not reproduced here.
- The fixture at lines 23–31 builds a real client.
- There are 10 async tests at lines 39–150 with no skip, marker or environment guard.
- `test_basics.py` is offline: registry, governor and monkeypatched key tests.
- The four Transcript test modules are offline.

**Risk.** Followed as written, construction validation would:
- make about 10 rate-limited live external calls (about 12 s spacing) using a committed credential, with no recorded authority for that service or its effects;
- tie "retained executed coverage" for Finance to external availability, quota and key validity, so pass or fail becomes non-reproducible;
- blur "existing failures remain failed/unwaived" with external outages.

This also contradicts the plan's own private-environment framing.

**Bounded document fix (test plan, P-14 row and REM row text only; no source or test edits):**
1. Classify `packages/friday-finance/tests/test_integration_massive.py` as a pre-existing live-provider module. It is excluded from INGEST construction validation unless the final directive records explicit maintainer authority naming the service, credential source and effects. It gets no retained-coverage credit and is not repaired under this unit.
2. Change the Finance example selector to the offline module, for example `uv run --no-sync pytest packages/friday-finance/tests/test_basics.py -q`, or an explicit `--deselect`/path form. Require the directive's inventory to classify each non-default suite module as offline or live before execution.
3. Mirror a one-clause note in the REM allowlist row and the P-14 migration row.

**Recheck:**
- The test plan names an offline-only Finance selector, or explicit live authority.
- The P-14 and REM rows agree.
- No retained-coverage claim depends on the live module.
- No other prescribed selector covers an unguarded live-network module. The Transcript `tests/` modules were inspected and are offline.

## Optional advisories (non-mandatory)

- **A-1 (security, pre-existing).** `test_integration_massive.py` line 20 commits a live API credential in tracked source. It is outside this unit, so it should not be repaired here. The maintainer may want to consider rotating it and recording a framework follow-up (for example, in the upgrade log). The value is intentionally not reproduced.
- **A-2.** The root `friday-framework` aggregate distribution is the 18th pyproject; it is not a member row. Its default dependencies include `friday-chat`, so its default install also inherits the new document stack. Its legacy `documents` extra (`tools[documents]` = pypdf/python-docx) does not mean Docling support. A one-line mention under *Dependency consequences* or the quick-start guide scope would help maintainers and operators.
- **A-3.** Root `tests/integration/` is also outside root `testpaths`. The annex and REM name exact integration nodes, so the risk is low. The explicit-selector paragraph could still state that named root integration nodes and `test_package_cohort_metadata.py` run by explicit path as well.

## Scores (independent, not averaged, not targeted)

| Coverage rubric | Max | Score |
| --- | --- | --- |
| All-package inventory and accurate source/dependency/test classification | 3.0 | 2.85 |
| Material behavior, configuration and data effects | 2.0 | 1.95 |
| Shared ownership and dependency/deployment consequences | 2.0 | 1.95 |
| Traceable boundaries, compatibility and required proofs | 2.0 | 1.75 |
| Unresolved readiness details and approval completeness | 1.0 | 1.00 |
| **Total** | 10 | **9.5** |

| Overall rubric | Max | Score |
| --- | --- | --- |
| Accuracy against current scope and source | 3.0 | 2.85 |
| Architecture and bounded delivery | 2.0 | 1.95 |
| Data/configuration/dependency safety | 2.0 | 1.80 |
| Evidence, future-work distinctions and reproducibility | 1.5 | 1.35 |
| Maintainer readability and approval/change control | 1.5 | 1.45 |
| **Total** | 10 | **9.4** |

The mandatory finding overrides the scores in any case. Gate outcome for this seat: not met.

## Limits and disclosures

- No product, test or import execution. The future pytest selectors were assessed only from source and metadata; none was run.
- The two dirty Chat example YAML files, `.friday-old/`, exports, stores, secrets, other scratch areas, peer reports and builder transcripts were not read. The `round4/*-report.md` file names appeared in a name-only diff listing and were never opened. No peer verdict was exposed.
- The pinned `verify_identity.py` hashes, but does not display, the dirty YAML files and exports as part of its preservation check.
- One wrapper receipt in own scratch stores the stdout of `git show` for the historical execution-log blob, kept for the byte-prefix check. It was not displayed or read.
- The Finance credential literal was seen once in a `grep` match while classifying the module. It is not reproduced in this report (see A-1).
- Required future outputs are intentionally deferred to readiness and construction, so their absence is not treated as a gap: full case inventory, rewritten suites, live architecture and guides, and real format, model, B/N/R and installed proofs.
- No reviewer writes to the repository, index, branch, worktrees or supplied scratch. No cleanup, restoration, delegation or additional round.

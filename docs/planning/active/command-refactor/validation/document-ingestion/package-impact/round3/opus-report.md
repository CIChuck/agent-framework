# INGEST-PACKAGE-IMPACT-001 — Council round 3/4, seat Opus (claude-opus-5-5)

**Verdict: CHANGES_REQUESTED**. Three mandatory findings (PI-R3-OPUS-001 to 003).
Coverage **9.1/10**, overall **9.0/10**. Neither score reaches 9.5, and the
scores do not waive any finding.

Candidate `c96ecbea685a2627e033d3a9cb62a2f05b72afb7` on branch
`feature/cmd-ingest-001`. Delta base `f591989e`, base `8390f368`.

This was a fresh, independent, read-only review. I received no builder
reasoning, peer reports or prior verdicts. I made no delegation, repair or
shared writes. This report covers the current documents only. It grants no
maintainer satisfaction, Gate-A activation, construction directive approval,
test, product or live-guide implementation authority, acceptance or delivery.

## Integrity

| Check | Result |
| --- | --- |
| Request SHA256 checked before reading | `475c9d63…faed2`: match |
| `read_only_command.py`, `verify_identity.py`, `current-controls.json`, `protected-manifest.json` | All four match their pins. I read both helpers before running them. |
| Opening `verify_identity` | PASS. Logical index `f358ac6c…abf2` was hashed before status. HEAD and branch match. 17,720 protected files checked; 6 preserved items checked; no errors. |
| Closing `verify_identity` | PASS with the same values and no errors. |
| `authority.json` | Hashed only: `d9ae79b9…aeadd` matches its pin. Raw content not read. |
| `execution-log.md` delta | Append-only. Numstat is +25/−0. The new bytes start with the old bytes (226,366 → 227,937). |
| Scope of changes since `8390f368` | Only `docs/planning/**` changed. No product source, test, package metadata or guide changed. |
| Annex and Tools companion | `1092a332…` and `8220e195…` are identical at `f43368c5` and at the candidate. |
| REM | `e1c90753…` from `f43368c5` through `f591989e`, then `4e428abd…` at the candidate. It changed only in this delta. |

Scratch directory: `/private/tmp/claude-501/-Users-chuckrussell-Dev-gendev-agent-framework/0254d659-b2fa-4da1-a778-95f6e0c0eb20/scratchpad/pi-r3-opus`.
It is outside the checkout and outside all supplied roots. The helper writes a
command receipt here for each Git/admin call.

## Commands run

All Git and admin commands went through
`python3 -B …/read_only_command.py OWN_SCRATCH -- ARGV`.

| Command | Exit |
| --- | --- |
| `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate` ("36 tasks") | 0 |
| `… scripts/friday-dev-board.py render --check` ("dashboard is current") | 0 |
| `… scripts/check-documentation-lifecycle.py` (1,033 Markdown files) | 0 |
| `… scripts/check-package-metadata.py` (18 pyproject files) | 0 |
| `git diff --check 8390f368..c96ecbea -- docs/planning` | 0 |
| `git diff --numstat` and scoped `git diff` (review_diff_paths only), `f591989e..c96ecbea` | 0 |
| `git show <rev>:<path>`: REM, annex, companion and log, at six commits | 0 |
| `git ls-files packages/friday-tui` (empty) | 0 |

I also used plain read-only tools: `grep`, `sed`, `cat`, `wc`, an isolated
`python3 -I` tomllib/AST read of the 17 `pyproject.toml` files and
`friday_commands/__init__.py`, and `shasum`. I executed no tests or product
code. I made no installs, downloads, provider or model calls, and touched no
stores. I did not read the dirty Chat YAML contents, `.friday-old`, the
exports, raw authority history, or peer and historical reports.

## Reproduced vs inspected

- **Reproduced:** hashes, identity, append-only log, admin checks and scoped
  whitespace.
- **Inspected as text or AST:** source and test anchors, current guides,
  package READMEs and pyproject declarations.
- **Not reproduced (intentional future obligations):** Gate-A, B/N/R, installed
  lanes, case-level inventory, the canonical architecture file and the guide
  rewrites.

## Source grounding performed

- **17 packages.** There are 17 `packages/*/pyproject.toml` files and root
  `members = ["packages/*"]`. `packages/friday-tui` holds only ignored
  `__pycache__` residue, has no pyproject and no tracked files, and is not a
  member.
- **Dependency edges match the rows.**
  - Tools depends on Finance.
  - The MCP `full` extra pulls Tools and Agent; Agent pulls Memory.
  - Optimization, Runtime, CLI and Agent each depend on Memory.
  - Memory depends on LLM.
  - Commands has no dependencies.
  - Tools has no declared dependency on Memory.
  - The legacy Tools extras `documents`, `spreadsheets` and `all-formats` exist.
- **Commands root API.** The root `__all__` has 54 entries (API54).
- **Chat.**
  - `commands/files.py` returns placeholders for `.pdf`, `.docx` and `.xlsx`, and has no PPTX handling.
  - `adapters.py:385/2462` uses `smart_file.chunk_size or 2048`; `_chunk_text` is the character slicer.
  - `config.py:477` defines `persist_directory`.
- **Runtime.**
  - `chroma_path`, `runtime_data_root` and `memory_mode` are in `{single_agent, multi_agent}`.
  - `di.py` builds the multi-agent controller, journal and coordinator stack.
- **Retained lazy edges.** Core `profiles.py` imports Memory adapters lazily.
  Memory `large_file_processor.py:525` imports `friday_tools`.
- **Other source anchors.** `mutation.py` has the 8192 ceiling. `FilesystemSandbox`
  is in `friday_tools/sandbox.py`.
- **Test anchors named by the migration plan all exist.**
  - Chat `test_read_dispatches_supported_extensions` mixes text cases with
    placeholder PDF/DOCX/XLSX cases. It is a genuine split/rewrite candidate.
  - `test_package_cohort_metadata.py` iterates optional extras for lockstep
    internal pins. It is a legitimate regression witness.
- **Guides and READMEs.** All guides and package READMEs named in the plans and
  the REM path table exist. `docs/architecture/README.md` says there is no
  current architecture document, so the future `command-execution.md` is a
  correct placement.

## PI-01–18 matrix

| ID | Result | Evidence |
| --- | --- | --- |
| PI-01 | PASS | 17 rows, each once: 8 implementation (CLI conditional) and 9 source-unchanged. The v0.3 wording "source-unchanged ≠ test-unchanged" is correct. |
| PI-02 | PARTIAL | Rows trace to REM, annex and companion paths. The G1/G2 path rows are added explicitly. The unchanged annex assertion-body rule is not reconciled with G1 (PI-R3-OPUS-002). |
| PI-03 | PASS | Ownership and dependency direction match the declarations. Retained lazy edges are disclosed. |
| PI-04 | PASS | INGEST and TOOLS-DOC are kept separate in the Tools row, the Basis section, the readiness table and the test plan ("companion-only routing cases"). |
| PI-05 | PASS | Default Chat document stack, optional Tools extra, Certifi floor, counter extra and headless inheritance. Versions are left unresolved. |
| PI-06 | PASS | Pool/non-pool, missing-field readiness, hosted-baseline uncertainty, Qwen illustrative only, positives required. |
| PI-07 | PASS | Identity-free store refusal, fresh-path rules, WAL and graph, `/read` availability, recovery v2, no reset or migration. |
| PI-08 | PASS | document/512 defaults, three strategies, precedence, `smart_file` keys are not aliases, records unsplit, no URL route. |
| PI-09 | PASS | Agent and multi-agent, metadata, telemetry, transcript and MCP consumers, with correct owners. |
| PI-10 | PASS | Memory has the broadest impact. Chat and Runtime wiring, admission before side effects, conditional CLI, no launcher. |
| PI-11 | PASS | MCP and backups are causal consumers. Live-marker protection is required. FU-013/014 are unwaived with no credit. |
| PI-12 | PASS | Future evidence is clearly separated from completed work. No static conformance claim. |
| PI-13 | PASS | Readiness table is complete. Missing qualification is treated as a stop. |
| PI-14 | PARTIAL | Exact post-Gate-A satisfaction binding is good. The conditional approval refers to REM bytes `e1c90753` but is presented without that qualification, next to a "frozen REM" claim (PI-R3-OPUS-001). |
| PI-15 | PASS | The table is readable. See advisory A-04. |
| PI-16 | FAIL | `package-impact-assessment.md:253-255` says the REM is frozen and its reviewed hash unaltered. The REM changed at this candidate (PI-R3-OPUS-001). The README, next-phase, tactical, handoffs and criteria are otherwise consistent, and the log is append-only. |
| PI-17 | PARTIAL | Strong plan: five dispositions, case/fixture/oracle map frozen before rewrites, gate IDs stable, API54 literals kept, no skips or count laundering, historical evidence immutable, all 17 package rows. The permission conflicts textually with normative annex lines 579–580 (PI-R3-OPUS-002). |
| PI-18 | PARTIAL | Concrete canonical path, six content areas, diagrams, a DI-36 evidence table that goes beyond link checks, and named guide sections. The CLI command-architecture scope omits Friday CLI's exported legacy slash-command registry and the three-registry disambiguation (PI-R3-OPUS-003). |

## Mandatory findings

### PI-R3-OPUS-001: Assessment claims a "frozen" REM with unaltered hashes; the REM was amended and the conditional approval is not qualified

- **Severity:** Medium.
- **Requirement:** PI-16 (current-state consistency; no fresh-review claim for
  edited technical contracts) and PI-14 (conditional approval and binding).
- **Affected text:** `package-impact-assessment.md:253-255` ("links it
  alongside the frozen REM; the REM/annex/companion are not rewritten to add a
  navigation link or alter their reviewed hashes") and line 13 ("Chuck's
  approval of REM-CMD-INGEST-001 is conditional").
- **Evidence:**
  - The REM SHA256 was `e1c90753…` at `f43368c5`, `1a040de3` and `f591989e`. It
    is `4e428abd…` at the candidate. The diff rewrites the status header,
    removes the old "keep old assertion bodies" rule, adds G1/G2, DI-35/36 and
    path rows, and changes the line-456 API54 wording.
  - `current-controls.conditional_maintainer_approval.document_sha256` is
    `e1c90753…`.
  - `review-criteria.md` itself was corrected from "frozen REM" to "current
    amended REM"; the assessment was not.
- **Risk:** A maintainer reading the change-control section could conclude
  that the REM bytes are unchanged and that the recorded conditional approval
  covers the amended REM. That misstates the approval basis, which this
  section exists to make exact.
- **Bounded document fix:** Replace lines 253–255 with an accurate statement:
  - The annex and Tools companion remain unchanged at their reviewed hashes.
  - The REM was amended at Chuck's direction (G1/G2, DI-35/36, path rows) and
    now requires fresh review.
  - Chuck's recorded conditional REM approval referenced the earlier bytes
    `e1c90753…`.
  - The final directive approval must cover the exact amended REM bytes.

  Optionally, add the same qualification in one sentence after line 13. Do not
  edit the annex, the companion or the historical evidence.
- **Recheck:**
  - `grep -n "frozen REM" package-impact-assessment.md` returns nothing.
  - The text names unchanged annex/companion hashes and amended REM status
    consistent with the README, next-phase and current-controls.
  - Hashes are re-verified.

### PI-R3-OPUS-002: The unchanged normative annex still requires keeping old assertion bodies; G1 and the migration plan do not reconcile it

- **Severity:** Medium.
- **Requirement:** PI-17 (coherent restructuring permission that preserves gate
  obligations) and PI-02 (trace to the unchanged annex). The request also asks
  for review against the unchanged normative annex.
- **Affected text:**
  - REM §G1 (lines 1321–1347).
  - `test-migration-plan.md:5-39`.
  - The assessment section "First-class test migration deliverable".
- **Evidence:**
  - `embedding-compatibility-contract.md:579-580` (unchanged `1092a332…`, and
    declared "part of this REM") says: "Keep old public signatures/classes and
    assertion bodies except the named final-directive fixture/oracle
    exceptions."
  - G1 permits renaming, moving, splitting, rewriting, replacing and retiring
    tests, and says not to require that bodies "remain AST-identical".
  - The REM text that was removed in this delta contained the matching
    assertion-body rule. The annex copy remains.
  - A grep of REM §F/G1 and all three plans finds no reference to this annex
    clause and no precedence statement.
  - Renames, retirements and helper splits are not "fixture/oracle exceptions"
    in the annex's terms.
- **Risk:** Two binding texts conflict:
  - A builder or validator applying the annex literally would reject the case
    restructuring Chuck authorized.
  - A reader applying G1 might treat the restructuring permission as reaching
    the public signature/class retention that the annex keeps.

  Either reading undermines DI-35 acceptance and the single-directive binding.
- **Bounded document fix:** Add a short reconciliation paragraph to REM G1 and
  the test migration plan, plus one sentence in the assessment. Do not edit the
  annex bytes. The paragraph should state:
  - The annex's public-signature/class retention is unchanged.
  - Each restructure, rewrite, replace or retire entry in the frozen
    final-directive case-level map is the "named final-directive fixture/oracle
    exception" the annex refers to.
  - Assertion-body changes that are not mapped remain prohibited.
  - The FC-named integration nodes stay as the annex tables list them unless
    the directive maps an approved equivalent that preserves the gate
    obligation.
- **Recheck:**
  - G1 and the plan cite `embedding-compatibility-contract.md` for this clause.
  - Annex SHA256 is still `1092a332…`.
  - No remaining text implies that unmapped body edits are allowed or that
    public signatures may change.

### PI-R3-OPUS-003: The canonical architecture plan omits Friday CLI's legacy slash-command registry and does not require disambiguating the three `CommandRegistry` classes

- **Severity:** Medium.
- **Requirement:** PI-18 (the plan must name the Chat/CLI/Runtime flow, with
  the CLI role mapped accurately). Maintainer direction: documentation must
  cover "key command architecture portions in Friday Chat and Friday CLI".
- **Affected text:**
  - `command-architecture-update-plan.md:26-29` (item 2 covers only the
    display/session components, container delegation, headless composition,
    origin and readiness).
  - REM G2 and its architecture path row.
  - The guide-handoff Core concepts and CLI rows.
- **Evidence:** Three distinct classes share the name `CommandRegistry`:

  | Class | Location | Role |
  | --- | --- | --- |
  | `friday_cli.commands.CommandRegistry` | 522 lines, with `arg` | Exported from the `friday_cli` root (`__init__.py:30,133`). The CLI README lists it as "Slash commands \| `CommandRegistry`, `arg`". |
  | `friday_chat.commands.registry.CommandRegistry` | `registry.py:89` | Built by `build_default_registry`. Used by `app.py`. |
  | `friday_commands.registry.CommandRegistry` | `registry.py:41` | The neutral foundation. |

  Chat delegates its pilot, session-views, diagnostics and memory-query
  families to `friday_commands`, and uses `friday_cli` display components.
  `friday_cli/repl.py`, `main.py` and `server/api.py` are 5-line placeholders.

  The plan mentions none of the following:
  - the CLI's own command dispatch surface;
  - which registry the maintained `friday-chat` executable actually uses;
  - the compatibility status of the CLI's legacy registry, REPL and server
    modules.
- **Risk:** A canonical "single account of command execution" written to this
  plan can omit or confuse the CLI's command layer. Same-named registries would
  remain unexplained, and the CLI README "Slash commands" row would stay
  inconsistent with the shared Commands foundation. That is exactly the
  CLI command-architecture area Chuck asked to have rewritten.
- **Bounded document fix:**
  - Add a requirement to plan item 2, mirrored as one clause in REM G2 and the
    guide handoff's CLI/README coverage, that the canonical document and the
    CLI README:
    - map `friday_cli`'s exported legacy `CommandRegistry`/`arg` and its
      placeholder REPL/main/server modules as compatibility surfaces;
    - disambiguate them from Chat's registry and from `friday_commands`'
      foundation registry;
    - state which registry the maintained `friday-chat` dispatches through.
  - Introduce no migration, removal or new feature for the legacy CLI registry.
- **Recheck:** The plan, G2 and guide handoff name all three registries with
  their owners and status. Source paths are cited. Item 2 still contains no
  launcher or new-feature claim.

## Advisories (non-blocking)

- **A-01: Unlisted guide pages.** `docs/guides/FRIDAY-FEATURES.md` (the
  capability-status catalogue) and `01-executive-summary.md` are not in the
  guide coverage or the allowlist.
  - FRIDAY-FEATURES line 23 says the CLI `friday` executable is a "declared
    placeholder entry point", which is stale against the current declarations.
    It also has no document-extraction or embedding-limit status row.
  - The executive summary says that changing embedding models "can require
    rebuilding compatible collections", which differs from the
    fresh-namespace, no-re-embed policy.
  - Either include them "where affected" or record why they are excluded, to
    keep DI-36 cross-document consistency coherent.
- **A-02: Test edits outside the allowlist.** Test-plan rows P-10 to P-15 and
  P-17 allow optional test additions or adaptations in Telemetry, Transcript,
  MCP, Optimization, Finance, Speech and Moltbook package-local suites. The
  REM G1 row covers only "named owners and focused source-unchanged consumer
  suites above" (Agent, multi-agent, MEMQ, CLI, Runtime, Core). Say that any
  such suite must be named in the final allowlist and surfaced to Chuck.
  Line 111 of the plan implies this, but not explicitly.
- **A-03: Missing test anchors.** Add anchors that pair with allowlisted
  source:
  - Runtime `tests_runtime/test_di.py` (`di.py` is the main Runtime change);
  - Memory `test_mcp_memory.py`, `test_large_file_processor.py`,
    `test_controller*.py` and `test_tool_lifecycle.py`.
- **A-04: Change-type column.** The column for P-01, P-03, P-04, P-05, P-07
  and P-08 omits the README/documentation that REM path rows now assign to
  them. The preamble covers this, but the table reads incompletely.
- **A-05: README list mismatch.** The guide handoff's package README paragraph
  names only the Tools and Chat READMEs. Align it with the REM row that adds
  the Core, Commands, LLM, Memory, Runtime and CLI READMEs.
- **A-06: Package counting.** The canonical "17-package map" should derive the
  count from pyproject membership. The ignored `packages/friday-tui` residue
  would otherwise inflate a directory glob.

## Rubric totals (honest, independent)

| Coverage | Score | Max |
| --- | --- | --- |
| All-package inventory and source/dependency/test classification | 2.9 | 3.0 |
| Material behavior, configuration and data effects | 1.9 | 2.0 |
| Shared ownership and dependency/deployment consequences | 1.7 | 2.0 |
| Traceable boundaries, compatibility and required proofs | 1.7 | 2.0 |
| Unresolved readiness details and approval completeness | 0.9 | 1.0 |
| **Total** | **9.1** | **10** |

| Overall | Score | Max |
| --- | --- | --- |
| Accuracy against current scope and source | 2.6 | 3.0 |
| Architecture and bounded delivery | 1.8 | 2.0 |
| Data/configuration/dependency safety | 1.9 | 2.0 |
| Evidence, future-work distinctions and reproducibility | 1.4 | 1.5 |
| Maintainer readability and approval/change control | 1.3 | 1.5 |
| **Total** | **9.0** | **10** |

Outcome: **CHANGES_REQUESTED**. The candidate does not meet the gate for this
seat: there are mandatory findings, and both scores are below 9.5.

## What is sound

These are not findings, and they earn no approval credit.

- The test-restructuring permission is well bounded: five dispositions, a
  frozen inventory and map before any rewrite, no skips or xfails, no
  count-based equivalence, call-phase witnesses, immutable historical evidence,
  stable gate IDs and API54 literals.
- Documentation acceptance properly goes beyond link checks: a
  content/source/example/independent-review matrix, alpha3 provenance and
  separate TOOLS-DOC claims.
- No new product feature, dependency, route or live implementation was
  introduced.
- All earlier PI-01–13 substance remains source-consistent.

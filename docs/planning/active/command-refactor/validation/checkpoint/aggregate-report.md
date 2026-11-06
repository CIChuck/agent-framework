# Aggregate checkpoint review

CHANGES_REQUESTED

Candidate: `dea496075de55060ad477820e04b71c78239cca0`

Base: `c34269867be50f71923c93c95a63236a35505812`

Branch: `feature/command-refactor`

Review: full aggregate checkpoint review, including product changes, tooling,
governance, archives and planning transfers. Fresh Codex validator
`/root/checkpoint_aggregate_validation`, GPT-6 family; exact serving version
unavailable. Evidence window: 2026-11-06T23:19:08Z–23:34:01Z. No builder
transcript/private reasoning, delegation, repository edits or external mutations.
Historical memory/prior reports supplied navigation/provenance only, not
correctness verdicts. The controller transcribed the returned report below.

## Mandatory findings

**AGG-001 — Medium: archival automation lacks recorded construction authority.**

Affected: `scripts/friday-dev-board.py:393` and
`tests/integration/test_development_board.py:491`, introduced through
`40f9ed6f8e510fcaf9da08c6638ba1338e2bb8e8`, from `78126dcd`/`c3bfff8b`.
These changes alter accepted-history validation, required evidence-path checks
and archive requirements. October 24 direction authorizes full-folder archival,
but no exact construction directive or explicit applicable exception was found
for these post-adoption script/test changes. The September exception covers
earlier automation; its documentation exemption excludes automation scripts.

Violation: AGG-01, `AGENTS.md:37`, and independent-validation-policy construction
directive requirements. Passing tests do not supply missing authority.

Required disposition: an explicit maintainer decision identifying this exact
historical scope, source revisions, requirements and verification, then fresh
independent validation. Preserve chronology; do not backdate approval or call
checkpoint delivery authorization retrospective construction approval. No
product/configuration repair is implied.

**AGG-002 — Low, mandatory: five formatting regressions fail the required check.**

These files pass Ruff formatting at the base and fail at the candidate:

| File | Representative line |
| --- | ---: |
| packages/friday-chat/tests_chat/test_mcp_http_integration.py | 139 |
| packages/friday-mcp/src/friday_mcp/client/protocol.py | 371 |
| packages/friday-mcp/tests_mcp/client/test_http_lifecycle.py | 1145 |
| packages/friday-runtime/tests_runtime/test_mcp_runtime_config.py | 418 |
| scripts/friday-dev-board.py | 568 |

Frozen-overlay `ruff format --check --no-cache` across 34 changed Python files
exits 1. Five other failures already exist at base and are separately classified.
Violation: required focused format check under AGG-04 and deterministic-check
gate. No applicable waiver was found. Required mitigation: authorized mechanical
formatting, preserving behavior/historical evidence, followed by fresh review of
the new candidate. No configuration/documentation behavior change is needed.

## Criterion results

| Criterion | Result and evidence |
| --- | --- |
| AGG-01 | CHANGES_REQUESTED: complete tooling/product authority review; AGG-001. Other examined units have bounded recorded authorities. |
| AGG-02 | VERIFIED: MCP compatibility/schema/admission/withholding/budget/generation/dispatch boundaries inspected; 1,858 MCP/Runtime, 60 core MCP and 826 Chat tests pass. |
| AGG-03 | VERIFIED: API-01–06, neutral imports, package/cohort/exact lock delta and CLI/finance fixes; Chat 50/3, no retirement or wiring. |
| AGG-04 | CHANGES_REQUESTED: functional/lint/type/metadata/package checks pass; AGG-002. Broad debt separated. |
| AGG-05 | CHANGES_REQUESTED: archive/lifecycle integrity passes, archival automation authority gap remains. |
| AGG-06 | VERIFIED: TUI documentation-only started/normal/design_only; historical authority separated; ten links identify historical Git objects; RET-001 unapproved. |
| AGG-07 | VERIFIED: frozen inputs/configurations preserved; no examined new snapshot secret/state/cache/unsafe-path issue. |
| AGG-08 | CHANGES_REQUESTED: publication/merge readiness awaits disposition and fresh validation; full feature/TUI acceptance separate. |

## Actual checks

All package/root checks used `uv run --offline --frozen --no-sync
--no-python-downloads --with-editable packages/friday-commands …`.
Source origin/version were established before tests. Tools: uv 0.11.3, Python
3.13.10, pytest 9.0.2, Ruff 0.14.10, mypy 1.19.1. Bytecode/pytest/Ruff caches
disabled; mypy/build outputs in scratch; UV used a private clone of existing cache.

| Check | Actual result |
| --- | --- |
| Foundation/cohort/development-board integration | Exit 0; 202 passed |
| Full framework CLI | Exit 0; 155 passed |
| Full MCP client + Runtime | Exit 0; 1,858 passed |
| Full provider-free Chat | Exit 0; 826 passed, zero skips, one deprecation warning |
| Core MCP | Exit 0; 60 passed |
| Focused tools | Exit 0; 9 passed |
| Offline PR-watcher regressions | Exit 0; 6 passed |
| Focused Ruff, 34 changed Python files | Exit 0 |
| Focused mypy, 18 source/script files | Exit 0 |
| Focused format | Exit 1; ten files, five demonstrated regressions |
| Board validate/next/show | Exit 0; 36 tasks, command initiative started/granted/local |
| Documentation lifecycle | Exit 0; 852 Markdown files |
| Package metadata | Exit 0; 18 projects |
| Offline lock | Exit 0; 214 packages |
| Exact foundation parsed-lock comparison | Exit 0; only approved new member/package/two root references |
| Working/full-diff whitespace | Exit 0 |
| Fresh offline builds/artifact checks | Exit 0; commands, Chat, CLI, tools, MCP, core, Runtime, finance, root; 9 wheels/9 sdists |
| Missing typing/dependency/entry-point probes | All three correctly refused |
| Fresh standalone foundation no-deps install/smoke | Exit 0 |
| Default dependency profile/replay | Exit 0; 129 compatible distributions, exact versions/metadata, 50/3/help/finance/SDK, no friday launcher |
| Installed source/metadata equality | 239 members across seven fresh wheels |
| Independent schema/reference/Unicode registry probes | Exit 0 |
| Skill metadata/deployment | Nine bundles and 22 discovery links valid |

Total: 3,116 passing tests across the seven listed test lanes. Chat used committed
examples in scratch, xterm, and the documented temporary plugin changing only
two example constants in designated modules. Only `test_live_lmstudio.py` was
excluded. External destinations were denied before imports; disposable loopback
fixtures were allowed. LiteLLM's remote price-map attempt was blocked and used
its local fallback.

Archive checks: eight historical manifests/126 records, 14,665 relocated records,
80 archive link replacements, seven completion proposals and ten checkpoint
repairs match. Transfer chain: 67 imported source documents, 280 transferred/
42 unchanged documents and 251 relocation records reconcile through preserved
snapshots. All 33 tar archives/7,650 members inspected without extraction. Cache
members in two older archives are byte-identical to base; new snapshots contain
none of the flagged cache/state/unsafe paths. Common secret/private-key shape
scans found no matches in 531 new/modified files or 344 snapshot members.

## Baselines, limits and preservation

- Root Ruff exits 1: 534 findings/13 files, all base-identical including mapped
  archive relocations. Not a passing broad gate.
- Root pytest exits 2 at existing Chat/CLI test_display import mismatch;
  source/discovery unchanged. Not a passing broad gate.
- Watcher helper has one SIM115, reproduced at its pinned original Git source;
  bundled test lint/format passes.
- Full optional-cohort install is offline cache-limited: Langfuse/wrapt and
  optimization dspy/xxhash. No full-cohort install success claimed.

Reviewer-only harness corrections: initial no-cache hid cached Hatchling;
initial Chat store guard followed a fixture's changed working directory;
initial Chat sdist included protected working examples. Corrected exclusively
in scratch; final Chat passed and artifacts were rebuilt from candidate Git
bytes. One exploratory nonexistent finance test path was corrected to the
actual tools tests. No original evidence was overwritten.

Final audit: HEAD/branch/complete working status unchanged; 17,061 tracked blob/
link identities and all 17,051 supplied worktree hashes, authorities and protected
configurations match. Only the two declared examples differ from candidate.
Request SHA-256:
`af6f090cf5eaef1d465f4ebb7e10fb7f4b2cb4ada1797c9519f29aa6183cee45`.
Manifest SHA-256:
`bb3cf3b9188fceb6c421d7550fe8c71cf61c9b7acea59ed8a27632424c6e4c92`.

Reproducible scripts/receipts/logs:
`/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/aggregate-independent-_81g1a95`.
No live provider/tool, credentials, real user stores, Linux/Windows, physical
terminal/audio or complete feature/TUI acceptance claimed. Remote PR requirements
remain the controller's delivery gate. Next: bounded AGG-001/002 disposition,
stable changed candidate and fresh independent review. No merge approval granted.

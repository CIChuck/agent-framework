# INGEST-PACKAGE-IMPACT-001 — Round 1 independent review — seat `opus`

- Reviewer: Claude Opus 5.5 (`claude-opus-5-5`). Fresh context, read-only, no delegation, no repairs, no shared writes.
- Deliverable: `docs/planning/active/command-refactor/package-impact-assessment.md` (SHA256 `df73594bd39c64190552b7e7e1d3deced9c73d49e09a24405711051492affb60`, v0.1 draft).
- Candidate `72ef265a981ef968a773172661bb512ddfd7da5e`; base `8390f3688d00985b1cac0443da8105f33fb1a6b7`; branch `feature/cmd-ingest-001`.
- Review request SHA256 `ff7c61995d8964b7f88e549d56debc1fb670b1cfed6ce6a5d2622ad583de3c76`. I verified this hash before reading the file, then verified the hashes of `read_only_command.py` (`3acff26f…037d`), `verify_identity.py` (`c4d9bf96…8452`), `current-controls.json` (`46511406…f9bb`) and `protected-manifest.json` (`4274fd36…10d4`). I read both helpers before executing them.

## VERDICT: **CHANGES_REQUESTED**

There are 4 mandatory findings (PI-R1-OPUS-001 to 004) and 8 advisories. I found no false statement of fact about the frozen REM, the annex or the Tools companion. Every checked dependency claim is source-accurate. The failures are omissions of material per-package effects and of evidence references that criteria PI-07/08/09/10/12/13 name explicitly.

- Coverage: **8.55 / 10**
- Overall: **8.65 / 10**

Both scores are below the 9.5 gate, and the mandatory findings block the gate regardless of score.

This report grants no maintainer satisfaction, Gate-A, construction, acceptance or delivery authority.

## Integrity, commands and exits

| Step | Exact command (cwd for the wrapper = repo) | Exit / result |
| --- | --- | --- |
| Opening identity | `python3 -B …/verify_identity.py …/round1/inputs/review-request.json OWN_SCRATCH opening-identity.json` | 0, PASS; logical index `db380f00…a9f4d` hashed before status; 17,694 protected files; 6 preserved items; HEAD/branch/status/staging/pins unchanged |
| Board validate | `read_only_command.py OWN -- uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate` | 0, "Development board validation passed: 36 tasks" |
| Dashboard | `… scripts/friday-dev-board.py render --check` | 0, "Planning dashboard is current" |
| Doc lifecycle | `… scripts/check-documentation-lifecycle.py` | 0, "1020 Markdown files checked" |
| Package metadata | `… scripts/check-package-metadata.py` | 0, "Validated 18 pyproject.toml files" (17 packages + root) |
| Whitespace | `read_only_command.py OWN -- git diff --check 8390f368..72ef265a -- docs/planning` | 0, no output |
| Delta inventory | `git diff --numstat`, `git log --oneline`, `git diff -U1` (navigation files only; raw authority.json diff not displayed) via the wrapper | 0 |
| Technical pins at reviewed commit | `git show f43368c5:<REM/annex/companion> \| shasum -a 256` via the wrapper | 0; `e1c90753…`, `1092a332…` and `8220e195…` equal the current pins, so line 24 of the assessment is true |
| Closing identity | `verify_identity.py … closing-identity.json` | 0, PASS, identical to opening |

Own scratch: `/private/tmp/claude-501/-Users-chuckrussell-Dev-gendev-agent-framework/d4d53d23-2b52-47b9-9ee8-9d6b70fa1638/scratchpad/pi-r1-opus/`. That folder is outside the checkout and outside both supplied scratch roots. Wrapper receipts are stored there.

**Reproduced:**
- The five required admin checks.
- Identity open and close.
- Pin equality at `f43368c5`.
- Link resolution: all 7 relative links in the assessment exist.
- Delta numstat: the execution log is append-only (+35/−0); board events were appended; current next-gate fields are consistent across board, README, next-phase, tactical-plan and both handoffs.

**Inspected (static reads only):**
- All 17 package `pyproject.toml` files and the root workspace config. `packages/friday-tui` contains only caches, is untracked and has no pyproject, so it is not a workspace package.
- Chat `adapters.py`, `config.py`, `commands/files.py`, `memory_mcp.py` and the packaged `config_templates/config.example.yaml`.
- Tools `filesystem/smart_read.py`, `read.py` and `execution/python.py`.
- Telemetry `models/mcp.py`; Runtime `config.py`, `kernel.py`, `tool_loading.py` and `mcp_loading.py`.
- CLI `container.py`; Core `profiles.py` and `interfaces/transcript.py`; Memory `multi_agent/*` and `retrieval/graph_scorer.py`.

**Not read, per scope:**
- The two dirty example YAML files in the repo.
- `.friday-old/` and exports.
- Raw authority.json historical fields. Its hash was verified by the helper pin only.
- Peer or prior reports.
- Any store.

No product imports, tests, builds, installs, network, provider, model or store operations were performed.

## Source facts that support the assessment (verified)

- **Workspace members.** `members = ["packages/*"]` gives exactly 17 packages. The 8/9 split in P-01 to P-17 matches the REM allowlist: there are no Agent, Telemetry, Transcript, MCP, Optimization, Finance, Speech, Sandbox or Moltbook source paths in it, and the `ContextAssembler` edit lives in Memory.
- **Dependency edges.** Tools→Finance is a required dependency (P-14 is correct). Runtime→MCP is required. Agent, CLI, Runtime, Chat and Optimization→Memory are required, so the inherited counter extra is real. Speech→Core. Sandbox and Moltbook have no framework dependencies. Core→Telemetry. Commands has `dependencies = []`.
- **Telemetry ownership.** `MCPEventReason` is defined in `friday_telemetry/models/mcp.py`. The P-10 statement "map at Chat's boundary, schema unchanged" is accurately owned.
- **Chat placeholder.** The Chat document placeholder exists at `commands/files.py:122-129`. The Chat character slicer exists at `adapters.py:383-386`.
- **Runtime tool catalog.** `_friday_tools_catalog` uses `pkgutil.walk_packages` (`tool_loading.py:60-72`), matching P-07.
- **CLI testing path.** `FridayConfig.for_testing` uses `.friday/test_chroma` (`container.py:100-106`), which matches P-08's "TESTING profile origin" and CF-04.
- **Graph scorer wiring.** Neither Chat nor Runtime source references `GraphPathScorer`.
- **Filesystem sandbox owner.** The Tools filesystem sandbox is `friday_tools.sandbox.FilesystemSandbox`. The `friday-sandbox` package is used only by `friday_tools/execution/python.py`.

## Mandatory findings

### PI-R1-OPUS-001 — Medium — Fresh-namespace/explicit-origin consequences for existing and new users are not explained

- **Affected text.** Dependency section, "Model replacement and existing data" (lines 107-112); P-06 (line 58); P-07 (line 59, "Preserve explicit path origin"); P-08 (line 60); the "Details to settle" table (lines 120-128).
- **Requirement.** PI-07 ("explicitly selected fresh namespaces, preserved legacy files"), PI-10 ("explicit path origin"), PI-13 (concrete final-directive decisions), PI-15 (maintainer usefulness).
- **Source evidence.**
  - REM "Existing-store upgrade policy":
    - L1093-1110: the selection mechanism is Chat `memory.persist_directory` or Runtime `RuntimeConfig.chroma_path` + `runtime_data_root`.
    - L1113-1121: **Unset is not explicit.** An unset `persist_directory` or absent Runtime raw path never authorizes creation, "even if their fallback … directory is absent on a first run".
    - L1131-1136: CREATE_FRESH requires the vector directory, the resolved graph file and the configured WAL to all be absent.
    - L1142-1148: reusing `runtime_data_root` refuses if the old graph or WAL exists. Choosing a new root "also selects fresh transcript/artifact locations … disclose that effect".
    - L1150: a pre-created empty directory refuses.
    - L897-902: enabling the verified Nomic prefixes is itself a preparation change for the *current* model.
    - L1199-1207: the operator upgrade/backup note.
  - Gate-A handoff OPUS-R4-A05: retaining the packaged template's explicit `.friday/vector` literal is an open directive decision. The packaged `config_templates/config.example.yaml:236` contains `persist_directory: .friday/vector`. OPUS-R4-A02 adds that reused recovery/log roots can block maintenance.
  - Grep of the assessment finds no `persist_directory`, `chroma_path`, `runtime_data_root`, `WAL`, `unset`, `first run`, `prefix`/`Nomic`, or graph-store path requirement.
- **Risk.** Line 111 says "Existing unbound stores refuse". It does not tell the maintainer that *every* current store is unbound, because no sidecar exists today. The upgrade therefore disables Memory for all existing Chat and Runtime users until they configure a new absent destination, even if they keep the current model. The document also omits five related facts:
  - An unset default never auto-creates Memory, which affects first-run and headless defaults.
  - The associated graph and WAL paths must also be new.
  - A new Runtime data root relocates transcripts and artifacts.
  - The packaged-template literal decides whether a copied template creates Memory on first use.
  - Operators should back up, or finish interrupted recovery, with the old release before upgrading.

  These are the largest user-visible data and configuration effects of Chat, Runtime and CLI. The maintainer's approval condition depends on seeing them.
- **Bounded document correction.**
  1. Add a short "Upgrade and first-run effect" bullet under "Dependency, configuration and data consequences", summarizing the REM facts above. Cite the REM existing-store policy and the gate-A handoff A02/A05/A06. Do not change the policy.
  2. Name `memory.persist_directory` in the P-06 row and `chroma_path`/`runtime_data_root` in the P-07 row as the explicit selection mechanism.
  3. Add a "Packaged template origin" row to "Details to settle", citing OPUS-R4-A05.
- **Recheck.**
  - The assessment states all of the following: every existing store refuses after upgrade; unset never creates; graph/WAL absence; the Runtime root relocation disclosure; template-literal decision; pre-upgrade backup/recovery with the old release; the Nomic prefix as a preparation change.
  - Each statement traces to a REM or handoff line.
  - No new policy appears and the REM/annex hashes are unchanged.

### PI-R1-OPUS-002 — Medium-Low — Chat `/ingest` configuration and execution effects are omitted

- **Affected text.** P-06 (line 58); the "Ingestion defaults" bullet (lines 95-100).
- **Requirement.** PI-08 (defaults and overrides for actual document-payload ingestion), PI-02 (do not omit a material planned effect), PI-15.
- **Source evidence.**
  - REM D L544-560 adds a new YAML section `ingestion.chunking.{strategy,max_tokens}`. Invalid values are rejected at configuration preflight. Precedence is per-command override, then YAML, then built-in default.
  - REM D L626-633: the existing `smart_file.chunk_size`/`chunk_overlap` "are not aliases … never … a hidden second ingestion default".
  - Source today: `friday_chat/adapters.py:383-386` chunks `/ingest` with `smart_file.chunk_size or 2048` and `chunk_overlap or 0`. `SmartFileConfig` (`config.py:530-535`) is documented as "Smart file reading and ingestion configuration". The packaged template carries a `smart_file:` section (line 491).
  - REM "Execution, cancellation and admission" L1061-1078: conversion, OCR and counting run in an owned worker off Chat's event loop. Shared command admission is held for the whole request, so competing maintenance can report busy. Cancellation waits for the worker to quiesce, and there is no hard kill. DI-11 and DI-26 cover this.
  - REM C L518-523: the effective line limit and truncation are reported.
- **Risk.**
  - A user who tuned `smart_file.chunk_size` or `chunk_overlap` will see those settings silently stop affecting `/ingest`.
  - The new `ingestion.chunking` keys and their precedence are not disclosed.
  - The long-running conversion and admission/cancellation behavior is a new user-visible Chat behavior. The package table hides all three effects.
- **Bounded document correction.**
  1. In P-06 and the "Ingestion defaults" bullet, name the new `ingestion.chunking` keys and their precedence.
  2. State that `smart_file.chunk_size`/`chunk_overlap` stop governing `/ingest` and remain only for scoped legacy read and summarization.
  3. Summarize the off-loop worker, admission held through conversion, and the bounded cancellation behavior. Cite REM D, the REM Execution section and DI-11/26.
- **Recheck.** The keys, precedence, legacy-key non-aliasing and execution/admission behavior all appear, with REM citations and no new semantics.

### PI-R1-OPUS-003 — Medium-Low — Multi-agent Memory consumers are absent from the per-package table

- **Affected text.** P-04 (line 56), P-07 (line 59), P-09 (line 72). The word "multi" appears nowhere in the assessment.
- **Requirement.** PI-09 ("Include Agent/multi-agent … consumers with correct package ownership and error/receipt obligations").
- **Source evidence.**
  - Annex consumer inventory L156: "Multi-agent controller/coordinator/journal — Underlying Memory space is shared; preserve authorization visibility and honest failed/partial-commit reporting. No new transaction promise."
  - Annex L37-39: visibility namespaces are authorization partitions, not embedding spaces.
  - FC-13 L496-499 covers the "Runtime multi-agent controller/coordinator".
  - REM allowlist L1263 lists "focused existing Agent, multi-agent, MEMQ … tests".
  - Source: the controller, coordinator, journal and policy live in `friday-memory/src/friday_memory/multi_agent/`. Runtime exposes them through `RuntimeKernel.multi_agent_memory` and `memory_mode: multi_agent` (`kernel.py:309-312`, `config.py:813-814`).
- **Risk.** A maintained consumer that the frozen annex requires proof for is invisible. Its owner (Memory, source-unchanged under the allowlist) and its Runtime assembly are not identified. Readers could also mistake multi-agent visibility partitions for separate embedding spaces.
- **Bounded document correction.**
  1. Add the multi-agent controller/coordinator/journal to P-04 as source-unchanged inside Memory, with existing focused tests.
  2. Add the multi-agent assembly to P-07 under `memory_mode: multi_agent`.
  3. State the obligations: shared namespace and space, authorization visibility retained, honest failed/partial-commit reporting, no new transaction promise. Cite FC-13 and annex L37-39/L156.
- **Recheck.** Multi-agent appears with the correct owner package, its source-unchanged status, its obligations and the FC-13 reference.

### PI-R1-OPUS-004 — Low — Verification references are incomplete

- **Affected text.** Line 157 "REM A–F and DI-01–33"; P-02 evidence "INGEST DI-01–24 and FC-01/07/12/13" (line 54).
- **Requirement.** PI-12 ("accurate verification references").
- **Source evidence.**
  - The REM defines DI-01 to **DI-34** (L1316). DI-34 is the whole-framework consumer audit binding all FC-01–14 and B01–B08, which underpins the nine compatibility rows. No row and no source reference cites it.
  - DI-25 (Office structural audit oracle, REM L1307) is Tools-owned by REM B L433-449.
  - DI-30 (destination/incarnation-specific storage receipts; unwired Chat smart_read storage refuses, L1312) covers Tools smart_read storage/cache. Both fall outside P-02's cited "DI-01–24".
- **Risk.** A directive author who maps evidence by package row will drop DI-34 and misassign Tools' structural-audit and receipt proofs.
- **Bounded document correction.**
  1. Change line 157 to "DI-01–34".
  2. Add DI-25 and DI-30 to P-02.
  3. Cite DI-34 in the introduction to the compatibility table, or in each of rows P-09 to P-17.
- **Recheck.** Every DI ID, DI-01 to DI-34, is reachable from at least one row or the source-reference line. P-02 includes DI-25 and DI-30.

## Advisories (non-blocking)

- **PI-R1-OPUS-A01.** P-16 cites "companion TD-03/04" for `friday-sandbox`. The document-path sandbox is Tools' own `friday_tools.sandbox.FilesystemSandbox`; `friday-sandbox` is used only by Tools `execution/python.py` (`sandbox` extra). Say so, so the citation is not read as `friday-sandbox` owning the converter boundary.
- **PI-R1-OPUS-A02.** P-13 says Optimization "can inherit" the counter stack. Because `friday-framework-memory==0.1.0a4` is a required dependency, Optimization *will* inherit it. MCP inherits only via its `full` extra (Agent→Memory). Runtime requires MCP.
- **PI-R1-OPUS-A03.** Record the existing undeclared or lazy edges that the plan retains but does not broaden: Memory→Tools code chunker; Tools memory wrappers→Memory; Core `profiles.py` and `interfaces/transcript.py`→Memory (REM L191-201). P-02 edits two of those Tools memory modules.
- **PI-R1-OPUS-A04.** In P-02, mention that the Tools maintenance/reset wrapper gains shared store-only admission of the whole target layout before any confirmed clear, and that a reset retains the binding sidecar (FC-13 L505-513). Today P-02 says only "truthful errors".
- **PI-R1-OPUS-A05.** Add `FC-02` to P-07. Runtime's `RuntimeMCPProvider` (`mcp_loading.py`) is an actual witness in `test_mcp_pending_retry_and_existing_telemetry_reasons`. Add FC-04's read-only transcript-SQLite analysis to P-11.
- **PI-R1-OPUS-A06.** Add the FC-11 `VectorCollectionDimension8192` ceiling to "Details to settle" as a replacement-model constraint.
- **PI-R1-OPUS-A07.** In "Backup/MCP compatibility", state explicitly that FU-013 and FU-014 receive **no positive-test credit** (PI-11 wording).
- **PI-R1-OPUS-A08.** In approval steps 1-3, clarify that the version bound into the directive must be the exact post-Gate-A hash with which Chuck recorded satisfaction. A refinement after his satisfaction, even a non-material one, should be reconfirmed. Today step 2 says "renewed review", while current-controls says "obtain maintainer review".

## PI-01–16 matrix

| ID | Result | Evidence / note |
| --- | --- | --- |
| PI-01 | Pass | 17 packages exactly once (P-01 to P-17), consistent with `packages/*` and 17 pyprojects. The 8 implementation / 9 compatibility split matches the REM allowlist. Lines 64-68 refuse to equate "no source edit" with "no impact". Direct versus inherited dependencies are accurate (A02 is wording only). |
| PI-02 | **Partial** | Every REM allowlist path maps to a row, and no unnamed owner or broadened boundary was found. Material planned Chat effects are omitted (**002**). Companion file set not enumerated (acceptable: it defers to "Exact package/path coverage"). |
| PI-03 | Pass | Core neutral contracts, Tools conversion, Commands parsing, Memory policy, LLM execution and Chat/Runtime composition are correctly owned. Injected entry and no new Tools→Memory edge are stated. A03 is optional. |
| PI-04 | Pass | Basis L29-38, the P-02 split between INGEST and Companion, and the "Tools completion boundary" row. Combining the units requires explicit revision. |
| PI-05 | Pass | Default Chat→Tools `document-ingestion`; legacy extras stay explicit; Certifi floor with post-install verification; the LLM `embedding-limits` extra inherited headless without Docling; lazy Core/Commands/LLM/Tools paths; versions and assets unresolved. |
| PI-06 | Pass | L101-112 plus P-05: pool/non-pool and Chat pool-default precedence, separate extraction and maintenance services, readiness records for missing fields, hosted B02 uncertainty, no swap, truncation or Qwen activation. Baseline and replacement positives are separate from refusals (row L124). |
| PI-07 | **Partial** | Same-dimension changes, preserved files and `/read` are covered. Explicit fresh-namespace selection, the unset/first-run effect, graph/WAL absence and Runtime root relocation are missing (**001**). Graph and recovery identity effects are summarized only tersely; strict v2 handoff present (P-06, P-11). |
| PI-08 | **Partial** | Document/512 defaults and overrides, unsplit structured records, no URL or automatic wiring, no double chunking are all present. YAML configuration and precedence, plus the `smart_file` non-aliasing, are absent (**002**). |
| PI-09 | **Fail** | Agent, metadata inspection, telemetry/transcript and MCP are covered with correct owners. Multi-agent is absent (**003**). |
| PI-10 | **Partial** | Memory is called the broadest impact. Admission before side effects, task/logging ownership, profile isolation and truthful counts are present, and CLI edits are conditional with no launcher. The explicit path-origin consequence is not explained (**001**). |
| PI-11 | Pass | P-04 says "only where the new guard requires it". Live-marker protection, defaults and pending IDs are retained, with no backup engine or MCP cleanup. FU-013/014 stay unwaived (A07 for explicit "no credit"). |
| PI-12 | **Partial** | Future proofs are clearly distinguished from completed work, and no conformance is claimed. References are incomplete (**004**). |
| PI-13 | **Partial** | Versions, backends, assets, licenses, resource limits, signatures and path coverage are listed, and missing qualification is a stop. The packaged-template origin decision is missing (**001**); A06 is optional. |
| PI-14 | Pass | L12-16 and L130-154 make satisfaction an explicit prerequisite, bind one canonical version/commit/SHA256, and return material changes for review. Neither conditional approval nor the council completes conditions (A08 is optional). |
| PI-15 | Pass (impaired) | The change-type, purpose, retained-behavior and evidence columns are useful, with no invented effort metrics or version-bump claims. Usefulness is reduced by 001 and 002. |
| PI-16 | Pass | Identity PASS open and close; pins verified at `f43368c5`; links resolve; log and board are append-only; preserved state intact; the council is separate from the technical verdict; no edited technical contract. Raw authority.json was checked by hash only. |

## Rubrics (independent and honest)

| Coverage | Max | Score | Basis |
| --- | --- | --- | --- |
| All-package inventory and source/dependency/test classification | 3.0 | 2.70 | Inventory and dependency edges are exact. Multi-agent consumer omitted (003). |
| Material behavior, configuration and data effects | 2.0 | 1.40 | Fresh-store/origin consequences (001) and Chat config/execution (002) are missing. |
| Shared ownership and dependency/deployment consequences | 2.0 | 1.85 | Accurate. Minor wording on optional inherited and undeclared edges (A02, A03). |
| Traceable boundaries, compatibility and required proofs | 2.0 | 1.75 | DI-34/25/30 reference gaps (004). Otherwise strong traceability. |
| Unresolved readiness details and approval completeness | 1.0 | 0.85 | Template-origin decision missing (001). |
| **Total** | 10 | **8.55** | |

| Overall | Max | Score | Basis |
| --- | --- | --- | --- |
| Accuracy against current scope and source | 3.0 | 2.70 | No false claims found. Omissions only. |
| Architecture and bounded delivery | 2.0 | 1.90 | Clean ownership, INGEST/companion separation and conditional CLI. |
| Data/configuration/dependency safety | 2.0 | 1.45 | 001 and 002 understate user-visible data and config effects. |
| Evidence, future-work distinctions and reproducibility | 1.5 | 1.30 | Future-work distinctions are good; references incomplete (004). |
| Maintainer readability and approval/change control | 1.5 | 1.30 | Clear approval control; dense rows; A08 is optional. |
| **Total** | 10 | **8.65** | |

## Limits

- This is a static document and source review. No behavior was executed, and implementation conformance is not claimed.
- Source inspection was targeted, not exhaustive. Consumers outside the inspected files are covered by the annex's own Gate-A audit obligation.
- I did not display the raw authority.json delta (+50/−5). I relied on its pinned hash and the current-controls snapshot.
- Intentional future Gate-A, installed and model proofs are not treated as document gaps.

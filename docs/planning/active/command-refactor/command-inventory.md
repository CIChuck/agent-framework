# Friday slash-command inventory and scoring sheet

**Status:** Working review sheet, 2026-10-22. Your scores and decisions will
set the proposed migration scope. My recommendations are advisory. The
accepted 50-command TUI parity baseline and Friday Chat behavior remain in
force until a product decision and bounded construction directive reconcile
them.

The [separate shared-command initiative](README.md)
now owns migration planning and the cross-client regression gates. This scored
sheet remains the maintainer's decision source and is paired with the
[TUI command matrix](command-matrix.md); neither is rewritten as though the
six selected retirements have already shipped.

**Source:** The live Friday Chat
[`build_default_registry()`](../../../../packages/friday-chat/src/friday_chat/commands/registry.py)
has 50 canonical commands and three aliases. [PAR-001–PAR-050](command-matrix.md)
and the [effect map](tui-source-baseline.md#per-command-effect-map)
provide the current inventory. The [pruning review](command-pruning-review.md)
records source, test and guide evidence behind the proposed retirements. The
separate `friday-framework-cli` command registry is outside this inventory.

## How to score

Enter **0–5** in *Your score*: 0 = no value, 1 = rare, 2 = occasional, 3 =
useful, 4 = important, 5 = essential. In *Your decision*, enter **Migrate**,
**Combine**, **Retire**, or **Defer**. For **Combine**, name the target or add a
note in [Notes and decisions](#notes-and-decisions). A high score can still
favor a better combined command; a low score does not automatically authorize
removal. The aliases `/quit`,
`/q`, and `/clearscreen` are scored with their canonical commands.
Score the [consolidation recommendations](#consolidation-recommendations)
separately; they propose command interfaces and do not fill in your command
decisions above.

## Focus-area scoring overview

Use a focus-area score to set migration priority. Individual command decisions
below control the proposed scope when they differ from a group preference.
Each command appears once under its primary focus area; cross-area connections
remain in the combine and optimization column.

| Focus area                                        | Commands | Your group score (0–5) | Group decision or note                                                |
| ------------------------------------------------- | -------: | ---------------------- | --------------------------------------------------------------------- |
| [Memory](#memory)                                 | 8        | 5                      |                                                                       |
| [Memory maintenance](#memory-maintenance)         | 4        | 5                      |                                                                       |
| [Agents](#agents)                                 | 5        | 5                      |                                                                       |
| [Context and prompts](#context-and-prompts)       | 3        | 5                      |                                                                       |
| [Debug and telemetry](#debug-and-telemetry)       | 4        | 5                      |                                                                       |
| [Session and interface](#session-and-interface)   | 7        | 5                      |                                                                       |
| [File access](#file-access)                       | 1        | 5                      |                                                                       |
| [Transcripts and replay](#transcripts-and-replay) | 5        | 5                      |                                                                       |
| [Tools](#tools)                                   | 6        |                        | Retire five; retain `/tools` read-only.                                        |
| [Security](#security)                             | 4        | 5                      | requires reevaluation of features and functions                       |
| [Workflows](#workflows)                           | 1        | 5                      |                                                                       |
| [Speech](#speech)                                 | 2        | 5                      | useful for now - maintain Friday-speech as a user-configurable option |

## Consolidation recommendations

These proposals reduce the number of top-level slash names by placing related
operations under a clear primary command. The syntax below is illustrative;
none is an accepted command contract. Score each proposal independently of the
50 command rows. A selected consolidation needs an explicit old-name behavior
and parity checks for arguments, results, errors and side effects in Chat and
TUI.

| ID   | Current commands                                                             | Suggested primary command                   | My recommendation                 | Your priority (0–5) | Your decision or note                                                                                                                                                                                                                                                                             |
| ---- | ---------------------------------------------------------------------------- | ------------------------------------------- | --------------------------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C-01 | `/memory`, `/entities`, `/insights`, `/meta`, `/summaries`, `/list-ingested` | `/memory` with named views                  | Recommend                         | 5                   |                                                                                                                                                                                                                                                                                                   |
| C-02 | `/agent`, `/agents`, `/status`, `/switch`, `/delegate`                       | `/agent` with inspect and action verbs      | Recommend with routing safeguards | 5                   |                                                                                                                                                                                                                                                                                                   |
| C-03 | `/debug`, `/timing`, `/debug-budget`, `/debug-retrieval`                     | `/debug` with named diagnostics             | Recommend                         | 5                   |                                                                                                                                                                                                                                                                                                   |
| C-04 | `/sessions`, `/transcript`, `/export`, `/export-prompts`                     | `/transcript` with inspect and export verbs | Recommend                         | 5                   | sessions are a critical part of being able to track conversations over time being able to select a specific section, a session, and then identify the transcript export and export prompts against that session is important the ability to activate a session found in history is also important |
| C-05 | `/context`, `/prompt`                                                        | `/context` with an explicit prompt view     | Optional                          | 5                   |                                                                                                                                                                                                                                                                                                   |
| C-06 | `/security`, `/security-config`                                              | `/security` with a `config` verb            | Recommend                         | 5                   |                                                                                                                                                                                                                                                                                                   |

**C-01 — Memory views.** Keep bare `/memory` as the current statistics view;
consider `/memory entities [nodes|name]`, `/memory insights`, `/memory meta`,
`/memory summaries` and `/memory ingested`. Preserve each record type, filter
and unavailable-store result. Repair `/list-ingested` against persisted
ingested-file metadata before treating the new view as a replacement. This is
read-only consolidation; `/ingest`, `/prime` and the guarded maintenance
commands have separate decisions.

**C-02 — Agents.** Consider `/agent [name]` for description, plus `/agent list`,
`/agent status`, `/agent switch [name]` and
`/agent delegate <agent> <task>`. Keep inspection, persistent active-agent
switching and temporary delegation as different effects; delegation must still
restore the prior active agent. Define how a real agent named `list`, `status`,
`switch` or `delegate` is addressed before reserving those words. The
`@agent_name <message>` route is outside this slash-command proposal.

**C-03 — Diagnostics.** Keep bare `/debug` as the last-turn view; consider
`/debug timing`, `/debug budget-config` and `/debug retrieval <query>` for the
other views. Preserve `/debug-retrieval`'s query argument and distinguish
configured context-window/output-buffer values from measured turn accounting.
One typed diagnostic source can serve the views without making them identical.

**C-04 — Transcripts.** Consider `/transcript sessions`,
`/transcript show [session_id]`, `/transcript export-current [format]`,
`/transcript export-all` and `/transcript export-prompts [session_id]`. Current
session export, all non-archived session export and captured raw-prompt export
have different scope and sensitivity. Resolve any session ID that matches a
new verb, and keep active `/replay` separate because it resets and reprocesses
turns.

**C-05 — Context and prompt inspection.** Consider bare `/context` for the
existing context view and `/context prompt` for the assembled prompt view.
Preserve each view's exact data, `--debug` or `--file` options, export effects
and privacy boundary. `/compact` changes context state and stays separate.

**C-06 — Security.** Keep bare `/security` for settings and counters; consider
`/security config <sensitivity|action|wrapping> <value>` for the existing
validated mutation. Preserve rollback and error behavior. `/security-test`
remains for the refactor; `/inject-payload` is selected for retirement with
`/run-tool`.

I do **not** recommend combining `/clear` with `/cls` (session state versus
display), `/read` with `/ingest` (display versus persistent vector storage), or
`/replay` with transcript inspection/export (runtime reprocessing versus
reading). The guarded maintenance commands can share admission, progress and
result contracts without hiding their distinct effects under one verb. The
five tool slash commands marked Retire are excluded from these proposals;
`/tools` remains a read-only command. C-01 through C-06 are backlog proposals,
so current command names and syntax remain during the refactor.

## Command focus areas

### Memory

Memory records, statistics, ingestion and priming status.

`/ingest` reads the source file, splits the resulting text into chunks and
stores those chunks with embeddings and source metadata in the persistent Chroma
`memories_short_term` vector collection. The records are marked `protected` and
can later be promoted to `memories_long_term`; they do not enter episodic or
graph memory through this command. The source file remains at its original path.
The Chroma directory comes from `memory.persist_directory` (default
`.friday/vector`, resolved against the app's launch directory). Current PDF,
DOCX and XLSX reading supplies placeholder text, so `/ingest` does not extract
those formats' document contents yet.

| Case    | Command          | Current effect                                                                                                                                                          | My recommendation       | Combine or optimization opportunity                                                                                              | Your score | Your decision                                                                    |
| ------- | ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ---------- | -------------------------------------------------------------------------------- |
| PAR-012 | `/entities`      | Query graph entities and relationships.                                                                                                                                 | Migrate                 | Share typed read-only memory record results with `/insights`, `/summaries`, `/meta`.                                             | 5          |                                                                                  |
| PAR-018 | `/ingest`        | Read a file and store protected text chunks in short-term Chroma vector memory; eligible for later long-term promotion.                                                 | Migrate                 | Share file-read primitive with `/read`, but preserve read-versus-write admission and fix placeholder handling for PDF/DOCX/XLSX. | 5          |                                                                                  |
| PAR-021 | `/insights`      | Query active insight records.                                                                                                                                           | Migrate                 | Common typed memory record query/render path.                                                                                    | 5          |                                                                                  |
| PAR-023 | `/list-ingested` | Intended to list ingested sources, but its current handler reads an `ingested_documents` attribute absent from the production memory adapter, so it reports none there. | Migrate; repair listing | Query persisted ingested-file metadata rather than a process-local test list; could later become a `/memory` subview.            | 5          | this must be wired into the application. ingested sources must also be validated |
| PAR-024 | `/memory`        | Show memory, transcript, session and last-turn statistics.                                                                                                              | Migrate                 | Main inspection surface; reuse typed metrics across diagnostic commands.                                                         | 5          |                                                                                  |
| PAR-025 | `/meta`          | Query active meta-insight records without running synthesis.                                                                                                            | Migrate                 | Common typed memory record query/render path.                                                                                    | 5          |                                                                                  |
| PAR-027 | `/prime`         | Report priming configuration; it does not load primed context.                                                                                                          | Retire                  | `/memory` already exposes priming status; preserve startup priming itself.                                                       | 0          | retire                                                                           |
| PAR-043 | `/summaries`     | Query active turn-summary records.                                                                                                                                      | Migrate                 | Common typed memory record query/render path.                                                                                    | 5          |                                                                                  |

### Memory maintenance

Guarded memory and storage maintenance, including destructive operations.

| Case    | Command       | Current effect                                                                           | My recommendation | Combine or optimization opportunity                                                    | Your score | Your decision                                                                                                                        |
| ------- | ------------- | ---------------------------------------------------------------------------------------- | ----------------- | -------------------------------------------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| PAR-022 | `/lifecycle`  | Inspect or execute guarded memory lifecycle work.                                        | Migrate           | Shared maintenance admission and progress; do not collapse distinct mutation modes.    | 5           | make recommendations for collapsing these many lifecycle commands                                                                    |
| PAR-026 | `/migrate`    | Preview or execute guarded storage migration.                                            | Migrate           | Share maintenance guard, dry-run and progress contracts; preserve explicit execution.  | 5           | this is a useful debugging aid, but will ultimately be removed for our version 1.0 product                                           |
| PAR-031 | `/reorganize` | Preview, execute or recover coordinated memory work.                                     | Migrate           | Keep a separate high-impact operation; share maintenance admission and typed progress. | 5           |                                                                                                                                      |
| PAR-033 | `/reset`      | Reset selected/all memory stores; full reset also affects transcripts and session state. | Migrate           | Shared guarded maintenance path, distinct destructive semantics.                       | 5           | because of the destructive nature of this command, we must prompt the user for an "Are you sure?" question within the UI and the CLI |

### Agents

Agent inventory, routing and active-agent selection.

| Case    | Command     | Current effect                                           | My recommendation | Combine or optimization opportunity                                                     | Your score | Your decision |
| ------- | ----------- | -------------------------------------------------------- | ----------------- | --------------------------------------------------------------------------------------- | ---------- | ------------- |
| PAR-001 | `/agent`    | Describe one agent or the active agent.                  | Migrate           | Share agent lookup with `/agents` and `/switch`; keep distinct read and change effects. | 5          |               |
| PAR-002 | `/agents`   | List agents, active marker and cache state.              | Migrate           | Use the same typed agent inventory as `/agent`.                                         | 5          |               |
| PAR-011 | `/delegate` | Route a task to an agent and restore prior active agent. | Migrate           | Share orchestrator adapter with `/agent`, `/agents`, `/status`, `/switch`.              | 5          |               |
| PAR-042 | `/status`   | Show orchestrator active agent, cache and message count. | Migrate           | Share orchestrator status snapshot with `/agent` and `/agents`.                         | 5          |               |
| PAR-044 | `/switch`   | Show or change active agent.                             | Migrate           | Share agent inventory and validation, preserving mutation semantics.                    | 5          |               |

### Context and prompts

Context inspection, assembled prompts and context compaction.

| Case    | Command    | Current effect                                                | My recommendation | Combine or optimization opportunity                                                    | Your score | Your decision |
| ------- | ---------- | ------------------------------------------------------------- | ----------------- | -------------------------------------------------------------------------------------- | ---------- | ------------- |
| PAR-006 | `/compact` | Request guarded context compaction.                           | Migrate           | Share maintenance admission, progress and result contracts; retain distinct operation. | 5          |               |
| PAR-007 | `/context` | Inspect last/current context; optional debug and file export. | Migrate           | Share read/export primitives with `/prompt`; keep their data meanings distinct.        | 5          |               |
| PAR-028 | `/prompt`  | Inspect last/current assembled prompt; optional file export.  | Migrate           | Share read/export primitives with `/context`, preserving privacy and exact meaning.    | 5          |               |

### Debug and telemetry

Turn diagnostics, retrieval diagnostics, budget configuration and timing.

| Case    | Command            | Current effect                                                                | My recommendation     | Combine or optimization opportunity                                         | Your score | Your decision                                                                                                    |
| ------- | ------------------ | ----------------------------------------------------------------------------- | --------------------- | --------------------------------------------------------------------------- | ---------- | ---------------------------------------------------------------------------------------------------------------- |
| PAR-008 | `/debug`           | Show last-turn debug data and execution telemetry.                            | Migrate               | Share a typed diagnostic snapshot with `/timing` and `/debug-budget`.       | 5          |                                                                                                                  |
| PAR-009 | `/debug-budget`    | Show configured context window and output buffer, not actual turn accounting. | Migrate; clarify help | Share diagnostic data source; `/memory` covers different last-turn metrics. | 5          | and only provides the context window budget and the output buffer budget the user experience is somewhat lacking |
| PAR-010 | `/debug-retrieval` | Query retrieval diagnostics for text.                                         | Migrate               | Use the memory diagnostic capability; keep query arguments.                 | 5          | useful but output needs to be more friendlycls                                                                   |
| PAR-045 | `/timing`          | Show last-turn timing and execution telemetry.                                | Migrate               | Share a typed diagnostic snapshot with `/debug`; keep timing view.          | 5          |                                                                                                                  |

### Session and interface

Conversation state, display, help, exit and scoped variables.

| Case    | Command                 | Current effect                                                    | My recommendation | Combine or optimization opportunity                                               | Your score | Your decision                                                                                               |
| ------- | ----------------------- | ----------------------------------------------------------------- | ----------------- | --------------------------------------------------------------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------- |
| PAR-003 | `/clear`                | Clear in-process conversation history and runtime session memory. | Migrate           | Keep distinct from display-only `/cls`; share safe session-state service.         | 5          | is to prompt the user that this is a destructive operation and ask if they are sure (yes or no) to continue |
| PAR-005 | `/cls` (`/clearscreen`) | Clear the visible conversation without clearing session memory.   | Migrate           | One typed UI-effect result used by Chat and TUI; do not merge with `/clear`.      | 5          |                                                                                                             |
| PAR-013 | `/exit` (`/quit`, `/q`) | Request normal app shutdown.                                      | Migrate           | One exit intent; each frontend owns safe shutdown and rendering.                  | 5          |                                                                                                             |
| PAR-016 | `/help`                 | Render registry help and focused command details.                 | Migrate           | Derive Chat help, TUI completion/palette and usage hints from one metadata owner. | 5          |                                                                                                             |
| PAR-017 | `/history`              | Show in-process user/answer pairs.                                | Migrate           | Keep distinct from persisted `/transcript` and editor recall.                     | 5          |                                                                                                             |
| PAR-039 | `/set`                  | Set a variable only on Chat command context.                      | Retire            | Retire with `/vars`; it does not change model or runtime configuration.           | 0          | retire                                                                                                      |
| PAR-049 | `/vars`                 | List Chat command-context variables.                              | Retire            | Retire with `/set`; remove orphaned `/memory` variable count when approved.       | 0          | retire                                                                                                      |

### File access

Read a local file without adding it to memory. `/read` returns formatted content
as a command result for display. Command dispatch then skips the model-turn path:
the content is not attached to the next prompt, written to vector memory, or
saved as a transcript turn. The source file remains at its original path. TUI
file selection for context is a separate planned interaction.

**Enhancement candidate:** Offer an explicit way to attach file content to
model context from a slash command, using the same UI-neutral attachment
capability planned for TUI file selection. Keep bare `/read` display-only and
keep attachment distinct from `/ingest` persistence. Whether Chat and TUI both
gain the new syntax, and how it maps to the accepted attachment lifetime and
removal behavior, is for your decision. [D-77–D-82](tui-source-baseline.md#decisions) already
require selected TUI files to attach while preserving existing Chat `/read`
behavior in the first release.

| Case    | Command | Current effect                                                                                                | My recommendation                              | Combine or optimization opportunity                                                                                                     | Your score | Your decision             |
| ------- | ------- | ------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ---------- | ------------------------- |
| PAR-029 | `/read` | Read a file and display its formatted content; does not add it to model context, memory or a transcript turn. | Migrate current behavior; evaluate enhancement | Consider an explicit attach-to-context option backed by the TUI file-attachment capability; keep display and memory ingestion distinct. | 5          | agree with recommendation |

### Transcripts and replay

Persisted session inspection/export plus active replay, which can reset and reprocess turns.

| Case    | Command           | Current effect                                                   | My recommendation | Combine or optimization opportunity                                                                      | Your score | Your decision                                                                                                                                   |
| ------- | ----------------- | ---------------------------------------------------------------- | ----------------- | -------------------------------------------------------------------------------------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| PAR-014 | `/export`         | Export the current persisted session in a selected format.       | Migrate           | Share neutral transcript export effects with `/export-prompts` and `/transcript`; keep data scope clear. | 5          |                                                                                                                                                 |
| PAR-015 | `/export-prompts` | Export captured raw prompts/responses for one session.           | Migrate           | Same export service family; preserve capture availability and sensitive-data boundary.                   | 5          |                                                                                                                                                 |
| PAR-032 | `/replay`         | Reset and reprocess CSV turns through the active runtime.        | Migrate           | Keep separate from read-only startup replay; share transcript parsing only where semantics match.        | 5          |                                                                                                                                                 |
| PAR-038 | `/sessions`       | List persisted transcript sessions and markers.                  | Migrate           | Share transcript query capability with `/transcript`; does not switch session.                           | 5          |                                                                                                                                                 |
| PAR-048 | `/transcript`     | Inspect a persisted session or export all non-archived sessions. | Migrate           | Shared transcript query/export service; preserve scope and no session switch.                            | 5          | It doesn't appear as though transcript is correctly identifying the model. maybe a recording problem in the Friday telemetry/transcript package |

### Tools

Tool discovery, selection, budget and direct execution.

| Case    | Command            | Current effect                                                               | My recommendation | Combine or optimization opportunity                                                          | Your score | Your decision                                                                                                                                   |
| ------- | ------------------ | ---------------------------------------------------------------------------- | ----------------- | -------------------------------------------------------------------------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| PAR-004 | `/clear-tools`     | Clear manual tool selection and restore automatic selection.                 | Migrate           | One tool-selection capability with `/inject-tools` and `/tool-budget`; preserve its effect.  | 0          | Retire                                                                                                                                          |
| PAR-020 | `/inject-tools`    | Select an exact manual tool set under schema budget.                         | Migrate           | Share selection/validation with `/clear-tools` and `/tool-budget`.                           | 0          | Retire                                                                                                                                          |
| PAR-030 | `/recommend-tools` | Rank tool metadata by substring matches, labeling any match high confidence. | Retire            | `/tools` lists real tools and `/tool-budget` shows admission; neither claims recommendation. | 0          | Retire                                                                                                                                          |
| PAR-034 | `/run-tool`        | Validate and execute a tool, then present bounded result and update state.   | Migrate           | One tool admission/execution contract; TUI Activity must reflect actual execution.           | 0          | Retire                                                                                                                                          |
| PAR-046 | `/tool-budget`     | Show tool-selection mode, schema budget and last rejection state.            | Migrate           | Reuse selection policy state with `/tools`, `/inject-tools`, `/clear-tools`.                 | 0          | Retire                                                                                                                                          |
| PAR-047 | `/tools`           | List/filter registered tools and parameters.                                 | Migrate           | Authoritative inventory; do not present a heuristic rank as permission.                      | 5          | this should be a read-only operation, listing valid tools loaded. very likely that the user experience for this command needs to be embellished |

### Security

In-process security settings and local test aids.

| Case    | Command            | Current effect                                                      | My recommendation | Combine or optimization opportunity                                                                                  | Your score | Your decision                                                                   |
| ------- | ------------------ | ------------------------------------------------------------------- | ----------------- | -------------------------------------------------------------------------------------------------------------------- | ---------- | ------------------------------------------------------------------------------- |
| PAR-019 | `/inject-payload`  | Append one staged synthetic string to the next manual tool result.  | Retire            | Move this diagnostic fixture into tests; do not mix test payloads into normal command state.                         | 0          | Retire |
| PAR-035 | `/security`        | Show in-process security settings and scan counters.                | Migrate           | Share a typed security status capability with `/security-config`.                                                    | 5          | we need to validate the /security command and understand what that really means |
| PAR-036 | `/security-config` | Validate and change in-process sanitization settings with rollback. | Migrate           | Shared security capability; keep read and mutation effects explicit.                                                 | 5          | this is unclear. Not sure what it means                                         |
| PAR-037 | `/security-test`   | Run fixed local sanitizer samples and increment counters.           | Retire            | Keep deterministic sample tests and test actual deployed paths; this command does not prove broad security coverage. | 5          |                                                                                 |

### Workflows

Workflow task discovery, execution and approval.

| Case    | Command     | Current effect                                      | My recommendation | Combine or optimization opportunity                                       | Your score | Your decision                                                                                                        |
| ------- | ----------- | --------------------------------------------------- | ----------------- | ------------------------------------------------------------------------- | ---------- | -------------------------------------------------------------------------------------------------------------------- |
| PAR-050 | `/workflow` | List, run, inspect, approve or skip workflow tasks. | Migrate           | One typed workflow service; keep subcommand policy, progress and effects. | 5          | at this stage of the game, I do not believe we have a comprehensive workflow implementation from within Friday-Agent |

### Speech

In-process speech configuration and its current deterministic test command.

| Case    | Command        | Current effect                                                       | My recommendation | Combine or optimization opportunity                                                  | Your score | Your decision |
| ------- | -------------- | -------------------------------------------------------------------- | ----------------- | ------------------------------------------------------------------------------------ | ---------- | ------------- |
| PAR-040 | `/speech`      | Inspect/change in-process speech settings and prompt snippet.        | Migrate           | Keep configuration command; separate from standalone provider audio tests.           | 5          |               |
| PAR-041 | `/speech-test` | Make one deterministic adapter call in both `once` and `loop` modes. | Retire            | Use standalone `SpeechHarness` for real audio testing; current `loop` name misleads. | 5          |               |

My earlier recommendation was **43 migrate / 7 retire**; the maintainer's
selected scope differs and that recommendation is superseded. A **Combine**
decision should specify whether the
old name remains as an alias or receives a migration message, and whether its
arguments, effects and error behavior change.

## Architecture opportunities to score separately

These are implementation and interface choices; they do not automatically
remove a command. Enter 0–5 for priority and a decision or note.

| ID   | Opportunity                                       | Benefit and boundary                                                                                                                                                                                | Your priority | Your decision or note                                                                                                                          |
| ---- | ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| A-01 | One UI-neutral command registry and handler owner | Chat and TUI share metadata, parsing, validation, execution and policy; no CLI import in TUI or duplicate maintained handlers.                                                                      | 5             |                                                                                                                                                |
| A-02 | Typed semantic results and UI-effect intents      | Chat preserves current text; TUI renders structured data without parsing CLI strings.                                                                                                               | 5             |                                                                                                                                                |
| A-03 | Smaller capability contracts by service family    | Replace the broad Chat `CommandContext` dependency with typed memory, transcript, tool, agent, speech and maintenance seams as families migrate.                                                    | 5             |                                                                                                                                                |
| A-04 | Shared diagnostics snapshot                       | `/debug`, `/timing`, `/debug-budget` and `/memory` reuse evidence, while retaining distinct meanings unless you choose a combined interface.                                                        | 5             | a more readable user interface and only provide a small amount of user interactivity within these diagnostics                                  |
| A-05 | Shared memory-record query path                   | `/entities`, `/insights`, `/summaries`, `/meta` and `/list-ingested` use typed reads and consistent unavailable/error results.                                                                      | 5             |                                                                                                                                                |
| A-06 | Shared guarded maintenance path                   | `/compact`, `/lifecycle`, `/migrate`, `/reorganize`, `/reset` reuse admission, progress and outcome contracts without weakening operation-specific safety.                                          | 4             | these are important features, but for the most part, much of the work behind these lifecycle maintenance routines is running in the background |
| A-07 | Shared tool-selection and execution paths         | Conditional on retaining a tool slash command: `/tools`, `/tool-budget`, `/inject-tools`, `/clear-tools`, `/run-tool` use one policy view; reading, selection and execution remain distinguishable. | 0             |                                                                                                                                                |
| A-08 | Shared transcript read/export services            | `/sessions`, `/transcript`, `/export`, `/export-prompts` reuse neutral effects with explicit current/all-session and raw-prompt boundaries.                                                         | 5             |                                                                                                                                                |
| A-09 | Metadata-driven help and discovery                | `/help`, TUI completion, palette and usage hints derive from the effective shared registry; TUI-only extensions remain isolated.                                                                    | 5             |                                                                                                                                                |
| A-10 | Shared file-content effects                       | Reuse file reading and extracted-content snapshots while keeping display (`/read`), active context attachment and persistent memory ingestion (`/ingest`) separately authorized and observable.     | 5             |                                                                                                                                                |

## Notes and decisions

Add any score rationale, combine target, retained alias, migration message,
release timing, or command you want reconsidered here. The three slash-command
aliases follow their parent cases. `@agent_name <message>` and startup
`--replay` are separate accepted routes; the optional `!<command>` route is
deferred from the first full TUI release. They are not part of the 50 rows.

- Add notes here.

**Recorded command decisions:** Retain `/tools` as a read-only listing and
retire `/clear-tools`, `/inject-tools`, `/recommend-tools`, `/run-tool`,
`/tool-budget` and `/inject-payload` as part of the shared command refactor.
Migrate `/security`, `/security-config`, `/security-test`, `/workflow` and
`/speech-test` unchanged.
Retain `/migrate` for the first TUI version. C-01 through C-06 go to the
[command follow-up backlog](../../backlog/friday-tui-command-followups/README.md)
without changing current names or syntax during this refactor. The six named
command retirements belong in the shared command refactor, with explicit
checks for removed names, help, errors and compatibility; retained commands
keep their current behavior. This sheet does not decide whether Friday's
underlying tool runtime remains available to the agent. Reconcile the accepted
PAR matrix, help, documentation and compatibility expectations in the bounded
command-refactor plan before implementing that scope change. `/inject-payload`
has no remaining consumer once `/run-tool` is retired.

After you score the sheet, reconcile the decision register, PRD, phase plan,
PAR matrix, Chat compatibility evidence and user guides before generating
command-refactor code. The current [TUI board gate](../../board.yaml) is
still the corrected shell review and physical macOS UAT; this sheet grants no
source, delivery or release authority.

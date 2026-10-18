# Friday TUI command coverage matrix

Status: Current source inventory; TUI behavior tests are still required.

Source: current Chat registry at `c3426986`. Each row requires positive, argument/choice,
alias, invalid-input and applicable unavailable-backend cases, plus output/state/UI
effects. Destructive operations use disposable stores or fakes. A registered name
is not a passed parity case. TUI handlers are independent of Chat; equivalent
behavior uses UI-neutral services where needed, while result presentation may
follow TUI conventions. Full argument/default/choice metadata is retained in
[the JSON inventory](validation/command-matrix.json).

| Case | Command | Aliases | Current usage |
| --- | --- | --- | --- |
| PAR-001 | `/agent` | — | `/agent [name]` |
| PAR-002 | `/agents` | — | `/agents` |
| PAR-003 | `/clear` | — | `/clear` |
| PAR-004 | `/clear-tools` | — | `/clear-tools` |
| PAR-005 | `/cls` | /clearscreen | `/cls` |
| PAR-006 | `/compact` | — | `/compact` |
| PAR-007 | `/context` | — | `/context [--debug] [--file]` |
| PAR-008 | `/debug` | — | `/debug` |
| PAR-009 | `/debug-budget` | — | `/debug-budget` |
| PAR-010 | `/debug-retrieval` | — | `/debug-retrieval <query>` |
| PAR-011 | `/delegate` | — | `/delegate <agent> <task>` |
| PAR-012 | `/entities` | — | `/entities [nodes\|name]` |
| PAR-013 | `/exit` | /quit, /q | `/exit` |
| PAR-014 | `/export` | — | `/export [csv\|jsonl\|markdown\|md\|training]` |
| PAR-015 | `/export-prompts` | — | `/export-prompts [session_id]` |
| PAR-016 | `/help` | — | `/help [command]` |
| PAR-017 | `/history` | — | `/history` |
| PAR-018 | `/ingest` | — | `/ingest <path> [description] [--lines=N]` |
| PAR-019 | `/inject-payload` | — | `/inject-payload <payload>` |
| PAR-020 | `/inject-tools` | — | `/inject-tools <name> [name ...]` |
| PAR-021 | `/insights` | — | `/insights` |
| PAR-022 | `/lifecycle` | — | `/lifecycle [--execute] [--stats\|--flush\|--optimize]` |
| PAR-023 | `/list-ingested` | — | `/list-ingested` |
| PAR-024 | `/memory` | — | `/memory` |
| PAR-025 | `/meta` | — | `/meta` |
| PAR-026 | `/migrate` | — | `/migrate [--force\|--execute\|--stats]` |
| PAR-027 | `/prime` | — | `/prime` |
| PAR-028 | `/prompt` | — | `/prompt [--file]` |
| PAR-029 | `/read` | — | `/read <path> [--lines=N]` |
| PAR-030 | `/recommend-tools` | — | `/recommend-tools <query>` |
| PAR-031 | `/reorganize` | — | `/reorganize [--execute] [--backup\|--dedupe\|--analyze\|--prune\|--synthesize\|--verify] [--skip-synthesis] [--skip-verify] [--skip-lifecycle] [--force-reembed]        /reorganize --recover <run-id> [--execute]` |
| PAR-032 | `/replay` | — | `/replay <csv_path> [delay_seconds]` |
| PAR-033 | `/reset` | — | `/reset [graph\|vector\|episodic]` |
| PAR-034 | `/run-tool` | — | `/run-tool <name> [json]` |
| PAR-035 | `/security` | — | `/security` |
| PAR-036 | `/security-config` | — | `/security-config <sensitivity\|action\|wrapping> <value>` |
| PAR-037 | `/security-test` | — | `/security-test [instruction\|delimiter\|jailbreak\|exfil\|all]` |
| PAR-038 | `/sessions` | — | `/sessions` |
| PAR-039 | `/set` | — | `/set <key> <value>` |
| PAR-040 | `/speech` | — | `/speech [on\|off\|config\|mode <live\|file>\|voice <name>\|provider <elevenlabs\|picovoice>]` |
| PAR-041 | `/speech-test` | — | `/speech-test [once\|loop]` |
| PAR-042 | `/status` | — | `/status` |
| PAR-043 | `/summaries` | — | `/summaries` |
| PAR-044 | `/switch` | — | `/switch [agent]` |
| PAR-045 | `/timing` | — | `/timing` |
| PAR-046 | `/tool-budget` | — | `/tool-budget` |
| PAR-047 | `/tools` | — | `/tools [category]` |
| PAR-048 | `/transcript` | — | `/transcript [session_id\|export]` |
| PAR-049 | `/vars` | — | `/vars` |
| PAR-050 | `/workflow` | — | `/workflow <list\|run\|status\|approve\|skip> [name] [key=value ...]` |

Additional routes: `@agent_name <message>` and disabled-by-default `!<command>` must
retain their application routing. Startup replay, config/runtime flags and installed
help/version need startup cases specified in the active
[replacement plan](replacement-plan.md) before a construction directive. D-62
keeps the successful startup replay result visible in a read-only screen until
Quit; D-63 limits its replay data to file and turn count. Interactive
`/replay` remains PAR-032. D-64 keeps startup replay failures in a read-only
file/error view until Quit, followed by nonzero exit. D-65 offers no in-process
Retry on that view; the user corrects the cause and relaunches.

D-66 requires the TUI's active command registry to supply automatic matches
for a leading `/` name as it is typed, including registered aliases. Display
alone does not edit or run the command; the palette remains a separate route.
D-67 lets inline selection complete the chosen command token in the current
draft, preserving following arguments; the user submits it separately.
D-68 uses `Up`/`Down` to highlight and `Tab` to insert while suggestions are
open. `Enter` still submits the editor draft; when the list is closed, `Tab`
returns to focus navigation.
D-69 extends inline matches to declared subcommands after a recognized command
and space; `/workflow r` can suggest `run`. Selection fills only that token,
and free-form argument values are not suggested.
D-70 shows the recognized command or subcommand's required/optional argument
shape as a display-only usage hint from the same active registry metadata.
For example, `/workflow run` can show `<name> [key=value ...]` without filling
values or dispatching.

D-71's editor history recalls submitted conversational prompts and `/`
commands into the editor without executing them. It is not PAR-017 `/history`,
which retains its Chat-compatible command behavior.
D-72 keeps this editor recall list in-process for one TUI run; it starts empty
after restart even when transcript data exists.
D-73 preserves an unsent editor draft during recall browsing and restores it
when the user leaves without submitting a recalled entry; browsing never
rewrites a submitted history item.
D-74 assigns `Up`/`Down` at editor caret boundaries to older/newer recall
entries only when no slash-suggestion list is open; open suggestions take
arrow-key priority. Interior arrow movement remains editor navigation.
D-75 includes accepted `@agent` and enabled/admitted `!` route submissions in
the same editor recall list. Recall fills the editor without re-routing until
the user explicitly submits the recalled entry.

PAR-005 covers both `/cls` and `/clearscreen`. In the TUI, each clears the
displayed conversation, pinned prompt and Activity without replacement text;
session history, memory and persisted transcripts remain. Verify the pin stays
empty until the next accepted conversational prompt.

PAR-038 `/sessions` lists persisted sessions, PAR-048 `/transcript` inspects
or exports transcripts, and PAR-044 `/switch [agent]` changes the active agent.
The first TUI release has no control for switching the active transcript
session; these cases must not be mistaken for such a control.

Coverage groups map to existing Chat tests for session/memory, diagnostics,
transcripts/export, maintenance, tools/security, speech, orchestration/workflows
and file/replay commands. Add TUI interaction/effect evidence for every row; the
current 241-test baseline covers selected existing behavior, not the full matrix.

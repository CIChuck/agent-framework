# Friday TUI user documentation requirements

**Status:** Accepted delivery requirement; guide content awaits implemented behavior

**Audience:** People installing and using Friday TUI on macOS or Linux. Write for
users who want to accomplish tasks, including users unfamiliar with Friday's
package structure. Define any necessary technical term at first use.

The completed TUI requires a dedicated guide in the numbered
[`docs/guides/`](../../../guides/README.md) series, provisionally
`docs/guides/20-tui.md`. It must describe the actual installed TUI, not a proposed
screen or command. Link it from the guide index and relevant getting-started,
configuration, CLI-command and troubleshooting paths. Keep the TUI guide and
configuration reference consistent, with one detailed source for each setting
and task-focused examples in the TUI guide.

## Content required for the first release

1. **Start and resume:** Supported macOS/Linux terminals, installation,
   `friday-tui --help` and version checks, first launch, choosing an existing
   runtime configuration from the launch folder when `--config` is absent,
   why model-library and CLI presentation YAML do not appear as runtime
   choices, why a custom-named runtime YAML can appear while an unrecognized
   file must be found through Browse, why a recognizable but incomplete file
   may be listed and then fail validation, what to do when the launch-folder list
   is empty, using Refresh after adding or editing a file, browsing folders or
   typing/pasting absolute, relative or `~` paths to an existing file elsewhere,
   and that relative entry uses the displayed Browse folder. Explain that a
   working `.yaml`/`.yml` link in the launch folder can appear even when its
   target is elsewhere, while a broken link needs correction or a different
   file through Browse. Show explicit config paths that bypass the list,
   real operation by default after selecting a config, explicit offline/fake
   test mode, startup failure without a silent mode switch, and how to
   recognize the active mode. Explain that the existing Chat-specific
   `FRIDAY_CHAT_RUNTIME` setting does not select the TUI mode; users choose
   fake with the TUI's own `--runtime fake` option. Cover startup
   `--replay FILE` and `--replay-delay` separately from interactive `/replay`:
   after success, a read-only result shows the file and processed-turn count,
   without a turn-by-turn list, until the user chooses Quit. Explain that this
   view does not accept prompts or `/` commands or open the configured
   interactive session. On replay failure, explain the read-only file/error
   screen, Quit and nonzero exit, and that the chooser does not open. Give a
   simple correction-and-relaunch step; there is no Retry on this screen.
2. **Read the screen:** Name the conversation, editor, status, help/discovery,
   command palette and the first-release Context file browser. Explain how to
   browse folders and select a file by keyboard or pointer, collapse the
   sidebar and return to the editor without changing the conversation.
   Explain that clicking or keyboard-activating a file immediately attaches
   it for Friday's next eligible turn, without submitting a prompt or requiring
   an Add button; moving focus or scrolling does not attach. Show the visible
   loading, attached and failed states, how an attached file continues to
   inform later turns, and how to use the focusable Remove action to stop
   including it in future turns. Explain that closing the TUI discards active
   attachments, so a new launch starts empty even when earlier conversation
   records remain available; users can reselect files. Explain that selecting
   another distinct file adds it alongside existing attachments, and show how
   to remove one without removing the others. Explain that Friday keeps the
   content captured when a file is selected, does not automatically notice
   edits to the source file, and refreshes that attachment when the same file
   is selected again. Explain that a failed refresh reports an error and
   keeps the last successfully attached content. List the shipped attachment
   formats in user language: text/code/data, PDF, Word DOCX and Excel XLSX.
   Explain that attaching an Excel workbook includes every worksheet, even
   hidden ones, with each sheet labeled by name in workbook order. Explain
   that if one sheet cannot be read, the whole new workbook is not attached,
   the problem sheet is named, and a failed refresh keeps the last complete
   version while other attached files remain available. Explain that
   formula cells show the formula and any result saved in the workbook as
   separate labeled information; when no saved result exists, say so, and
   do not imply Friday recalculates the workbook.
   Explain what content is extracted, including Tesseract OCR text
   from scanned PDFs and how mixed PDFs use embedded text on readable pages
   and OCR on scanned pages in page order; how to install Tesseract separately
   on macOS and Linux, check that it and the selected OCR language packs are
   available, and relaunch after fixing a missing-install error; that the
   PDF page renderer comes with the installed TUI package and needs no separate
   user installation;
   how a failed scanned page rejects the whole PDF attachment with its page
   identified, while a failed refresh retains the last complete attachment;
   the visible failure when OCR or another read yields no usable content;
   that an oversized file is not attached, its estimated-token limit error is
   shown, and
   a failed refresh leaves the last complete version available; that adding
   a file which would exceed the combined attachment budget leaves existing
   files attached, and users can remove one and retry; and any spreadsheet,
   language or numeric size limits settled before release. Do not
   describe Chat `/read` placeholders as attached document content.
   Distinguish model context from storing a file in memory. Explain inline
   command results, the pinned latest prompt above its
   scrolling answer,
   the rolling tool-activity log, `Not run` entries and responsible-agent labels,
   and how Activity sits inline within the exchange or tool command that
   produced it rather than in a separate pane. Show its internal scrolling,
   Activity opening when its first entry arrives, how to collapse and reopen it,
   and that the collapsed header counts new entries. Explain that retained
   entries remain available when reopened, while an eviction indicator means
   older entries are no longer inspectable. Explain that opening Activity
   does not move the reader away from older conversation. Show how to scroll
   Activity without being pulled to new entries and how to click or
   keyboard-activate `Jump to latest Activity` to resume following.
   Explain that a new prompt does not collapse older exchanges' Activity;
   users can return to each retained section in the state they left it.
   Cover prompt/response role colors and labels, focus, scrolling, resizing,
   narrow-terminal behavior, busy/pending-Quit and failures using the shipped
   labels and keys. Explain that the pin hides while browsing older exchanges
   and that new output does not pull the view away. Show how to click or
   keyboard-activate `Jump to latest` to reach the bottom, restore the pin when
   available and resume following; ordinary scrolling to the bottom does the
   same. Distinguish the two return controls and explain the same cues for
   users who cannot rely on color.
3. **Interact by keyboard:** Explain that `Enter` submits the editor draft and
   `Ctrl+Enter` inserts a newline without submitting when the terminal supports
   distinct key events. Show the focusable Submit and Insert newline controls
   and identify terminals where the newline shortcut is unavailable. Explain
   how to click or keyboard-activate Insert newline there; do not imply that
   another default newline shortcut exists. Explain
   that multiline paste does not submit. Explain editor history for submitted
   prompts, `/` commands, `@agent` messages and enabled `!` commands, recall
   without execution, and how it differs
   from the `/history` command. State that editor recall resets when the TUI
   exits, even if a saved transcript exists. Explain that browsing preserves
   an unsent draft and restores it when history is left without submission.
   Describe `Up`/`Down` history traversal at the multiline editor's top/bottom
   caret boundaries, ordinary cursor movement inside the editor, and the
   priority of an open slash-suggestion list. Do not advertise F3/F4 as
   first-release history keys.
   Cover help and command
   discovery, copying text, inspecting tool-call
   parameters and execution status,
   navigating long activity logs, output navigation, normal safe Quit and the
   separately warned emergency Force quit. Document what
   happens when a slash command is submitted during an active operation,
   including retained editor text and the separate Ctrl+Q/Quit action.
4. **Use commands:** List every shipped `/` command and alias with its purpose,
   syntax, relevant arguments/subcommands, a working example and the effect or
   prerequisite a user needs to understand. Explain that typing `/` shows
   matching command suggestions as the name is entered, without running one.
   Show that selecting a suggestion fills the command name or alias in the
   current draft while keeping typed arguments, and still requires Submit.
   Explain `Up`/`Down` highlighting and `Tab` insertion while suggestions are
   open, ordinary `Tab` focus movement when they are closed, and `Enter` Submit
   in both cases; verify these keys in the installed terminal candidate. Show
   that recognized commands also suggest declared subcommands, such as
   `/workflow r` → `run`, while free-form argument values remain typed by the
   user. Explain the short usage hint for a recognized command or subcommand,
   including how required and optional argument shapes appear without filling
   values. Explain that choosing a `/` command in the palette fills the editor
   for review and argument entry,
   while `Enter` or Submit runs it. Show the replacement prompt when a draft
   already exists: Cancel keeps the draft; Confirm replaces it without
   running the command. Cover `@agent` and optional `!`
   input as distinct routes. Explain that `/cls` and `/clearscreen` clear the
   displayed conversation, pinned prompt and Activity, while session history,
   memory and persisted transcripts remain; the pin returns after the next
   accepted conversational prompt. If a failed first prompt is waiting to be
   restored, explain that the display clear also removes its error notice but
   leaves `Restore failed prompt` beside the editor during this run.
   Distinguish this from `/clear` and `/reset`,
   explain that `/sessions` and `/transcript` list, inspect or export persisted
   sessions but do not change the active one, and state that `/switch [agent]`
   changes agents.
   Explain when a command is unavailable because a service is not configured.
   Describe how users discover newly added TUI commands.
5. **Complete common tasks:** Show short, reproducible workflows for a
   conversation, inspecting and changing memory safely, using available tools
   and agents/workflows, reading or ingesting a file, exporting/replaying a
   transcript, following a multi-tool agentic task, and quitting after long
   work. Mark any destructive example as
   using disposable data; do not suggest a success message alone proves a
   persistent state change.
6. **Configure the TUI:** Explain the shared runtime config/model files and
   existing presentation file from a user's perspective, including the
   optional `tui:` settings, dark/light mode, keyboard/layout/output choices,
   English OCR by default and selection of installed languages for scanned
   PDFs, including a missing-language recovery example, and optional per-file
   and combined attachment limits with defaults, expressed as estimated tokens
   of the text sent to Friday rather than raw file size. Explain that omitted
   limits default to 4,000 estimated tokens per file and 8,000 combined across
   models, that users can set explicit limits, and that these limits do not
   guarantee a turn fits the model context. Use an 8,192-token model example
   to show why other turn content still needs room. Explain that the TUI
   checks each complete conversational model request before sending it. When
   one is over budget, explain that the TUI can ask Friday to compact older
   saved turns once if runtime compaction is enabled and eligible, then recheck
   and continue automatically if the request fits. Explain that compaction
   can use a separate model call and update stored memory, and that it may
   be unavailable or unable to make enough room. If the first request still
   cannot fit, the draft and files stay available for correction; if a later
   agent-loop step cannot fit, the turn ends incomplete and already performed
   tool work remains visible. Distinguish the runtime compaction setting from
   TUI-only attachment limits and explain that no TUI setting enables
   compaction implicitly. Explain
   that the estimate can differ from a provider's final token count. Explain path selection,
   defaults, validation errors and how to recover. Explain the
   default-hidden reasoning display option, its in-app forward-only toggle,
   and what to expect when a provider supplies no reasoning text. State
   accurately which settings change only the TUI and which control the Friday
   runtime. Keep secrets out of examples and never imply startup rewrites files.
7. **Recover from problems:** Give actionable steps for missing/invalid config,
   including an empty chooser list with Refresh, Browse and Quit, and the chooser's
   validation error with Retry of the selected path after
   correcting the file, Browse to another file and Quit. Explain the error
   shown for a mistyped or missing Browse path and how to correct it.
   Distinguish this chooser recovery from an invalid explicit `--config` file,
   which reports an error and exits nonzero without opening the chooser.
   Explain that a failed real-runtime start after chooser selection returns to
   the chooser with an error and Retry, Browse and Quit after successful cleanup. If
   cleanup fails, explain that the TUI reports both failures and exits nonzero
   with best-effort terminal restoration, without in-process retry. With
   explicit `--config`, explain that failed real startup reports the error
   and exits nonzero after cleanup, without opening the chooser; report cleanup
   failure separately. Cover
   absent optional services, unsupported terminal size or key mapping, long
   operations, view truncation, startup/cleanup failure, emergency Force quit
   with potentially incomplete work, and terminal recovery.
   Explain that older messages evicted from the on-screen view can be inspected
   with `/transcript` only when they were saved; if no saved transcript is
   available, the UI must say so. Do not describe a first-release `Load older`
   control or imply transient Activity or reasoning can be recovered there.
   Explain a turn-over-budget message with estimated total, available budget
   and overage: the blocked conversational request was not sent; an eligible
   compaction attempt may have used a separate model service and changed
   stored memory. For a failed first request, the draft and attachments remain,
   and the user can shorten the prompt or remove a file before retrying.
   For a failed later request, state that the turn is incomplete, earlier
   tool effects remain and no further loop step ran. Explain that the
   incomplete turn and Activity remain visible only during this TUI run while
   retained on screen; they are not saved in the transcript or restored by
   `/transcript` after relaunch. Distinguish this from a
   provider context-length error after a request passed the estimate: the
   request was sent, the TUI will not automatically compact or retry, and the
   user can correct the preserved initial draft and attachments or inspect an
   incomplete later turn with earlier tool work retained during this run and
   no incomplete-turn transcript entry. Explain that the
   failed prompt returns automatically when the editor is empty. If the user
   typed a newer draft, it stays in place and a `Restore failed prompt` action
   is available with the error. If the error scrolls out of the bounded chat
   view, the same action remains beside the editor during this run while the
   failed prompt is available to restore. Users can click it or reach it by
   keyboard; using it asks before replacing the newer draft, and neither
   path submits automatically. Clearing the conversation with `/cls` or
   `/clearscreen` also keeps that action available during this run. Explain
   that the failed initial attempt is not saved in the transcript and its
   error/prompt recovery ends with this TUI run; a corrected successful
   submission is a new recorded turn. If the user sends a different prompt,
   explain that Restore stays available while Friday works and disappears
   only after that new answer completes successfully. A failed new attempt
   alone does not clear the older Restore action; neither does running a slash
   command. An older error message may remain visible without a Restore action
   until the view is cleared or it scrolls out. If more than one failed prompt
   is waiting, explain the single
   `Restore failed prompts (N)` control beside the editor and its newest-first
   chooser. Explain that the individual error messages do not each have a
   separate Restore action while the chooser is shown. Show how to open it by
   keyboard or pointer, identify and choose a prompt, and cancel without
   changing the current draft. Choosing a prompt asks before replacing a
   nonempty draft and never sends it automatically. The original remains in
   the chooser, with the same count, after its copy enters the
   editor. Editing or replacing that copy does not lose the original; a user
   can restore it again until a conversational turn succeeds or the user
   dismisses it. Show how to choose `Dismiss` beside a single Restore control
   or on one prompt in the chooser, and explain that Confirm removes only that
   saved recovery entry while Cancel keeps it. If the user already restored a
   copy into the editor, dismissal leaves that editable draft in place. The
   number shown updates as entries are dismissed; the controls disappear when
   none remain. Do not imply that provider telemetry or separately
   completed maintenance work is erased. Link to the general troubleshooting
   guide where it has the full procedure.

Use task-oriented headings and plain language. Prefer a small number of
verified examples over internal class/API descriptions. Separate ordinary user
steps from advanced options. Do not copy the CLI guide's screen output or claim
identical formatting; command effects and state must remain equivalent.

## Configuration placement and maintenance

The detailed `tui:` settings reference belongs in
[`10-configuration.md`](../../../guides/10-configuration.md), as confirmed by
Chuck Russell. For each supported setting, including both attachment limits, give its
valid values, default, effect and a complete example in plain language. The new TUI guide gives the
short setup steps users need for everyday tasks and links to that reference.
The configuration guide must also link back to the TUI guide for instructions
on using the finished application. Keep the two pages consistent without
duplicating the full settings table.

The first-release guide must explain the
[reasoning display capability](reasoning-display-requirement.md): how to hide
or show provider-supplied reasoning, that the in-app toggle affects later
events only and does not rewrite configuration, how it differs from the final answer,
and what happens when the provider supplies no viewable text. Document its
values and default in `10-configuration.md`, then verify the instructions
against the installed candidate before release acceptance.

The first-release guide must explain the
[tool-activity view](tool-activity-requirement.md): its step and actor labels,
running/completed/failed and `Not run` states, parameters displayed as
passed to tools without TUI masking up to the view-size limit, collapsed and
expanded views, and
how it differs from
the final response. Explain that
automatic tool-result content is sent back to Friday but does not appear in
Activity or scrolling chat. Explain that manual `/run-tool` retains its inline
command result and gets an Activity entry; delegated/workflow calls show the
responsible actor. Explain the explicit truncation notice for an oversized
parameter, that its overflow is not retained in TUI Activity, and that the
tool still receives the complete value. State that Activity is available
only in the running TUI session and is not added to transcripts or exports.
Explain how to select and copy visible Activity and shown provider reasoning.
For a truncated parameter, copied text includes only the preview and notice;
hidden reasoning and discarded overflow cannot be copied. Copying does not
add these views to transcripts or exports.
Show where provider-supplied reasoning appears after tool
calls when reasoning display is enabled. Verify the example against a task
that actually invokes more than one tool and more than one internal model step.
Do not claim a requested call ran if execution was rejected; show the
`Not run` reason. A tool excluded by selection or budget policy before any
request is not shown as a `Not run` call.

At each user-visible construction increment, update the draft guide or its
command/configuration inventory alongside behavior and tests. Before release
acceptance, update its framework-version basis and verify the guide against
the installed final candidate on both
supported platforms: commands and aliases, flags, config files, keys, screen
labels, example results, links and troubleshooting steps. Have real users follow
the first-launch, config-choice, everyday-command and safe-Quit instructions as
part of UAT. Record discrepancies as defects and correct them before the guide
claims to describe the released TUI. Include the controlled real-provider/tool
UAT task once its provider is selected; describe provider reasoning availability
accurately. Guide creation, index/navigation updates
and configuration-guide updates are completion criteria, not post-release work.

The guide itself is not written yet because no TUI executable or screens have
been implemented. Existing `docs/guides/` pages describe the current published
application and must not claim TUI availability before that changes.

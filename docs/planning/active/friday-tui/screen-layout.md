# Friday TUI screen and interaction proposal

**Status:** Inline timeline, role color coding, pinned latest prompt,
history-return and editor keys accepted; remaining layout details are proposals;
no UI has been implemented

**Branch:** `feature/friday-tui`; authority `design_only`

This proposal describes what a user would see and do in the independently
installed `friday-tui`. It follows the accepted multiline editor, explicit
submit, safe Quit, command parity and shared-configuration requirements in
[decisions.md](decisions.md). It does not authorize product implementation or
restore the withdrawn Chat-dependent integration contract.

## Normal screen

The conversation is the center of the application. A typical wide terminal
(about 120 columns by 30 rows or larger) would look like this:

```text
+ Friday TUI  |  session: work  |  mode: real  |  model: configured route ---+
| Context                 | Browsing older conversation                   |
|                         | Conversation and command results              |
| Session: work           | You                                            |
| Working directory: ...  | Please summarize the selected file.            |
| Active agent: Friday    |                                                |
| Available services: ... | Activity [Collapse]                            |
| Files: [Browse]         |                                                |
| Attached: notes.md      |                                                |
|   [Remove]              |                                                |
| Attached: report.py     |                                                |
|   [Remove]              |                                                |
|                         | Step 1: file_read(path=...)  Completed         |
|                         | Step 2: Friday reasoning... [if shown]        |
|                         | Step 2: file_grep(pattern=...) Completed       |
|                         | Friday: Here is the summary...                 |
|                         |                                                |
|                         | /history  |  12 entries                        |
|                         | 1. ...                                         |
|                         |                                                |
|                         | [Jump to latest]                               |
+-------------------------+------------------------------------------------+
| Ask Friday or enter a / command                              [editor]   |
| Multiline text stays here until a submission is accepted.              |
|                                                                        |
| [Submit: Enter] [New line: Ctrl+Enter] [Help: F1] [Quit: Ctrl+Q]        |
+ Status: Ready  |  browsing history  |  config: config.yaml --------+
```

This sketch shows the history-browsing state: the latest prompt pin is hidden
and the clickable `Jump to latest` control is visible. The exact labels and
spacing are design details to verify in terminal UAT.
The zones have distinct jobs:

| Zone | What the user sees | Behavior |
| --- | --- | --- |
| Header | Friday, current session, runtime mode and a safe model/route label when available. | Fixed while content scrolls; no credentials or secret values. Compact on narrow screens. |
| Context sidebar | Current transcript session, working directory, active agent and available service information that the runtime can report reliably, plus a navigable folder/file list, visible attachment status and a focusable Remove action for each attachment. | Focusable and independently scrollable if needed; hide/collapse without losing the conversation. In the first release, deliberate file selection immediately captures content for Friday's next eligible model turn (D-76/D-77); keyboard focus movement and list scrolling do not select. Show extraction/OCR progress and success or failure without starting a turn, including failure when no usable content can be extracted. Text/code/data, PDF, DOCX and XLSX attachments contain real extracted content (D-82), never a placeholder. XLSX includes every worksheet, even hidden sheets, labeled by name in workbook order (D-89). An unreadable worksheet fails the whole new workbook attachment with its name shown; failed refresh retains the last complete snapshot (D-90). Formula cells supply the formula and any saved result with distinct labels; a missing saved result is shown as unavailable rather than calculated (D-91). An oversized file shows estimated token usage and the limit rather than a partial attached excerpt; failed refresh retains the last complete snapshot (D-92/D-95). A new file that would exceed the combined attachment budget fails without changing existing files; users remove files and retry, while an over-budget refresh keeps its old snapshot (D-93). Mixed PDFs keep page order, using Tesseract only for pages without usable embedded text (D-83/D-84); a missing system-installed Tesseract shows a setup error only when OCR is needed (D-85). A required OCR page failure rejects the whole new PDF attachment with the page identified; failed refresh keeps the last complete snapshot (D-86). English is the OCR default, and a missing configured language pack is named in the attachment error (D-87). The installed TUI supplies the PDF page renderer; users install Tesseract separately (D-88). Attached files remain active across later turns until individually removed (D-78); selecting another distinct file adds it alongside them (D-80). The selected content stays fixed until the same file is reselected to refresh it (D-81); failed refresh preserves the last good snapshot with an error. Removal affects future turns, not one already admitted, and does not change the source file or memory. A new TUI run starts with no attachments (D-79); users reselect files as needed. A UI-neutral runtime contract supplies content; browsing does not switch transcript sessions, ingest memory or edit files. |
| Conversation | User prompts, Friday responses, command results, errors and relevant progress in time order. | The main independently scrollable area. User and Friday entries use distinct role colors plus explicit labels, so meaning does not depend on color alone. |
| Latest prompt | The last accepted conversational prompt, labeled and accented as a user entry. | Stays at the top while its Friday response scrolls below; hides while the user browses older exchanges and returns at the bottom when available. It is a view of the existing prompt, not a second transcript or model turn. |
| Jump to latest | A labeled control at the lower edge of the conversation when the view is away from the bottom. | Clickable and keyboard-focusable. Activating it scrolls to the bottom, restores the latest pin when available and resumes following new output without changing session state. |
| Activity | Ordered model-step, executed tool-call, `Not run` and optional provider-reasoning entries for submitted work. | Inline within its conversation exchange or user-entered tool-command entry, ahead of that entry's final answer/result. Opens on the first entry. Shows actor, tool identity, parameters as passed to the tool without TUI masking, and execution status without automatic tool-result payloads. Oversized values show a marked, bounded preview; the tool still receives the full value. Covers agent, delegated/workflow and manual `/run-tool` calls; users can collapse or reopen the section without losing retained entries or the final answer. The collapsed header shows new-entry count and any eviction indicator. Its expanded viewport scrolls independently of the conversation. |
| Jump to latest Activity | A labeled control on expanded Activity when its view is away from the bottom. | Clickable and keyboard-focusable. Returns Activity to its newest retained entry and resumes following without moving the conversation or its prompt pin. |
| Prompt editor | A multiline place to ask Friday a question or enter a `/` command; compact recovery controls appear beside it after a failed-prompt error notice leaves the conversation. | Fixed near the bottom; wraps and scrolls internally for long drafts. Its height follows available space and the supported `tui.layout` setting. One pending prompt shows `Restore failed prompt` and `Dismiss` together at the notice or editor, as applicable; multiple show `Restore failed prompts (N)` beside the editor and open a newest-first chooser with per-prompt Dismiss (D-107/D-109). The controls remain reachable in a narrow layout without relying on the Context sidebar. |
| Actions | Visible, focusable Submit, Insert newline, Help, Commands and Quit controls with shortcut hints. | Keyboard access is always available; mouse use may be convenient but is not required. |
| Status | Ready, working, waiting for a safe Quit point, cleanup or failure; concise activity/configuration context. | Fixed at the bottom. While normal Quit is pending, a separate warned/confirmed emergency Force quit action is available; it never claims graceful cleanup. |

## Entering a prompt or command

The editor is the primary interaction surface. The user types a question,
pastes text or enters any supported `/` command in the same place. In the
editor, `Enter` submits the complete draft once; `Ctrl+Enter` inserts one
newline without submitting. Pasting, including multiline paste, never
submits. Visible, keyboard-focusable Submit and Insert newline controls
provide the same actions. A terminal may deliver `Ctrl+Enter` as plain
`Enter`; record actual key events during macOS and Linux UAT and document
the Insert newline control as the fallback where the shortcut is unavailable.
No second default newline shortcut is assigned. No synthetic key event alone
establishes physical key support. Safe
remapping remains a separately validated configuration design. Textual's
[input guide](https://textual.textualize.io/guide/input/) describes inspecting
the key events a terminal actually delivers.

An accepted submission appears once in the conversation and clears the editor.
For a conversational prompt, the latest accepted prompt also appears in the
fixed prompt strip above the response viewport. The strip updates only after a
new prompt is accepted; an unsent or busy-rejected draft never replaces it.
Keep long prompts compact by default with a clear Expand/Collapse action and
independent scrolling when expanded, so the answer retains usable space.
For a model-bound draft that would exceed the selected model's effective
input budget after Friday assembles its first request, Submit shows bounded
older-turn compaction progress when configured and eligible (D-98/D-99).
Friday then rechecks the assembled request and proceeds automatically if it
fits. If compaction is unavailable or insufficient, the TUI reports estimated
total, available budget and overage before sending the conversational request.
The draft and caret remain in the editor and attached files remain selected;
the failed attempt does not create a conversation turn, editor-recall entry or
new latest-prompt pin. The user edits the draft or removes a file and submits
again. Compaction may have called its own model service and updated stored
memory, so the status must distinguish that work from the blocked prompt.
If a later agent-loop model request remains over budget, the inline exchange
shows an incomplete-turn notice and retains earlier tool activity; no further
conversational model request or tool runs for that turn. The incomplete turn and
Activity stay in the bounded current-run view only; they are not written as a
transcript entry (D-103). Earlier tool effects remain where they occurred.
If a request passed Friday's estimate but the provider rejects it for context
length, show a distinct provider-error notice and leave correction/retry to
the user (D-100). For the first request, restore the exact submitted prompt
and caret to an empty editor automatically (D-101). If the user typed a newer
draft while Friday was working, leave its text, caret and focus untouched and
show a clickable, keyboard-focusable `Restore failed prompt` action with the
error. If the bounded conversation evicts that error notice, keep a compact,
labeled Restore action beside the editor while the failed prompt remains
recoverable in this run (D-104). The action appears without moving editor
focus and is absent when no failed prompt is recoverable. Activating it uses
the D-41 Confirm/Cancel prompt before replacing a nonempty draft: Cancel keeps
the newer text and caret, while Confirm restores the exact failed text and
caret for editing. It does not submit or change attachments. Attachment
snapshots remain active. After earlier tool calls, mark the exchange incomplete
and keep their Activity visible in this run without a transcript entry (D-103).
The TUI does not automatically compact or resend after this post-send error.
For a failed first request, the error and prompt recovery exist only in the
current TUI run; no failed-attempt transcript entry is written (D-102). A
corrected submission is a new attempt. If the user instead submits a different
conversational prompt, the older Restore action
stays available while that turn runs. Only when Friday reports the newer turn
completed successfully does the TUI discard the older failed prompt and
remove Restore from the editor and any retained error notice (D-106). The
older error text may remain in the bounded conversation without an action;
acceptance, partial output or a failed newer turn alone does not clear recovery.
If a second initial request also fails for context length before the first is
resolved, retain both recoverable prompts and show one
`Restore failed prompts (N)` control beside the editor (D-107). Its chooser
lists distinct pending prompts newest first and accepts pointer or keyboard
selection. Retained error notices have no separate Restore controls in this
multiple-prompt state. Opening, navigating and canceling the chooser leave any
newer draft text and caret unchanged; closing it returns focus predictably.
Selecting a failed prompt uses the existing Confirm/Cancel protection before
replacing a nonempty editor
and never submits automatically. A single pending prompt uses the singular
Restore label, and no pending prompt shows no Restore control. Confirming
Restore keeps the original pending entry and count unchanged while placing an
editable copy in the editor (D-108). Later edits or replacement of that copy
do not change the recoverable original; the user may restore it again. A
successful conversational turn clears all earlier pending recoveries. The
user can also choose `Dismiss` for an individual failed prompt (D-109). With
one pending prompt, Dismiss appears beside Restore at its current placement; with multiple, each chooser
entry offers Dismiss. Confirm removes only the chosen recovery snapshot, while
Cancel leaves it available. The count and Restore label update immediately;
removing the last entry removes the controls. Confirmation leaves the editor
draft and caret, including any restored copy, and active attachments unchanged.
An older error notice may remain visible without a recovery action. Closing
the confirmation returns focus predictably; neither path sends a request.
Friday processes one accepted operation at a time. While it is working, the
user may keep editing a new draft, scroll through earlier output, use Help or
inspect Context. A submit attempt during that time shows a brief busy message
and keeps the draft unchanged; it does not queue another operation. This rule
also applies to `/q` and `/quit`. Ctrl+Q or the Quit control remains available
to request a safe exit during work.

Editor history is a separate action. It includes accepted conversational
prompts and submitted `/` commands in the running TUI (D-71), plus accepted
`@agent` messages and enabled, admitted `!` commands (D-75). Disabled or
rejected routes are not added. Recalling an entry fills the editor for review
or editing and never runs it. These recall
entries are in-process only and start empty on a new TUI launch (D-72),
independent of persisted transcripts. If browsing starts with an unsent draft,
keep its text and editing position and restore both when the user leaves
history without submitting a recalled entry (D-73). Browsed entries are
editable copies, not changes to submitted history. With no inline suggestion
list open, `Up` at the editor's upper caret boundary moves to an older entry;
while browsing, `Down` at the lower boundary moves newer and eventually
restores the saved draft (D-74). Elsewhere, these keys move the multiline
caret. While slash suggestions are open, D-68's match navigation takes
priority. `F3`/`F4` are not history keys in the first release.
Under D-66, typing a leading `/` command automatically shows matching
suggestions as the command name changes, drawn from the TUI's active command
registry, including aliases. Displaying suggestions leaves the editor draft
untouched and does not run a command; `Enter` still submits the draft under
D-38. Under D-67, selecting an inline suggestion completes its command-name
or alias token in the current draft, preserves any following argument text and
keeps editor focus; the user submits separately. Keyboard selection uses
`Up`/`Down` to highlight and `Tab` to insert while suggestions are open
(D-68). `Enter` still submits; with no suggestion list open, `Tab` moves focus.
After a recognized command and a space, the same list offers declared
subcommands as the next token is typed (D-69); for example, `/workflow r` can
suggest `run`. Selection completes only that subcommand token without running
the command or changing later arguments. Free-form values are not suggested.
Once a command or subcommand is recognized, show a short, display-only usage
hint for its expected arguments from active TUI metadata (D-70); for example,
`/workflow run` can show `<name> [key=value ...]`. The hint changes with the
recognized syntax and never fills values or starts a command.
Pointer and dismissal controls remain technical UI contract work. Help and the
command palette show names, aliases, purpose and usage. Choosing a `/` command
from the palette places its command text in the editor and focuses it for
review and argument entry; it never runs merely because it was selected.
`Enter` or the Submit control then uses the same
admission path as a typed command. If the editor already holds an unsent draft,
ask before replacing it. Cancel leaves that draft unchanged; confirm fills the
editor with the chosen command without submitting it. With an empty editor,
fill it directly. No command requires a menu to be usable.

## How Friday responds

The maintainer selected one chronological timeline for the conversation and
command results. A normal question shows a labeled user entry followed
by one Friday response entry. When the runtime streams text, that response
grows in place and remains a single item after completion. If a service only
returns a final answer, the final entry appears when ready. Markdown and code
should stay readable and selectable; tool output and filenames remain literal
data. Users may select and copy visible Activity entries and provider reasoning
shown by the current view setting. An oversized tool argument contributes
only its displayed preview and truncation notice to a copy operation; its
discarded overflow and reasoning received while hidden are unavailable.

During the latest exchange, keep its prompt visible above the response as the
response scrolls. This pinned view does not create another history entry, send
the prompt to the model again or change export contents. Hide the pin while
the user browses older exchanges; new output does not move that viewport.
`Jump to latest` returns to the bottom and restores the latest prompt with its
response. `/cls` and `/clearscreen` clear the displayed timeline,
pin and Activity view; the pin stays empty until the next accepted
conversational prompt. Session history and persisted transcripts remain
available. If a failed first prompt is still recoverable, display clearing
removes its error notice but keeps `Restore failed prompt` beside the editor
for this run (D-105). The action remains keyboard- and pointer-accessible and
does not submit the prompt. Returning to the bottom by scrolling also restores
the pin when one exists and resumes following new output. Verify both return
paths in UAT.

User prompts and Friday responses must be color coded with different, consistent
role accents. Apply the color to a speaker label and/or a narrow border or
background cue; keep body text, Markdown and code readable. Use explicit
`You`/configured user and `Friday`/configured assistant labels and distinct
spacing or borders as additional cues. Command results have their own labeled
visual treatment; warnings and errors use semantic warning/error styles rather
than being mistaken for either speaker. The actual palettes must work in dark,
light and high-contrast modes and be tested in terminals with different color
capabilities. Root presentation styles and `tui.appearance` settings influence
the TUI mapping without changing CLI rendering.

A slash command shows a labeled result in that timeline, with structured
success, warning or error presentation as appropriate. The TUI may use tables
or compact cards for clarity while keeping the command's arguments, effects,
errors and state equivalent to `friday-chat`. High-impact commands must make
their effect clear, especially display clearing (`/cls`), session
history clearing (`/clear`) and persistent-store reset (`/reset`). Progress
appears as a concise working state and, where useful, an in-order activity
entry. Repeated stream chunks do not become separate completed messages.

The requested [tool-activity log](tool-activity-requirement.md) sits within
the same exchange or user-entered tool-command entry, ahead of its final
answer or command result. It has no persistent side pane. It shows each tool
that actually starts, its actor, parameter values and execution status across
successive model steps, without TUI-specific credential filtering. Oversized
values have a
visible truncation notice and no retained full copy in the TUI. This includes
manual `/run-tool`, delegated-agent and workflow calls. An actual model or user
request rejected before invocation is labeled `Not run` with the reason and
must not be styled or counted as an executed call. A tool excluded before it
is requested creates no Activity entry. Automatic tool-result payloads stay
out of Activity and scrolling chat; `/run-tool` keeps its inline command
result. Keep the activity section scrollable or collapsible so a long agentic
loop does not bury the final answer. Open it automatically when its first
entry arrives; once a user collapses it, later entries accumulate without
reopening it.
Keep a visible control to reopen the retained log and show a count of new
entries while collapsed. Count an appended entry once, not a status update
to one already shown. Reopening or clearing Activity resets the count;
eviction while collapsed adds a header indicator, with detail on reopen.
Auto-opening does not steal editor focus or scroll a user away from older
conversation. If the provider supplies reasoning during a later model step,
show it in sequence
as a separately labeled Friday reasoning entry only when reasoning display
is enabled.

When expanded Activity is at its own bottom, it follows newly added entries.
Scrolling up pauses that following while later entries accumulate. Show a
clickable and keyboard-focusable `Jump to latest Activity` control while away
from the Activity bottom; activating it or scrolling to the bottom resumes
following. The conversation's `Jump to latest` is a separate control with
no effect on the Activity viewport, and the Activity control does not move
the conversation or change the latest-prompt pin.

Each inline Activity section keeps its chosen expanded or collapsed state
when a new conversational prompt is accepted. The new exchange's section
opens independently on its first entry; older sections do not collapse
automatically and remain inspectable while retained in the bounded view.

The status line shows what is happening now: for example Ready, Generating,
Running `/ingest`, Quit requested, Cleaning up or Cleanup failed. It must use
typed TUI state or UI-neutral runtime signals, never guesses from formatted
Chat text. A startup or cleanup failure remains readable until the user
acknowledges it; the terminal is released only after owned work has stopped.

The first-release [reasoning display option](reasoning-display-requirement.md)
can show provider-exposed thinking text in separately labeled, collapsible
entries within the Activity view, including later model steps after tools run.
The default view shows the final answer and tool-call status without reasoning
text. A discoverable in-app toggle affects subsequent reasoning events without
rewriting the config file or revealing earlier hidden text. This display choice does not control whether the model generates
reasoning and must not change the existing CLI's output.

## Scrolling and overlays

- The conversation scrolls independently of the editor and sidebar. It follows
  new output only while the reader is at the bottom. If the user scrolls up,
  new output does not pull the view away. The latest-prompt pin remains while
  reading its own response but hides when older exchanges enter view. A
  visible, clickable and keyboard-focusable `Jump to latest` control appears
  at the lower edge of the conversation without covering its text. Activating
  it returns to the bottom, restores the pin when available and resumes
  automatic following. Scrolling back to the bottom has the same effect.
- A long draft scrolls inside the editor without moving conversation history.
  The editor remains usable while Friday is busy.
- The sidebar scrolls only when focused and its contents exceed its height.
  Hiding it gives that space to the conversation.
- Help, command discovery, the command palette, config selection and detailed
  errors open as focused overlays or views with their own scrolling and a
  visible close/back action. Dismissing one returns focus to the prior control
  and does not cancel backend work.
- Rendered conversation history and any single oversized result have visible
  limits so memory use stays bounded. When older conversation messages are
  evicted, show a clear notice directing the user to `/transcript` if they
  were saved; if no saved transcript is available, say so. The first release
  has no `Load older` control. UI trimming must not delete persisted memory or
  transcripts. The notice must not promise recovery of transient Activity or
  provider reasoning. A truncated tool parameter is not recoverable from TUI
  Activity, though the tool received the complete value. The exact per-entry
  and total limits belong in the replacement technical contract.

## Narrow and small terminals

At widths below about 100 columns, collapse the sidebar and keep its contents
reachable from a Context action or command palette. The conversation and
editor use the full width. At the proposed minimum 80x24 size, show the
conversation, a shorter internally scrolling editor, visible Submit/Quit
fallbacks and concise status. Inline Activity remains collapsible and
internally scrollable so it does not take the entire conversation area.
If the terminal is smaller, show a resize hint
while keeping a safe Quit path reachable. Do not hide a running operation or
release the terminal before cleanup merely because it was resized.

## Interaction defaults and validation

The accepted editor keys are `Enter` Submit and `Ctrl+Enter` Insert newline.
With inline `/` suggestions open, `Up`/`Down` highlight and `Tab` inserts a
highlighted suggestion without submitting; without suggestions, `Tab` moves
focus (D-68). A list with no highlighted match cannot use `Tab` to insert.
When suggestions are closed, `Up` at the editor's upper boundary browses
older history, while `Down` at the lower boundary browses newer history only
when already browsing. Interior `Up`/`Down` move the caret (D-74).
The remaining proposed keys are `F1` Help,
`Ctrl+P` command palette, `Ctrl+L` as a shortcut for the accepted `/cls`
display effect, `Ctrl+Q` safe Quit,
`Shift+Tab` reverse focus navigation and `Escape` dismiss overlay. The TUI
must support copying selected visible text, including Activity and shown
reasoning. `Ctrl+C` is the proposed copy binding where the terminal delivers
it; a focusable copy fallback is required. It is not the TUI Quit key. These are
proposals, not finalized key-delivery claims. Test actual behavior in macOS and
Linux terminals and keep focusable fallbacks for essential actions, especially
newline insertion where `Ctrl+Enter` is indistinguishable from `Enter`. The
Insert newline control is the accepted fallback; there is no second default
newline key.
Dark/light, high-contrast and reduced-motion choices affect presentation; role
labels and status remain
meaningful without color.

The [replacement build/test plan](replacement-plan.md) should verify prompt admission, retained busy
drafts, a pinned latest prompt while a long response scrolls, long-prompt
expansion, pin retained while reading its response and hidden in older
exchanges, mouse and keyboard
`Jump to latest`, return-by-scrolling and resumed following, no duplicate
transcript/export or model input,
an older-message eviction notice with saved and unavailable transcript cases,
one in-place streamed response, an ordered multi-step tool-activity log that
shows execution status without tool output, provider reasoning in sequence
when enabled, manual/delegated tool calls, `Not run` reasons, the `/run-tool`
result exception, `/cls`/`/clearscreen` display clearing with preserved
session history, normal and confirmed Force quit, command results/errors, independent
scroll positions, Jump to latest, sidebar collapse, focus order, resize,
configuration effects, role color distinction in dark/light/high-contrast
themes, color-independent labels, failure visibility and safe Quit. The eventual
[user guide](user-guide-requirements.md) must describe the behavior that ships.

The maintainer selected inline command results and distinct role colors. Exact
accent hues, widget spacing, keyboard defaults and terminal behavior remain
construction/UAT details.

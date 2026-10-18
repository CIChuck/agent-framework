# Friday TUI startup bootstrap contract

**Status:** Draft technical contract for review; product decisions D-47 through
D-65 are accepted, but this document does not grant construction authority.

**Branch and authority:** `feature/friday-tui`; `design_only`

**Source baseline:** `c34269867be50f71923c93c95a63236a35505812`

This contract consolidates the accepted [startup decisions](decisions.md) into
one testable path for the independent TUI. The [replacement plan](replacement-plan.md)
still controls unit order. `friday-tui` must not import or depend on
`friday-chat` or `friday-cli`; Chat source and tests below are behavior evidence,
not implementation dependencies. The existing CLI packages keep their current
startup defaults and behavior.

## Entry and configuration ownership

- `--version` and installed help do not create a runtime. Startup replay retains
  the current version/replay/configured-start precedence. D-62 fixes its
  successful completion view, D-63 fixes its summary-only content, D-64
  fixes its persistent error view and nonzero exit, and D-65 excludes Retry.
- Capture the process launch working directory once before showing the chooser
  or constructing services. Existing runtime file, model-library reference,
  environment and relative data-path meanings must match Chat under the same
  launch context. The [neutral loader proposal](neutral-config-loader-contract.md)
  covers file loading; service assembly and close ownership still need their
  own contracts.
- With explicit `--config`, bypass candidate discovery and the chooser. Without
  it, list likely runtime files directly in the captured launch directory and
  let the user select one or Browse to an existing file elsewhere. Browse
  supports folder navigation and typed or pasted absolute, relative, and `~`
  home paths. A relative Browse path resolves from its currently displayed
  folder, initially the captured launch directory. Do not scan a user
  home/config directory or recurse automatically. Do not create or rewrite
  files.
- For configured interactive startup, omitted `--runtime` means `real` in TUI;
  `--runtime fake` is explicit test mode. Chat's present fake default remains
  unchanged. `FRIDAY_CHAT_RUNTIME` stays Chat-only and never changes the TUI's
  mode (D-61); there is no first-release TUI mode environment override. A
  real failure never silently changes modes. Runtime YAML interpolation and
  credential lookup still use their normal environment values.

## Startup replay result

With `--replay FILE`, run the replay as a separate fake operation before any
configured interactive startup, using the compatible `--replay-delay`
semantics. Do not show the configuration chooser, load `--config` for a real
session, or let `--runtime` change this replay path. After successful replay,
show a read-only result screen with the input file and processed-turn count as
the replay data; do not show a browsable turn-by-turn record in the first
release (D-63). It remains open until the user chooses Quit (D-62). No prompt
editor, slash-command admission or automatic transition to a configured
session is available from that screen. The TUI must use a UI-neutral replay
service without importing Chat's current `ReplayService`. A separate directive
must bind neutral error categories and resource cleanup.

If the replay file is missing or invalid, the delay is invalid, or replay
processing fails, show a read-only error screen with the file and an actionable
error (D-64). Keep it visible until Quit, then exit nonzero. Do not silently
retry, open the configuration chooser, enter an interactive session or show the
success count. Offer Quit only, without an in-process Retry; the user corrects
the cause and relaunches (D-65). Any partially started replay resources still
need the neutral close contract.

## Candidate discovery

**Accepted approach (D-48, D-49, D-55):** Shallow, read-only inspection of
top-level YAML content identifies likely runtime files regardless of basename.
Recognized model-library and CLI presentation files stay out of the initial
list. This inspection never interpolates environment values, resolves
credentials, opens a referenced model library, fully validates runtime config,
or starts services. Browse can select an unrecognized file for full validation.
Under D-57, an incomplete but recognizable runtime-shaped file remains in the
initial list. Its missing setting is reported only when the user selects it.
Under D-59, a visible keyboard-focusable Refresh action reruns this same check
for the captured launch directory on demand. The list stays as shown until
Refresh is activated; there is no filesystem watcher or automatic wider search.
Refresh never performs full validation or starts services. A selected-path
Retry under D-50 rereads that path without requiring a list Refresh.
Under D-60, a direct-child `.yaml` or `.yml` symbolic link may be listed when
it resolves to a readable regular runtime-shaped file, even if its target is
outside the launch folder. This reads only that explicitly linked file for
candidate classification; it does not scan the target's directory. A broken,
cyclic, unreadable, directory-target or unrelated link is omitted from the
automatic list but can still be entered through Browse and receive D-50
error handling.

**Proposed signature for the bootstrap directive:** Consider direct-child
`.yaml` and `.yml` regular files and D-60 symbolic links in the captured
launch directory. A mapping with a top-level `llm`, `model_library`, `llm_pool`
or `embedding_pool` key is a likely runtime candidate. Exclude a recognized
`schema: friday.model-library/v1`
catalog and files whose only recognized fields are presentation fields such as
`theme`, `icons` or `banner`. A filename alone never makes a file a candidate.
Malformed, unreadable, non-mapping and unrelated YAML are not auto-listed but
remain available through Browse and then follow the selected-file error path.
The final key signature, parser size/depth bounds, link-resolution safeguards
and filesystem error handling must be bound and reviewed in the TUI bootstrap
directive.

This proposed signature comes from the current
[`FridayChatConfig` shape](../../../../packages/friday-chat/src/friday_chat/config.py)
and the packaged [runtime](../../../../packages/friday-chat/config.example.yaml),
[model-library](../../../../packages/friday-chat/models-config.example.yaml)
and [presentation](../../../../packages/friday-chat/cli-config.example.yaml)
examples. It is a discovery heuristic, not a substitute for the compatible
UI-neutral loader's full validation. D-57 requires incomplete runtime-shaped
files to remain visible and then use the D-50 validation error when selected.

## Observable startup outcomes

| Entry and result | Required behavior |
| --- | --- |
| No `--config`, at least one candidate | Show the chooser. Selection invokes full validation; Browse permits folder navigation or typed/pasted paths to another existing file. Listing itself does not start Friday. |
| Browse path entry | Accept absolute, relative and home-shorthand paths, including a file outside the launch folder. Resolve relative entry from the displayed Browse folder and `~` from the user's home; apply full validation and D-50 recovery to the selected file. No automatic search or file creation (D-58). |
| Incomplete but recognizable runtime YAML | Include it in the initial list. Selection runs full validation and, if invalid, follows D-50; do not silently hide it (D-57). |
| No `--config`, no candidates | Keep the chooser open with a clear message, Refresh, Browse and Quit (D-52, D-59). |
| Refresh while chooser is open | Rescan only the captured launch folder on activation. Add newly recognizable candidates, remove ineligible ones and update the empty message; offer Browse and Quit throughout. No automatic watcher, full validation or runtime start (D-59). |
| Linked runtime file in launch folder | List a `.yaml` or `.yml` link resolving to a readable regular runtime-shaped file, including an outside-folder target. Omit broken, cyclic, unreadable, directory-target and non-runtime links from the automatic list; keep Browse and D-50 error handling available (D-60). |
| Chosen file fails validation | Keep the chooser open with the error, Retry of the same path, Browse and Quit (D-50). Retry rereads the file. |
| Explicit `--config` file fails validation | Report the error and exit nonzero; no chooser or runtime start (D-51). |
| Valid chosen file, selected runtime starts | Enter the TUI using the selected config; real is the default and fake requires an explicit flag (D-47). |
| `FRIDAY_CHAT_RUNTIME` is set during TUI launch | Ignore it for TUI mode selection. Omitted TUI `--runtime` remains real; explicit TUI `--runtime fake` remains fake, even when the Chat variable is set to `real`, `fake` or an invalid value (D-61). Configuration-value environment lookup is unaffected. |
| Successful startup `--replay FILE` | Run an isolated fake replay before configured startup, then show a read-only result with file and processed-turn count until Quit. No first-release turn-by-turn list. Do not show a chooser, admit prompts or commands, auto-exit or enter a configured session (D-62, D-63). |
| Failed startup `--replay FILE` | Show the file and actionable error in a read-only view until Quit, then exit nonzero. Offer no in-process Retry, chooser, interactive session or success count; correct the cause and relaunch (D-64, D-65). |
| Valid chosen file, real startup fails, cleanup succeeds | Show the startup error and return to the chooser with Retry of the same file, Browse and Quit (D-53). No fake fallback. |
| Valid chosen file, real startup and cleanup fail | Report both failures, restore the terminal as far as possible and exit nonzero. Do not offer in-process Retry or Browse (D-56). |
| Valid explicit `--config`, real startup fails | Close partial services, report startup and any cleanup failure, and exit nonzero without a chooser or fake fallback (D-54). |

The TUI owns resources it creates. A partial-start failure must retain the
original startup error while teardown runs; teardown errors must not overwrite
it. A return to the chooser is allowed only after cleanup succeeds. The exact
neutral resource-close interface, teardown order and terminal recovery
mechanism remain construction-contract work.

## Testable bootstrap slice

The first bootstrap directive should bind disposable fixtures and assertions
for these groups before code generation:

1. Candidate inventory: canonical and legacy runtime YAML with default and
   custom basenames; incomplete `llm:` with no model; recognized model library,
   presentation-only, unrelated, malformed and unreadable YAML; direct-child
   links to in-folder and outside-folder runtime files, plus broken, cyclic,
   unreadable, directory-target and non-runtime links; empty and mixed
   launch directories; Browse by folder navigation and typed/pasted absolute,
   relative and `~` paths to files inside and outside the launch directory.
   Check relative resolution before and after navigating folders, home
   expansion, missing/unreadable targets and D-50 recovery. Check Refresh
   from empty to populated and populated to empty, reclassification after a
   content change, unchanged list before activation, and no automatic watcher.
   Assert no service construction, credential resolution, referenced-file read
   or filesystem mutation during listing or Refresh. Keep this test distinct
   from full config validation.
2. Validation and selection: selected invalid file then corrected Retry,
   Browse to a second file, empty-list recovery, explicit valid/invalid paths,
   and unchanged model-library/path/environment interpretation versus Chat.
3. Modes and failures: real default through both selection routes, explicit
   fake, and TUI mode unaffected by `FRIDAY_CHAT_RUNTIME` values `real`, `fake`
   or invalid. Verify Chat's current environment override separately. Check
   no fake fallback, partial-start cleanup success and failure through both
   routes, both errors retained, nonzero exit and terminal restoration.
4. Startup replay: `--version` wins when both flags are present; otherwise
   `--replay FILE` bypasses config discovery, configuration loading and mode
   selection. Check zero and multiple turns, delay parsing/spacing, a
   read-only file/count result view that remains until Quit, no prompt or
   command admission, no browsable per-turn record, and no automatic
   transition. For missing/invalid CSV, invalid delay and a processing
   exception, check a read-only file/error screen until Quit and nonzero exit,
   without Retry, chooser or interactive session. Verify Quit and relaunch
   after correction. Compare the replay effect and error categories with Chat
   through a neutral service; resource-close details still need their own
   contract.
5. Independence and regressions: installed TUI dependency/import closure has
   no Chat/CLI code, while both existing CLI applications retain their
   baseline startup behavior with and without TUI installed. Automated Linux
   checks run during construction; physical macOS and final-candidate Linux
   terminal UAT follow the [UAT plan](replacement-plan.md#4-verification-and-uat-gates).

**Not yet bound:** review and final binding of the proposed
[UI-neutral loader API](neutral-config-loader-contract.md), plus service
assembly owner; exact
candidate key/parser bounds, link-resolution safeguards and path error text;
startup replay error/cleanup categories; partial resource
ownership and terminal teardown details;
real-provider UAT fixture.
These are review items before an exact construction directive. No product
tests or user UAT have been run for this planning contract.

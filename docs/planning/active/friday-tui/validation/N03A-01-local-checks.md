# TUI-N03A-01 local construction checks

**Branch:** `feature/friday-tui`.
**Authority:** [CD-TUI-N03A-01](../directives/CD-TUI-N03A-01-installable-shell.md),
approved by Chuck Russell on 2026-10-19 for local package construction.
**Status:** Builder evidence before independent validation. This is an
installable development shell, not a working Friday conversation or accepted
first-release TUI.

## Scope and behavior

The new `friday-tui` package supplies its own `friday-tui` and
`python -m friday_tui` entry points. `--help`, `--version` and unknown-option
handling complete before importing Textual or runtime services. The shell
contains a fixed header, Context placeholder, scrollable conversation area,
multiline editor, Submit, Insert newline, Help, Quit and status. It does not
load Friday configuration, start runtime services, send a prompt, write a
transcript or import Friday Chat/CLI. An attempted Submit preserves the draft
and caret and reports the unavailable runtime connection.

## Automated and installed checks

- `uv run --package friday-tui pytest packages/friday-tui/tests_tui -q`:
  **11 passed**. Headless Textual interaction checks cover 80×24 and 120×30
  geometry, focus, scrolling, Enter, distinct Ctrl+Enter, keyboard and pointer
  actions, paste, empty draft, Help, resize and Quit. Synthetic keys do not
  establish what a physical terminal transmits.
- `uv run ruff check packages/friday-tui` and `uv run ruff format --check
  packages/friday-tui`: pass after formatting. `uv run mypy
  packages/friday-tui/src`: pass, four source files.
- `uv run pytest packages/friday-cli/tests_cli -q`: **155 passed**.
  The selected Chat CLI/config/lifecycle suites: **50 passed**.
- `uv lock --check --offline` with the disposable
  `/private/tmp/friday_tui_n03a01_uv_cache`: **218 packages resolved**.
  Package-identity comparison against the previous lock found no removed or
  upgraded existing package. The five additions are `friday-tui`, `textual
  8.2.8`, `linkify-it-py`, `mdit-py-plugins` and `platformdirs`. The lock also
  normalizes one existing runtime metadata ordering and records
  `markdown-it-py`'s linkify extra needed by Textual.
- `uv build packages/friday-tui`: wheel and sdist built. Archive inspection
  confirms `styles.tcss` in both, version `0.1.0a4`, Python `>=3.13.4`, the
  documentation URL, the console script, and only Runtime and Textual direct
  requirements.
- The built wheel installed into a fresh `/private/tmp` Python 3.13.10
  environment outside the checkout. Installed `--help`, `--version`, module
  version, a headless shell/quit probe, resource lookup and no-Chat/CLI import
  checks passed. `uv pip check` passed for **116 installed packages**.
- The installed console script and `python -m friday_tui` each opened in a
  macOS PTY and exited with status 0 on Ctrl+Q. The console script displayed
  the 80×24 zones and controls. Typing `smoke prompt` then Enter left the
  draft visible and changed status to “Runtime connection pending. Draft kept
  for editing.” A bracketed multiline paste added a second line without a
  new submission. Exit emitted terminal-mode reset and alternate-screen
  teardown sequences.

## Open terminal UAT

The computer-use surface denied direct macOS Terminal control. Cursor's
integrated terminal was visible but control failed with stale-window and
screen-capture errors. The PTY check above is useful terminal smoke evidence,
but it does not verify physical Ctrl+Enter delivery, mouse operation, live
terminal resizing or a human visual/readability assessment. The
[directive](../directives/CD-TUI-N03A-01-installable-shell.md) requires those
observations before the bounded shell milestone can be claimed complete.
Hands-on Linux UAT and runtime/command behavior remain later gates. There is
no authorization for a push, PR, merge or release.

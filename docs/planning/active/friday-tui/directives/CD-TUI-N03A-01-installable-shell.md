# CD-TUI-N03A-01: installable Friday TUI shell

**Status:** Approved by Chuck Russell on 2026-10-19 for exact local construction
by current-session reply “approved” to the linked directive. Independent
validation and terminal UAT remain open; no push or release is authorized.
**Initiative/unit:** `friday-tui` / TUI-N03A-01.
**Branch and planning source:** `feature/friday-tui` at
`adfb92e6b100bda46a4215183f4942b947b0460c`. Recheck source, board,
package state and dependency resolution before implementation.

## Authority and purpose

Apply explicit maintainer direction, the
[repository engineering policy](../../../../reference/policies/repository-engineering-policy.md)
and [independent validation policy](../../../../reference/policies/independent-validation-policy.md),
[AGENTS.md](../../../../../AGENTS.md), [accepted TUI decisions](../decisions.md),
[requirements](../README.md), [replacement plan](../replacement-plan.md),
[screen layout](../screen-layout.md), and
[before-code characterization](../validation/N03A-01-before-code-shell-characterization.md).
If these conflict, stop and reconcile before editing. This directive pulls the first visible package
subunit of TUI-N03A forward; the rest of N03A, N01C runtime assembly, N03B
backend bridge and all first-release command parity remain later units.

Deliver an independently installable `friday-tui` package and executable
with a genuine Textual screen shell. The shell is a development milestone,
not a working Friday conversation or first-release TUI. It provides a stable
place to build and test UI behavior while neutral runtime integration follows.

## Exact local change boundary

Only these product, test and dependency paths may change:

1. `packages/friday-tui/pyproject.toml` and `packages/friday-tui/README.md`.
2. `packages/friday-tui/src/friday_tui/__init__.py`, `__main__.py`, `cli.py`,
   `app.py`, and `styles.tcss`.
3. `packages/friday-tui/tests_tui/test_cli.py` and `test_shell.py`.
4. `uv.lock`, solely for the new workspace package and its resolved Textual
   closure.

Scoped TUI planning/evidence, the `friday-tui` board task/event and generated
dashboard may be updated. Do not edit root `pyproject.toml`, any existing
package source/test/metadata, workflows, scripts or user guides in this unit.
The root workspace already includes `packages/*`. If an additional path or
dependency change is genuinely needed, stop for an amended directive and
approval before editing it.

## Package and behavior contract

- Package name and console script are `friday-tui`; import package is
  `friday_tui`. Match the workspace `0.1.0a4` version, Python `>=3.13.4`,
  documentation URL `https://gendevx.com/friday/`, and existing Hatch package
  conventions. Include the Textual stylesheet in wheel and sdist artifacts.
- Depend on `friday-framework-runtime==0.1.0a4` and
  `textual>=8.2.8,<8.3` without the optional syntax extra. Pin the resolved
  Textual version in `uv.lock`. Do not depend on or import `friday-chat`,
  `friday-framework-cli`/`friday_cli`, or the umbrella
  `friday-framework` package. Keep existing CLI dependency graphs and
  entry points unchanged. Current [PyPI Textual metadata](https://pypi.org/project/textual/)
  declares Python 3.13 support; prove the actual lock and installed closure.
- `friday-tui --help` and `--version` exit successfully without constructing
  a Textual app, loading YAML, resolving credentials or starting Runtime.
  Unknown arguments fail clearly and do not start services. `python -m
  friday_tui` and the installed console script use the same launcher.
- A normal `friday-tui` launch opens the development shell. Show a fixed
  header, a clearly labeled Context sidebar placeholder, a scrollable
  conversation region, a multiline editor, visible focusable Submit and
  Insert newline actions, Help and Quit controls, and a status area. At
  80x24, the editor and controls remain usable; at a wider size, the zones
  follow the accepted [screen layout](../screen-layout.md). Distinguish
  labeled user/Friday roles without relying on color alone. No fabricated
  conversation, transcript or tool activity is shown.
- `Enter` attempts to submit the complete editor draft once; `Ctrl+Enter`
  inserts one newline without submission when the terminal delivers a
  distinct event. Multiline paste never submits. Both visible actions are
  keyboard and pointer operable. Empty/whitespace-only drafts do not submit.
  The shell has no connected Friday runtime yet: a nonempty Submit leaves
  draft text and caret intact and reports that runtime connection is pending.
  A narrow test injection seam may count admission attempts, but no
  production fake answer, provider call, transcript write or CLI handler is
  permitted. Do not describe this milestone as conversational parity.
- Help identifies only shipped shell controls and the preview limitation.
  Quit and Ctrl+Q close this no-backend shell and restore the terminal. The
  full safe-stop/Force-quit contract is later N03B/N06 work; do not claim it
  here. No runtime config chooser, `--config`, `--runtime`, `--replay`, slash
  command registry, attachment, Activity, reasoning view or persistence is
  introduced by this unit.
- The package README must plainly describe this development milestone and
  its limits, installation from a local wheel, launch/help/version, editor
  controls and Quit. The completed user-oriented `docs/guides/20-tui.md` and
  `docs/guides/10-configuration.md` update follow actual implemented
  features; do not publish a guide implying working prompts at this stage.

## Required verification

1. Package tests cover no-service `--help`/`--version`, unknown options,
   module and installed-script entry points, and no Chat/CLI imports.
2. Textual [headless run_test/Pilot](https://textual.textualize.io/guide/testing/)
   tests at 80x24 and a wider size cover all zones and focusable actions,
   editor wrapping/caret retention, one Submit attempt per Enter/click,
   exactly one newline for distinct Ctrl+Enter or Insert newline, multiline
   paste without submission, empty draft, no-backend status with unchanged
   draft, Help, resize and Quit. These are meaningful interaction tests,
   not snapshots of source constants. Simulated keys do not prove physical
   terminal key delivery.
3. Focused Ruff/Mypy and package tests pass. Re-run the protected full
   `friday-cli` suite and the Chat CLI/config/lifecycle tests. Inspect the
   lock diff for unexpected upgrades or dependency changes in existing
   packages; resolve any conflict without altering CLI behavior.
4. Build wheel and sdist, inspect metadata/resources, and install the wheel
   in a disposable Python 3.13 environment outside the checkout. Run
   `--help`, `--version`, module launch and a shell/quit smoke probe there.
   Inspect installed dependencies/imports to prove no Chat/CLI package
   requirement or import and run `uv pip check`. Keep local state and
   credentials out of artifacts.
5. Record a macOS terminal smoke/UAT observation of visible layout, focus,
   Enter, Ctrl+Enter as physically delivered, Insert newline fallback,
   paste, resize and Quit before claiming the shell milestone complete.
   Linux automation may follow a separately authorized push; hands-on Linux
   UAT remains a later release gate. Record limitations rather than claiming
   physical key behavior from headless tests alone.
6. Freeze a stable candidate commit and obtain fresh-context, read-only
   independent validation with exact authority and diff. `VERIFIED` closes
   this bounded shell only. No push, PR, merge, release or initiative
   acceptance is implied.

## Stop conditions

Stop if Textual cannot resolve for the supported Python/platforms without
changing existing CLI dependencies or behavior; if the new installed package
imports or requires Chat/CLI; if the shell needs runtime assembly, existing
package edits or a new file outside the allowlist; if Submit cannot preserve
an unadmitted draft; if Enter and newline actions cannot be distinguished in
headless tests; or if a terminal failure leaves the screen unusable. Record
the issue and request a bounded directive amendment. Do not turn this shell
unit into another neutral transcript extraction or claim a working Friday
conversation before the N01C/N03B integration gates.

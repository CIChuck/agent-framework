# CD-TUI-CI01: Linux verification on GitHub Actions

**Status:** Approved for TUI-CI01 construction on 2026-10-18 by Chuck Russell.

**Initiative/unit:** `friday-tui` / TUI-CI01

**Branch/source baseline:** `feature/friday-tui` /
`d69c1d72fb841e4b3e51683ef16d7dcd4eac1f00`

**Current authority:** Granted for this exact CI workflow unit only. Chuck
Russell answered "approved" to the explicit TUI-CI01 scope question in the
current session. Remote push, pull request, merge, release and TUI product
work remain unauthorized.

## Purpose and observable result

Add an automated Ubuntu check for the already closed TUI-N01A neutral
configuration loader and protected Chat/`friday-cli` behavior. N01A was
independently verified under a maintainer waiver of its Linux smoke for that
unit's closeout only. A passing CI run supplies the deferred Linux evidence
for the later TUI cross-platform gate; it does not reopen N01A, establish
terminal user UAT or accept the full TUI.

## Exact implementation boundary after approval

- Add `.github/workflows/friday-tui-linux.yml` only. Permitted planning
  updates are this directive, `../authority.json`, `../README.md`,
  `../execution-log.md`, a TUI-CI01 local check record and independent report
  under `../validation/`, the TUI entry/events in `docs/planning/board.yaml`,
  and its generated `docs/planning/README.md` dashboard.
- Do not edit package source, tests, metadata, lockfile, Chat or CLI code, or
  create the TUI package under this unit. A test failure requiring one of
  those paths stops this unit for a separately scoped directive.
- Use GitHub-hosted `ubuntu-24.04` and a Python 3.13 patch meeting the
  repository's `>=3.13.4` requirement. Use full-commit-SHA-pinned checkout
  and uv setup actions, `permissions: contents: read`, and locked workspace
  dependency resolution. No provider credentials or release permissions are
  needed. Keep LiteLLM's cost map local for deterministic imports.
- Trigger on pushes to `feature/friday-tui` and pull requests into `master`.
  Do not use `pull_request_target`. Manual dispatch may be added after the
  workflow exists on the default branch; it is not the first-run path.

## Checks and evidence

1. Run `test_application_config.py` and `test_config_facade.py` on Ubuntu.
   Run the full Runtime, Chat and unchanged `friday-cli` test directories in
   separate pytest invocations so duplicate test module names do not collide.
   Tests use synthetic files/fake providers and do not require real secrets.
2. Build the Runtime and Chat wheels and their local Friday dependency
   closure. Install the Runtime wheel with its declared dependencies in a
   disposable environment outside the checkout. From outside the checkout,
   import `friday_runtime.application_config` and prove neither
   `friday_chat` nor `friday_cli` is installed or imported. Inspect the Runtime
   wheel metadata for direct Pydantic/PyYAML dependencies and no Chat/CLI
   dependency. Install Chat separately and prove its config facade exports
   the same model and error class objects. Run `uv pip check`.
3. Log the source commit, Ubuntu release, Python and uv versions, test results,
   wheel hashes and installed-import results. A green job on another commit
   does not establish this candidate's Linux result. Record the Actions run
   URL and any platform-specific failure in this packet. Do not mark a skipped
   or failing job as Linux coverage.
4. Check the workflow syntax and allowed-path diff locally; run board
   validation, dashboard check and `git diff --check`. Commit a stable CI
   candidate. After separately recorded delivery authorization, push that
   candidate to run Actions. Then obtain fresh-context, read-only independent
   review of the exact candidate and Linux run evidence before claiming this
   unit verified. Workflow approval alone does not authorize a push.

## Stop conditions and later gates

Stop and revise the directive if CI requires product or test edits, changes
Chat/`friday-cli` behavior, needs secrets or write permissions, or cannot
prove the installed Runtime import closure. Keep the previous N01A waived
closeout intact. A real Linux terminal session and guide-based user UAT remain
required on the final installed TUI candidate. Additional TUI construction
units, including TUI-N01B, require their own approved directives.

**Approval record:** Maintainer Chuck Russell; approved 2026-10-18 by the
current-session reply "approved" to the explicit TUI-CI01 directive question.
The approval covers only the workflow and scoped planning/evidence paths above.
Remote push authorization is a separate delivery decision.

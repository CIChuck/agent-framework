# TUI-CI01 local workflow checks

**Date/branch:** 2026-10-18; `feature/friday-tui`.

**State:** Local checks for the first candidate and its bounded preflight
remediation, followed by the locked MCP test-dependency correction. This
record is not an independent `VERIFIED` result, terminal UAT or TUI release
acceptance.

The only automation file added is
`.github/workflows/friday-tui-linux.yml`. It targets GitHub-hosted
`ubuntu-24.04` on TUI-branch pushes and `master` pull requests with a
read-only token, full-SHA-pinned actions, Python 3.13.4+ and locked uv
workspace installation. It uses no provider secret, publication token or
write permission. Runtime, Chat and CLI source/tests/metadata and `uv.lock`
are unchanged.

## Local verification

- Parsed the workflow with YAML BaseLoader. Checked the exact event set,
  runner, Bash shell, `contents: read`, full-SHA action references, every
  embedded Bash script with `bash -n` and every embedded Python block with
  `ast.parse`; all passed. The first-candidate independent reviewer found that
  syntax checks alone missed an invalid `runner.temp` job-level expression and
  missing PR source-SHA logging. See the retained
  [preflight review](VAL-TUI-CI01-preflight-7d97aacd.md) and the directive's
  `RD-TUI-CI01-01` remediation addendum. After correction, reran YAML parsing,
  `bash -n` on all nine `run` steps, Python AST parsing on all four embedded
  blocks, and explicit context-scope checks: no job-level `runner` expression;
  every wheel/venv consumer has step-level `runner.temp`; the source-SHA
  expression uses PR head with a push fallback; the version step prints both
  source and tested checkout SHAs. Executed the two log lines with a synthetic
  source SHA and checked both printed values. All passed. These are local
  checks, not an Actions run.
- On macOS Python 3.13.10, the focused neutral-loader/facade tests passed
  (**21**). Full Runtime passed (**334**) after permitting loopback for its
  synthetic HTTP tests; the sandbox-only attempt had nine localhost-bind
  `PermissionError` failures and 325 passes. Full Chat passed (**839**, five
  skipped, one existing deprecation warning). The unchanged `friday-cli`
  suite passed (**155**). These test directories run separately in CI to
  avoid existing duplicate test module names.
- Built the 11 local Runtime/Chat dependency-closure wheels offline. The
  Runtime wheel declares direct Pydantic and PyYAML dependencies and no
  Chat/CLI dependency. Ran the workflow's wheel metadata script against the
  built wheel successfully.
- Ran the workflow's installed-package script from outside the checkout in
  a disposable venv, using locally built Friday wheels and cached declared
  third-party dependencies. The Runtime-only environment passed `uv pip
  check` with **111** packages; `friday_chat` and `friday_cli` were neither
  installed nor importable, and the neutral module loaded from the venv.
  After local Chat/CLI/tool wheels were installed, `uv pip check` passed with
  **127** packages; the Chat facade loaded from the venv and exported the
  identical Runtime model and error objects. LiteLLM used its local cost map;
  no provider request or credential was used.
- `uv lock --check --offline`, board validation (**34 tasks**), dashboard
  check and `git diff --check` passed. The documentation lifecycle checker
  still reports the six pre-existing broken absolute links in the unrelated
  telemetry `VAL-001` report; it reported no new TUI links.

The package source, lockfile, focused/full test invocations, wheel build and
installed-import scripts were unchanged by `RD-TUI-CI01-01`. The full package
suites and wheel installation were not repeated after the workflow-only
correction. The new version-log command and environment placement need the
actual Ubuntu run before they count as platform evidence.

## Locked MCP test-dependency correction

The first pushed Ubuntu run failed while collecting the full Runtime suite
because its HTTP integration test imports `cryptography`, absent from the
root-only `dev` sync. See the [failed-run evidence](TUI-CI01-ubuntu-run-39172562601.md).
For `RD-TUI-CI01-02`, the workflow now selects both the workspace root and
`friday-framework-mcp` with `--extra dev` under `uv sync --locked`.

- `uv export --locked --offline` for those exact package/extra selections
  includes `mcp==2.3.0`, `cryptography==50.0.2` and
  `pytest-mock==3.15.1`. A locked/offline dry run against a fresh temporary
  project environment would install all three from the existing lock.
- YAML parsing, the job/step context-scope assertion, `bash -n` on all nine
  workflow `run` steps, and AST parsing of all four embedded Python blocks
  passed. The direct dependency-version print in the install step parses.
- `uv lock --check --offline`, board validation (34 tasks), dashboard check
  and `git diff --check` passed. No package code, tests, metadata or lockfile
  changed. A new Ubuntu run must execute every step before this unit can be
  verified.

## Remaining gate

The first authorized GitHub Actions run failed; it supplies no Linux
verification. Rerun the corrected workflow on its own source SHA and retain
the URL, tested commit/merge SHA, Ubuntu/Python/uv versions, exit codes and
wheel hashes. Investigate any further Linux failure without modifying package
source or tests under TUI-CI01. Fresh-context, read-only independent review
of the committed candidate and complete Linux evidence is required before
calling TUI-CI01 `VERIFIED`. Hands-on Linux terminal UAT remains a separate
final installed-candidate gate.

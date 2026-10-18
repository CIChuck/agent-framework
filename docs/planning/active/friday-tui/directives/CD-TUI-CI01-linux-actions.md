# CD-TUI-CI01: Linux verification on GitHub Actions

**Status:** Approved for TUI-CI01 construction on 2026-10-18 by Chuck Russell.

**Initiative/unit:** `friday-tui` / TUI-CI01

**Branch/source baseline:** `feature/friday-tui` /
`d69c1d72fb841e4b3e51683ef16d7dcd4eac1f00`

**Current authority:** Granted for this exact CI workflow unit only. Chuck
Russell answered "approved" to the explicit TUI-CI01 scope question in the
current session. Chuck Russell separately authorized the TUI-CI01 branch push
for Ubuntu verification with "yes, authorized" on 2026-10-18. Pull request,
merge, release and TUI product work remain unauthorized.

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
The later current-session reply "yes, authorized" separately authorized
pushing this TUI-CI01 branch to `origin` for the Ubuntu run and bounded
workflow-only corrections needed to complete that run; it does not authorize
a pull request, merge, release or product implementation.

## RD-TUI-CI01-01: bounded preflight remediation

The fresh-context review of candidate `7d97aacdd11c3cdf9903b52866a6896a21302e3e`
returned `CHANGES_REQUESTED` on 2026-10-18. This addendum directs only the
following mechanical corrections within the workflow path already approved
above. It does not expand TUI-CI01 implementation or delivery authority.

- **CI01-01:** Move `WHEEL_DIR` and `RUNTIME_VENV` expressions using
  `${{ runner.temp }}` from job-level `env` to the steps that consume them.
  Verify YAML/Bash/Python syntax and statically assert that job-level `env`
  has no `runner` expression while each consuming step declares its path.
  No package, test, dependency, credential or runner change is authorized.
- **CI01-02:** Record the event source SHA in addition to the tested checkout
  SHA. For pull requests use the PR head SHA; for pushes use `github.sha`.
  Keep the default PR merge checkout so the workflow tests the merge result.
  Verify the step expression and logging script. No trigger or checkout
  behavior change is authorized.

Record the review and correction in the scoped validation evidence and
execution log. The corrected candidate must be committed and receive a new
fresh-context read-only review. The previous review cannot verify the changed
candidate. Linux Actions evidence and separate branch-push authorization
remain mandatory for TUI-CI01 verification.

## RD-TUI-CI01-02: locked MCP test-dependency selection

The first authorized Ubuntu run
[`39172562601`](https://github.com/CIChuck/agent-framework/actions/runs/39172562601)
tested source `e3e2e974b22d193794dc5420cbad29a36b40e3e8` and failed during
full Runtime test collection: `test_mcp_http_integration.py` imports
`cryptography`, absent from the root `dev` sync. Later checks were skipped.
This is a workflow dependency-selection defect. The existing `uv.lock`
contains `mcp==2.3.0` and `cryptography==50.0.2` through the MCP package's
`dev` extra, so no package or lock change is required.

- Select both the `friday-framework` root and
  `friday-framework-mcp` workspace member with `--extra dev` in the existing
  `uv sync --locked` step. Keep the Python version check and print the
  installed `mcp`, `cryptography` and `pytest-mock` versions before tests.
- Verify by locked/offline dry run and export that the selected closure
  includes those three test dependencies; rerun YAML, Bash and Python syntax,
  board/dashboard and changed-path checks. The definitive acceptance test is
  a green Ubuntu run for the new source SHA, including all separate suites,
  built-wheel metadata and installed-import checks.
- No product source, tests, metadata, lockfile, trigger, action permission,
  credential, or wheel-isolation behavior change is authorized. A further
  failure requiring any protected path stops for a separate directive.

Record the failed run and its disposition in the packet. Commit and obtain
fresh-context read-only review of the corrected candidate; then use the
maintainer-authorized TUI-CI01 branch push to rerun Actions. A skipped or
failed step never counts as Linux verification.

## RD-TUI-CI01-03: current packet and board state

Fresh-context review of `3086f7d73efd48533c69d329305cb27c4c03dfcc`
returned `CHANGES_REQUESTED` for CI01-03: the execution-log header still
named N01A as awaiting validation, and the board next gate still called for
the locked MCP selection already present in that candidate. This conflicts
with the current TUI-CI01 validation state required by the lifecycle policy.

Correct the execution-log header and board next gate, regenerate the
dashboard, and retain the finding as validation evidence. Validate board and
dashboard consistency and the exact changed-path diff. No workflow, package,
test, metadata, lockfile, trigger, permission or credential edit is authorized
by this addendum. Commit the corrected packet and request a fresh-context
read-only review before the authorized Ubuntu rerun.

## RD-TUI-CI01-04: finance test closure and MCP observation

The second Ubuntu run
[`39173445329`](https://github.com/CIChuck/agent-framework/actions/runs/39173445329)
tested `7a41004aae8b375ebd01ff23fa0fb5f4e62bee1a`. The locked MCP dev
dependencies installed and the focused tests passed. Full Runtime ran 334
tests, with 331 passing and three failing. Two failures came from importing
`friday_tools`, whose package initializer imports `friday_finance`; the CI
selection had omitted the existing `friday-framework-finance` workspace
package. The third was one required synthetic MCP stdio server startup under
the `auto`/modern profile. The log gives no underlying lifecycle outcome, so
this failure must remain open until a new full Ubuntu run resolves it or
supplies more evidence. Chat, CLI, wheel and installed-import steps were
skipped; this run is not Linux verification.

- Add the existing `friday-framework-finance` workspace package to locked CI
  selection and print its installed distribution version. Build its wheel
  and include it in the isolated Chat-side wheel installation; keep Runtime's
  initial isolated environment frontend-free.
- Confirm the selected package is in a locked/offline export and dry run.
  Run workflow syntax, board/dashboard and allowed-path checks. Commit and
  independently review the correction, then use the recorded branch-push
  authorization to rerun the exact candidate. Inspect the MCP case in the
  complete Runtime result; do not skip, mark expected, or change that test.
- No product source, tests, metadata, lockfile, trigger, action permission or
  credential change is authorized here. A repeat MCP failure requiring
  protected code/test changes stops for a separately scoped directive.

## RD-TUI-CI01-05: current validation and board state

Fresh-context preflight of `89a875acb14c02007cf6a1873428960210598a45`
returned `CHANGES_REQUESTED` for CI01-04. The workflow correctly selects
finance, but the packet index said the Ubuntu rerun was pending while the
execution-log header retained `changes_requested`; the board next gate still
called for the completed finance selection. Reconcile the two current
validation fields as pending the next Ubuntu run, update the board to the
remaining full-run and independent-review gate, regenerate the dashboard and
retain the review as evidence. No workflow or package change is authorized
by this addendum. Commit and obtain fresh-context read-only review before
the authorized branch push.

# CD-TUI-001: additive Chat presentation contracts

**Status:** Withdrawn; must not be approved or executed

**Initiative:** `friday-tui`; two bounded construction units after planning gate G0

**Branch/base:** `feature/friday-tui` / `c34269867be50f71923c93c95a63236a35505812`

The maintainer requires `friday-tui` to operate independently of all CLI code.
Both proposed Chat APIs in this directive are unnecessary for that boundary.
This exact-file directive is retained only as historical planning evidence.
See [architecture-reset.md](../architecture-reset.md) for the controlling
requirement and prepare a new directive after the technical plan is replaced.

## 1. Controlling authority

Follow explicit maintainer requirements, repository engineering/lifecycle and
independent-validation policies, the [README](../README.md),
[build plan](../build-plan.md) and [integration contract](../integration-contract.md).
[Current authority](../authority.json) is design-only. Authoring this directive
does not approve it. Before execution, record explicit maintainer approval,
reconcile the source baseline, pin these controlling document hashes, and grant
only this unit's product scope on the board/authority record.

## 2. Objective and exact scope

Provide two additive public Chat interfaces needed by a TUI without changing
existing CLI behavior: a pure display-config reader and a categorical shutdown
report. Implement only these product/test paths:

| Path | Permitted change |
| --- | --- |
| `packages/friday-chat/src/friday_chat/display.py` | Add/export `read_display_config`; preserve `resolve_display_config` activation and error behavior. |
| `packages/friday-chat/src/friday_chat/lifecycle.py` | New immutable typed `AppShutdownReport` and its closed categorical field types. No Textual imports. |
| `packages/friday-chat/src/friday_chat/app.py` | Add a read-only `shutdown_report` property and per-run report capture; no cleanup/order/command changes. |
| `packages/friday-chat/tests_chat/test_presentation_contracts.py` | New focused pure-reader and CLI compatibility tests. |
| `packages/friday-chat/tests_chat/test_shutdown_report.py` | New focused report truth/reset/failure tests. |

### Separate execution boundaries

| Unit | Exact product/test paths from the table above | Required evidence |
| --- | --- | --- |
| TUI-00A | `display.py` and `test_presentation_contracts.py` only | CD1-01..03 and CD1-09, its focused static checks and a separately frozen/independently verified candidate. |
| TUI-00B | `app.py`, new `lifecycle.py` and new `test_shutdown_report.py` only | CD1-04..09, retained 00A tests, combined static checks and a new frozen/independently verified candidate. |

Build and check 00A before starting 00B. Pin 00A's exact base/candidate and
authority hashes in its validation request. The verified 00A candidate becomes
00B's recorded base; do not use the original source commit as though 00A did not
exist. Preserve 00A source/tests during 00B; any needed change requires bounded
remediation and renewed review. Both scopes remain drafts pending approval.

These API units have no standalone TUI UAT because no usable TUI exists yet.
Their user-visible configuration and cleanup behavior is exercised in UAT-01
and UAT-03 under the [incremental test/UAT plan](../test-and-uat-plan.md).

Retain evidence and execution checkpoints inside the active TUI packet; update
only its board record/dashboard as necessary. Existing CLI/Chat tests remain
unchanged. `packages/friday-cli/**`, all other packages, `pyproject.toml`,
`uv.lock`, dependency installation, package helpers and workflows are outside
this unit. A later directive owns the TUI package and dependency registration.

## 3. Required behavior

### Pure configuration

Implement the signature and semantics in contract section 4. Validate explicit,
sibling and default paths; return fresh values; preserve response/banner parsing
and current errors. A successful pure read must leave both CLI global config
and console identity unchanged, whether globals are initialized or not.

Preserve the existing activating resolver's signature and observable behavior.
It must still activate on success and retain its existing failure behavior.
Do not modify `friday-cli`, monkey-patch its production functions, or redirect
stdout to obtain pure behavior.

### Shutdown observation

Implement contract section 6's immutable `AppShutdownReport` and read-only
property. Report `None` before/during each run; publish a new per-run snapshot
before return/raise. Clear prior-run state on reuse.

Distinguish no attempted lifecycle cleanup, successful cleanup, and failed
cleanup. Preserve application failure versus cleanup outcome; report caught
cleanup failures honestly. Startup errors, normal exits, EOF, keyboard interrupt,
operation exceptions and external cancellation need defined report results.

Do not change `AppRunResult` fields/equality, exception types/propagation,
shutdown ordering, telemetry events/content or command handlers. Do not perform
additional cleanup or retries to make the report look successful. Report fields
must contain no prompts, paths, tool data, credentials or exception messages.

## 4. Acceptance tests

| ID | Required test |
| --- | --- |
| CD1-01 | Pure explicit/sibling/default reads match current resolved values and precedence, including malformed/missing files and schema errors. |
| CD1-02 | Sentinel CLI config and console objects retain identity/state after pure reads, including failures; pure reading creates no singleton when none existed. |
| CD1-03 | Activating resolver still sets config and resets console exactly as before; normal CLI rendering/startup regression tests pass unchanged. |
| CD1-04 | Normal `/q`, EOF and keyboard interrupt produce the correct stop reason and successful cleanup report. |
| CD1-05 | Startup failure before lifecycle entry reports cleanup `not_attempted` and preserves the original exception. |
| CD1-06 | Operation failure with successful cleanup differs from cleanup failure; test coordinator/client failures already caught by current code as well as propagating failures. |
| CD1-07 | External cancellation retains its current exception/cleanup behavior while reporting accurately; no new cancellation policy is introduced. |
| CD1-08 | Report is immutable, unavailable until termination, reset for each run and contains only closed categorical values; returned `AppRunResult` and existing telemetry assertions remain unchanged. |
| CD1-09 | All existing CLI package tests and the captured selected Chat baseline pass; no protected CLI or out-of-scope product diff exists. |

Tests use disposable paths and fake providers only. They must exercise observable
behavior, not merely inspect field declarations or duplicate implementation text.

## 5. Required validation

Run from the repository root using the existing environment without implicit
`uv sync`. Preserve local state and record actual commands/results. Tests are
part of each unit's construction, not a final batch after both units are built.

### TUI-00A required checks

```bash
.venv/bin/python -m pytest --import-mode=importlib -q -p no:cacheprovider \
  packages/friday-cli/tests_cli \
  packages/friday-chat/tests_chat/test_command_registry.py \
  packages/friday-chat/tests_chat/test_command_foundations.py \
  packages/friday-chat/tests_chat/test_display.py \
  packages/friday-chat/tests_chat/test_cli.py \
  packages/friday-chat/tests_chat/test_app_lifecycle.py \
  packages/friday-chat/tests_chat/test_session_identity.py \
  packages/friday-chat/tests_chat/test_input_sources.py \
  packages/friday-chat/tests_chat/test_presentation_contracts.py
.venv/bin/ruff check packages/friday-chat/src/friday_chat/display.py \
  packages/friday-chat/tests_chat/test_presentation_contracts.py
.venv/bin/mypy --follow-imports=silent \
  packages/friday-chat/src/friday_chat/display.py \
  packages/friday-chat/tests_chat/test_presentation_contracts.py
```

The shutdown-report test/module do not exist in 00A and must not be prerequisites
for checking it. Freeze/review the 00A candidate before executing 00B.

### TUI-00B required checks, including retained 00A regressions

```bash
.venv/bin/python -m pytest --import-mode=importlib -q -p no:cacheprovider \
  packages/friday-cli/tests_cli \
  packages/friday-chat/tests_chat/test_command_registry.py \
  packages/friday-chat/tests_chat/test_command_foundations.py \
  packages/friday-chat/tests_chat/test_display.py \
  packages/friday-chat/tests_chat/test_cli.py \
  packages/friday-chat/tests_chat/test_app_lifecycle.py \
  packages/friday-chat/tests_chat/test_session_identity.py \
  packages/friday-chat/tests_chat/test_input_sources.py \
  packages/friday-chat/tests_chat/test_presentation_contracts.py \
  packages/friday-chat/tests_chat/test_shutdown_report.py
.venv/bin/ruff check packages/friday-chat/src/friday_chat/app.py \
  packages/friday-chat/src/friday_chat/display.py \
  packages/friday-chat/src/friday_chat/lifecycle.py \
  packages/friday-chat/tests_chat/test_presentation_contracts.py \
  packages/friday-chat/tests_chat/test_shutdown_report.py
.venv/bin/mypy --follow-imports=silent \
  packages/friday-chat/src/friday_chat/app.py \
  packages/friday-chat/src/friday_chat/display.py \
  packages/friday-chat/src/friday_chat/lifecycle.py \
  packages/friday-chat/tests_chat/test_presentation_contracts.py \
  packages/friday-chat/tests_chat/test_shutdown_report.py
.venv/bin/python scripts/friday-dev-board.py validate
.venv/bin/python scripts/friday-dev-board.py render --check
git diff --check
```

Run the board/dashboard/whitespace checks in the block above for both units,
along with changed-packet links and the respective two-path or three-path
product diff allowlist. For 00B also verify the cumulative five-path scope.

The baseline app/display modules pass Ruff and focused Mypy; require the changed
files and new interfaces/tests to pass without new suppressions. Reuse the offline test
guard/profile captured in the technical evidence. Compare protected source hashes
and the exact five-path product allowlist. Check updated packet links. The known
six historical telemetry-report links are baseline documentation debt, not a
reason to edit frozen evidence.

Current baseline: 241 existing tests pass under the importlib collection mode.
Default collection collides on the two packages' `test_display.py` names; do not
rename tests or delete caches to work around that harness condition.

## 6. Candidate and stop conditions

After each unit's implementation/checks, create a stable candidate and hand exact source and
authority hashes, this directive, diff, tests and known baselines to a fresh
read-only independent validator under repository policy. Do not self-accept,
advance from 00A into 00B before 00A is `VERIFIED`, or advance into TUI widgets
before 00B is `VERIFIED`.

Stop on CLI behavior drift, changed cleanup/order/exception behavior, new
substantive test or type failure, needed paths outside the allowlist, a Textual
dependency in shared interfaces, source/authority mismatch, or a need to change
existing tests to make regressions disappear. Record the issue and required
scope change. This directive authorizes no live providers, remote MCP, release,
push, merge, PyPI upload or modification of existing user state.

# TELEM-01 implementation report

Date: 2026-10-05. Work unit: CD-001 / TELEM-01.
Branch: `feature/friday-telemetry-rewire`.
Base: `2155a0fc51f5b20dea4e35c6cfc70f1d52002735`.
Formal candidate and diff are pinned in the post-commit validation request.
Independent validation: pending; no completion or acceptance is claimed.

## Behavior and scope

Chat has a strict default-disabled local telemetry section. The CLI and embedded
fake/real runtime assembly create one retained `ChatTelemetryObserver`, before
services are constructed. Explicit custom injection remains a borrowed override
even when config is disabled. No provider is closed by Chat.

The observer stores immutable safe records in a 256-event ring and retains
cumulative failure/rejection/drop counts. It accepts closed lifecycle fields and
validated public MCP events, uses opaque session references, rejects arbitrary
legacy events, and keeps local diagnostics when a sink fails. Optional lifecycle
spans accept only closed names and outcomes, map borrowed IDs, and cap active
local span ownership at 128. Runtime ready means successful assembly; application
stop distinguishes completion, startup/foreground failure, cancellation, and
cleanup failure. Existing cleanup order and exception behavior remain intact;
explicit flags observe failures previously retained only as maintenance warnings.

Composite providers map each sink's span/parent IDs, snapshot span membership,
copy payloads independently, end once, and attempt all sinks before reporting a
content-free aggregate failure. Partial start failure closes opened children.
Package READMEs describe defaults, inspection, borrowing, and deferred coverage.
No changes to LLM/memory metrics, OTel, Langfuse, raw capture, storage, dependencies,
tool selection, or the existing example-config trial were made.

## Criteria and reproducible verification

| Criteria | Evidence |
| --- | --- |
| AC-01 | `test_telemetry.py`: disabled defaults, strict malformed/unsupported config, safe loader errors, enabled YAML; compatibility suite |
| AC-02 | `test_telemetry.py`: fake injection/override, stubbed-real pre-construction observer and no false ready on failure; CLI state tests |
| AC-03 | `test_telemetry.py`: immutable bounded history and counters, app lifecycle, failures at startup/foreground/cleanup, cancellation and keyboard interrupt |
| AC-04 | `test_telemetry.py`: planted sentinel rejection, safe lifecycle fields, MCP schema validation and equal two-sink payloads, invalid span outcomes |
| AC-05 | `test_providers.py`: both sinks ended with own parent IDs, empty/unknown/repeated end, dynamic membership, mutation isolation, failure fan-out and rollback |
| AC-06 | focused/package logs, affected Ruff/mypy, board/docs checks, frozen candidate and pending fresh-context independent review |

Commands use `UV_CACHE_DIR=/private/tmp/friday-uv-cache`; pytest additionally uses
`LITELLM_LOCAL_MODEL_COST_MAP=true`. The exact required pytest commands are in
CD-001. Logs here preserve command output:

- Baseline full Chat + telemetry: 675 passed, 5 skipped, 2 failed, 3 errors.
- Post-change full Chat + telemetry: 717 passed, 5 skipped, same 2 failures and
  3 errors. No new failing test identifiers.
- Final focused directive suite: 129 passed (see `focused-tests.log`).
- Baseline affected Python 3.13 mypy: success for 5 source files.
- Post-change affected Python 3.13 mypy: success for all 6 changed source files.
- Ruff: all 10 changed Python source/test files pass.
- Board validation: 25 working tasks; staged candidate intentionally excludes
  the unrelated new task and contains 24 tasks.
- Documentation lifecycle: passed, 392 Markdown files before report addition;
  final check passed with 393 Markdown files and is recorded in the execution log.
- `git diff --check`: passed.

## Baseline limitations and review profile

The three `test_llm_adapter_migration.py` setup errors are denied localhost
listener binds in the restricted sandbox. The two failures are
`test_command_disposable_uat.py::test_real_app_cli_pty_command_uat_is_contained_and_provider_free`
and `test_reorganization_terminal.py::test_provider_free_pty_acknowledges_before_bounded_progress_completes`.
The first sees the pre-existing example required-tool trial fail selection; the
second has no terminal acknowledgement in the restricted PTY run. Neither was
edited. Review must compare the frozen clean candidate separately from these
mixed-checkout baselines and report any remaining infrastructure or baseline
failures explicitly. No failure is waived by the builder.

The old OTel provider test can print an atexit console-export failure after
pytest reports its results. This also occurs in the baseline; OTel repair is a
later directive. Do not interpret the console output as a newly activated Chat
exporter. No live-vendor calls or exporter activation are permitted for review;
synthetic local loopback fixtures and temporary files are the deterministic
verification environment.

## Preservation and delivery

All 64 files/nonexistence entries in the pre-edit preservation manifest match
byte hashes. The unrelated tool-continuity packet and working board additions
remain uncommitted. Separate board/dashboard index content excludes that task
while preserving it in the working tree. The example YAML, its backup, audit
Dockerfile, docker-bench-security tree, `.DS_Store`, and deleted family-tree file
remain outside the candidate. Existing runtime data was not inspected or cleaned.
No push, merge, release, external deployment, or later-unit authority is implied.

# REM-004 Implementation Report

Status: Correction implemented; fresh independent VAL-007 delta and entire WS-02 review required
Date: 2026-09-28
Branch: `feature/friday-mcp-ws02-lifecycle`
Finding: VAL-006 F-001 only
Approval commit: `cdd808ed653f2f5fe4ccc4a695782d97c39c2ce8`
Execution baseline: `bd10656fed43083ff1d81ef2232205b50f58ac99`
Bounded correction base: `097bbd9eced5e5ba2ffcc97fbe60273285bf605e`
Reviewed defective candidate: `26f4d7d4bfd0514b6eb76bed71cb4797da91a067`
Entire WS-02 comparison base: accepted WS-01 `a64e423cffca6162c43b8cfa193792508cf87fd6`

## Authority And Role Disclosure

The complete approved [REM-004 directive](../remediation/REM-004-directive.md),
approved [WS-02 directive](../directives/ws-02-runtime-lifecycle-provider-loading.md)
with its cleanup amendment, [readiness checkpoint](WS-02-readiness-checkpoint.md),
and complete [VAL-006 report](../validation/VAL-006-report.md) were read before
editing, together with AGENTS.md, repository policies, packet build/tactical
plans, and current board authority. Board validate/next/show confirmed the
started, granted, local work unit and current branch. The correction base adds
only controller dispatch metadata to the execution baseline.

This existing thread formerly performed the separate WS-01 VAL-004 review.
After readiness-only inspection it was explicitly reassigned by the controller,
under maintainer approval and the user's proceed instruction, solely as the
separate REM-004 remediator. It is not the original WS-02 builder, does not
independently validate its own resulting candidate, and does not claim review
context freshness. Agent capacity prevented creating a new remediator thread;
that does not waive the future fresh-context VAL-007 gate. No other agent was
spawned. This is the second WS-02 remediation cycle; unsuccessful independent
aggregate review returns to the maintainer without an automatic correction loop.

## Correction And Ownership

All production changes are inside `StdioTransport`. Public signatures, schemas,
connection/discovery/RPC deadlines, registry behavior, and REM-003 manager and
provider retained ownership are unchanged. No Python subprocess internals or
private cross-package access were added.

- Disconnect immediately refuses new protocol I/O. An explicitly owned cleanup
  task is shielded from caller cancellation; cancellation still propagates to
  the caller, and a later public disconnect joins or retries that task.
- The transport explicitly owns its stdout protocol read. Cleanup cancels and
  settles that reader before taking over stdout, avoiding competing readers.
- Stdout and stderr are discarded in 4096-byte reads without accumulation,
  logging, or persistence. The existing stderr reader is reused through process
  termination; a completed successful EOF drain is not restarted.
- Stdin closes through its public API. The five-second graceful-termination
  policy remains; forced kill and its process wait are bounded. Success requires
  process exit, both output drains at EOF, and settled owned tasks before owner
  references are cleared.
- An incomplete attempt cancels its owned I/O/wait tasks with a finite settlement
  wait, preserves process/task slots (including resistant pending tasks), and
  raises only `MCP stdio cleanup incomplete`, suppressing raw exception context
  in displayed diagnostics. A subsequent public retry reuses pending readers
  or restarts settled failed readers, never a competing reader.

Asynchronous phase budget per attempt: protocol-reader stop 1 second, graceful
process exit 5 seconds, forced exit 2 seconds, pipe EOF 2 seconds, failed-attempt
task settlement 1 second: at most 11 seconds, plus ordinary event-loop scheduling.
The last phase applies on failure, not successful teardown. Test bounds use
13 seconds (two seconds scheduling slack); startup-failure tests additionally
allow two seconds for existing request/connection deadlines. These are not a
universal two- or seven-second shutdown SLA. Unit doubles shorten these private
phase constants; real-process regressions use production values.

## Before And After Evidence

Before editing the production source, an independent local probe used a child
that installed SIGTERM ignore, emitted a valid `{}` line, wrote 1 MiB of
unterminated stdout, and slept. After the valid receive, the second receive
failed at the asyncio line limit, proving the receiver stopped. Public transport
disconnect exceeded a seven-second detector; the child return code was `-9`
and its transport process owner remained retained. Probe teardown explicitly
drained stdout in 4096-byte reads, reaped the already-killed child, then retried
public disconnect; every synthetic probe resource was released. This is a
before-fix direct-transport observation, not a claim that this remediator
reproduced the historical VAL-006 public-kernel probe before editing.

The committed regressions use an authorized synthetic peer that ignores SIGTERM,
emits more than 1 MiB on each output stream in producer chunks, and leaves
stdout unterminated. Oversized-line failure or a static receiver-failure log is
observed before the asserted shutdown; readiness does not rely on a fixed sleep.

| Criterion | Regression evidence |
| --- | --- |
| AC-01 | `test_real_direct_transport_noisy_forced_kill_is_bounded`: valid protocol replies, observed oversized receive failure, public disconnect within 13 seconds, forced `-9` exit, public pipe EOF/closed stdin and no transport tasks. |
| AC-02 | `test_real_public_kernel_noisy_success_stop_and_restart`: real normal discovery, two public start/stop cycles, receiver failure observed, cleared public manager and prepared handoff, exited children and settled tasks; no saved/private owner cleanup. |
| AC-03 | `test_real_public_kernel_noisy_partial_start_cleanup`: handshake and discovery failures, optional and required variants, with a successful peer. Optional partial discovery retains only the good peer until public stop; required failure cleans both. No tool registration or worker/receiver/drain remains. |
| AC-04 | Multi-megabyte stdout/stderr real peers plus `test_stdio_discard_is_incremental_and_redacted` verify 4096-byte read requests and no raw sentinel command/args/env/peer logs. Kernel lifecycle/discovery representations are checked for sentinel content; stream failure has only a static displayed error. |
| AC-05 | New caller-cancel, active-reader settlement, unreaped-process retry, resistant-drain retry, and static stream-error retry cases pass alongside prior already-exited, repeated disconnect, spawn-cancel, EOF, RPC deadline, successful-peer, and REM-003 provider/public-kernel recovery regressions. |
| AC-06 | Exactly the six authorized paths below; unchanged public signatures/schema, no new broad typing suppression, passing prescribed typed check, bounded report correction. |

Fixtures track only their own public process objects and transport connections.
Their finally blocks retry public disconnect, defensively kill if needed, drain
both pipes incrementally, and reap even after assertions fail. This defensive
work occurs after public-cleanup assertions and cannot make those assertions
pass. Resource assertions use public process/stream APIs and `asyncio.all_tasks`.
All six new in-process double cases also have a finally-backed owner fixture
that clears only synthetic obstructions and retries public disconnect. Caller
and protocol-receiver tasks are cancelled/joined in test finally blocks; event
gates for resistant I/O and process waits are released in finally. Fixture
teardown errors are separate pytest outcomes, not replacements for failed
public-cleanup assertions. This final hardening follows a controller scope
reminder and is implementation verification, not independent review.

During construction, the first 37-case run had 4 failures/33 passes: two exposed
successful EOF drains being restarted, fixed by reusing those completed tasks;
two were expectations corrected to the existing timeout outcome and failed-start
public diagnostics API. The subsequent 37-case run passed. Adding both optional
noisy failure variants produced the final 39-case passing run below.

## Required Check Results

Every `uv` invocation used `UV_CACHE_DIR=/private/tmp/friday-uv-cache`; all tests,
mypy/imports, and board/documentation diagnostics additionally used
`LITELLM_LOCAL_MODEL_COST_MAP=true`. Commands are the directive's exact targets.

| Command (after `uv run`) | Result |
| --- | --- |
| `pytest packages/friday-mcp/tests_mcp/client/test_lifecycle.py tests/integration/test_mcp_runtime_lifecycle.py -q` | 39 passed in 40.95s; 12 additional cases. |
| `pytest packages/friday-runtime/tests_runtime/test_mcp_loading.py -q` | 32 passed in 7.00s. |
| `pytest packages/friday-core/tests_core packages/friday-mcp/tests_mcp packages/friday-runtime/tests_runtime tests/integration/test_mcp_runtime_lifecycle.py -q` | 333 passed in 46.92s. |
| `pytest packages/friday-chat/tests_chat/test_mcp_config_compatibility.py packages/friday-chat/tests_chat/compat/test_config_compatibility.py packages/friday-chat/tests_chat/test_llm_config_migration.py -q` | 46 passed in 1.38s. |
| `pytest tests/integration -q --tb=short` | 44 passed, 1 declared baseline failure in 44.20s. |
| `ruff check packages/friday-runtime packages/friday-mcp tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py` | Passed. |
| `mypy packages/friday-runtime packages/friday-mcp` | Declared baseline: installed NumPy `__init__.pyi:737`, type statement requires Python 3.12+; default target 3.10 stops before project checking. |
| `mypy --python-version 3.13 packages/friday-runtime packages/friday-mcp tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py` | Passed, 42 source files. |
| `python scripts/friday-dev-board.py validate` | Passed, 23 tasks. |
| `python scripts/friday-dev-board.py render --check` | Passed, dashboard current. |
| `python scripts/check-documentation-lifecycle.py` | Passed after report addition, 335 Markdown files. |
| `git diff --check` (not an uv command) | Passed after report addition. |

Broad integration's only failure is unchanged
`tests/integration/test_development_board.py:75`, expecting `22 tasks` while
the current and accepted baseline board contains 23. Neither declared baseline
was repaired or counted as a correction-specific regression. Implementation
checks are not independent validation or maintainer acceptance.

## Exact Scope, Freeze, And Residual Limits

The locally committed candidate contains exactly:

1. `packages/friday-mcp/src/friday_mcp/client/stdio.py`
2. `packages/friday-mcp/tests_mcp/client/test_lifecycle.py`
3. `tests/integration/mcp_fake_server.py`
4. `tests/integration/test_mcp_runtime_lifecycle.py`
5. `docs/planning/active/friday-mcp/execution/REM-004-implementation-report.md`
6. `docs/planning/active/friday-mcp/execution/WS-02-implementation-report.md`

The full candidate hash is supplied in the controller handoff after committing;
this report intentionally does not attempt a self-referential commit hash.
Approved authority was unchanged from the correction base. Key SHA-256 pins:

```text
1079756e6f6738c1dd4fb61126d2a1b3159c3ca48ef092470b47f22a09fec37b REM-004-directive.md
a432dc3c17e7cff9e767ed9dc78f6a1f65ea0d51dead3fc7e5421ef04327f55d ws-02-runtime-lifecycle-provider-loading.md
e09d7114a37ccd9c8cb3a547227bfbf5937eddc5564afc14003b7df6194da976 WS-02-readiness-checkpoint.md
bd01da21b20fc30c579c0b1b8f281752910d7f060d56cc5dff2bc5e1e6d3ca16 VAL-006-report.md
```

Preserved unrelated manifest: modified `.DS_Store`; deleted `family-tree.md`;
untracked `docker-bench-security/`,
`packages/friday-chat/config.example.yaml.pre-typed-llm-20260828.bak`, and
`packages/friday-sandbox/docker/Dockerfile.audit`. None is staged in this candidate.

Finite cooperative asyncio budgets are not hard real-time guarantees under
event-loop starvation. If the OS cannot reap a process, a descendant holds
output open, or an I/O task resists cancellation, cleanup reports a static
incomplete error and preserves ownership instead of promising release or
abandoning it; retry requires the obstruction to clear. Process-tree control,
broader lifecycle redesign, SSE/remote transports, and arbitrary executable
confinement remain out of scope. No directive stop condition was encountered.
No network, endpoint, provider, credential, paid, external, or delivery effects
were performed. No controller board/index/log/queue or authority edits were made.
Controller owns process metadata and the fresh review
request. VAL-007 must independently review both the delta and entire WS-02;
no self-validation, `VERIFIED`, acceptance, merge, push, or delivery is claimed.

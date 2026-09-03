# Mitigation Plan 1: Nonblocking and Cancellable Friday Chat Input

## Status

Implemented on 2026-08-06. Automated, package-level, lock/sync, and real
pseudo-terminal validation are complete. The live provider-backed
idle-maintenance smoke test was attempted on 2026-08-06, but the configured
embedding endpoint at `127.0.0.1:1234` was unreachable from the execution
environment. The real-runtime acceptance criterion therefore remains open.

## Execution Record

- Restored the pinned compatibility-plan paths and established a green
  pre-change baseline of `174 passed`.
- Added a shared lazy `prompt_toolkit` async reader and migrated both production
  input sources without changing the `InputSource` protocol.
- Added direct Friday Chat dependency metadata; `uv lock` changed only the two
  expected Friday Chat dependency-edge entries.
- Added deterministic coverage for both input sources and an application-level
  idle-background regression covering extraction, tool decay, incremental
  graph maintenance, and compaction.
- Adapted isolated Typer CLI tests at the async input boundary; no synchronous
  production fallback was added.
- Verified real PTY Ctrl-C and Ctrl-D behavior: both exited immediately with
  status 0, without an extra Enter or traceback.
- Completed `uv lock`, `uv sync`, and `uv sync --all-extras`.
- Final automated validation: `182 passed`, Ruff passed, and mypy passed for 60
  source files.
- Attempted the approved provider-backed idle-maintenance smoke against the
  current configuration and existing `.friday` state. Friday Chat exhausted
  four embedding attempts before the first turn because the configured
  loopback embedding endpoint was unreachable. A metadata-only direct probe
  also failed to connect and returned HTTP status `000`; no idle-maintenance
  observation was possible, and no configuration or runtime state was removed
  or reset.

## Problem Statement

Both production Friday Chat input sources call the synchronous built-in
`input()` function from an asynchronous `read()` method:

- `ConsoleInputSource` in `packages/friday-chat/src/friday_chat/app.py`
- `FridayCliInputSource` in `packages/friday-chat/src/friday_chat/display.py`

After a turn, `FridayChatApp` schedules extraction, tool decay, incremental
graph maintenance, and budget-triggered compaction through
`BackgroundWorkCoordinator`. The application then immediately waits for the
next prompt. Because `input()` blocks the event-loop thread, the scheduled
maintenance cannot make progress while the user is idle at that prompt.

Moving `input()` to `asyncio.to_thread()` would allow maintenance to run, but
it would introduce an unsafe shutdown path. Ctrl-C is delivered to the main
thread rather than to the worker blocked in `input()`. `asyncio.run()` can then
wait for the default executor during shutdown until the input thread returns.
The existing `KeyboardInterrupt` handling would also no longer accurately
represent the real terminal path.

## Decision

Use `prompt_toolkit`'s native asynchronous prompt API rather than a thread or
executor workaround.

`prompt_toolkit` is already a direct dependency of `friday-framework-cli` and
is already present in `uv.lock`. Friday Chat will declare it directly because
Friday Chat will import it directly. This is a package-contract correction,
not the introduction of a new resolved library.

The implementation will use:

- one `PromptSession` per input-source instance;
- `PromptSession.prompt_async()` for cancellable event-loop-native input;
- `patch_stdout()` while the prompt is active so output from other coroutines
  does not overwrite the prompt; and
- an injectable asynchronous prompt boundary for deterministic tests.

References:

- [prompt_toolkit async prompt guidance](https://python-prompt-toolkit.readthedocs.io/en/3.0.20/pages/asking_for_input.html)
- [prompt_toolkit Ctrl-C and Ctrl-D behavior](https://python-prompt-toolkit.readthedocs.io/en/3.0.18/pages/tutorials/repl.html)

The implementation will not use:

- `asyncio.to_thread()`;
- `ThreadPoolExecutor`;
- daemon-thread customization;
- private executor internals; or
- a synchronous fallback in production.

## Scope and Boundaries

Allowed implementation targets are:

- `packages/friday-chat/src/friday_chat/`;
- `packages/friday-chat/tests_chat/`;
- `packages/friday-chat/pyproject.toml`;
- `uv.lock` if dependency metadata changes it; and
- this planning document.

Do not modify `friday-cli` source. Friday Chat may consume public external
interfaces, but the FridayV2 implementation boundary keeps existing framework
package source frozen.

Preserve all unrelated local changes and generated runtime state.

Output sinks remain out of scope. No changes are planned for `print()`, Rich
console writes, or `sys.stdout.write()`/`flush()`.

## Behavioral Contract

The remediation must preserve or establish the following behavior:

1. Waiting at either production prompt yields control to the asyncio event
   loop.
2. Background work can finish while the next prompt remains idle.
3. `ConsoleInputSource` retains its default `"> "` prompt.
4. `FridayCliInputSource` retains its required configured prompt text.
5. Input text is returned without new stripping or normalization.
6. Ctrl-D propagates as `EOFError` and produces the existing EOF exit path.
7. Ctrl-C propagates as `KeyboardInterrupt` and produces
   `exit_reason="keyboard_interrupt"`.
8. Ctrl-C exits promptly without requiring an additional Enter.
9. Prompt shutdown leaves no executor worker or input thread behind.
10. The `InputSource` protocol remains unchanged.
11. `ListInputSource` and replay paths remain unchanged.

## Work Package 1: Restore the Validation Baseline

The current command:

```text
uv run pytest packages/friday-chat -q
```

reports `172 passed, 2 failed`. Both failures come from
`packages/friday-chat/tests_chat/compat/test_contract_coverage.py`, which still
references planning documents at their former locations.

Before changing input behavior:

1. Update both `PARITY_MATRIX` and `CONTRACTS` to the pinned documents under
   `docs/archive/completed/2026/friday-chat-v2/`.
2. Document in the test that these archived documents are the compatibility
   authority for the parity assertions.
3. Run the focused compatibility test.
4. Run the complete Friday Chat suite and establish a green baseline.

Keep this correction separate from the input remediation so validation debt
cannot be confused with new input failures.

## Work Package 2: Add a Shared Async Prompt Boundary

Add a package-private Friday Chat input helper, provisionally
`packages/friday-chat/src/friday_chat/input_sources.py`, that owns the
`prompt_toolkit` interaction.

The helper will:

1. Create and retain a `PromptSession` rather than rebuilding one per read.
2. Await `prompt_async()` with the caller-provided prompt.
3. Activate `patch_stdout()` only while waiting at the prompt.
4. Expose an injectable async prompt callable or a narrow declared protocol for
   tests.
5. Preserve `KeyboardInterrupt` and `EOFError` without translation.
6. Return the prompt result unchanged.

The injected boundary must be asynchronous. Do not inject a synchronous
`Callable[[str], str]`, because that would allow the blocking behavior to be
reintroduced behind the abstraction.

## Work Package 3: Migrate Both Production Input Sources

Update both adapters to delegate to the shared helper:

1. `ConsoleInputSource` keeps its current default constructor behavior and
   default prompt.
2. `FridayCliInputSource` keeps its required prompt argument and the exact
   display-generated prompt.
3. Both sources accept the test boundary as an optional keyword-only
   dependency.
4. Neither source directly calls built-in `input()`.

Do not merge or relocate the public adapter classes if doing so would change
their import paths. The helper is shared to prevent the two implementations
from drifting while preserving the existing public surfaces.

## Work Package 4: Declare the Direct Dependency

Add `prompt-toolkit>=3.0.0` to
`packages/friday-chat/pyproject.toml`.

The package already arrives transitively through `friday-framework-cli`, but
Friday Chat must not rely on an incidental transitive dependency for a direct
import.

Run `uv lock` and inspect the result. The expected outcome is an update to
Friday Chat's declared dependency edge without an unrelated version change.
Preserve the existing uncommitted package-metadata changes while editing this
file.

## Work Package 5: Input-Source Regression Tests

Add focused tests, preferably in a dedicated
`packages/friday-chat/tests_chat/test_input_sources.py` module.

Parameterize applicable tests across both `ConsoleInputSource` and
`FridayCliInputSource`.

### Nonblocking test

1. Inject an async prompt callable controlled by `asyncio.Event` objects.
2. Start `read()` as a task.
3. Wait until the prompt callable confirms that it entered its waiting state.
4. Schedule a marker coroutine through `BackgroundTaskManager`.
5. Assert the marker completes while the read task remains pending.
6. Release the prompt in a `finally` block.
7. Await the read task and close the background manager.

Using asyncio events avoids the deadlock inherent in an event-loop-blocking
`threading.Event` test. Every test must guarantee prompt release and task
cleanup even when an assertion fails.

### Contract tests

Cover the following for both adapters:

- exact prompt forwarding;
- exact response return value;
- `EOFError` propagation;
- `KeyboardInterrupt` propagation; and
- preservation of the existing constructor defaults and requirements.

## Work Package 6: Application-Level Background Regression

Add an application-level test that exercises the actual reported sequence:

1. Configure the fake runtime so extraction, tool decay, and incremental graph
   maintenance are due after the first turn.
2. Allow the first input and chat turn to complete.
3. Block the second asynchronous prompt.
4. Wait for the second prompt to confirm it is idle.
5. Assert that the expected records appear in
   `runtime.maintenance.background_actions` before releasing the prompt.
6. Release the prompt with EOF.
7. Verify transcript finalization, supervised-task closure, and the normal EOF
   result.

This is the primary proof that Friday Chat maintenance progresses while the
interactive session is quiet.

## Work Package 7: Terminal Shutdown Validation

The existing synthetic `KeyboardInterruptInputSource` test remains useful but
is not sufficient proof of OS-level terminal behavior.

Add or perform a pseudo-terminal validation that:

1. Starts the real Friday Chat CLI with a fake runtime.
2. Waits until the interactive prompt is visible.
3. Sends Ctrl-C without sending Enter.
4. Requires the process to exit within two seconds.
5. Verifies that no traceback is printed.
6. Verifies the keyboard-interrupt shutdown path.
7. Repeats the test with Ctrl-D and verifies the EOF path.

If a portable automated pseudo-terminal test is not practical on every CI
platform, run it automatically on supported POSIX platforms and retain a
documented Windows manual check. Do not replace it with another test double.

## Work Package 8: Manual Idle-Maintenance Smoke Test

Use a real runtime configuration with `extraction.interval: 1`.

1. Start Friday Chat.
2. Send one ordinary message.
3. Leave Friday Chat untouched at the next prompt.
4. From a second terminal, observe the extraction provider request or a change
   in the configured persisted-memory store.
5. Do not press Enter in Friday Chat before observing the result.
6. Confirm Ctrl-C exits without another Enter.

For automated assertions, use `maintenance.background_actions`.
`maintenance.actions` does not record ordinary background extraction, tool
decay, or incremental graph maintenance and must not be cited as the proof.

## Validation Sequence

Run validation in this order:

1. Focused compatibility baseline tests.
2. New input-source tests.
3. Application lifecycle tests.
4. Background-work tests.
5. Existing CLI tests, including `CliRunner` non-TTY input.
6. `uv run pytest packages/friday-chat`
7. `uv run ruff check packages/friday-chat`
8. `uv run mypy packages/friday-chat`
9. `uv lock`
10. `uv sync`
11. Repeat the full Friday Chat test, lint, and type-check gates after sync.
12. Run the pseudo-terminal Ctrl-C and Ctrl-D checks.
13. Run the real idle-maintenance smoke test.

If `prompt_toolkit` cannot consume Typer's isolated `CliRunner` stdin, adapt
the CLI tests to inject the async prompt boundary. Do not add a synchronous
production fallback to make the tests pass.

## Sequencing and Review Units

Use two separately reviewable changes:

1. Restore the compatibility-test document paths and establish a green
   baseline.
2. Implement the async input boundary, migrate both input sources, declare the
   dependency, and add regression coverage.

Do not combine unrelated repository cleanup, package publication work, or
output-sink changes with either unit.

## Acceptance Criteria

The remediation is complete only when all of the following are true:

- Both production input sources use native async prompt input.
- No input path uses a worker thread or executor.
- Background extraction, tool decay, graph maintenance, and compaction can
  progress while the prompt is idle.
- Ctrl-C exits promptly without Enter or a traceback.
- Ctrl-D retains the normal EOF behavior.
- Both production adapters have direct regression coverage.
- The application-level test proves maintenance completion before prompt
  release.
- The complete Friday Chat suite is green.
- Friday Chat lint and type checking pass.
- `uv lock` and `uv sync` complete without unrelated dependency drift.
- The real-runtime idle-maintenance smoke test succeeds.

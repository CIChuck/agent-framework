# P0 current-worktree baseline receipt

Date: 2026-11-04
Source HEAD: `fc028f3bf128a610aae7d95b59afb4b601bec0eb`
Status: Partial characterization; Chat baseline red; P0/P1 not complete

## Identity and scope

Python 3.13.10 on macOS 27.0.1 arm64. Both distributions report 0.1.0a4.
This is the current workspace environment, not a clean-checkout or isolated-wheel
baseline. Three pre-existing dirty inputs were preserved: the command-follow-up
backlog README and Chat's repository config/model examples. Their SHA-256 hashes
are in [worktree-inputs.json](p0/worktree-inputs.json). The source inventory hashes
84 command/CLI source and test files. No product source or tests were edited.

## Commands and observed outcomes

Run these separately from the repository root:

```sh
uv run pytest -q -ra packages/friday-chat/tests_chat --ignore=packages/friday-chat/tests_chat/test_live_lmstudio.py --junitxml=/tmp/friday-command-p0-chat.xml
uv run pytest -q -ra packages/friday-cli/tests_cli --junitxml=/tmp/friday-command-p0-cli.xml
uv run python docs/planning/active/command-refactor/validation/p0/capture_inventory.py
uv run python docs/planning/active/command-refactor/validation/p0/probe_contracts.py
```

| Evidence | Result | Receipt |
| --- | --- | --- |
| Chat owning suite, explicit live-provider lane excluded | 823 passed, 3 failed, 1 deprecation warning; 50.39s | [log](p0/chat.log), [JUnit](p0/chat.xml) |
| Generic CLI owning suite | 155 passed; 0.21s | [log](p0/cli.log), [JUnit](p0/cli.xml) |
| Live registry vs frozen metadata | 50 names, 3 aliases; zero metadata drift | [inventory](p0/inventory.json) |
| Stateless dispatch/parser/entry-point probes | Observations below | [probes](p0/probes.json) |

No live-model lane was run. No skips were reported in the two separate suite
summaries. JUnit copies omit system-out/system-err blocks; test results and failure
traces remain. Stored logs/XML have trailing line whitespace normalized.
These suite totals do not establish every PAR behavior class.

The first combined invocation of both suites failed during collection with a
`test_display` import-file mismatch (same module basename in two package trees).
It ran no tests. See [combined log](p0/baseline.log). Separate invocations avoid
this collection collision without changing caches, source or test configuration.

## Baseline failures: preserve and reconcile

1. `compat/test_config_compatibility.py::test_repository_and_packaged_examples_share_model_bindings`:
   repository and packaged model-library profiles differ. Repository examples are
   already dirty; do not classify this as a refactor regression or clean-HEAD defect.
2. `test_command_disposable_uat.py::test_real_app_cli_pty_command_uat_is_contained_and_provider_free`:
   fails before the PTY command sequence because `_framework_tools(runtime)`
   requires `FrameworkToolRegistryAdapter` but gets a different adapter. The
   test derives configuration from the dirty repository example. Causation is
   unproven; terminal command UAT did not complete.
3. `test_display.py::test_production_clear_emits_control_sequence_through_pty`:
   `select` observes no PTY output within one second after clear-screen. This
   establishes a failing local observation, not a diagnosed product defect.

No repairs or exclusions beyond the explicit live lane were made. Before an
affected construction unit, reproduce against a controlled baseline or record
an approved disposition. A failed baseline cannot be silently waived as a quirk.

## Contract-relevant observations

- Chat currently returns a `CommandResult` with display-ready `output: str`,
  handled/exit flags and a tuple of UI effects. It consumes concrete Chat runtime,
  session, maintenance/replay, security, speech and tool objects. The neutral
  owner needs explicit capability/result seams, not copied Chat object types.
- Chat uses whitespace splitting; the generic CLI preserves quoted strings.
  `/read "a b.txt"` becomes two quoted fragments in Chat's generic parser, one
  argument in generic CLI parsing. Individual Chat handlers may rejoin arguments;
  this probe does not claim the full `/read` behavior is broken. Parser replacement
  could change behavior and requires explicit characterization.
- Bare `/` produces an unknown-command result in Chat, but parses as non-command
  in the generic CLI. Generic CLI supports sync/async handlers and returns
  `str | None`; Chat awaits its typed handlers. Do not merge these contracts blindly.
- The `/q` and `/quit` probes request exit. `/clearscreen` returns one clear-screen
  UI-effect intent and no text; this is dispatch evidence, not proof that a real
  terminal cleared. Unknown names and plain text take their respective existing
  dispatch paths. Alias help includes `/quit` and `/q`.
- The installed workspace metadata declares `friday = friday_cli.main:app`, but
  entry-point loading raises `AttributeError` because `app` is absent. Chat's
  `friday-chat = friday_chat.cli:app` loads a Typer object; it was not invoked.
  Neither result establishes isolated installed-wheel behavior.
- Source search finds the generic registry implementation/export and package tests;
  Chat uses its own registry and imports generic CLI display utilities. This is
  evidence to preserve the generic registry separately until a small compatible
  shared primitive is justified; not proof of all external consumers.

## Next work and gate

Use the [PAR source ledger](par-coverage-ledger.md) to audit the exact existing
behavioral assertions and transitive effect/failure ordering per command. Add
fixture/result expectations and explicit inapplicability reasons; close the
baseline provenance/failure gaps before affected construction. Draft the exact
neutral API and capability ownership map, with separate adapters preserving each
parser/result contract. Build/isolated-install baselines and supported-platform
proof remain open. No phase completion, independent VERIFIED result, maintainer
acceptance or TUI construction authority is claimed.

## Follow-up controls

The [failure disposition](p0-failure-disposition.md) explains all three initial
failures. A full committed-example/xterm control passed 826 Chat tests. This
follow-up does not replace the dirty-worktree observations above.

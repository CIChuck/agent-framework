# FridayV2 Startup Config Remediation Plan

This plan fixes the post-parity gap where `packages/friday-chat` does not yet
match the startup presentation, response heartbeat, and effective system-prompt
behavior of the reference CLI at `tests/integration/memory/friday.py`.

## Problem

FridayV2 currently loads the main Friday runtime config, but it does not load the
companion CLI/client config used by the reference app. It also lacks the
interactive heartbeat shown while the user waits for model and tool-turn
responses. It also needs stricter proof that command-line startup uses the
configured `chat.system_prompt` everywhere the reference app uses it.

The reference startup path does three relevant things:

- Loads `cli-config.yaml` from the selected `config.yaml` sibling directory.
- Resets the terminal console and prints the Friday banner.
- Starts a thinking indicator immediately after prompt submission while waiting
  for the first no-tool streaming chunk.
- Starts a thinking or tool-processing indicator around each model call in a
  tool turn.
- Reads `chat.system_prompt` from `config.yaml`, then passes that prompt into
  transcript/session metadata and the interactive chat session.

## Decisions

- FridayV2 will use a comparable `cli-config.yaml` client configuration file.
- `cli-config.yaml` is not a secrets file. It should be safe to commit as an
  example or user-managed display preference file.
- The default migration path is sibling discovery:
  `friday-chat --config /path/to/config.yaml` looks for
  `/path/to/cli-config.yaml`.
- FridayV2 will also expose `--cli-config /path/to/cli-config.yaml` for explicit
  override.
- Implementation should reuse existing `friday-cli` package primitives where
  they are adequate: `CLIConfig`, `load_cli_config`, display helpers,
  `reset_console`, input helpers, and `ThinkingIndicator`.
- FridayV2 must provide visible progress feedback after prompt submission and
  during tool-turn model calls. This is a required CLI behavior, not cosmetic
  polish.
- No existing framework package source or tests may be modified during this
  remediation. If `friday-cli` needs improvements, log them in the framework
  upgrade log and adapt inside `packages/friday-chat`.

## Scope

Allowed files:

- `packages/friday-chat/src/friday_chat/`
- `packages/friday-chat/tests_chat/`
- `packages/friday-chat/config.example.yaml`
- `packages/friday-chat/cli-config.example.yaml`
- `scripts/run-friday-chat-example.sh`
- `scripts/source-friday-chat-example-env.sh`
- FridayV2 planning docs

Out of scope:

- Editing `tests/integration/memory/friday.py`
- Editing `tests/integration/memory/cli-config.yaml`
- Editing existing framework package source or tests
- Committing local secrets or local runtime state
- Replacing the main runtime `config.yaml` format

## User-Facing Startup Contract

Supported command forms:

```bash
friday-chat --runtime real --config packages/friday-chat/config.example.yaml
friday-chat --runtime real --config packages/friday-chat/config.example.yaml --cli-config packages/friday-chat/cli-config.example.yaml
```

Expected behavior:

- If `--cli-config` is present, FridayV2 loads that file.
- If `--cli-config` is absent and a sibling `cli-config.yaml` exists next to
  `--config`, FridayV2 loads the sibling file.
- If neither exists, FridayV2 starts with typed display defaults.
- Startup emits a banner or greeting before the first prompt.
- The input prompt, status icons, spinner messages, and display styles come from
  the effective CLI config.
- After the user submits a normal conversation turn, a thinking heartbeat starts
  before the LLM call and stops when the first streamed response chunk arrives,
  when the call completes without chunks, or when the turn fails/cancels.
- During a tool turn, the first model call uses a thinking heartbeat and later
  model calls use a tool-processing heartbeat. Each heartbeat stops in a
  `finally`-equivalent cleanup path.
- The effective base system prompt comes from `chat.system_prompt`.
- Speech prompt text is appended only when speech mode is enabled.
- Disabling speech restores the original configured base prompt.

## Implementation Steps

1. Add compatibility tests first.

   Add tests under `packages/friday-chat/tests_chat/compat/` proving sibling
   `cli-config.yaml` discovery, explicit `--cli-config` override, missing-file
   defaults, invalid YAML diagnostics, heartbeat lifecycle behavior, and
   shell-launcher command shape.

2. Add a FridayV2 display boundary.

   Add a small `friday_chat.display` module that adapts the existing
   `friday-cli` display primitives behind FridayV2-owned protocols. This keeps
   the app testable without binding core app tests to Rich globals.

3. Add CLI config resolution.

   Add a resolver that accepts the main config path and optional CLI config path,
   returns the effective CLI config, and records whether it came from an explicit
   path, sibling path, or defaults.

4. Update `friday_chat.cli`.

   Add `--cli-config`, load the display config before constructing the app, and
   pass the display boundary into `FridayChatApp`. Config errors should fail
   clearly before runtime services start.

5. Update `FridayChatApp` startup.

   Replace plain `input("> ")` and plain `print(...)` behavior for interactive
   runs with display-aware input and output adapters. Render the banner/greeting
   once during startup.

6. Add heartbeat/progress feedback.

   Add a FridayV2-owned heartbeat protocol and production adapter over
   `friday_cli.ThinkingIndicator`. Start it after prompt submission for no-tool
   conversation turns, stop it on first streamed chunk, and always stop it on
   completion, cancellation, timeout, retry exhaustion, or circuit-breaker
   failure. In tool turns, use the thinking message family for the first model
   call and the tool-processing message family for subsequent model calls.

7. Harden system prompt flow.

   Make the base prompt and effective prompt explicit in FridayV2 state. Ensure
   transcript/session creation, turn processing, context-budget calculation,
   `/prompt`, and `/debug` all use the configured effective prompt.

8. Preserve speech prompt behavior.

   Keep speech augmentation reversible. Speech commands should update the
   effective prompt from the immutable configured base prompt rather than
   repeatedly mutating the same string.

9. Add examples.

   Add `packages/friday-chat/cli-config.example.yaml` based on the reference
   `tests/integration/memory/cli-config.yaml`. Do not add secrets because this
   file has no secret material.

10. Update shell scripts.

   Update `scripts/run-friday-chat-example.sh` to pass
   `--cli-config packages/friday-chat/cli-config.example.yaml` when that file
   exists. Update the usage comments in
   `scripts/source-friday-chat-example-env.sh` to show the same command-line
   option. Keep the env script ignored because it contains local provider keys
   for the main runtime config.

11. Run validation.

    Run the package compatibility tests, package unit tests, lint, type checks,
    diff whitespace check, and a no-`uv` CLI smoke run through the launcher.

## Test Matrix

| Area | Required proof |
| --- | --- |
| CLI config sibling discovery | `--config tmp/config.yaml` loads `tmp/cli-config.yaml` |
| CLI config override | `--cli-config custom.yaml` wins over sibling config |
| CLI config defaults | No display config starts with typed defaults |
| CLI config validity | Invalid YAML or invalid section types fail with actionable diagnostics |
| Startup banner | App startup emits banner/greeting through a fake output/display sink |
| Conversation heartbeat | Prompt submission starts thinking heartbeat and stops on first chunk, completion, cancellation, timeout, and error |
| Tool-turn heartbeat | First tool-turn model call uses thinking heartbeat; later model calls use tool-processing heartbeat |
| Heartbeat config | Spinner type, styles, randomization, thinking messages, and tool messages come from effective `cli-config.yaml` |
| Prompt source | Startup uses `chat.system_prompt`, not a hard-coded default |
| Session metadata | Transcript/session metadata persists the configured system prompt |
| Turn processing | Prompt formatting and context budget use the effective configured prompt |
| Debug commands | `/prompt` and `/debug` expose the effective configured prompt |
| Speech | Enable appends speech instructions; disable restores the base prompt |
| Shell scripts | Launcher invokes `friday-chat` with `--config` and `--cli-config` |

## Acceptance Commands

```bash
uv run pytest packages/friday-chat/tests_chat/compat
uv run pytest packages/friday-chat/tests_chat
uv run ruff check packages/friday-chat
uv run mypy packages/friday-chat
git diff --check
printf '/q\n' | scripts/run-friday-chat-example.sh
```

## Completion Criteria

- The parity matrix rows for CLI display config, startup banner/greeting, and
  startup system prompt initialization move from `deferred` to `tested`.
- The parity matrix row for conversation and tool-turn heartbeat feedback moves
  from `deferred` to `tested`.
- Task 17 in the code-generation task list is fully checked.
- `packages/friday-chat/cli-config.example.yaml` exists and is secrets-free.
- The launcher and env-script usage comments include the new `--cli-config`
  option.
- No frozen framework package source or tests were changed.

# Friday Chat slash-command pruning review

**Status:** Historical source-backed recommendation, 2026-10-22. The seven-name
proposal below was superseded by the maintainer's scored
[command inventory](command-inventory.md#notes-and-decisions): five tool slash
commands and `/inject-payload` are selected for retirement within the shared
command refactor, while `/tools`, `/security-test` and `/speech-test` are
retained for now. In particular, the `/tool-budget` replacement advice below is no longer
valid because that command is among the selected retirements. This report
records why the original proposal was made; it does not amend the accepted
50-command parity baseline, Chat behavior or construction authority.

## Current baseline and review method

The live `build_default_registry()` has 50 canonical commands and three aliases:
`/quit`, `/q`, and `/clearscreen`. The source-derived [command
matrix](command-matrix.md) is still the accepted TUI migration inventory.
Focused, unchanged Chat tests covering command registry, session/memory, tools,
security/speech and legacy surface parity passed **46/46** on 2026-10-22:

```text
uv run pytest -q \
  packages/friday-chat/tests_chat/test_security_speech.py \
  packages/friday-chat/tests_chat/test_session_memory_commands.py \
  packages/friday-chat/tests_chat/test_tool_commands.py \
  packages/friday-chat/tests_chat/test_command_registry.py \
  packages/friday-chat/tests_chat/compat/test_command_surface_parity.py
```

This is code and documentation review, not usage telemetry. It establishes
current effects and documented workflows, not how often people invoke a name.
The separate `friday-framework-cli` registry is outside this review.

## Recommendation by candidate

| Current command | Source effect and user-facing exposure | First-pass recommendation and replacement |
| --- | --- | --- |
| `/set`, `/vars` | Set/list only `CommandContext.variables`; the only other production read is `/memory`'s `scoped_variables` count. The [CLI reference](../../../guides/09-cli-reference.md) explicitly limits them to command-context state. | **Retire together.** No application or runtime setting is changed by these commands. Remove the orphaned variable state and `/memory` metric in the same bounded change; normal runtime configuration and the TUI's separately specified model chooser remain authoritative. |
| `/prime` | The [handler](../../../../packages/friday-chat/src/friday_chat/commands/registry.py) reads configured `enabled` and `previous_sessions`; it does not load context. Its current help claims loading. `/memory` already reports both priming metrics. | **Retire.** Use `/memory` to inspect priming state. Preserve startup priming behavior itself. |
| `/speech-test` | Both `once` and `loop` make one call to Chat's deterministic speech adapter. The [speech guide](../../../guides/speech.md) states that neither proves provider audio and points to the standalone `SpeechHarness`. | **Retire from Chat/TUI.** Keep `/speech` configuration. Document the standalone harness as the actual test path; preserve direct adapter/harness tests. |
| `/security-test` | Runs four fixed `sanitize_payload` samples and increments Chat command-context counters. The [security guide](../../../guides/security-configuration-guidelines.md) says it does not prove the Core scanner or other tool paths. | **Retire from public Chat/TUI commands.** Keep deterministic sanitizer tests and actual-path security tests; keep `/security` and `/security-config` unchanged except that this test command no longer increments their counters. |
| `/inject-payload` | Stores one synthetic string on `CommandContext`; the next manual `/run-tool` appends it to a raw result before the command's narrow script-pattern handling. It does not exercise every tool path. | **Retire with `/security-test`.** Move the single-use synthetic-result regression to a disposable test fixture. Keep `/run-tool` and its actual execution/sanitization behavior. |
| `/recommend-tools` | Ranks registered tool names/descriptions/categories by query-word substring count and calls any positive match `high` confidence. The [tool guide](../../../guides/05-tools.md) and [troubleshooting guide](../../../guides/13-troubleshooting.md) mention it. | **Retire.** Direct users to `/tools` for the registered inventory and `/tool-budget` for selection/admission state. This deliberately drops heuristic ranking; neither replacement claims to recommend a tool. |
| `/debug-budget` | Reports configured `context_window` and `output_buffer`. `/memory` reports measured last-turn budget metrics, so these are different views. The [CLI reference](../../../guides/09-cli-reference.md) already discloses the distinction. | **Retain.** Correct its description to say “configured context window and output buffer” in the later command-contract unit. Do not silently replace it with `/memory`. |

If the seven retirements are accepted, the maintained command set becomes **43
canonical commands and three aliases**. `/clear` and `/cls`, interactive
`/replay`, startup replay, `/speech`, `/security`, `/run-tool`, `/tools`, and
`/tool-budget` remain. No new command is proposed.

## Compatibility and migration decision

**Recommended old-name behavior:** In the first release containing the prune,
exclude retired commands from normal help, completion and the TUI parity
matrix, but return a bounded migration message when a retired name is entered.
The message must not execute the old effect. It points to `/memory`, the
standalone speech harness, `/tools`/`/tool-budget`, or the documented
test-fixture path as applicable. A later removal of these name-only notices is
a separate decision. This keeps the public supported set at 43 while making
the alpha transition understandable. Friday Chat and TUI should use the same
retired-name behavior once both depend on the shared command owner;
`friday-framework-cli` is unchanged.

The source change must explicitly reconcile the historical
[`legacy_command_names.yaml`](../../../../packages/friday-chat/tests_chat/compat/fixtures/legacy_command_names.yaml)
test fixture rather than rewriting that frozen legacy list as though the
commands never existed. Record the accepted seven-name exception and check
every other legacy name/alias. The current [CLI reference](../../../guides/09-cli-reference.md),
tool/troubleshooting, speech and security guides need exact replacement text.
The decision register, vision, PRD, phase plan, command matrix, AC cases and
their validation inventory must be reconciled together before a reduced TUI
parity target is claimed. Historical accepted/archive documents stay historical.

## Construction boundary and stop point

Pruning is an intentional change to maintained Friday Chat behavior, not a
behavior-preserving shared-engine extraction. A proposed exact construction
directive must name the source/test/doc paths, old-name response, before/after
checks, installed-package gates and independent review. The current board
still names N03A-01 shell review and macOS physical UAT as the TUI next gate;
the existing shell directive does not authorize command edits. Do not change
source, tests, accepted command inventories or user guides until the exact
pruning decision and bounded directive are approved and the board/packet are
reconciled.

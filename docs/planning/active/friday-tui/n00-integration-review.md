# TUI-N00 source and integration review

**Status:** Source-backed planning review; no TUI product code or acceptance evidence

**Branch/authority:** `feature/friday-tui`; `design_only`

**Source revision:** `c34269867be50f71923c93c95a63236a35505812`

This review checks the first integration gate in the
[replacement plan](replacement-plan.md). It uses the maintained Chat application
as the command-behavior baseline while keeping the TUI independent of both
`friday-chat` and `friday-cli`. The [command matrix](command-matrix.md) and
[neutral-capability map](neutral-capability-map.md) remain the detailed route
inventory; neither is evidence that a TUI handler has run.

## Verified inventory and protected baseline

- The saved JSON command inventory matches the live
  [`build_default_registry()`](../../../../packages/friday-chat/src/friday_chat/commands/registry.py)
  for all 50 canonical names, three aliases, descriptions, categories, usage,
  argument metadata and details. All 50 PAR IDs appear exactly once in the
  neutral-capability map. The two non-slash routes and launcher options remain
  separately identified there.
- The existing [Chat session identity](../../../../packages/friday-chat/src/friday_chat/session.py)
  is a small dependency-free value object plus resolver. Chat runtime,
  application, replay, command context and transcript adapters already share
  the resolved identity. Its value validation and mismatch text are observable
  and must be characterized before extraction.
- The current [Chat loader](../../../../packages/friday-chat/src/friday_chat/config.py)
  owns compatible YAML models, diagnostics, environment interpolation and
  model-library binding. The headless
  [`RuntimeConfig`](../../../../packages/friday-runtime/src/friday_runtime/config.py)
  has different allowed keys, defaults and path rules. The
  [loader proposal](neutral-config-loader-contract.md) is therefore a distinct
  future extraction, not a substitute for session identity work.
- [`friday-llm`](../../../../packages/friday-llm/src/friday_llm/streaming.py)
  has typed reasoning and tool-call stream events, while the current
  [`FrameworkChatModel` text path](../../../../packages/friday-chat/src/friday_chat/adapters.py)
  yields only text and discards reasoning. The retained
  [MCP tool record](../../../../packages/friday-chat/src/friday_chat/tools/output.py)
  intentionally has empty arguments even when the callable received them.
  The event contract must capture actual invocation arguments before that
  record is created and must distinguish request from execution.
- [Chat shutdown](../../../../packages/friday-chat/src/friday_chat/app.py)
  stops MCP tools, uses maintenance coordination to close admission and drain
  work, then closes async clients. The headless
  [DI shutdown](../../../../packages/friday-runtime/src/friday_runtime/di.py)
  currently stops its MCP provider but does not establish equivalent Chat
  maintenance/transcript/client cleanup. A TUI cannot claim safe Quit by
  calling the headless shutdown alone.

Read-only baseline on this revision:

| Check | Observed result | Meaning |
| --- | --- | --- |
| Focused Chat identity, transcript, registry, CLI and config tests plus Runtime config/model-library tests | 108 passed | Before-code comparison only. |
| `packages/friday-cli/tests_cli` | 155 passed | Protected CLI package behavior baseline. |
| `friday-chat --version` and `--help` in the workspace environment | Exit 0; version `0.1.0a4`, expected launcher options and fake default | Launcher smoke baseline. Import also emitted LiteLLM's failed remote cost-map warning before falling back locally. |
| `friday --help` in the workspace environment | Exit 1: `ImportError: cannot import name 'app' from 'friday_cli.main'` | Existing console-entry limitation; TUI work does not fix or redefine it. |
| Import `friday_runtime` and inspect loaded modules | No `friday_chat` or `friday_cli` modules loaded | Before-code dependency-closure check, not proof of future installed closure. |

These commands used the current workspace environment; they do not establish
outside-checkout wheel behavior, Linux behavior, a TUI, or user UAT. Later
candidate checks must compare the same fixtures and CLI outcomes after each
neutral extraction without treating an existing CLI limitation as a new defect.
The repository-wide documentation lifecycle checker currently fails on six
absolute `/private/tmp/telem-01/review/...` links in the tracked
`friday-telemetry-rewire/validation/VAL-001/report.md`. That file is unchanged
in this TUI branch. The TUI packet's own Markdown/link check passes; the
unrelated broken links are not repaired under this initiative.

## Integration gates and order

1. [TUI-N01S](directives/CD-TUI-N01S-session-identity.md) is the first bounded
   candidate: move only the typed identity primitive into `friday-runtime`,
   re-export the same objects from Chat, and leave Chat session state and both
   CLI applications in place. It has its own exact scope and tests. The
   directive was approved on 2026-10-18 for this identity slice only.
2. TUI-N01A must close the
   [loader contract](neutral-config-loader-contract.md) before implementation:
   fix exported names, Chat facade/monkeypatch behavior, errors and path
   fixtures, with no service assembly. The existing proposal supplies the
   required semantics but is not yet an approved directive.
3. TUI-N01B/N01C must bind neutral effect, startup, ownership and ordered
   cleanup contracts against Chat's real and fake paths. The
   [startup contract](startup-bootstrap-contract.md) controls chooser/replay
   behavior; the [event/lifecycle proposal](neutral-event-lifecycle-contract.md)
   identifies cleanup stages. The loader alone does not create a runnable
   runtime.
4. TUI-N02A/N02B must bind provider-step, reasoning, tool request/admission,
   invocation and terminal events at the real neutral execution boundary.
   The [event/lifecycle proposal](neutral-event-lifecycle-contract.md)
   narrows their semantics. Typed `friday-llm` events can inform that contract, but text-only Chat
   streaming and retained MCP records do not satisfy it by themselves.
5. Each later command family receives a small directive, equivalent effect
   fixtures, after-code Chat/CLI regressions and rolling TUI UAT. Final macOS,
   Linux and real-provider UAT remain distinct acceptance gates.

The current executable gate is the approved N01S directive. All later contracts stay
design-only until their exact owners, signatures, failure cases and checks are
bound in separate directives. No product source, package metadata or existing
test was changed by this review.

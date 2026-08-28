# Planning

Active and proposed work for the Friday Agent Framework.

Contents:

- `build-plans/` - Active or proposed implementation plans.
- `backlog/` - Backlog notes.
- `features/` - Feature proposals.
- `prds/` - Product requirement documents and exploratory PRDs.
- `security/` - Security implementation plans.
- `upgrades/` - Source requirements for separately governed package upgrades.

## Active Planning Packets

FridayV2 is planned through an active planning packet:

- [FridayV2 feature inventory](features/friday-v2-feature-inventory.md)
- [Friday Chat V2 build plan](build-plans/friday-chat-v2-build-plan.md)
- [FridayV2 parity matrix](build-plans/friday-chat-v2-parity-matrix.md)
- [FridayV2 behavioral contracts](build-plans/friday-chat-v2-behavioral-contracts.md)
- [FridayV2 compatibility testing protocol](build-plans/friday-chat-v2-compatibility-testing-protocol.md)
- [FridayV2 framework upgrade log](build-plans/friday-chat-v2-framework-upgrade-log.md)
- [FridayV2 code generation task list](build-plans/friday-chat-v2-code-generation-task-list.md)
- [FridayV2 startup config remediation plan](build-plans/friday-chat-v2-startup-config-remediation-plan.md)
- [FridayV2 turn integration remediation plan](build-plans/friday-chat-v2-turn-integration-remediation-plan.md)

Use the feature inventory as the feature source map, the parity matrix as the
feature-loss guardrail, the behavioral contracts as the command and subsystem
rule source, the build plan as the implementation sequence, the code generation
task list as the step-by-step execution checklist, the compatibility testing
protocol as the release gate, and the startup config remediation plan as the
open repair plan for client config, banner/greeting, heartbeat, and effective
system-prompt startup parity. Use the turn integration remediation plan for
tool-call execution, prompt/context delivery, current-session history, and
background memory-work parity. The matrix should be updated as implementation
proceeds.

Configuration compatibility is a first-class FridayV2 migration requirement.
The current `tests/integration/memory/config.yaml` shape should be preserved as
the primary user-facing format unless a change is explicitly documented with a
compatibility adapter and tests.

Framework package stability is also a first-class FridayV2 implementation
requirement. Existing `packages/friday-*` framework packages are frozen during
the FridayV2 parity pass, except for the new `packages/friday-chat` app package
and minimal workspace metadata needed to run it. Framework changes discovered
during FridayV2 work must be recorded in the framework upgrade log for a
separate follow-up pass.

Move completed or superseded planning material to `../archive/`.

## Active Framework Upgrade Packets

The Friday LLM reasoning-controls upgrade was approved for implementation on
2026-08-27. The FridayV2 framework-package freeze is released only for its
documented implementation scope; TestPyPI and PyPI publication remain
separately gated:

- [Friday LLM reasoning and sampling controls requirement](upgrades/friday-llm/friday-llm-reasoning-and-sampling-controls-requirement.md)
- [Friday LLM tactical implementation and release plan](upgrades/friday-llm/friday-llm-reasoning-controls-tactical-implementation-plan.md)

The Friday Chat typed-LLM migration was approved for implementation on
2026-08-28. It adopts the Friday LLM `0.1.0a1` public contracts only for the
primary Chat model path, preserves legacy flat configuration for one
deprecation window, and defines independent implementation, live-provider,
TestPyPI, PyPI, and tagging gates. Implementation is complete, but clean
installation exposed an unsatisfiable published LLM dependency cohort. The
tactical plan records the required Memory, Runtime, and CLI `0.1.0a1` scope
amendment; the rejected Chat artifact must not be published:

- [Friday Chat typed LLM configuration migration tactical plan](upgrades/friday-chat/friday-chat-typed-llm-config-migration-tactical-plan.md)
- [Friday Chat typed LLM deferred consumer handoff](upgrades/friday-chat/friday-chat-typed-llm-deferred-consumer-handoff.md)

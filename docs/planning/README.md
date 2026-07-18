# Planning

Active and proposed work for the Friday Agent Framework.

Contents:

- `build-plans/` - Active or proposed implementation plans.
- `backlog/` - Backlog notes.
- `features/` - Feature proposals.
- `prds/` - Product requirement documents and exploratory PRDs.
- `security/` - Security implementation plans.

## Active Planning Packets

FridayV2 is planned through an active planning packet:

- [FridayV2 feature inventory](features/friday-v2-feature-inventory.md)
- [Friday Chat V2 build plan](build-plans/friday-chat-v2-build-plan.md)
- [FridayV2 parity matrix](build-plans/friday-chat-v2-parity-matrix.md)
- [FridayV2 behavioral contracts](build-plans/friday-chat-v2-behavioral-contracts.md)
- [FridayV2 compatibility testing protocol](build-plans/friday-chat-v2-compatibility-testing-protocol.md)
- [FridayV2 framework upgrade log](build-plans/friday-chat-v2-framework-upgrade-log.md)

Use the feature inventory as the feature source map, the parity matrix as the
feature-loss guardrail, the behavioral contracts as the command and subsystem
rule source, the build plan as the implementation sequence, and the
compatibility testing protocol as the release gate. The matrix should be updated
as implementation proceeds.

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

# TUI planning source provenance

This command packet is independent of the Friday TUI branch. Some earlier
command notes cited TUI planning written before the initiatives were separated.
Those citations are historical input, not a dependency on TUI source or a
current command contract. The source snapshot is `01cbaa0b` on
`feature/friday-tui`; the files are deliberately absent from this branch.

To inspect a source file in a local clone that has the TUI branch, use
`git show 01cbaa0b:<path>`. The command packet's scored inventory, matrix,
build plan, and reviewed future contract must make every current refactor
decision independently.

## Decisions

The original D-123 and D-77–D-82 citations refer to
`docs/planning/active/friday-tui/decisions.md` at `01cbaa0b`. D-123 proposed
one shared semantic command implementation with frontend-owned rendering.
Retirement and old-name behavior require an exact command contract in this
initiative before implementation.

## Per-command effect map

The original effect-map citation refers to
`docs/planning/active/friday-tui/neutral-capability-map.md` at `01cbaa0b`.
It is a TUI planning aid. Characterize live Chat and `friday-framework-cli`
effects afresh under this initiative's test strategy.

## Replacement plan

The original replacement-plan citation refers to
`docs/planning/active/friday-tui/replacement-plan.md` at `01cbaa0b`.
It governs later TUI integration, which remains deferred until this refactor
is completed, tested, and accepted.

## Phase build plan

The original phase-plan citation refers to
`docs/planning/active/friday-tui/planning/phase-build-plan.md` at `01cbaa0b`.
The TUI branch owns its future adapter, parity, and terminal UAT work. It does
not control command-refactor construction.

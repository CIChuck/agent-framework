# FridayContainer Disposition Record (Phase 3)

## Decision Context

Phase 3 requires a formal checkpoint for `FridayContainer` disposition while preserving compatibility constraints.

## Current State

1. `FridayContainer` remains present in `packages/friday-cli/src/friday_cli/container.py`.
2. Phase 3 implementation work in this cycle did not introduce breaking changes requiring immediate container abstraction removal.
3. Compatibility posture prioritizes stable runtime behavior over structural deprecation in the same release window.

## Disposition

`Retain wrapper for current release candidate; defer sunset decision until migration/rollback evidence set is expanded in next cycle.`

## Rationale

1. Preserves operational stability while Phase 3 orchestration contracts are being finalized.
2. Avoids coupling container-sunset risk to current compatibility-gate closure.
3. Aligns with phased governance approach in transition planning.

## Required Follow-ups

1. Produce explicit migration and rollback runbooks for any future container-sunset proposal.
2. Add targeted integration evidence for non-containerized runtime parity before disposition change.
3. Re-evaluate disposition in next planning checkpoint after closeout gates and baseline debt reduction.

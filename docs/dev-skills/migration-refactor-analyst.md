---
name: migration-refactor-analyst
description: Use when planning a major refactor, architecture replacement, schema migration, legacy removal, or old-vs-new implementation comparison. Focuses on current inventory, target inventory, object-by-object migration matrices, replace/adapt/split/retain/quarantine/remove/defer decisions, CLI/API migration, test migration, risks, and legacy rejection criteria.
metadata:
  short-description: Analyze migrations and architecture refactors
---

# Migration Refactor Analyst

Use this skill before a major refactor or architecture replacement.

The goal is to prevent old architecture from surviving under new names.

## Governing Standard

Follow `docs/methodology/constitution/gendev.md` when available.

## Inputs

Use:

- current codebase or code review;
- current architecture docs;
- target architecture specification;
- build plan;
- tactical planning prep;
- compatibility requirements;
- migration constraints.

## Classification Terms

Classify current objects as:

- replace;
- adapt;
- split;
- retain;
- quarantine;
- remove;
- defer.

Define these terms in the output so implementers cannot reinterpret them.

## Output Structure

Produce a Markdown migration/refactor analysis with:

- purpose;
- authority;
- executive finding;
- current implementation inventory;
- target object inventory;
- object-by-object migration matrix;
- superseded concepts;
- retained/adapted subsystems;
- removal requirements;
- schema/store migration requirements;
- CLI/API migration requirements;
- test migration requirements;
- risks;
- recommended migration sequence;
- acceptance criteria.

## Analysis Rules

- Compare old and new object models point by point.
- Identify old concepts that must fail validation.
- Identify old tests that must be rewritten rather than patched.
- Identify schema and persistence implications.
- Identify CLI/API behavior changes.
- Identify compatibility or no-compatibility policy.
- Mark deferred behavior clearly.

## Risk Focus

Look for:

- in-place renames that preserve old architecture;
- runtime behavior that bypasses new authority;
- mutable config remaining runtime authority;
- old schemas creating new records;
- old tests validating superseded behavior;
- security/governance drift.

## Completion Standard

The analysis is complete when a tactical implementation plan can include migration/removal as first-class work rather than cleanup.

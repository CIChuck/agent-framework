---
name: ai-construction-directive-builder
description: Use when creating construction directives or direct build prompts for Codex, Claude Code, Art, or similar AI implementation agents. Focuses on source authority, bounded scope, non-goals, implementation requirements, security constraints, tests, verification, documentation close-out, reporting, and anti-drift instructions.
metadata:
  short-description: Build AI implementation directives
---

# AI Construction Directive Builder

Use this skill to create implementation authority for an AI builder.

The goal is to produce a prompt/directive precise enough to guide implementation and strict enough to prevent drift.

## Governing Standard

Follow `docs/methodology/constitution/gendev.md` when available.

## Inputs

Use:

- tactical implementation plan;
- phase build plan;
- architecture specification;
- governance/security specification;
- PRD;
- migration/removal analysis;
- test/UAT plan.

## Output Structure

Produce a Markdown directive or prompt with:

- title;
- AI builder role;
- source authority and precedence;
- implementation objective;
- allowed scope;
- explicit non-goals;
- required workstreams;
- migration/removal instructions;
- security/governance requirements;
- testing requirements;
- verification commands;
- CLI/API/UAT requirements;
- documentation close-out;
- reporting requirements;
- stop conditions.

## Anti-Drift Requirements

Always instruct the AI builder:

- do not implement deferred features;
- do not broaden scope;
- do not silently change architecture;
- do not weaken security/governance behavior;
- do not remove unrelated code;
- do not mark planned behavior as implemented unless it is implemented;
- report skipped verification honestly.

## Accuracy Pass

Before finalizing, verify:

- every tactical workstream is represented;
- every required test category is included;
- non-goals are explicit;
- migration/removal behavior is explicit;
- documentation close-out is included;
- reporting requirements are clear.

## Completion Standard

The directive is complete when it can be sent to an implementation agent as the controlling build authority.

## Operational Coherence Requirements

A construction directive binds the implementation agent to accepted authority, stable tactical task
IDs, verification commands, negative tests, documentation close-out, and stop conditions. It must
not authorize unplanned requirements, architecture, governance, migration, deployment, or
blast-radius changes.

---
name: phase-build-planner
description: Use when defining build definitions or phase build plans from accepted PRD and architecture authority. Focuses on bounded scope, phase objectives, dependencies, deferred items, sequencing, risks, test strategy, migration behavior, acceptance criteria, and documentation close-out.
metadata:
  short-description: Plan bounded build phases
---

# Phase Build Planner

Use this skill to turn product and architecture authority into a bounded build phase.

The goal is to prevent feature smuggling and create a phase that can become a tactical implementation plan.

## Governing Standard

Follow `docs/methodology/constitution/gendev.md` when available.

## Inputs

Use:

- PRD;
- architecture specification;
- governance/security specification;
- build definition;
- prior phase reports;
- deferred feature backlog;
- code review findings, if applicable.

## Output Structure

Produce a Markdown build plan with:

- title;
- status;
- date;
- source authority;
- phase objective;
- in-scope work;
- out-of-scope work;
- deferred items;
- dependencies;
- assumptions;
- workstreams;
- sequencing;
- migration/removal requirements;
- security/governance implications;
- architecture mirror check;
- test strategy;
- CLI/API/UAT strategy;
- phase exit test traced to PRD requirements and the vision;
- acceptance criteria;
- documentation close-out;
- risks;
- open decisions.

## Scope Rules

- Label every major item as included, deferred, out of scope, or blocked.
- Do not let implementation details override architecture.
- If scope is too broad, recommend subphases.
- Make migration/removal work first-class for refactors.
- Make documentation close-out part of definition of done.

## Architecture Mirror Check

Hold the accepted G3 architecture up as a mirror: confirm the phase still conforms
to it, and surface anything the phase reveals that the architecture did not
anticipate. If the architecture must change, raise it as a regression against G3,
not as a silent phase decision.

## Accuracy Pass

Before finalizing, identify:

- scope ambiguity;
- deferred items that look included;
- included items without acceptance criteria;
- a phase exit test that does not trace to PRD requirements and the vision;
- an unperformed architecture mirror check;
- missing test strategy;
- missing migration work;
- missing security/governance work;
- unresolved decisions that block tactical planning.

## Completion Standard

The build plan is complete when a tactical implementation planner can convert it into executable workstreams.

## Operational Coherence Requirements

A phase plan must declare the coverage contract, phase sequence, integration criteria, and whether
any phase is deferred. Phase-specific planning is just in time: build plan, tactical plan,
construction directive, build prompt, test/UAT plan, review, remediation disposition,
traceability, and as-built evidence are produced for the active phase instead of fabricated for
future phases.

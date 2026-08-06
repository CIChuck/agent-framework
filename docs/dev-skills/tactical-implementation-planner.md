---
name: tactical-implementation-planner
description: Use when creating detailed tactical implementation plans from phase build plans and architecture authority. Focuses on executable workstreams, module/file ownership expectations, schema/API/CLI changes, migration order, test requirements, negative tests, verification commands, acceptance criteria, and documentation close-out.
metadata:
  short-description: Create executable tactical implementation plans
---

# Tactical Implementation Planner

Use this skill immediately before code generation or implementation delegation.

The goal is to convert phase intent into precise, testable, executable implementation work.

## Governing Standard

Follow `docs/methodology/constitution/gendev.md` when available.

## Inputs

Use:

- PRD;
- architecture specification;
- governance/security specification;
- phase build plan;
- migration/removal analysis, if applicable;
- code review findings, if applicable.

## Output Structure

Produce a Markdown tactical plan with:

- title;
- status;
- date;
- source authority and precedence;
- implementation objective;
- assumptions;
- non-goals;
- workstreams;
- file/module ownership expectations;
- data/schema changes;
- API/CLI/config changes;
- migration order;
- security/governance work;
- tests by workstream;
- negative tests;
- CLI/API/UAT checks;
- verification commands;
- acceptance criteria;
- documentation close-out;
- deferred items;
- risks.

## Workstream Rules

Each workstream must define:

- purpose;
- implementation tasks;
- affected areas;
- required tests;
- acceptance criteria;
- dependencies;
- non-goals.

## Accuracy Pass

Before finalizing, identify:

- missing implementation steps;
- vague ownership;
- missing tests;
- missing negative tests;
- missing migration steps;
- missing security/governance verification;
- missing CLI/API/UAT evidence;
- documentation close-out gaps;
- contradictions with source authority.

## Completion Standard

The plan is complete when an AI construction directive can be built from it without inventing scope, architecture, or tests.

## Operational Coherence Requirements

Use stable workstream/task IDs for every authorized implementation task. IDs must be durable enough
for implementation evidence, review findings, remediation records, and traceability rows to cite.
Declare dependencies and stop conditions explicitly.

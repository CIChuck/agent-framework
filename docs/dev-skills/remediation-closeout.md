---
name: remediation-closeout
description: Use when converting review findings into remediation prompts/plans and reconciling documentation after implementation. Focuses on finding-to-fix mapping, targeted remediation, tests, verification, documentation close-out, as-built status, deferred backlog updates, and residual risk.
metadata:
  short-description: Build remediation prompts and close-out docs
---

# Remediation Closeout

Use this skill after code review finds issues or after implementation is ready for documentation reconciliation.

The goal is to fix precisely what was found and make documentation match the as-built system.

## Governing Standard

Follow `docs/methodology/constitution/gendev.md` when available.

## Inputs

Use:

- code review report;
- remediation target scope;
- tactical implementation plan;
- construction directive;
- architecture specification;
- PRD;
- test results;
- implementation summary.

## Remediation Plan Structure

For each finding include:

- finding ID;
- severity;
- source authority violated;
- required code change;
- required test change;
- required documentation change;
- acceptance criteria;
- non-goals.

## Remediation Prompt Rules

Instruct the AI builder to:

- fix only listed findings;
- avoid unrelated refactors;
- preserve architecture;
- preserve security/governance behavior;
- add or update required tests;
- run relevant verification;
- report skipped verification;
- map each fix back to finding IDs.

## Documentation Close-Out

Update or identify needed updates to:

- developer guide;
- architecture docs;
- PRD status;
- CLI/API/config docs;
- examples;
- schemas;
- diagrams;
- traceability matrix;
- deferred backlog;
- known limitations;
- test evidence.

## Quality Rules

- Every finding must be covered exactly once.
- Do not introduce new scope through remediation.
- Do not describe planned behavior as implemented.
- Record residual risk.

## Completion Standard

Close-out is complete when findings are remediated or accepted, tests are evidenced, and docs match the implemented system.

## Operational Coherence Requirements

For each finding, record one disposition and the evidence that supports it. Close-out must reconcile
traceability, phase evidence, as-built behavior, deviations, known limitations, deferred items, and
any amendment or regression decisions. Do not mark planned behavior as implemented without evidence.

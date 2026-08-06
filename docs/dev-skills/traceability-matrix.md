---
name: traceability-matrix
description: Use when mapping requirements to architecture rules, build-plan items, tactical tasks, implementation areas, tests, UAT evidence, review findings, and documentation close-out. Identifies coverage gaps, untestable claims, unmapped tests, deferred items, and blocked requirements.
metadata:
  short-description: Build requirement-to-test traceability matrices
---

# Traceability Matrix

Use this skill to prove continuity from requirement to verification.

The goal is to ensure that requirements, architecture, implementation work, and tests remain connected.

## Governing Standard

Follow `docs/methodology/constitution/gendev.md` when available.

## Inputs

Use:

- PRD;
- architecture specification;
- governance/security specification;
- build plan;
- tactical implementation plan;
- test/UAT plan;
- code review report;
- implementation summary, if available.

## Matrix Columns

Use these default columns:

- requirement ID;
- requirement summary;
- source document;
- architecture rule;
- governance/security rule, if applicable;
- build-plan item;
- tactical task;
- implementation file/module, if known;
- test or UAT evidence;
- status;
- notes.

Status values:

- planned;
- implemented;
- verified;
- deferred;
- rejected;
- blocked.

## Gap Analysis

Identify:

- requirements without architecture coverage;
- architecture rules without implementation tasks;
- implementation tasks without tests;
- tests that do not map to requirements;
- security rules without negative tests;
- deferred requirements;
- blocked requirements;
- untestable or vague requirements.

## Quality Rules

- Do not invent implementation status without evidence.
- Keep IDs stable.
- Mark unknowns explicitly.
- Prefer precise file/module references when available.
- Use the matrix to drive remediation and close-out.

## Completion Standard

The matrix is complete when major requirements have visible architecture, implementation, and verification paths or are explicitly deferred/blocked.

## Operational Coherence Requirements

Traceability rows must distinguish planned, implemented, reviewed, and verified states. A row may
claim `verified` only when it cites real execution or UAT evidence and review status. Do not count
template examples, future commands, or legacy examples as approval evidence.

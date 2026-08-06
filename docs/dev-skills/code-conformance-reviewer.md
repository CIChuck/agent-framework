---
name: code-conformance-reviewer
description: Use when reviewing generated or human-written code against PRDs, architecture specifications, governance/security specifications, build plans, tactical implementation plans, construction directives, tests, and documentation close-out requirements. Focuses on spec drift, security risks, missing tests, CLI/UAT gaps, deferred-feature leakage, and engineering quality.
metadata:
  short-description: Review code against documented authority
---

# Code Conformance Reviewer

Use this skill after implementation or remediation.

The goal is to review whether code conforms to documented authority, not merely whether it looks reasonable.

## Governing Standard

Follow `docs/methodology/constitution/gendev.md` when available.

## Inputs

Use:

- PRD;
- architecture specification;
- governance/security specification;
- build plan;
- tactical implementation plan;
- construction directive;
- code diff or codebase;
- tests;
- prior review/remediation docs, if applicable.

Use fresh context for conformance review. Do not rely on the implementation agent's session
transcript, private reasoning trace, or broad conversational history unless the exception is
explicitly justified in the review report.

## Context Provenance

Record:

- reviewing agent;
- model/version;
- review context created on;
- inputs provided;
- authority document revisions used;
- implementation diff or commit reviewed;
- whether the implementer session was shared with reviewer;
- exceptions.

## Review Questions

Evaluate:

- did code drift from the specification?
- does code support documented assertions?
- is implementation internally consistent?
- does it preserve architecture boundaries?
- does it preserve security/governance behavior?
- are identity, permission, audit, approval, and policy requirements met?
- are required tests present and meaningful?
- are CLI/API/UAT surfaces implemented?
- were deferred features accidentally implemented?
- was documentation close-out completed?
- are there engineering quality risks?

## Finding Format

Use:

- finding ID;
- severity;
- affected files/modules;
- violated requirement or architecture rule;
- problem;
- risk;
- required remediation;
- required tests;
- documentation impact.

Order findings by severity.

## Review Modes

Full review:

- use when implementation is new or broad.

Delta review:

- use when reviewing remediation or a narrow update.
- focus on changed code and prior findings.

## Quality Rules

- Findings first.
- Be precise.
- Do not overstate risk.
- Identify residual risk if no findings remain.
- Do not change code unless explicitly requested.
- Preserve reviewer independence and record context provenance.

## Completion Standard

The review is complete when the user can decide whether to accept, remediate, or reopen planning.

## Operational Coherence Requirements

Report whether the review is per-phase or aggregate. Cite the exact reviewed revision, source
authority revisions, tactical task IDs, test/UAT evidence, and traceability rows. G6 readiness is
not final acceptance; G7 acceptance requires review/remediation disposition and human approval.

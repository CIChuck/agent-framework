---
name: governance-security-spec
description: Use when defining governance, security, identity, permission, policy, approval, audit, data sensitivity, tool access, agent identity, and threat-surface requirements for a project or phase. Especially important for agent platforms and systems with side effects.
metadata:
  short-description: Define security and governance specifications
---

# Governance Security Spec

Use this skill whenever a system involves agents, tools, automation, external APIs, secrets, persistent state, user data, file access, approvals, or side effects.

The goal is to make security and governance behavior explicit and testable.

## Governing Standard

Follow `docs/methodology/constitution/gendev.md` when available.

## Inputs

Use:

- PRD;
- architecture specification;
- known threat model;
- compliance constraints;
- current permission model;
- data sensitivity requirements;
- audit requirements.

## Output Structure

Produce a Markdown specification with:

- title;
- status;
- date;
- source authority;
- governance principles;
- identity model;
- actor model;
- permission model;
- authorization boundaries;
- policy model;
- approval model;
- audit model;
- data sensitivity model;
- secrets handling;
- trust boundaries;
- tool/external-system access rules;
- revocation/deactivation behavior;
- failure and recovery behavior;
- threat scenarios;
- security test requirements;
- negative test requirements;
- CLI/API inspection requirements;
- documentation close-out requirements.

## Agentic System Requirements

For agent platforms, explicitly define:

- durable agent identity;
- agent definition/version model;
- agent session model;
- agent participation records;
- agent effect records;
- tool-use attribution;
- artifact attribution;
- cross-run or cross-workflow lineage;
- approval requirements;
- policy decisions;
- audit records.

## Quality Rules

- Treat security requirements as musts, not preferences.
- Every governance rule needs a verification path.
- Define denial behavior, not just allowed behavior.
- Define what happens when approval is missing.
- Define who or what has authority to override policy.
- Define audit record shape for security-relevant behavior.

## Accuracy Pass

Before finalizing, identify:

- ambiguous identity or actor concepts;
- implicit permissions;
- missing denial behavior;
- missing audit records;
- untestable policy claims;
- missing revocation behavior;
- high-risk tool or side-effect gaps.

## Completion Standard

The specification is complete when security-sensitive behavior can be implemented and tested without inference.

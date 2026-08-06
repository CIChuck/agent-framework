---
name: vision-framing
description: Use when starting a new product, project, feature, refactor, or research effort and the user needs a clear vision/problem framing document before PRD, architecture, or implementation planning. Focuses on problem statement, users, outcomes, non-goals, success criteria, risks, assumptions, and open questions.
metadata:
  short-description: Create vision and problem framing documents
---

# Vision Framing

Use this skill before requirements, architecture, or build planning.

The goal is to convert a vague idea into a stable authority document that explains why the work exists and what success means.

## Governing Standard

Follow `docs/methodology/constitution/gendev.md` when available.

## Inputs

Collect or infer:

- project or feature name;
- problem being solved;
- target users/operators;
- current pain or opportunity;
- desired outcomes;
- known non-goals;
- constraints;
- security, governance, or compliance concerns;
- timeline or phase expectations;
- open questions.

Ask clarifying questions only when missing information would materially change the framing.

## Output Structure

Produce a Markdown document with:

- title;
- status;
- date;
- purpose;
- problem statement;
- target users/operators;
- user pain or opportunity;
- desired outcomes;
- success criteria;
- non-goals;
- assumptions;
- constraints;
- security/governance considerations;
- testability implications;
- risks;
- open questions;
- recommended next artifact.

## Quality Rules

- Do not prescribe implementation architecture.
- Separate facts from assumptions.
- Make success criteria observable.
- Make non-goals explicit.
- Identify what must be answered before PRD writing.
- If the idea is too broad, recommend phase boundaries.

## Completion Standard

The result is complete when a PRD author can use it without relying on chat history.

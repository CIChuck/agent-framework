---
name: prd-author
description: Use when turning a vision/problem framing document into a Product Requirements Document with stable requirement IDs, acceptance criteria in EARS form (for C2/C3), user workflows, functional and non-functional requirements, edge cases, non-goals, deferred items, and testability notes.
metadata:
  short-description: Write testable PRDs with requirement IDs
---

# PRD Author

Use this skill after vision/problem framing is stable.

The goal is to create a product requirements document that is specific, testable, and traceable without prematurely dictating implementation details.

## Governing Standard

Follow `docs/methodology/constitution/gendev.md` when available.

## Inputs

Use:

- vision/problem framing document;
- user/operator notes;
- known workflows;
- product constraints;
- security/governance expectations;
- known out-of-scope items.

If no vision document exists, recommend creating one first or clearly label assumptions.

## Output Structure

Produce a Markdown PRD with:

- title;
- status;
- date;
- source authority;
- product objective;
- target users;
- product context;
- requirements table with stable IDs;
- functional requirements;
- non-functional requirements;
- user workflows;
- edge cases;
- explicit non-goals;
- deferred items;
- acceptance criteria;
- security/governance requirements;
- observability/audit requirements when applicable;
- testability notes;
- open questions.

## Requirement Rules

Each requirement should include:

- stable ID;
- short name;
- requirement statement;
- priority or phase;
- acceptance criteria;
- testability notes;
- status: baseline, deferred, optional, or open.

### Acceptance Criteria Form (EARS)

For C2 and C3 projects, write acceptance criteria in EARS notation so each criterion
is structurally already a test and the G2 gate can be checked mechanically. C1
contained projects may use plain observable criteria.

- Ubiquitous: The system shall <response>.
- Event: When <trigger>, the system shall <response>.
- State: While <state>, the system shall <response>.
- Unwanted: If <condition>, then the system shall <response>.
- Optional: Where <feature>, the system shall <response>.

Where a requirement has error paths, include the unwanted-behavior (If/then) cases,
not only the happy path. Cross-cutting concerns (security, performance, operational,
deployment) appear as behavioral criteria in EARS form, not as a separate category.
EARS disciplines form, not correctness: a criterion can be EARS-formed and still
wrong, so human approval still certifies that it is right.

## Quality Rules

- Requirements must be observable or testable.
- Avoid architecture unless required by the vision.
- Mark ambiguity as open questions.
- Do not bury non-goals in prose.
- Highlight requirements that need security or governance treatment.

## Accuracy Pass

Before finalizing, identify:

- vague requirements;
- missing acceptance criteria;
- untestable claims;
- contradictions;
- scope that exceeds the vision;
- security/governance gaps;
- likely architecture questions.

## Completion Standard

The PRD is complete when architecture and test planning can begin without inventing product intent.




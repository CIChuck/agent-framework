# Development Skills

Repository-owned guidance for Friday planning, review and authorized execution.

Repository `AGENTS.md`, applicable policies, initiative authority and maintainer
direction govern each task. Copying, reading or discovering a skill does not
invoke its workflow. Explicit workflow invocation grants only its stated effects
within the user's scope; it never approves a product gate or accepts work.

## Authoring and review skills

- `vision-framing.md`
- `prd-author.md`
- `architecture-spec-author.md`
- `governance-security-spec.md`
- `phase-build-planner.md`
- `tactical-implementation-planner.md`
- `ai-construction-directive-builder.md`
- `independent-code-validator.md` — perform a fresh-context, read-only review of
  a frozen candidate and return evidence-backed `VERIFIED`,
  `CHANGES_REQUESTED`, or `BLOCKED`.
- `code-conformance-reviewer.md`
- `migration-refactor-analyst.md`
- `remediation-closeout.md`
- `traceability-matrix.md`
- [`friday-dev-board/SKILL.md`](friday-dev-board/SKILL.md) — operate current
  development tasks from the canonical board without inferring authorization.

## Execution workflows

- [Council](council/SKILL.md) — explicitly requested multi-provider review;
  scores remain advisory.
- [Sol loop](sol-loop/SKILL.md) — bounded advisory review and findings disposition.
- [File PR](file-pr/SKILL.md) — create or update the requested PR with the
  selected base and verified head.
- [Babysit PR](babysit-pr/SKILL.md) — monitor authorized PR work using the
  active harness's watcher and wait/resume mechanism.
- [Full send](full-send/SKILL.md) — explicitly requested completion through a
  merged PR, subject to approval, validation and branch-protection requirements.
- [Full stop](full-stop/SKILL.md) — explicitly requested PR preparation for
  human merge; ordinary stop/pause instructions do not invoke this workflow.
- [Leaving PR comments](leaving-pr-comments/SKILL.md) — attribution and evidence
  for comments that the user has authorized.
- [Modernize](modernize/SKILL.md) — reassess and update an existing PR against
  its actual base; assessment alone grants no mutation authority.
- [Takeover](takeover/SKILL.md) — continue inherited work while preserving
  intent, contributor credit and scope boundaries.

## Reference templates

These two documents have no skill metadata and are references rather than
standalone discoverable skills:

- [Subagent directives](subagent-directives-template.md) — dispatch a bounded builder, freeze its
  candidate, and hand it to a fresh-context read-only validator.
- [Worktree planning](subagets=worktrees-template.md) — retained with its historical filename until
  backlink-safe spelling correction is performed.

## Local discovery and packaging

This directory contains the maintained sources. Repository discovery entries
under `.agents/skills/` have not yet been deployed. Keep bundled scripts and
`agents/openai.yaml` alongside their skill when deploying; exclude `__pycache__/`
and `*.pyc`, which are already ignored by the repository. Preserve the two
reference templates as supporting documentation instead of installing them as
standalone skills.

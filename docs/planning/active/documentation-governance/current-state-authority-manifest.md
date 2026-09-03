# Current Development State And Authority Manifest

---
title: Current Development State And Authority Manifest
initiative: documentation-governance
document_type: authority-manifest
status: active
created: 2026-09-03
updated: 2026-09-03
branch: feature/docs-information-architecture-remediation
baseline_commit: 482b857507409fb73556e273f96acdce1c398480
release_baseline: v0.1.0a2
---

## Purpose

This manifest freezes the development state that existed before documentation
paths were reorganized. Directory placement is not authority. The documents and
Git evidence named here remain controlling until an explicit successor or
maintainer decision changes them.

## Repository Baseline

| Field | Value |
| --- | --- |
| Baseline date | 2026-09-03 |
| Integration branch | `master` |
| Local baseline | `482b857507409fb73556e273f96acdce1c398480` |
| Remote baseline | `origin/master` at `482b857507409fb73556e273f96acdce1c398480` |
| Remediation branch | `feature/docs-information-architecture-remediation` |
| Published source tag | `v0.1.0a2` at `fc8ea18` |
| End-user guide boundary | `docs/guides/` unchanged |

The worktree already contained an intentional, uncommitted spelling correction
from `docs/planning/build-plans/friday-chat-v2-aechive/` to
`docs/planning/build-plans/friday-chat-v2-archive/`. It also contained unrelated
tracked and untracked local files. Those files are preserved and are not evidence
of unfinished package implementation.

## Development State

| Initiative | State at baseline | Controlling authority | Next action |
| --- | --- | --- | --- |
| Friday package cohort `0.1.0a2` | Completed, merged, published, verified, and tagged | `docs/reference/releases/friday-package-cohort-0.1.0a2-release-evidence.md`; `docs/planning/upgrades/friday-packages/friday-framework-typed-llm-execution-log.md` | Archive completed planning material while retaining release evidence as reference |
| Typed LLM adoption across Friday packages | Completed | `docs/planning/upgrades/friday-packages/friday-framework-typed-llm-adoption-plan.md`; execution log above | No implementation action |
| Model-aware reasoning control | Deferred | `docs/planning/upgrades/friday-llm/friday-llm-model-aware-reasoning-control-deferred-feature.md` | Revisit only through separate approval |
| Friday Chat client-session shutdown | Live defect observed after release; not yet planned or implemented | Friday Chat behavioral contracts, especially clean shutdown and final resource cleanup requirements | Reproduce, identify resource ownership, create bounded remediation authority, test, and repair before another release |
| Friday MCP client enhancement | Draft and not authorized for implementation | `docs/planning/build-plans/friday-framework-mcp-enhancements.md`; draft tactical plan and construction directives | Review and approve the plan; then begin `MCP-WS-00` contract and policy foundation |
| Friday Chat V2 parity implementation | Completed historical packet with a newly corrected directory spelling | Friday Chat V2 behavioral contracts, parity matrix, task list, and compatibility protocol | Preserve as historical contract/evidence; repair backlinks and archive the packet |
| Reorganization Remediation 1 | Implemented and validated | `docs/planning/build-plans/construction-directives/reorg-remediation-1-construction-directive.md`; implementation commit `baed8f2` | Archive packet after separating any surviving follow-up |
| Friday Chat Command Remediation 1 | Implemented; Gates A-F passed | `docs/planning/build-plans/construction-directives/friday-chat-command-remediation-1-construction-directive.md`; completion commit `dbd840f` | Archive packet after preserving deferred and blocked items |
| Documentation information architecture | Active on isolated branch | `docs/planning/active/documentation-governance/README.md` | Complete DG-01 inventory and classification |

## Authority Rules During Migration

- The repository engineering policy remains the canonical engineering policy.
- Release evidence establishes publication state; a stale planning index cannot
  reopen a completed release.
- A behavioral contract remains evidence of required behavior even after its
  implementation packet is archived, unless a named current contract supersedes
  it.
- A draft build plan, tactical plan, or construction directive does not authorize
  implementation.
- An execution log and Git history establish completed work more reliably than a
  stale directory name or unchecked task-list placement.
- A moved document retains its exact lifecycle and approval state.
- Unresolved work found inside a completed packet must be split into a current
  follow-up before the parent packet is archived.

## Current Next-Step Chain

1. Complete documentation inventory and classification without changing package
   behavior.
2. Independently remediate the Friday Chat unclosed-client-session shutdown
   defect under its own authority and branch.
3. Review and approve the Friday MCP packet before any MCP implementation.
4. Once approved, begin MCP work at `MCP-WS-00`; runtime MCP loading is a later
   dependent workstream.

This ordering must remain visible in the planning dashboard after all path moves.

## Baseline Validation Evidence

The following read-only facts were checked immediately before this packet was
created:

- `git rev-parse HEAD` returned
  `482b857507409fb73556e273f96acdce1c398480`;
- `git rev-parse origin/master` returned the same commit;
- `git tag --points-at fc8ea18` returned `v0.1.0a2`;
- the production release evidence reports all 17 distributions published and
  post-publication verified; and
- all Friday MCP implementation documents inspected were still marked Draft.


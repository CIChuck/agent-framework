# Documentation Information Architecture Remediation

---
title: Documentation Information Architecture Remediation
initiative: documentation-governance
document_type: remediation-plan
status: active
created: 2026-09-03
updated: 2026-09-03
owner: repository maintainer
branch: feature/docs-information-architecture-remediation
baseline_commit: 482b857507409fb73556e273f96acdce1c398480
release_baseline: v0.1.0a2
next_gate: DG-08 maintainer final review
---

## Authorization

The repository maintainer authorized this remediation on 2026-09-03 and
required that it run on a completely separate feature branch so the entire
change can be reviewed or rolled back independently.

This document controls documentation-organization work on
`feature/docs-information-architecture-remediation`. It does not authorize new
framework features or changes to package behavior.

## Objective

Make the documentation tree easy to navigate and make the current development
state unambiguous by:

- organizing planning material by lifecycle and initiative;
- separating current authority from completed or superseded history;
- recording the controlling document and next action for every active effort;
- preserving backlinks and Git history during moves;
- validating lifecycle metadata and internal links; and
- keeping end-user guides unchanged.

## Source Authority And Precedence

1. Explicit maintainer instructions in the active task.
2. [Repository engineering policy](../../../reference/policies/repository-engineering-policy.md).
3. This remediation plan and its approved amendments.
4. The [current-state authority manifest](current-state-authority-manifest.md).
5. Initiative-specific requirements, architecture, build plans, tactical plans,
   construction directives, execution logs, and closeout evidence.
6. Current package source and tests for as-built behavior when historical
   documentation conflicts with implementation reality.

Moving a document never changes its approval state or authority. Authority may
change only through an explicit status update that identifies the maintainer
decision, successor, or closeout evidence.

## Scope

Included:

- `docs/README.md` and documentation landing/index pages;
- `docs/planning/`;
- `docs/architecture/`;
- `docs/reference/`;
- `docs/archive/`;
- `docs/dev-skills/`;
- internal repository references to moved documentation paths;
- focused tests or validation scripts whose sole purpose is documentation path
  or lifecycle integrity; and
- minimal repository metadata needed to prevent documentation-only generated
  files from recurring.

## Protected And Excluded Content

- `docs/guides/` is immutable for this remediation. No guide may be edited,
  renamed, moved, generated, or deleted.
- Package source behavior is out of scope.
- Local runtime state, `.friday/`, Chroma data, transcripts, caches, and provider
  credentials are out of scope.
- Untracked review documents and configuration backups are preserved and remain
  unstaged until the maintainer confirms whether they belong in this branch.
- Ignored credential and recovery-code material must not be opened, copied,
  staged, or committed. Its removal or relocation requires explicit maintainer
  authorization.

## Current Development Boundary

The documentation migration must preserve these facts:

- `master` and `origin/master` were both at `482b857` when this branch was
  created.
- The 17-package typed-LLM cohort `0.1.0a2` is merged, published to production
  PyPI, post-publication verified, and tagged `v0.1.0a2`.
- Model-aware reasoning controls are deferred.
- The observed Friday Chat unclosed-client-session shutdown defect is the next
  bounded remediation candidate. It has not yet been implemented.
- Friday MCP enhancement work is a draft feature packet. MCP implementation is
  not authorized; its next gate is plan review followed by `MCP-WS-00` approval.

The detailed evidence and controlling documents are recorded in the
[current-state authority manifest](current-state-authority-manifest.md).

## Target Information Architecture

```text
docs/
  README.md
  guides/                         # unchanged
  architecture/                   # current architecture and decisions
  planning/
    README.md                     # current-work dashboard
    active/<initiative>/
    queued/<initiative>/
    blocked/<initiative>/
    deferred/<initiative>/
    backlog/<initiative>/
  reference/
    README.md
    policies/
    specifications/
    providers/
    releases/
    security/
    testing/
  archive/
    README.md
    completed/<year>/<initiative>/
    superseded/<initiative>/
    research/
    source-materials/
  dev-skills/
```

Existing archive collections with meaningful provenance may remain grouped
under a clearly indexed compatibility directory rather than being flattened.

## Canonical Planning Statuses

Planning packets and controlling planning documents use exactly one of:

- `draft`: incomplete and not approved;
- `approved`: approved but implementation has not started;
- `active`: implementation or remediation is in progress;
- `blocked`: work cannot continue until a recorded condition changes;
- `deferred`: deliberately postponed but still potentially relevant;
- `completed`: implementation and required closeout evidence are complete;
- `superseded`: replaced by a named successor; or
- `archived`: retained history that is not current authority.

Publication and deployment are outcome evidence, not planning statuses. A
completed release packet records those outcomes in its closeout metadata.

## Initiative Packet Contract

Every active, queued, blocked, or deferred initiative has one directory with a
`README.md` that states:

- lifecycle status;
- controlling authority;
- scope and package boundaries;
- current implementation or release checkpoint;
- next action or approval gate;
- validation and closeout evidence;
- unresolved decisions and known debt; and
- predecessor and successor documents.

Supporting requirements, architecture, tactical plans, construction directives,
execution logs, and evidence remain with the initiative unless they become a
durable repository-wide reference.

## Migration Gates

### DG-00: Baseline And Containment

Status: complete

- Create the dedicated feature branch from the synchronized `master` baseline.
- Record the baseline commit and release tag.
- Preserve unrelated tracked and untracked state.
- Freeze `docs/guides/` for the full remediation.
- Create this controlling plan and the current-state authority manifest.

Acceptance:

- The remediation can be abandoned by deleting the feature branch without
  changing `master`.
- Current development and release state is visible without relying on directory
  placement.
- No user-owned untracked document or backup is staged.

### DG-01: Inventory And Classification

Status: complete

- Build a complete tracked-document inventory excluding `docs/guides/` content.
- Assign each document a role, lifecycle state, initiative, current authority,
  and proposed destination.
- Identify broken backlinks, duplicate authorities, stale status claims,
  misspellings, and sensitive local artifacts without reading secret contents.
- Present ambiguous classifications as explicit decisions rather than guessing.

Acceptance:

- Every moved document has one old-path-to-new-path manifest entry.
- Every active initiative has exactly one proposed controlling index.
- Ambiguous and user-owned files remain unmoved.

### DG-02: Navigation And Lifecycle Foundation

Status: complete

- Replace the stale planning index with a current-work dashboard.
- Expand the root, architecture, reference, and archive indexes.
- Introduce the lifecycle metadata contract without rewriting historical content.
- Document archive entry and exit rules.

Acceptance:

- A contributor can find current development state and next gates from
  `docs/README.md` within two links.
- Indexes distinguish current authority from historical evidence.

### DG-03: Existing Friday Chat Archive Rename

Status: complete

- Record the maintainer's spelling correction from
  `friday-chat-v2-aechive` to `friday-chat-v2-archive` as a Git rename.
- Move the completed packet to its final archive destination.
- Update every tracked backlink and path-based test.
- Do not change the seven document bodies except for links that cannot remain
  correct after the move.

Acceptance:

- Git recognizes the seven files as renames.
- No tracked reference uses `friday-chat-v2-aechive`.
- Path-based compatibility tests pass.

### DG-04: Completed And Superseded Packets

Status: complete

- Move completed typed-LLM, package-release, Friday Chat remediation, and other
  verified packets into `archive/completed/<year>/<initiative>/`.
- Move deprecated material into `archive/superseded/` and name a successor when
  one exists.
- Keep durable release evidence under `reference/releases/`.
- Split unresolved follow-ups out before archiving a parent packet.

Acceptance:

- No completed or superseded plan remains in an active planning lane.
- Every archived packet links to closeout evidence or clearly states why no
  implementation occurred.

### DG-05: Active, Queued, Blocked, Deferred, And Backlog Packets

Status: complete

- Group remaining documents by initiative.
- Place each packet in exactly one lifecycle lane.
- Reconcile stale status claims against Git history, execution logs, source,
  tests, and release evidence.
- Preserve unapproved plans as draft or queued; moving them must not imply
  authorization.

Acceptance:

- The planning dashboard lists every non-archived initiative and its next gate.
- Friday Chat shutdown remediation and Friday MCP authorization state are
  explicit.

### DG-06: Architecture And Reference Authority Review

Status: complete with an explicit hold on the mixed `reference/specs` collection

- Identify the canonical architecture and specification documents.
- Move historical drafts, source collections, and presentation artifacts to the
  appropriate archive lane.
- Preserve policies and release evidence as durable reference authority.
- Add indexes that explain which documents are normative.

Acceptance:

- No historical draft appears authoritative merely because it is in
  `reference/` or `architecture/`.
- Durable reference documents retain stable, indexed locations where practical.

### DG-07: Automated Integrity Checks

Status: complete

- Add a local documentation-lifecycle and link-integrity checker.
- Reject missing or invalid lifecycle metadata for current planning packets.
- Reject broken internal links and references to retired paths.
- Reject loose planning documents outside recognized lifecycle packets, with an
  explicit allowlist for transition compatibility if required.
- Verify that `docs/guides/` is byte-for-byte unchanged from the baseline.

Acceptance:

- The checker passes on the migrated tree.
- A focused test proves representative invalid states fail.

### DG-08: Validation And Closeout

Status: in progress; maintainer final review remains

- Run link, lifecycle, path-reference, Markdown, and whitespace checks.
- Run affected package tests for any path-based fixtures.
- Compare `docs/guides/` against baseline commit `482b857`.
- Review `git diff --summary`, `git diff --check`, and staged scope.
- Record remaining ambiguities and obtain an independent review before merge.

Acceptance:

- Validation evidence is recorded in this packet.
- No unrelated local file is committed.
- The branch can be merged or discarded as one independently reviewable change.

## Commit And Rollback Strategy

Use small, reviewable commits:

1. baseline authority and remediation plan;
2. corrected Friday Chat archive rename and backlinks;
3. completed and superseded packet migration;
4. current planning lanes and navigation indexes;
5. architecture/reference classification;
6. lifecycle validation and closeout evidence.

Do not use broad staging commands. Stage explicit paths only. Do not delete or
clean unrelated local state. Any gate can be rolled back by reverting its commit;
the whole remediation can be rolled back by abandoning the feature branch.

## Stop Conditions

Stop before moving or staging a document when:

- its current authority cannot be established;
- it contains or may contain credentials, recovery codes, or local runtime data;
- it is an untracked user-owned document without an explicit inclusion decision;
- the move would require changing end-user guide content;
- a path consumer cannot be updated and validated in the same gate;
- a move would silently change a plan's approval or implementation status; or
- the requested change conflicts with repository engineering policy.

## Maintainer Decisions

On 2026-09-03, the maintainer decided:

1. Include and classify the previously untracked Memory and tool-security review
   documents in this branch.
2. Remove the ignored PyPI recovery-code export after confirming that it is
   safely stored elsewhere. The file was removed without being opened or staged.
3. Keep this feature branch local until the maintainer completes final review.

Historical `docs/dev-skills/` remains a top-level contributor resource and will
receive an index. This default can be revisited during final review.

## Execution Record

### Baseline checkpoint

- Branch created from synchronized `master` and `origin/master` at `482b857`.
- Release baseline `v0.1.0a2` retained at `fc8ea18`.
- Authority and migration documents committed in `18ab7d1` and `5622481`.

### Structural migration

- Completed plans moved under `docs/archive/completed/2026/`.
- Deprecated and overtaken plans moved under `docs/archive/superseded/`.
- Current planning grouped under `active`, `queued`, `blocked`, `deferred`, and
  `backlog` initiative packets.
- Durable release records consolidated under `docs/reference/releases/`.
- The implemented model-library specification promoted to `docs/reference/llm/`.
- Raw Massive provider inputs moved to archive source material.
- Friday Chat V2 spelling correction recorded as Git renames, then moved to the
  completed archive.
- Approved Memory and tool-security reviews added to their queued initiative
  packets.
- Mixed `docs/reference/specs/` material left in place with an explicit
  classification warning; no wholesale authority assumption was made.
- `docs/guides/` remained unchanged.

### Validation evidence

- `python3 scripts/check-documentation-lifecycle.py`: passed, 282 Markdown files.
- Focused lifecycle and Friday Chat contract coverage: `3 passed`.
- Ruff for the checker, its test, and touched Python path consumers: passed.
- `git diff --check`: passed after whitespace cleanup.
- `git diff --quiet 482b857 -- docs/guides`: passed.

The branch remains local pending maintainer final review and explicit push
authorization.

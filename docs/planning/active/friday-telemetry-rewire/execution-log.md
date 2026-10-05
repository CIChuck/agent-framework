# Telemetry execution log

## 2026-10-04 — approval and construction preparation

- Maintainer direction: "approved", after the controller identified telemetry
  contract review, settling open decisions, and approval of the first slice.
- Recorded scope: provider-neutral initiative direction and first-slice
  preparation; Langfuse remains optional. The newly prepared CD-001 is pending
  approval rather than retroactively included in that decision.
- Work state: `approved`; execution phase: `planning`; validation state:
  `not_ready`. Product source/test changes: none.
- Preparation base: `2155a0fc51f5b20dea4e35c6cfc70f1d52002735` on `master`,
  matching local `origin/master` before branch preparation (no remote fetch).
- Preparation branch: `feature/friday-telemetry-rewire`; no preparation commit
  or frozen product candidate yet.
- Baseline board validation: passed, 25 tasks. Before recording approval, board
  `next` selected queued Memory V2; the maintainer's explicit telemetry selection
  controls this preparation. No Memory V2 authority was changed.
- Read current lifecycle, engineering, independent validation, and construction
  directive instructions. Source inventory confirms no Chat telemetry assembly,
  existing optional runtime/MCP injection, and mismatched composite child IDs.
- Prepared contract, tactical criteria, exact CD-001 product manifest, and
  deterministic verification requirements. Product baseline tests belong to
  the approved start checkpoint; they have not been run or claimed here.
- Next gate: approve CD-001, record tactical/contract approval, move packet and
  board to `started`, record baseline checks, then implement TELEM-01.
- Preparation verification: board validation passed (25 tasks), documentation
  lifecycle passed (392 Markdown files), and `git diff --check` passed.
- After approval, the board `next` command still selects higher-priority queued
  Memory V2. Telemetry remains explicitly selected by the maintainer for this
  work; existing queue priorities were preserved.

### Preserved pre-existing local path manifest

| Path | Initial state | Handling |
| --- | --- | --- |
| `.DS_Store` | modified | preserved |
| `family-tree.md` | deleted | preserved |
| `packages/friday-chat/config.example.yaml` | modified | preserved; no edits in this preparation |
| `docker-bench-security/` | untracked | preserved |
| `packages/friday-chat/config.example.yaml.pre-typed-llm-20260828.bak` | untracked | preserved |
| `packages/friday-sandbox/docker/Dockerfile.audit` | untracked | preserved |
| `docs/planning/queued/friday-tool-manifest-continuity/` | untracked | preserved |
| `docs/planning/board.yaml` | modified | preserved tool-continuity and telemetry proposal entries; only telemetry approval/event updated |
| `docs/planning/README.md` | modified generated view | regenerated from the preserved board |
| `docs/planning/queued/friday-telemetry-rewire/` | untracked draft packet | this task's authorized planning target |

## 2026-10-05 — CD-001 approved; TELEM-01 started

Maintainer explicitly directed "proceed" after the CD-001 approval request.
Contract and TELEM-01 tactical scope are approved with that directive.
Branch/base unchanged. Work state: `started`; execution phase: `implementation`;
validation state: `not_ready`. Later units remain unapproved. A SHA-256
manifest of unrelated local paths was saved outside the checkout before edits.
The packet moved from queued to active; baseline tests are running.

## 2026-10-05 — TELEM-01 builder checks and freeze preparation

Work state: `started`; execution phase: `validation`; validation state: `pending`.
Implementation and regression coverage are recorded in
[the implementation report](execution/implementation-report.md). Baseline:
675 passed / 5 skipped / 2 failures / 3 listener setup errors. Current package
run: 717 passed / 5 skipped / the same 2 failures / 3 setup errors. Focused:
129 passed. Affected Ruff and Python 3.13 mypy pass. All 64 preserved path hashes
match; no unrelated files are staged. Candidate board/dashboard blobs exclude
the unrelated tool-continuity task while the working versions retain it.
Next gate: freeze the candidate, pin its authority, and dispatch a fresh-context
read-only validator. The whole initiative is neither completed nor accepted.

Final preparation gates: board validation passed; documentation lifecycle
passed with 393 Markdown files; `git diff --check` passed. Authority SHA-256
manifest prepared before candidate freeze.

Raw package/baseline logs are stored as lossless gzip artifacts to retain
pytest output without staging its trailing-whitespace formatting.

## 2026-10-05 — VAL-001 CHANGES_REQUESTED

Frozen candidate: `0c7b6d4c416402443d140a5ee09abed70be34c69`. Fresh independent
review found VAL-001-F01: medium mandatory AC-05 ownership collision when
a replacement provider reuses a local span ID. AC-01 through AC-04 passed.
AC-06 still has an independently reproduced baseline PTY startup timing gate;
no waiver was inferred. Independent checks: 129 focused tests, 13 probes,
Ruff/mypy, board/docs, and 3 permitted loopback fixtures pass; collision probe
fails. Candidate/authority and all 2,015 tracked review files were unchanged.

Complete report and archival evidence: `validation/VAL-001/`. Work remains
`started`; execution phase: `remediation`; validation state: `changes_requested`.
Proposed REM-001 reconciles the public-ID collision contract and regression
coverage; proposed WVR-001 covers only the unchanged timing test, conditionally
on fresh remediation validation. Neither proposal is authorized yet. No source
was changed after freeze; no completion, acceptance, or delivery is claimed.

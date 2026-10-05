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

## 2026-10-05 — CD-001 A01 verification amendment approved

The maintainer directed "approved, proceed" after the independent construction
review returned CDR-001 and CDR-002 (both medium). Approval is recorded for
verification-profile and reporting corrections only. No product code or tests,
package metadata, behavior contract, REM-001, or WVR-001 is changed or approved.
The original directive review is retained in `validation/CDR-001/`, including
its complete original hash/state evidence bundle.

Documentation-only exemption: authorized by repository maintainer on 2026-10-05
through the quoted instruction; exact scope is CD-001, tactical AC-06 mapping,
verification profile, authority manifest, this log/index, directive review
artifacts/requests, and telemetry-only board/dashboard metadata. The reason is
to correct verification authority; runtime behavior cannot change. Appropriate
checks are board validation, documentation lifecycle, diff whitespace, exact
preservation hashes, and a fresh independent directive-readiness review.

A01 adds required repository Ruff and deterministic root pytest, with only the
two named live-model modules excluded under the existing no-live boundary.
It requires a frozen safety preflight before collection, stops for additional
unsafe paths, and never treats package suites or baseline failures as waivers.
Minimum-version evidence includes Python 3.10 mypy, syntax parsing, and explicit
stdlib/dependency API review alongside retained 3.13 typing. Future added checks
must compare preparation base and product candidate as retrospective evidence.
Old implementation reports and VAL-001 requests/results remain historical;
new authority requires fresh subsequent implementation validation.

Work state remains `started`; execution phase: `validation`; validation state:
`pending` for directive readiness, while implementation still has unresolved
VAL-001 findings. Next gate: fresh CD-001 A01 readiness review, then return to
separate REM-001 and WVR-001 decisions. Advisory contract clarifications are
retained in the review and deferred, without changing product authority.

A01 pre-freeze checks: board passed (25 working tasks), documentation lifecycle
passed (399 Markdown files), diff whitespace passed, and all 64 unrelated
preservation hashes matched. Product source/tests are unchanged. These are
documentation-amendment checks; newly required product gates remain unrun.

## 2026-10-05 — independent CD-001 A01 review: READY

Fresh-context read-only reviewer `/root/cd001_a01_reviewer` assessed frozen
authority candidate `6013be5e6c280a3c93f6686e0b53e7d7cd6b9bf3`. Complete
request, report, evidence, and original evidence bundle are retained in
`validation/CDR-002/`. Verdict: `READY` for directive readiness only;
this is not implementation `VERIFIED`, completion, or acceptance.

No product source/tests changed, no newly required product checks were claimed
as run, and no REM-001/WVR-001 authority was inferred. VAL-001 remains historical
defect/baseline evidence under the old authority; A01 requires fresh subsequent
implementation review after separately approved work and all required evidence.
Work remains `started`; execution phase: `remediation`; validation state:
`changes_requested`. Next gate: approve REM-001 for VAL-001-F01; decide WVR-001 and satisfy amended A01 verification before fresh implementation review.

Review-evidence closeout checks: board passed (25 working tasks), documentation
lifecycle passed (400 Markdown files), diff whitespace passed, and all 64
preserved entries matched. Product diff from candidate `0c7b6d4` is empty.
Only review metadata is added after the frozen authority review.

## 2026-10-05 — REM-001 approved; waiver deferred

Maintainer: "i Approve your recommendations. Continue." This approves the
recommended collision fix and rerun-first sequence. REM-001 and the necessary
CD-001 A02/contract identity amendment are approved. WVR-001 remains proposed;
no timing, typing, broad-gate, or other exception is granted. Published composite
IDs remain reserved for instance lifetime to prevent stale ends; finished
provider/payload references are released and cumulative ID retention is disclosed.

Branch is `feature/friday-telemetry-rewire`, HEAD before preparation `f953fc9`;
product candidate remains `0c7b6d4`. Board validation passes (25 tasks), while
board `next` still selects queued Memory V2. Maintainer explicitly selected
telemetry; no other task priority or authority changes. Existing 64-path
preservation manifest remains controlling. Work stays `started`; execution
phase: `validation`; validation state: `pending` for fresh A02 readiness review,
then implementation checks and independent delta/aggregate review. No source
change occurred before this authority preparation.

## 2026-10-05 — REM-001 implemented; candidate freeze preparation

CDR-003 independently returned READY at `98cc9e7` before source generation;
all eleven authority hashes remained unchanged. REM-001 changes only the three
approved product paths. Six deterministic regressions reproduce on old source;
135 focused tests and 14 reused synthetic probes pass after remediation.
Affected Ruff, mypy 3.10/3.13 and syntax pass. Full package matrix is 676/718/724
passes at preparation base/pre-remediation/remediation, with the same one timing
failure, five skips and three sandbox listener errors. Root Ruff has the exact
same 337 diagnostics; root pytest has the same duplicate-module collection
error. Actual installed 3.10 stdlib smoke passes, but package imports fail on
missing pydantic in that interpreter, on base and candidate. Full smoke is not
claimed passed. Newly required baseline checks are explicitly retrospective.

Warm isolated timing reruns still fail; no WVR-001 approval is inferred, and
its all-other-gates-pass condition remains unmet. Board/product authority and
unrelated 64-entry preservation remain intact. Full preflight, commands, hashes,
limits and reports are retained in the packet. Work stays `started`; execution
phase: `validation`; validation state: `pending`. Next gate: committed candidate
and fresh REM-001 delta plus aggregate TELEM-01 independent review.

Candidate preparation gates: working board passed (25 tasks), documentation
lifecycle passed (402 Markdown files), whitespace passed, and all 64 preservation
entries matched. Only named authorized paths enter the commit; the unrelated
tool-continuity board/dashboard edits remain outside the index.

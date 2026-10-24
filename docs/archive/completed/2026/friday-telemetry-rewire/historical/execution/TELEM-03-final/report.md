# TELEM-03 builder evidence

Status: stable candidate submitted for independent validation; not acceptance.
Date:2026-10-07. Candidate:dd543fd6a6819ec0c4fb2529fa384fea886f5509.
Unit base:4ca9baecdcdcf26fc5e8055b326c3a54cda36cb7.
Aggregate base:2155a0fc51f5b20dea4e35c6cfc70f1d52002735.

CD-003 implements a20-path subset of the approved28 targets. Closed version-one
LLM events replace the services' unsafe legacy hooks on four completion APIs and
both embedding APIs. Request, actual attempt and dispatched batch identities are
independent per invocation; no stream-held LLM span or process-global callback is
introduced. Presence-aware usage, final cumulative stream usage and bounded local
estimate provenance avoid fabricated counts/current-price/billing claims. Borrowed
Chat observers flow through canonical/legacy/fallback role factories. Shared legacy
extraction/compaction aliases retain identity and construction role. The declared
snapshot-publisher boundary preserves underlying bool values. Documentation records
the event consumer migration, legacy-helper safety exclusion and deferred work.

| Required check | Builder evidence |
| --- | --- |
| New four-file tests |105 pass, no skip |
| Chat+LLM+telemetry |1,115 pass, no skip |
| Root collection |2,997 collected |
| Root regressions |2,996 pass; one unchanged optional SciPy skip |
|13 owning-package trees |2,978 pass; same one optional skip |
| Unit Ruff |17 actual changed Python paths; exit0 |
| Full aggregate Ruff |120 paths derived from exact frozen diff; exit0 |
| Unit/aggregate Mypy |11/74 package source paths; genuine exit0 |
| Raw root Ruff |exit1;327 exact WVR-005 approved identities, no additional debt |
| Lock/board/dashboard/docs |independent commands exit0 |
| Static/API/preservation |24 current+19+19 accepted pins;120 ASTs;18 unchanged >=3.13.4 floors; existing dependency/lock/config selection and public call shapes retained |
| Actual SDK consumer |separate owned in-memory exporter:9 scalar-identical events across Debug/Composite/managed SDK,3 standalone spans and6 events in an accepted application span; no new LLM spans/channel/listener/global registration; owned exporter/worker closed |

Raw commands, cwd, sanitized environment, revision, path expansions, exits,
source-resolution/owned-worker audits and hashes are retained under `raw` with the
[artifact manifest](artifact-manifest.json). The immutable source candidate's fresh
tracked snapshot contains zero product overlays. All28 allowed target hashes equal
the last passing full-regression snapshot; those regression runs used the candidate
bytes before the product commit. A separate frozen-candidate SDK/scalar probe and
control/root-lint audits confirm the committed revision.267 protected tracked runtime
paths were omitted before every snapshot checkout. Only the13 approved unchanged
synthetic localhost nodes ran; new fixtures are fake-only. No live credentials,
remote/TLS endpoint, real state, provider readiness, dependency install or delivery.

Earlier failed evidence stays explicit: initial changed-source Mypy reported five
typing errors, corrected before the genuine passing11/74-source checks. first new-test run had10 test-double
failures, then corrected89 pass; expanded coverage105 pass. First package run had
one failure and15 setup errors because a disabled factory was called with a new
keyword. Runtime preserves its historical disabled call shape using the factories'
None defaults; enabled assembly forwards the same observer. The final full package,
root and owning runs pass without changing out-of-scope fixtures or adding exclusions.
The initial package-only112 aggregate lint expansion omitted eight historical
nonpackage Python paths; the independently corrected120-path gate passes. A static
helper's metadata inventory initially omitted the lab pyproject and was corrected to
all18; the original product controls/dependency floors did not change. Whole-file
pricing suppression is removed; no new suppression or waiver was added.

Root/owning skip is the existing
`packages/friday-memory/tests_memory/test_adapters/test_graph.py:250` optional
SciPy import (`No module named scipy`). The two explicit live LM Studio files remain
excluded exactly as approved. Warning counts are retained as observed, not hidden.
Raw root lint does not pass: WVR-005 separately covers only the pinned327 identities,
four archive hashes,17 lint configuration hashes, unchanged registry source/class AST,
Ruff0.14.10 and target. WVR-004 remains expired.

[Fresh-context VAL-008 request](../../validation/VAL-008/request.md) asks a read-only
validator to independently review the full unit and complete aggregate. Builder
checks and this report do not close that gate. Initiative remains started/local;
execution_phase validation, validation_state in_review. Maintainer acceptance,
TELEM-04/05 scope and delivery stay separate.

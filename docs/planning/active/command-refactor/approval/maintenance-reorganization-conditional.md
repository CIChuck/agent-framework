# MAINT-001 — fixed vectors and conditional construction approval

Maintainer: Chuck Russell. Recorded by Codex at `2026-11-10T16:05:14.348162+00:00`.
Exact instruction:

> Yes, add Astra's fixed vector requirement. Reinvoke the council. Proceed only if council scores 9.5 or greater.

This follows the completed document-readiness handoff and the recommendation to
make Astra's literal-vector test explicit before implementation. It authorizes
that bounded document/test-requirement amendment, fresh Astra/Sol high read-only
review, and subsequent bounded construction only if the controller confirms all
conditions below. It is not active implementation authority while reviews run.

## Exact conditional inputs

| Input relative to packet | SHA256 |
| --- | --- |
| `maintenance-reorganization-specification.md` | `56e3cd5fc75b402ab4aeda46f80807873b79a3df96debadb83164c2c0debfdad` |
| `directives/CD-CMD-MAINT-001-reorganization-order.md` | `931d42538d9f100392743d8e9826eec00b67297af788dd84e4453e820ebea2e7` |
| `validation/maintenance/construction-preparation-v4.json` | `66e940efd0271b03bd3ae5c358c1320cf30e4d0d474d3c278be67d5e593f8f4d` |
| `validation/maintenance/selection-digest-vectors.json` | `398b65267321aeda278c2f161aaefc306a71187e57655941afcf03774e8b41d5` |

Both fresh named reviewers must return VERIFIED, each with an independently
reported score >=9.5/10, and no mandatory findings may remain open. Do not average,
round up, use missing/provisional scores or let a score override a finding.
BLOCKED, missing score, lower score or open mandatory finding means stop and
report to Chuck Russell; no automated review loop to chase scores. Prior
round3 scores do not satisfy this new condition for changed directive bytes.

On a passing gate, record the exact candidate/reports/integrity and activation
before source edits. Continue only the directive's bounded implementation and
planned OpenAI implementation validation, then stop for human UAT/acceptance.
The human document-review opportunity before this requested council is satisfied
by the explicit revision/review instruction above. No additional providers or
reviewers are authorized. No live models/personal stores, configuration, dependency,
lock, cleanup, push, PR, merge or release authority is granted. Preserve unrelated
work and accepted MEMQ. A failed condition is not permission to broaden scope.

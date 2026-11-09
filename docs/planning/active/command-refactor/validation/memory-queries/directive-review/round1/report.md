# MEMQ directive council round 1 — CHANGES_REQUESTED

Frozen candidate: `76b949b2e621e7a44ddec6ed527784e781696c8c`.
This is directive/design readiness only. The historical outcome does not apply
unchanged to a corrected candidate. All original report bytes and hashes are
preserved in [evidence](evidence.json).

| Seat | Result | Score | Exact report |
| --- | --- | --- | --- |
| GPT-6.1 Sol/high | CHANGES_REQUESTED | 8.7/10 | [Sol](sol.txt) |
| GPT-6 Astra/high | CHANGES_REQUESTED | 8.5/10 | [Astra](astra.txt) |
| Claude Opus 5.5/high | CHANGES_REQUESTED | 8.3/10 | [Claude](claude.txt) |

Four mandatory findings were reconciled by evidence:

1. MEMQ-DIR-SOL-001 / MEMQ-DIR-ASTRA-001: D5 must name DIAG's 38-name retained
   SESSION neutral baseline; original SESSION's 24 plus 16 is only 40.
   Claude identified the same problem as advisory A3; it remains mandatory.
2. MEMQ-DIR-CLAUDE-001: precisely permit the 13-model existing contracts owner
   extension plus the three-name memory_queries row and its necessary import.
3. MEMQ-DIR-CLAUDE-002: classify existing format debt in memory.py/runtime.py/
   adapters.py in addition to registry.py, without broad reformatting.
4. MEMQ-DIR-CLAUDE-003: append an explanation of the erroneous 15:20Z
   preparation timestamp; preserve the original board event and log entry.

[Bounded correction directive](../../../../remediation/REM-CMD-MEMQ-DIR-001-readiness.md)
binds the authorized changes and verification. Other suggestions stay advisory;
no architecture, option R behavior, package or product scope is added.

All seats freshly replayed 76-case source captures and four supplemental cases,
plus bounded guard/comparator/docs checks, and returned matching frozen identities.
Claude also ran Commands/cohort 498, lint/types and private synthetic controls.
Historical owning-suite receipts remain inspected evidence, not reruns by the
controller. Future implementation/build/install proof was not requested here.

The controller independently corroborated 24/38/54 export arithmetic, per-file
formatting failures and the timestamp discrepancy. The [audit](controller-reconciliation-audit.json)
records unchanged reviewed identities; the [request](council-request.json) and
[manifest](frozen-manifest.json) preserve the exact round-1 freeze.

Known root Ruff534, test_display collection conflict and legacy format debt
remain failed/unwaived. Claude reported an external fetch changing Git's
FETCH_HEAD/objects; its origin was not established. It changed no reviewed
HEAD/index/worktree identity. The early import without -B produced no measured
cache write. No product conformance, acceptance or delivery result follows.

# REM-007 — Restore Malformed Native Tool-Call Compatibility

Status: Approved continuation within the existing REM-006 authorization
Date: 2026-09-28
Approved by: repository maintainer, through existing "fix them - proceed" instruction
Authorization: REM-006 approval/start `5145f0638fe644c97dc74e0dcf8f7657f8fbcd12`
Initiative: `friday-mcp`
Work unit: `MCP-WS-05`
Branch: `feature/friday-mcp-ws05-execution`
Reviewed candidate: `f24ed20f82eac0cbce17e4b86615497cc9993921`
Follow-up base: `446e3a6f4e445a456dcbe6ef25058e60af54fe53`
Original aggregate base: `a609f948fe2d869ac29d0cce29d22d9334cd7d08`
Original remediation base: `dd6a337eb2928ab4050ea70fb41dc77072210e34`
Finding: `VAL-012-F-001`, complete independent [VAL-012](../validation/VAL-012-report.md)

## Authority And Scope

Explicit maintainer direction, repository policies, accepted WS-00 through WS-04,
the approved WS-05 directive, approved REM-006 and complete VAL-012 control.
The maintainer's "fix them - proceed" authorized REM-006's eight paths, required
regressions and preservation of native compatibility. This continuation repairs
a regression introduced by that unfinished remediation within its existing file
manifest and mandatory REM006-AC03 / WS05-AC09 requirements. It adds no feature,
package, implementation path or external effect. The controller records this
requirement-preserving continuation of that approval; no new maintainer approval
or acceptance is inferred. Use the same separate remediator, not the validator.

Only these three already-approved implementation paths may change:

- `packages/friday-chat/src/friday_chat/tools/loop.py`
- `packages/friday-chat/tests_chat/test_mcp_execution_security.py`
- `docs/planning/active/friday-mcp/execution/REM-006-implementation-report.md`

Controller directive/start, review/evidence/status, index/queue/log and
board/dashboard are separate process artifacts. All other source, tests,
configuration, dependency files, authority and original review evidence stay
frozen. Preserve unrelated .DS_Store, deleted family-tree.md, docker-bench-security,
Chat config backup and Sandbox audit Dockerfile. Historical REM-006 report and
archive remain byte-exact in the reviewed candidate and original evidence bundle;
the unaccepted working report may append this follow-up and its new evidence.

## Finding And Required Correction

`VAL-012-F-001` is converted exactly once here. Native ID reservation performs set
membership on a non-string tool name. Present IDs with dictionary/list names,
in flat or function-object tool-call forms, raise TypeError before established
invalid-call filtering. Both original and remediation bases skipped these calls
with zero execution. Restore the explicit string guard at reservation while
preserving reservation of actual native IDs, valid MCP allocation/reconciliation,
strict transcript pairing, actual native identifiers and all original privacy fixes.
Do not catch broad TypeError, weaken parsing/DTO contracts, add casts/suppressions,
change failure thresholds, drop valid calls or refactor neighboring code.

Add regressions for dictionary/list names in both forms with present/missing IDs,
native-only/no-MCP and mixed valid native/MCP sequences. Assert invalid names never
execute or crash; valid names execute with native IDs unchanged and MCP pairs
consistent; existing failure handling remains unchanged. Use synthetic local
stdio peers and scratch SQLite only. No historical storage rewrite, real secrets,
provider credentials, network UAT, paid calls or delivery.

## Acceptance And Verification

| ID | Required evidence |
| --- | --- |
| REM007-AC01 | Numbered malformed-name regression closes for both call forms, both invalid name types, present/missing IDs, native-only and mixed calls; no exception or invalid execution; native identifiers preserved. |
| REM007-AC02 | Both original High findings remain closed; MCP ID reservations/reconciliation, pairing/storage, privacy/caps/security/failure/cancellation and accepted WS-04 selection/budgets remain intact. |
| REM007-AC03 | Exactly the three allowed paths change; prior authorities/review archives/other product bytes and all unrelated fingerprints remain intact. |
| REM007-AC04 | Required checks and public reproductions are complete and reproducible; stable candidate receives a new fresh read-only VAL-013 delta followed by the full original WS-05 aggregate, with no mandatory violation left. |

Run regressions first, then the full 18 required commands in VAL-012 against the
new candidate, adding the exact follow-up delta whitespace check. All twelve
affected aggregate sources receive unfiltered Python-3.13 typing. Retain complete
logs, command exits and unchanged baseline failure evidence; do not suppress new
errors. Reuse only explicitly identified unchanged baseline logs when a repeat
would add no evidence; never label inherited results fresh runs. Required package,
full-suite and independent review evidence remain distinct. The implementation
report appends exact source/test candidate, authority/finding mapping, counts,
all commands/results, cleanup and frozen preservation. A separately named scratch
archive may hold new evidence; original REM-006 archive/report member bytes stay
unchanged. Controller archives the new bundle as process metadata.

Start only after this continuation, canonical started/granted/current branch and
separate assignment are recorded. Stop for new implementation paths or authority
conflicts, unclassified failures, unsafe cleanup or missing evidence. This is the
second WS-05 remediation cycle; if fresh VAL-013 is unsuccessful, stop and return
remaining findings to the maintainer under the independent-validation policy.
After a stable commit mark VAL-012 superseded only for the changed candidate,
retain its complete evidence, and dispatch a new validator with fork_turns none.
A VERIFIED result permits a WS-05 closeout proposal, not maintainer acceptance,
WS-06+, initiative completion or delivery.

# Friday MCP Client Enhancement

---
title: Friday MCP Client Enhancement
initiative: friday-mcp
document_type: initiative-index
status: active
updated: 2026-09-28
next_gate: execute pinned fresh VAL-009 delta and complete WS-03 aggregate review
implementation_authority: granted for MCP-WS-00 through MCP-WS-03 with approved predecessor amendments
execution_phase: validation
validation_state: pending
---

Current checkpoint: fresh-context [VAL-008](validation/VAL-008-report.md)
completed the full frozen WS-03 aggregate review and returned
`CHANGES_REQUESTED` for one medium finding, F-001: collision diagnostics omit
both source identities, provider labels and bounded original-name summaries.
All required checks, predecessor baselines, ten criterion assessments,
independent probes and freeze checks are preserved in the unchanged report and
[archived evidence](validation/VAL-008-evidence.yaml). Fresh-agent capacity is
resolved. The maintainer explicitly approved the complete bounded
[REM-005 directive](remediation/REM-005-directive.md) and separate remediator
with "That's approved. Proceed." Approved execution may now correct only F-001,
add its regressions and reports, run required checks and freeze a replacement
candidate for fresh VAL-009 delta and full WS-03 aggregate review. Initiative
remains started/normal/local; accepted WS-00/01/02 remain intact. No WS-03
verification/acceptance, later-slice approval or delivery is inferred.

Separate remediator `/root/mcp_ws03_rem005` completed the exact eight-path
correction in candidate `d395acdba9e233cb226f54e6258575f480157cf1` from approval
checkpoint `215e54d`. The [REM-005 report](execution/REM-005-implementation-report.md)
records typed bounded both-source diagnostics, retained public history, privacy/
cleanup regressions and all required checks/baselines. The pinned
[VAL-009 request](validation/VAL-009-request.yaml) freezes the delta, complete
original WS-03 aggregate, twenty-two authority hashes, both report hashes,
six remediation/ten work-unit criteria and seventeen independent commands.
Request preparation is not dispatch or verification. Historical VAL-008 remains
byte-exact; [separate status](validation/VAL-008-status.yaml) supersedes it only
for decisions on this changed candidate.

The repository contains substantial standalone MCP client and server code.
Runtime-owned stdio startup/discovery/shutdown is implemented in a WS-02
candidate. REM-004 corrects the noisy-subprocess shutdown hang in frozen
candidate `a257f04`; fresh independent [VAL-007](validation/VAL-007-report.md)
verified both the delta and complete WS-02 aggregate with no findings,
including the prior startup-retry ownership correction. The
[WS-02 closeout](execution/WS-02-closeout.md) records explicit maintainer acceptance
on 2026-09-28. WS-00, WS-01 and WS-02 are accepted work units; the wider
initiative remains started and local.
WS-00 contracts and WS-01 strict
configuration are implemented and independently verified. WS-02 and its
bounded startup-cleanup/stdio-redaction amendment are approved;
WS-03 is now approved; later workstreams remain Draft. The
[2026-09-27 rebaseline](rebaseline-2026-09-27.md) distinguishes the existing
package from this integration initiative and narrows the first slice.

Controlling packet:

- [Build plan](build-plan.md) — proposed feature and architecture authority.
- [Tactical plan](tactical-plan.md) — proposed workstream ordering.
- [Current-code rebaseline](rebaseline-2026-09-27.md) — baseline evidence,
  workstream status, and outstanding decisions.
- [Design notes](design-notes.md) — historical input, not controlling authority.
- [Construction directives](directives/) — approved WS-00/01/02/03 and draft later slices.
- [Execution log](execution-log.md) — approval, baseline, and work-unit progress.
- [Ordered task queue](task-queue.md) — approved next action and dependency/approval gates for subsequent work.

The maintainer approved the rebaselined `MCP-WS-00` contracts/defaults-only
scope, stdio-only first-pass runtime posture, and no stored argument hashes by
default on 2026-09-27. Execution started on
`feature/friday-mcp-ws00-contracts` from baseline `20c70dd`. Local
implementation and focused checks are recorded in the
[WS-00 report](execution/WS-00-implementation-report.md). Independent
[VAL-001](validation/VAL-001-report.md) returned `CHANGES_REQUESTED` for two
contract findings. [REM-001](remediation/REM-001-directive.md) bounds the
required corrections. The maintainer authorized a separate remediator for the
cross-package architecture finding on 2026-09-27. REM-001 produced candidate
`b79754f`; [the report](execution/REM-001-implementation-report.md) records
its checks. Fresh independent [VAL-002](validation/VAL-002-report.md) verified
both the remediation delta and complete WS-00 candidate. The
[WS-00 work-unit closeout](execution/WS-00-closeout.md) records the result and
remaining boundaries. The wider `friday-mcp` initiative remains `started`.
At that closeout, WS-02 through WS-08 were draft, and runtime loading was not
authorized by that work-unit verdict. The maintainer accepted the WS-00 work-unit result and
approved the bounded [WS-01 directive](directives/ws-01-configuration-model-validation.md)
on 2026-09-27. WS-01 was implemented on
`feature/friday-mcp-ws01-config`.
The [WS-01 implementation report](execution/WS-01-implementation-report.md)
records the typed configuration model, tests, and known baseline failures.
Independent [VAL-003](validation/VAL-003-report.md) returned
`CHANGES_REQUESTED` for the MCP default mode and missing Friday Chat
config-consumption evidence. [REM-002](remediation/REM-002-directive.md)
bounds the fixes. A separate remediator and fresh delta plus aggregate
review were required for the corrected WS-01 verdict. The maintainer authorized the
separate REM-002 remediator on 2026-09-27. The remediator encountered the
directive's F-002 dependency stop condition before editing: a runtime-package test
cannot import downstream Friday Chat without an undeclared reverse
dependency. The maintainer approved moving only the F-002 compatibility test
to Friday Chat's test package. Revised REM-002 resumed within that scope;
candidate `dd6c65b` passed fresh delta and complete WS-01 aggregate review in
[VAL-004](validation/VAL-004-report.md). The
[REM-002 report](execution/REM-002-implementation-report.md) and
[WS-01 work-unit closeout](execution/WS-01-closeout.md) record the bounded
fixes, checks, and remaining gates. The maintainer explicitly accepted WS-01
on 2026-09-27. This is work-unit acceptance only; the wider initiative remains
`started` and delivery remains local.

The maintainer explicitly approved bounded WS-02 on 2026-09-27 with
"ws-02 approved". Execution preparation is on
`feature/friday-mcp-ws02-lifecycle` from accepted WS-01 checkpoint `a64e423`.
The [readiness checkpoint](execution/WS-02-readiness-checkpoint.md) reproduces
failed-handshake cleanup loss and identifies raw stdio logging below the
directive's allowed files. That inspection changed no source or tests. The
maintainer subsequently authorized the narrow amendment for MCP
`client/base.py` and `client/stdio.py` with "continue next steps", after the
scope request and defect explanation. The
[WS-02 implementation report](execution/WS-02-implementation-report.md)
records the lifecycle candidate and bounded verification. Fresh independent
[VAL-005](validation/VAL-005-report.md) returned `CHANGES_REQUESTED`: F-001
finds that failed-start retries can discard the retained provider/manager and
strand a live client after cleanup failure. That review required maintainer
authorization of a separate remediator under the bounded
[REM-003 directive](remediation/REM-003-directive.md). The maintainer replied
"proceed" on 2026-09-27, explicitly authorizing that correction and separate
remediator. The separate remediator committed `26f4d7d`; its
[implementation report](execution/REM-003-implementation-report.md) records
the bounded correction and regressions. Fresh
[VAL-006](validation/VAL-006-request.yaml) pinned the corrected candidate for
delta and complete WS-02 aggregate review. Its
[report](validation/VAL-006-report.md) verifies REM-003's delta but returns
aggregate `CHANGES_REQUESTED`: production stdio shutdown can hang after a child
is killed while unread stdout prevents pipe closure. This is one separate
high-severity finding, not renewed ownership loss. The
[REM-004 directive](remediation/REM-004-directive.md) limits the
correction to stdio transport cleanup, local regressions, and documentation.
The maintainer explicitly approved that scope and a separate remediator on
2026-09-28 with "aproved... make a list of next steps in our task queue".
The [task queue](task-queue.md) records the ordered next steps. Next is dispatch
of the authorized separate remediator and a committed scoped candidate;
this approval-recording turn made no product edits and dispatched no agent.
WS-03 and later still require their own approvals. Current
process fields describe WS-02, not a change to the independently verified and
accepted WS-00/01 results.

The maintainer subsequently said "proceed" after the readiness audit. The
attempt to dispatch `/root/mcp_ws02_rem004` returned `agent thread limit reached`;
attempting to resume the prior separate remediator returned the same error.
No supported close/reset operation is exposed. A readiness-only check confirmed
that existing `/root/mcp_ws01_val004` can be reassigned as the separate REM-004
remediator. It has now received the execution instruction: it previously
reviewed WS-01, did not build/remediate WS-02, and
will not validate its own new work. Remediation can proceed under the existing
approval without creating another thread. Fresh independent VAL-007 remains
mandatory and its capacity is unresolved; an existing reviewer will not be
relabeled fresh. The [queue](task-queue.md) and
[execution log](execution-log.md) record the capacity stop and bounded recovery
without granting later-workstream authority.

The separate remediator completed REM-004 in stable candidate
`a257f041d1d68f8aea2f5b9773df1b88acd82379`, with exactly the six approved
source/test/report paths. The [REM-004 report](execution/REM-004-implementation-report.md)
records bounded incremental pipe discard, finite process/task cleanup,
retained-owner retries, real direct/public-kernel noisy-peer regressions, and
all required checks. The controller checked scope, unchanged authority and
preserved unrelated work. Historical VAL-006 is superseded for current
decision purposes without changing its findings. The pinned
[VAL-007 request](validation/VAL-007-request.yaml) requires fresh read-only
delta and entire WS-02 aggregate review; request preparation is not dispatch
or verification. Execution phase is `validation`, validation state `pending`.
No WS-02 acceptance, later-workstream approval or delivery is inferred.

Fresh `/root/mcp_ws02_val007` was successfully created with `fork_turns: none`
after the remediator completed. It is performing the pinned read-only review;
the earlier capacity stop is historical, not a current blocker. Execution phase
remains `validation`, validation state is now `in_review`. No verdict exists yet.

VAL-007 subsequently returned delta, complete WS-02 aggregate and overall
`VERIFIED` on 2026-09-28 with no findings. Its complete report is preserved,
including all eighteen authority hashes, exact ranges, independent required
checks, production noisy-peer and incomplete-cleanup/retry probes, baseline
separation and residual limits. [WS-02 closeout](execution/WS-02-closeout.md)
records the verified work unit, not wider initiative completion. Current
execution phase is `closeout`, validation state `verified`; next gate is
explicit maintainer WS-02 acceptance. No acceptance or WS-03 authority has
been inferred. The wider initiative remains `started` and local.

The maintainer subsequently explicitly said "WS-02 accepted" on 2026-09-28.
That acceptance is recorded in the closeout and execution log for frozen
candidate `a257f041d1d68f8aea2f5b9773df1b88acd82379` and its complete VAL-007
review. Queue tasks 1–4 are complete. Next is bounded WS-03 directive/readiness
reconciliation, followed by an explicit approval request; no WS-03 code is
authorized. Current process fields now describe that next-slice preparation:
`execution_phase: planning`, `validation_state: not_ready`, not a reversal of
accepted WS-02's independently verified result. The wider initiative remains
`started` and local, with no packet archive or delivery transition.

Following the maintainer's "continue", WS-03 planning/readiness reconciliation
is complete at [the checkpoint](execution/WS-03-readiness-checkpoint.md).
The [revised WS-03 draft](directives/ws-03-tool-naming-metadata-registry.md)
uses the accepted handoff/normalizer/sidecar, exact edit paths, guarded registry
ownership, strict explicit includes, schema-specific sanitization and final
export caps, with ten criteria and fresh review requirements. It remains
unapproved. Next gate is explicit approval of that complete bounded directive;
no WS-03 branch, product edit or validator dispatch occurred. Current phase is
`planning`, validation state `not_ready`; accepted predecessors remain intact.

The maintainer subsequently said "ws-03 approved" on 2026-09-28, approving the
complete reconciled directive at checkpoint `2c0d6bd1fe481fff9bb180f9e6dfb4a9a2131641`.
Execution starts on `feature/friday-mcp-ws03-registry` from that frozen work-unit
base. Current phase is `implementation`, validation state `not_ready`.
Queue task 5 is complete and task 6 is in progress. A stable candidate and
fresh read-only VAL-008 are required before proposed closeout. No later-slice
authority, verification, acceptance, or delivery is inferred.

WS-03 builder candidate is frozen at
`397caa9898612cd989f6404951b3e1f5005dfac2`. The
[implementation report](execution/WS-03-implementation-report.md) records the
sixteen approved implementation paths, public contracts, checks and baselines.
[VAL-008 request](validation/VAL-008-request.yaml) pins exact candidate/base,
twenty controlling authority hashes, all ten criteria and independent checks.
Current phase validation, state pending; request preparation is not dispatch,
verification or acceptance. Accepted predecessors remain intact.

Attempted fresh `/root/mcp_ws03_val008` creation with `fork_turns: none` returned
`agent thread limit reached`. No reviewer was created or dispatched, and no
independent verdict exists. Existing contexts are completed historical workers,
not fresh reviewers; no supported close/reset action is exposed. Current
validation workflow is blocked on fresh-context capacity, distinct from a
validator's BLOCKED verdict. Board remains started/granted/local with condition
blocked. Resume the pinned request in a session with fresh-agent capacity;
do not rebuild the candidate or require redundant scope approval. Source/tests/
configuration and controlling authority remain frozen at `397caa9`.

Lifecycle policy requires the packet relocation to
`docs/planning/blocked/friday-mcp/`. Board/backlinks follow the new working
location. The request's relocation mapping preserves original candidate/authority
Git paths and byte hashes; no controlling document or product contents change.
The fresh reviewer resolved the request/mapping revision as `b8e1f04`, matched
all twenty authority hashes at start and closeout, and completed the review
without inherited parent/builder context. The original request and frozen
authority remain unchanged. Current result and next gate are recorded above.

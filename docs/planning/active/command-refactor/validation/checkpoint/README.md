# Command foundation checkpoint — aggregate delivery review

Date: 2026-11-06
Target: `master` in `CIChuck/agent-framework`
Base: `c34269867be50f71923c93c95a63236a35505812`
Status: CHANGES_REQUESTED at dea49607; bounded maintainer disposition pending before correction/push

## Maintainer authorization and scope

Chuck Russell agreed to the controller's checkpoint recommendation and directed
“i agree with your recommendations. proceed”. That authorizes classification
and preservation of remaining work, committing agreed checkpoint files, pushing
the current branch, opening a PR, aggregate review/required checks, merging,
then deleting the merged branch and creating `feature/command-retirement` from
updated `master`. It does not approve the retirement directive or TUI construction.

The checkpoint includes all existing committed branch work: command planning,
the accepted neutral foundation, separately verified legacy CLI/required-finance
metadata fixes, bounded MCP compatibility/schema/dispatch work and repository
governance/historical archives. Aggregate review covers the entire base-to-head
diff; individual prior verdicts do not replace that review.

The remaining authorized TUI planning transfer/reconciliation, active planning
state and follow-up backlog are included as documentation. Imported TUI source
and implementation verdicts remain historical; no TUI source is copied or
approved. The two unrelated working example configurations in
`packages/friday-chat/` are explicitly excluded from the PR and preserved
byte-for-byte, with protected hashes and private safety copies outside Git.

## Documentation-only preparation

This continuation adds no product implementation, tests, dependencies or lock
changes. It records the already-authorized planning transfer and repairs
historical navigation. The [link-repair receipt](../../../../reconciliation/2026-11-05-tui-active-planning/checkpoint-link-repairs.json)
records ten source links across four imported reports, with original/new file
hashes. Each link now identifies the exact historical source commit whose Git
object was checked; review verdicts and source content are unchanged. Original
transfer/relocation receipts retain their original snapshot meanings.

Maintainer: Chuck Russell; exemption date: 2026-11-06. The explicit checkpoint
instruction authorizes this documentation-only preparation under the policy's
lightweight-change exemption. Its scope is planning/approval/provenance and
relative-link correction only, so runtime behavior cannot change. Verification
is board/docs/whitespace validation, file/hash preservation and independent
aggregate inspection. Any needed product or behavioral repair leaves this
exemption and must receive its applicable bounded authority.

## Review and merge conditions

Freeze a stable candidate and pin its complete diff, exact authorities,
component directives/reports, tracked-file manifest, dirty exclusions and
required checks in the review request. A fresh-context, read-only validator
must inspect the complete branch and return VERIFIED before delivery.

Required evidence includes applicable MCP/Runtime/Chat regressions, the full
provider-free Chat control with committed examples/xterm, framework CLI,
foundation/cohort and board tests, focused static/type checks, package metadata,
lock consistency, isolated artifact/import behavior and archive/authority/link
integrity. Full root pytest and Ruff failures must be reproduced and separated
from new regressions. No live provider, credential, user-store or TUI acceptance
is authorized. Disposable loopback test servers may run; external application
network must be blocked.

GitHub reports `master` unprotected and no rulesets; the checkout has no CI
workflows. The connector lacked branch-protection administration access, so the
authenticated CLI independently confirmed `protected: false` and the specific
“Branch not protected” response. Recheck actual PR requirements and exact base/
head before merge; never treat missing CI as a passing CI run. Resolve any
required review/check first. Use a merge commit to retain reviewed commit
identities and authority provenance.

## After merge

Confirm remote merge and preservation of excluded work before deleting the old
branch. Create `feature/command-retirement` from updated `master`; align current
board/packet branch references and update the draft retirement source base,
recording administrative descendants separately. Keep frozen historical review
requests/directives/reports intact. Present the exact retirement directive for
approval before product work. The command-refactor initiative stays started;
foundation delivery does not claim whole-feature acceptance.

## Aggregate outcome and exact next decision

The [independent aggregate report](aggregate-report.md) returned
CHANGES_REQUESTED for AGG-001 (historical archival-board construction authority)
and AGG-002 (five new formatting failures). All seven test lanes pass: 3,116
tests total, including the full 826-test provider-free Chat control. Packaging,
typing, focused lint and archive integrity pass; disclosed broad debt remains.
[Durable receipts](aggregate-evidence.json) preserve the independent check evidence.

The controller prepared [CD-CMD-CHK-001](../../directives/CD-CMD-CHK-001-checkpoint-reconciliation.md)
for one explicit decision: permit retaining the exact inherited archival behavior
under a current one-time construction-gate exception, and authorize the five-file
AST-preserving formatter correction. No retrospective approval is inferred from
the prior publication instruction. After exact approval, perform only that
bounded correction and obtain fresh aggregate verification before delivery.
No product source has been changed by this review/disposition preparation.

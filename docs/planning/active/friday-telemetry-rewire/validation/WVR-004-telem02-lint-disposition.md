# WVR-004 approved disposition: TELEM-02 exact baseline lint disposition

Status: approved by Chuck Russell. Date: 2026-10-06.
Owner: Chuck Russell. Work unit: TELEM-02 / proposed CD-002 only.

WVR-002/WVR-003 expired after TELEM-01 acceptance and are historical evidence.
This is a fresh, separately approvable exception, not an automatic continuation.
The [scope](WVR-004-telem02-lint-scope.json) freezes exactly326 findings in four
immutable accepted MCP probe artifacts plus one UP046 in unchanged invariant
CommandRegistry. The original source/AST hashes, all17 lint-config hashes,
Ruff0.14.10 and py313 are included. Fresh unchanged root Ruff must independently
reproduce this exact sorted diagnostic multiset before construction readiness
and again at final candidate. The preparation-base raw579 also included252
closeout script findings, corrected only by byte-preserving evidence packaging,
not covered by this proposal. New source/test findings are never covered.

Archive edits would rewrite prior validation evidence. Modernizing the unchanged
registry header changes its publicly invariant generic contract. Preserve those
contracts while the bounded OTel work proceeds; no archive rewrite, registry
redesign, new suppression, rule exclusion or config change is permitted.

Only if the maintainer explicitly approves this proposal may raw root Ruff
exit1 with those exact327 identities be disposed for TELEM-02. Keep the nonzero
raw result and compare path/code/start/end/message, source/archive/config hashes
and tool/target. Any mismatch or other diagnostic fails. Changed-unit Ruff and
all tests, syntax, API, typing, lock and safety checks must pass; no other gate
is waived. Without separate WVR-004 approval, raw root lint remains a blocking
TELEM-02 acceptance gate. CD-002 approval alone supplies no lint exception.

Cleanup/follow-up: REM-004-HIST-01 (archive-validation policy) and
REM-004-GENERIC-01 (registry compatibility/lint policy) remain maintainer-owned.
Approval of this exact temporary disposition constitutes only a TELEM-02 scoped
policy decision before its acceptance, not permanent resolution of those items.
Consider a permanent policy separately before accepting work beyond TELEM-02.

Expiry: after the TELEM-02 acceptance decision, or immediately on any covered
content/AST/diagnostic identity, tool version/target, or lint configuration drift.
Renewal requires explicit maintainer approval and fresh independent review.
Evidence-only closeout does not extend unit scope. No source changes, public
services, exporter activation, credentials, costs, push/merge or release authority.

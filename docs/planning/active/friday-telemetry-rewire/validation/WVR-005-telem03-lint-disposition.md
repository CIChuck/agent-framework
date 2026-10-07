# Proposed WVR-005: TELEM-03 exact baseline lint disposition

Status: proposed; not approved. Date: 2026-10-06.
Owner: Chuck Russell. Scope: TELEM-03 / CD-003 only.

WVR-004 expired at TELEM-02 acceptance. This is a separately approvable proposal,
not renewal inferred from "proceed" or the initiative's started/granted state.
[Exact scope](WVR-005-telem03-lint-scope.json) retains the same 326 diagnostics in
four immutable accepted MCP probe artifacts and one UP046 in unchanged invariant
CommandRegistry. Freeze original source/class AST hashes, all 17 lint-config hashes,
Ruff 0.14.10 and py313. Fresh preparation root Ruff exits 1 with exactly these 327
identities; the [planning evidence](../execution/TELEM-03-planning/report.md)
records that as a failing raw result, not an approved disposition or PASS.

Reason: archive edits rewrite accepted validation evidence; mechanical registry
modernization changes its publicly invariant generic contract. Preserve both while
bounded safe LLM metrics proceed. No rule suppression, exclusion, config weakening,
archive rewrite, registry change or new source/test finding is covered.

If approved separately, permit only this exact nonzero root result for TELEM-03,
after fresh independent review/reconciliation and exact baseline/candidate matching.
Compare sorted path/code/start/end/message, archive/source/AST/config hashes and
tool/target. Every mismatch fails. Changed-unit/aggregate lint, typing, all tests,
API, lock, privacy, ownership and other gates require their normal pass result.
CD-003 approval alone supplies no exception.

Follow-ups: maintainer-owned REM-004-HIST-01 (archive evidence/lint policy) and
REM-004-GENERIC-01 (registry compatibility/lint policy). This temporary proposal does
not resolve those policy items. Cleanup point/expiry: TELEM-03 acceptance decision,
or immediately on covered identity/content/AST/tool/target/config drift. No carry
forward to TELEM-04/05; any renewal requires explicit approval and fresh review.

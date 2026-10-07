# Proposed WVR-006: TELEM-04 exact historical lint disposition

Status: proposed, not approved. Prepared2026-10-07.
Owner: Chuck Russell. Scope: TELEM-04/CD-004 only.

WVR-005 expires with TELEM-03 acceptance and supplies no authority for this unit.
This separate proposal covers only the same326 findings in four immutable accepted
MCP probe artifacts and one UP046 in unchanged invariant CommandRegistry. The
[exact scope](WVR-006-telem04-lint-scope.json) pins sorted diagnostic identities,
original archive/source/class AST hashes,17 configuration hashes, Ruff0.14.10 and
py313 target at preparation e6209e3. Fresh raw root Ruff exits1 with exactly327;
the [planning evidence](../execution/TELEM-04-planning/report.md) records comparison.

Reason: editing accepted archive probes rewrites evidence; mechanical PEP695
CommandRegistry modernization changes its invariant public generic contract.
Preserve those inputs while correlated execution work proceeds. No new finding,
source suppression, excluded file/rule, config weakening, archive/registry change,
typing/test/behavior failure or broader debt is covered. Raw root lint remains
nonpassing even if this narrow disposition is approved.

Approval must be explicit and separate from CD-004. Fresh independent review and
exact authority/baseline reconciliation are required before construction, then
baseline/candidate comparison in the full product review. Every identity/input
mismatch fails; changed-unit/aggregate lint and typing require exit0.

Follow-ups: maintainer-owned REM-004-HIST-01 and REM-004-GENERIC-01. Cleanup/expiry:
TELEM-04 acceptance or immediate identity/content/AST/tool/target/config drift.
This does not resolve those policy follow-ups or continue to TELEM-05.

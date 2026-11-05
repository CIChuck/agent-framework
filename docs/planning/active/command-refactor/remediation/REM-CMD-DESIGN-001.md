# REM-CMD-DESIGN-001 — bounded council documentation corrections

Date: 2026-11-05
Maintainer: Chuck Russell
Authorization: “approved resolve them” in response to the three council findings
Cycle: 1; documentation only; corrected candidate awaiting fresh review
Base: `fa94f180e95ba75022e81bb269b18543e6360e38`

## Scope and exclusions

Resolve SOL3-ARCH-001–003 and incorporate the related optional normalization
fixtures. Allowed: API/directive, active retirement instructions in test strategy,
canonical intent/inventory, approval/index/log, new review pins/request and this
finding record. Preserve the original council report and prior review manifests
as historical evidence. No product source, tests, package metadata, configs,
lockfiles, board lifecycle, baseline JSON snapshots or raw scored rows change.
Runtime behavior cannot change: only repository planning documents are edited.
This is a documentation-only exemption within the maintainer's explicit scope,
not a product-construction directive or design approval.

## Finding-to-correction and acceptance

| Finding | Disposition in corrected draft | Verification |
| --- | --- | --- |
| SOL3-ARCH-001 | Constructor table specifies scalar/model/union/enum/collection checks, strict booleans, exact TypeError/ValueError boundaries, immutable snapshots, request/spec identity and data/error/handled relationships. Directive binds independent negative fixtures for each. | Cross-check every public dataclass/alias/enum against table and FND-02 tests; no trusted-only bypass. |
| SOL3-ARCH-002 | Registration reconstructs one canonical stored spec after one-pass name/alias normalization and field trimming; blank alias/argument behavior and duplicate atomicity are explicit. Lookup/dispatch share stored identity and do not renormalize parsed keys. | Frozen source-derived parser/registration fixtures; before/after registry proof requirements and explicit response identity checks. |
| SOL3-ARCH-003 | Active test strategy and canonical intent/inventory now instruct nine removals. Historical six-name clarification and old open product questions are explicitly superseded. Raw scoring and old execution receipts remain historical. | Search active instructions for stale six/44/unsettled-prime wording; compare exact nine-name set and 41/3 target. |

Advisory SOL1-ARCH-A01 / SOL3-ARCH-ADV-001: adopted explicit //HELP, ///HELP,
slash/space order and normalized-collision fixtures. This clarifies current
Chat behavior and does not add shell quoting or change supported command syntax.
Blank aliases are explicitly rejected by the new foundation; existing default
aliases are unaffected. Future custom-registration adapter compatibility remains
a review obligation, not authorization to alter the existing Chat API now.

## Checks and limits

Run board and documentation lifecycle validation, whitespace checks, exact
source parser observations and no-product-diff/dirty-input preservation checks.
No new package exists, so constructor/registry tests are future implementation
requirements, not claimed passing tests. No broad suite rerun is needed for
these planning changes. A fresh independent review must evaluate the revised
candidate; no automatic council or replacement reviewer is authorized here.

## Review disposition

The prior individual VERIFIED reports and round-1 CHANGES_REQUESTED report stay
historical; none verifies the corrected bytes. The new pinned request describes
the required delta plus whole-foundation consistency check. Freeze a local
candidate and hand back for review. No design approval, P0/P1 closure, push,
merge, release, acceptance or implementation authority is inferred.

## Round 2 residual wording correction

Round 2 confirmed SOL3-ARCH-001/002 but found R2-SOL1-ARCH-001, a residual of
SOL3-ARCH-003 in command-pruning-review.md. After all reviewers completed, the
controller corrected that document under the same authorized retirement-wording
scope. Current guidance lists all nine/41+3; the old seven-name and notice
recommendations remain explicitly historical. No API/directive/approval byte
changed. See the round-2 report for the disagreement and review limitation.
No automatic delegate or third council round was started.

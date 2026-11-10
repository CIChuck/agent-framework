# REM-CMD-PILOT-D3-001 — installed inventory and origin proof

Authorization: bounded mechanical correction under the exact original pilot
approval and the maintainer's [two-member council direction](../approval/pilot-two-member-council.md).
Remediation cycle 1; branch `feature/command-retirement`; base `f4186b56`.
No new product behavior, API, dependency or contract decision is introduced.

## Required corrections

| Finding | Correction and acceptance proof |
| --- | --- |
| D3-SOL-001 | Enumerate actual Chat/Commands installed source/data file and directory sets; require exact equality and bytes against Git/wheel. Refuse symlinks and non-file members. Installer-generated dist-info metadata lives outside these package trees. The closed no-bytecode proof profile permits no generated package files or extra cache directories. Test unexpected source, data, empty directory, bytecode and symlink in private copied environments, normal/optimized; prove the copied interpreter/package roots first. |
| D3-SOL-002 | Validate both a module's file and every package search-path entry when present. Retain missing-origin refusal; test valid file with escaped-only and mixed valid/escaped package paths in normal/optimized modes. Apply the same origin checker inside the installed entry-point help subprocess. |

Allowed code: `validation/pilot/installed_probe.py` only. Keep all existing
positive and refusal checks. Required environment is recorded with a nonsecret
allowlist, including REVIEW_REPO and LITELLM_LOCAL_MODEL_COST_MAP (Claude ADV-04).
Correct the stale neutral README sentence about future Chat integration
(Claude ADV-05), an allowed documentation closeout. Other optional advisories
remain deferred; no test-label/private-helper/dispatch redesign is included.

Preserve package runtime/tests, dependency/lock, app/contracts, all frozen
approved contract/directive/harness/baseline and historical receipts/reports.
Record exact finding dispositions and known failed root gates. Rebuild clean
current artifacts and replay with pinned offline inputs; rerun both isolated
probes, old and new refusal controls and relevant static/metadata/docs checks.
Product/test source equivalence supports prior full-suite evidence; rerun any
suite if product/test bytes change or a new concern appears. No broad P0/P1,
family/TUI, acceptance or delivery claim follows these checks.

Freeze a new candidate/request, then obtain fresh read-only Claude/Sol delta
and full bounded D3/pilot aggregate review. Both mandatory findings require
independent closure. Scores cannot override conformance; two unsuccessful
remediation cycles return to the maintainer. New scope needs reconciliation.

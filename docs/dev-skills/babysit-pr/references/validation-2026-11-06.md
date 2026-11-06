# SKILL-MAINT-001 — independent validation closeout

Outcome: **VERIFIED** for scoped maintenance; maintainer acceptance unrecorded.
Date: 2026-11-06

This is a controller transcription of the final fresh-context validator's
returned report, with the two prior findings retained below. It does not change
the frozen deliverables or grant deployment, push, merge or release authority.

## Frozen identity and independence

- Candidate: `a66fb276dab6e1abdb5aba83c119c116389b6396`.
- Aggregate base: `f6f018150391dcf0ffa870258250f254eb22d899`.
- Final delta base: `c82461a405c02706a629d3ed83f1c1d1e67751fa`.
- Aggregate scope: 18 files, 1,659 insertions and seven deletions, all under
  `docs/dev-skills/`; no product files.
- Reviewer: independent Codex agent `/root/skill_maintenance_final_review`;
  exact model variant/context-creation timestamp unavailable. Review clock:
  November 6, 2026, 17:24:48 UTC.
- Fresh context without builder transcript/private reasoning; prior findings
  were delta-review inputs only. Read-only shared checkout, dirty outside the
  selected files. No edits, staging, commits, network effects or delegation.
- All six authority pins and 18 deliverable pins matched at start/end, including
  committed bytes. HEAD stayed pinned; the index remained empty and selected
  skill files had no working-tree differences.
- All 16,916 protected file hashes matched at start/end. The raw external
  preservation manifest hash was
  `14be56211db864896306cd4440d71632dd4eee31f9bb1a2e254150cb17ed23d3`.

The [review request](review-request-2026-11-06.json) retains the authority and
deliverable pins and original local input locations. Its protected snapshot
and baseline helper paths refer to temporary review inputs, not distributable
skill dependencies. The baseline is reproducible from the source revision below.

## Mandatory acceptance evidence

| Criterion | Independent result |
| --- | --- |
| Unknown required-check configuration prevents readiness | VERIFIED: either failed protection query produces an explicit unknown-configuration error and exit 1. Six bundled tests plus an independent 16-case matrix passed for green/ready, HTTP 403/404/429/500 and first/second source failure. No visible-check fetch followed failed discovery. |
| Successful discovery remains functional | VERIFIED: union/deduplication, successful empty results, green/ready success and unstarted required checks remaining pending are covered. Helper comparison shows only authorized refusal behavior and exit documentation changed. |
| T3 waiting and unwatch agree | VERIFIED: one watch is registered before turn yield, retained for continuation, and removed at actual handoff, blocker or decision request. Full-stop incorporates the handoff rule. |
| Formal validation precedes applicable delivery | VERIFIED: full-send/full-stop, modernize, sol-loop and standalone babysit explicitly freeze and pin the candidate, require fresh read-only independent VERIFIED, limit exemptions and invalidate review after candidate/authority changes. |
| Index and reference distinction | VERIFIED: nine execution workflows are indexed; two metadata-free templates are identified as references. All nine bundles validate; 22 unique metadata names and zero broken relative skill links. |
| Bytecode exclusion and preservation | VERIFIED: no bytecode in candidate/index; existing ignore rules match it; all protected hashes unchanged. |

## Independently reproduced checks

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s docs/dev-skills/babysit-pr/tests -v`:
  six tests passed.
- Ruff lint and format checks for `babysit-pr/tests/test_pr_wait.py`: passed.
- `quick_validate.py` checks for all nine imported bundles: valid. Independent
  metadata/link scan: 22 unique names, no duplicate names or broken skill links.
- `uv run python scripts/friday-dev-board.py validate`: passed, 36 tasks.
- `uv run python scripts/check-documentation-lifecycle.py`: exactly the four
  declared baseline TUI link failures; no new documentation failures.
- Worktree and aggregate `git diff --check`: passed.
- Candidate/baseline helper lint: one identical pre-existing SIM115 in `lock()`;
  no new lint issue.
- Regression suite against the original helper: ten failures, zero errors.
  The repaired helper passes, demonstrating that the tests detect the defect.

The final reviewer used offline/no-sync UV, disabled bytecode and Ruff caching.
Initial Ruff attempts rejected `RUFF_NO_CACHE=1`; corrected reruns using
`RUFF_NO_CACHE=true` passed as recorded. No required scoped check was skipped.

Baseline helper SHA-256:
`90393f85b95b78bff1b039744bdfb09dc88ff2b430e1c3df687ee6f449c97214`.
Controller independently confirmed those bytes in the methodology-v3 repository
at commit `cf3d781d200f057d8b1f1742d43bf5577968d2c4`, path
`docs/methodology/dev-skills/babysit-pr/scripts/pr-wait`.

## Prior findings and disposition

1. Round 1, `/root/skill_maintenance_review`, candidate `052c6aa657f6696a1f58710bdb1cf4d1147c8a1b`:
   CHANGES_REQUESTED, VAL-SKILL-MAINT-001 (medium). Standalone modernize and
   sol-loop permitted delivery without explicitly freezing/pinning the final
   candidate and obtaining fresh independent VERIFIED. Corrected only those
   two skill documents in `c82461a405c02706a629d3ed83f1c1d1e67751fa`.
2. Round 2, `/root/skill_maintenance_confirmation`, candidate `c82461a405c02706a629d3ed83f1c1d1e67751fa`:
   CHANGES_REQUESTED. VAL-SKILL-MAINT-001 resolved; VAL-SKILL-MAINT-002 (medium)
   identified the same omission in standalone babysit's fix/rebase/push path.
   Corrected only that document in `a66fb276dab6e1abdb5aba83c119c116389b6396`.
3. Final fresh review: VERIFIED for the delta and aggregate; no remaining
   mandatory violations. Earlier reports remain historical for their exact
   candidates and do not verify changed bytes.

Both earlier reviewers independently confirmed the helper behavior, required
checks, baseline limits and preservation; neither made repository edits.

## Limits and next gate

The four excluded broken links remain in imported TUI validation documents:
`N01B-04-before-code-export-path-characterization.md:37`,
`N01B-05-before-code-single-file-export-characterization.md:49`,
`N01B-06-before-code-all-session-export-characterization.md:37`, and
`VAL-N01B-07-prepush-a196e95a.md:35`. Helper SIM115 also remains baseline debt.
This is not a repository-wide cleanliness or live-provider claim.

No live GitHub/provider behavior, PR mutation or deployment was exercised.
Repository `.agents/skills/` deployment remains pending. The controller may
present this scoped maintenance for maintainer acceptance. No command-refactor
design, construction or phase approval is inferred.

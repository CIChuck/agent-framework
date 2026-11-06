# SEC-003 independent full work-unit review

VERIFIED

## Candidate and authority

- Initiative: `friday-deprecated-credential-cleanup`; directive: `CD-SEC-003`.
- Base: `53df04a94d1085aa4f3b6de8dba0db254879c29c`.
- Candidate: `494febf7d3eb128ec26b9f777428324cd939ce8e`.
- Exact reviewed range: `53df04a94d1085aa4f3b6de8dba0db254879c29c..494febf7d3eb128ec26b9f777428324cd939ce8e`.
- Review mode: fresh, read-only, full bounded work-unit review. Candidate checkout was clean at review and final recheck. Main checkout had the same installed HEAD with unrelated working-tree changes retained.
- Authority manifest SHA256: `4493d3d312ae5082cd1a7daf0c0db7f7139e1b59ecf25ead5de9ad7837b4a100`.
- Directive SHA256: `6814bf5fcd2125c4c133a2fefb31bc8df6d014c0b786f60141d93279a092648d`.
- All read operational/engineering/validation authority content hashes appear in [authority hashes](authority-hashes.json).

The contextual authorization is untracking and ignoring `tests/integration/memory/` while retaining local files. The directive expressly records the maintainer's wording and contextual interpretation. The current controller request confirms this scope and explicitly forbids local deletion. The current credential confirmation is maintainer-reported rotation and retirement, with no issuer-side validation.

## Reviewer and independence

Reviewer: `/root/sec003_untracking_review`, a separate fresh agent instance. Exact model/version was unavailable to the reviewer. Review occurred on 2026-10-15 UTC (2026-10-14 America/New_York); final preservation/candidate recheck was `2026-10-15T01:29:52.313412+00:00`.

The reviewer received the controller's frozen task request, scoped safety constraints, artifact locations and claimed builder checks, without the builder's private reasoning or implementation session. Builder conclusions were not adopted. The candidate, safe metadata diff, authority, run scripts, guard and hashed raw check outputs were examined directly. The reviewer independently reran all focused checks and metadata verification. This report and evidence are outside both checkouts. No candidate/root edits, data moves, staging, commits, branch mutations or external calls were performed by the reviewer.

## Findings

No mandatory requirement violation or unresolved blocker, critical or high finding was found.

## Requirement-to-evidence matrix

| CD-SEC-003 criterion | Evidence and result |
| --- | --- |
| 1. Zero tracked descendants and intact local files | [Metadata verifier](verify_metadata.py), [result](metadata.json): both candidate and main index have zero tracked descendants. Exact 287-path removal set equals authority. All 287 main-checkout inventory records match inode, size, mtime_ns and mode before and after independent checks. Local database contents were never read. |
| 2. Entire subtree ignored, including new paths | Verifier calls `git check-ignore --no-index -v` in both checkouts for hypothetical immediate and deeply nested new files. Both resolve to anchored `/tests/integration/memory/`. The complete `.gitignore` diff only replaces the narrow retired-config rule/comment with the folder rule/comment. |
| 3. Compatibility, board, documentation, render and whitespace checks | Independent [runner](run_independent_checks.py) and receipts linked below: 30 compatibility tests pass, board validates 27 tasks, documentation validates 585 Markdown files, render is current, whitespace passes. Builder raw outputs and receipt hashes were independently verified against the exact final candidate; all five recorded runs attest private directory unavailable and restored. Independent rerun additionally denies every Python open of the private deprecated subtree, without moving it. |
| 4. Exact product scope and unrelated preservation | Verifier compares complete `git diff --no-renames --name-status` set against authority: exact 287 deletions, `.gitignore`, and packet/board metadata only. No source/runtime/package-test modifications occur in this unit. All 16 non-board/README snapshot entries retain their hashes or prior absence; the two intentional planning overlays are independently checked for unchanged unrelated tasks/events and the exact selected next-gate README replacement. Main staged diff is empty. |
| 5. Fresh full review before completion | This independent report reviews the frozen candidate. Candidate board and packet remain started/granted, validation pending, and name SEC-003 independent review as the next gate. No completion or acceptance is inferred. |
| Credential confirmation provenance and non-goals | Candidate confirmation explicitly says maintainer-confirmed rotation/retirement and no provider requests/issuer verification. No scans, key use, deletion, history rewrite, provider access, installation, push or publication occurred. |

## Commands and exact results

The following reproducible scripts contain the full commands and use absolute private paths. No deleted-file content diff was requested. The safe diff was confined to `.gitignore`, packet and planning metadata; all removal inspection used path/status/tree/index metadata only.

- `/private/tmp/friday-mcp-upgrade/venv/bin/python .../sec003-review/verify_metadata.py`: exit 0 twice, before and after independent checks. See [script](verify_metadata.py) and [result](metadata.json).
- `/private/tmp/friday-mcp-upgrade/venv/bin/python .../sec003-review/run_independent_checks.py`: exit 0. See [script](run_independent_checks.py).
- Focused pytest through the runner's additional deprecated-directory read-denial bootstrap: exit 0, `30 passed in 3.08s`; [receipt](compat-protected/receipt.json), [stdout](compat-protected/stdout), [stderr](compat-protected/stderr).
- `python scripts/friday-dev-board.py validate`: exit 0, `Development board validation passed: 27 tasks`; [receipt](board/receipt.json).
- `python scripts/check-documentation-lifecycle.py`: exit 0, `Documentation lifecycle validation passed: 585 Markdown files checked`; [receipt](docs/receipt.json).
- `python scripts/friday-dev-board.py render --check`: exit 0, `Planning dashboard is current`; [receipt](render/receipt.json).
- `git diff --check 53df04a94d1085aa4f3b6de8dba0db254879c29c..494febf7d3eb128ec26b9f777428324cd939ce8e`: exit 0, no output; [receipt](whitespace/receipt.json).

The runner supplies an explicit environment with no inherited credential variables, existing private Python environment, no sync/install, offline flags, private fresh HOME/TMP/cache paths and disabled telemetry. It retains the existing guard unchanged; guard SHA256 is `38f6a7483d66a066336d63c14980f1acfe307ec38848f0761c6928a66989a7a8`. The guard disallows external transports and shared-checkout access during validation. Metadata preservation checks separately stat the main files and hash only authorized unrelated snapshot paths. No loopback service or provider requests were needed.

## Skipped checks and baseline

The directory-moving builder runner was read but not executed. Its exact-candidate raw receipts, outputs and output hashes were verified; independent checks instead enforced a read prohibition on the deprecated private subtree. Main data was never moved. No new tests, whole-suite run, provider checks, broad credential/history scan, Ruff or Mypy run was required for this deletion/index/ignore work unit with no source/runtime changes.

All required bounded checks passed; no baseline failure or regression was observed in these runs. Earlier work-unit reports were read only as packet context and did not establish this verdict.

## Residual risk and next gate

Untracking affects the current tree and normal Git discovery; historical commits, existing clones and deferred exposed artifacts remain outside this unit. Ignored local files remain on disk under maintainer control and can still be force-added deliberately. Preservation establishes the required metadata equivalence, without reading or hashing private databases. Credential rotation/retirement is maintainer-reported and was not independently checked with issuers.

The controller may record SEC-003 verification and propose bounded completion. Maintainer acceptance, whole-initiative reconciliation and any delivery/publication remain separate gates.

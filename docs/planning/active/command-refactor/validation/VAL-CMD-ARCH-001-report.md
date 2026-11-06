# VAL-CMD-ARCH-001 — scoped foundation design approval readiness

VERIFIED — AP-01 through AP-06 only.

This result supports presenting the foundation design to the maintainer. It
grants no API approval, construction authority, P0/P1 closure, implementation
verification, acceptance or delivery authority.

## Reviewer and frozen identity

Reviewer: independent Codex agent `/root/foundation_design_review`.
Date: 2026-11-04. Separate fresh context; no builder transcript or private
reasoning supplied. Exact deployed model/version was not exposed to reviewer.
This repository report is controller-transcribed from the reviewer's returned
report; the reviewer made no repository edits.

- Repository: `/Users/chuckrussell/Dev/gendev/agent-framework`.
- Branch: `feature/command-refactor`.
- Candidate and start/end HEAD: `0124d14bb8e91091d35eb73c09f6640e6f558289`.
- Deliverable base: `25d2dcb6b6120c852d35da2f84c8e778ea6d7099`.
- Deliverable basis: `e083116a27556a93f1e9ac9df14f514927f8fee6`.
- Deliverable diff: `25d2dcb6..e083116a` (six documentation files, 442 additions).
- Review request/authority delta: `e083116a..0124d14b` (three documentation files).
- [Manifest](architecture-review-manifest.json) SHA-256:
  `d76b05d4be320cda7a76206771270864f5c160ea2cdecde195a4e37df5fdef72`.
- All 19 manifest hashes matched at start and end.
- [Request and mandatory criteria](architecture-review-request.md).

## Findings

No mandatory semantic ambiguity, violated scoped requirement or approval blocker
was established. No mandatory remediation is requested.

### FND-ADV-001 — low, optional parser fixture clarification

Affected: `shared-command-api.md:79–88` and foundation directive lines 94–96.
Related criteria: API-02/API-03 and AP-02/AP-04; no violation found.

Current Chat removes the dispatch slash, then name normalization removes one
additional leading slash (`commands/registry.py:1459–1468`). Include multi-slash
and normalization-order examples such as `//HELP` in independent frozen parser
fixtures. Derive expected tokens from frozen Chat source/probes, not through the
new registry under test. No fix is required for this design approval. This is
optional test-detail guidance, not a product-scope change.

Controller disposition: retain as advisory for future fixture preparation. The
reviewed design and directive have not been changed after review.

## Acceptance matrix

All packet paths below are under `docs/planning/active/command-refactor/`.

| Criterion | Result | Evidence assessed by reviewer |
| --- | --- | --- |
| AP-01 | VERIFIED | `scope-decisions.md` S-02/S-03 and O-01–O-05; API lines 19–33,108–127,164 preserve nine removals, tools, 41/3 target, shared ownership, separate CLI and quirks. Directive lines 32–35 exclude actual migration/removal/client wiring. |
| AP-02 | VERIFIED | API lines 35–57 specify public data/invariants; lines 59–98 specify registry signatures, normalization, parsing, atomicity and execution. Chat registry lines 1459–1468 corroborate the current grammar. Metadata does not introduce new handler grammar enforcement. |
| AP-03 | VERIFIED | API lines 19–27,42–53 exclude frontend dependencies and broad runtime contexts. Lines 92–98 preserve exception/cancellation propagation, no retry or false success. Lines 100–151 retain family ownership and safety gates. |
| AP-04 | VERIFIED | Directive lines 69–85 map FND-01–04 to API-01–06; lines 38–67 bind allowed paths/amendments; 87–108 bind independent positive/negative fixtures; 110–151 bind checks/isolated installation; 153–165 bind entry/scope/handoff stops. API-07–09 remain later obligations. |
| AP-05 | VERIFIED | Production/effects audit lines 3–16,37–61 distinguishes historical assertion receipts, source observations and missing probes. Failure disposition retains dirty-worktree/controlled evidence and remaining gaps. Independent receipt/hash inspection corroborated counts and identity; no future implementation/install claim. |
| AP-06 | VERIFIED | Request lines 13–17,31–32 limit the gate to design readiness. Planning authority lines 6–15 excludes source/tests/metadata/configs/lockfiles. Directive lines 12–24 requires separately recorded API/base approval and P0/P1 disposition. Review supplies no automatic source authority. |

## Actual checks and results

| Check performed by reviewer | Result |
| --- | --- |
| git HEAD/candidate/branch resolution at start/end | Candidate `0124d14b...`; branch matched; unchanged. |
| git status at start/end | Same three excluded dirty paths; no additional tracked changes. |
| SHA-256 verification of every manifest entry, repeated at end | 19/19 match; manifest unchanged. |
| `uv run python scripts/friday-dev-board.py validate` | Passed, 36 tasks. |
| `uv run python scripts/check-documentation-lifecycle.py` | Passed, 680 Markdown files. |
| `git diff --check` | Exit 0, no output. |
| `git diff --check 25d2dcb6..e083116a` | Exit 0, no output. |
| `git diff --check e083116a..0124d14b` | Exit 0, no output. |
| Full selected deliverable diff and focused complete-file/source reads | Six-file additive deliverable and relevant source/evidence inspected. |
| Compare source/test files with P0 inventory | All 84 hashes match. |
| Parse stored Chat/CLI JUnit receipts | Historical Chat: 826 cases, 3 failures, zero errors/skips; CLI: 155 cases, zero failures/errors/skips. |
| Inspect four production-module JUnit groups | 8 + 7 + 12 + 27 = 54 cases, no failures/errors; module hashes match. |
| Inspect controlled full Chat log/manifests | Stored 826 passed, one warning, committed-example/xterm controls and live-LM exclusion disclosed. |

No pytest suite, provider, tool, persistent-store probe, build, install, external
action, board mutation or repository edit was performed by the reviewer.
Historical results were inspected, not rerun.

## Preservation and limitations

The excluded dirty paths retained identical start/end SHA-256 hashes:

| Path | SHA-256 |
| --- | --- |
| `docs/planning/backlog/friday-tui-command-followups/README.md` | `404b94f2c4773b6597946e7cbb1679f2040901078f1e86c625155c95cf586c95` |
| `packages/friday-chat/config.example.yaml` | `c2f728c98adc5ca773bfdf3170d846a610f15d77eae9a380e1a815534b93c3e7` |
| `packages/friday-chat/models-config.example.yaml` | `11e99116d885a431f085b6bd05b5bd30348eb37654fd4c9350a7cca58c527896` |

Complete per-command evidence, family schemas, service relocation, installed
Chat/CLI operation, maintenance cancellation/progress behavior, P0/P1 completion,
and later TUI parity/UAT remain open. These retained gates do not block the
limited foundation design approval. Next gate: maintainer design decision.

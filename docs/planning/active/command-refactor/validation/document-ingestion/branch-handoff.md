# INGEST-001 — scoped branch handoff

Status: **planning/design only; no construction approval**.
Working branch: `feature/cmd-ingest-001`. Created from `df62b77d551491cfb33ad2492c711036b09c9d4c` on 2026-11-10.

[Parent PR #15](https://github.com/CIChuck/agent-framework/pull/15) is merged
into `master` at `c36e7ee51a9328918b9bb97712aa7f1d4a850d19` (2026-11-10T20:54:01Z).
GitHub confirms the regular merge parents include submitted head `df62b77d`;
remote `feature/command-retirement` is deleted. The local historical branch is
retained; no local branch or personal state was deleted.

This branch incorporates the merged `master` through `c7d6476358acf6a11534bfae0d912d17d432ce46`,
without rebasing or rewriting its published `070764d4` planning commit. Future
INGEST-only PRs/reviews target `master`; the merge-base is now the merged parent,
so the earlier 127-commit command-refactor history is not repeated in that diff.
Only planning/status changes currently differ. No second PR, implementation or
human acceptance is created by this reconciliation.
[External delivery evidence](../delivery/command-retirement-merge.json).

## Bounded work

The [proposed remediation](../../remediation/REM-CMD-INGEST-001-pdf-docx.md) and
[Tools companion](../../proposals/tools-document-adoption.md) remain the scope:
PDF/DOCX/XLSX/PPTX extraction, shared all-source document/512-token chunking with
document/recursive/fixed overrides, and shared input-limit/vector-dimension
guards. Exact package/model/counter readiness and approved construction paths
are still required. Qwen4B remains illustrative; Certifi>=2026.10.19 is mandatory.
Fresh disposable test stores require no legacy migration. No model is installed
or selected, and no store is reset as part of preparing this branch.

Only a planning/status handoff differs from the parent at branch preparation.
Product/tests/scripts/metadata/lock still match MAINT artifact source
`ae15a5374350807bd909bc823078087a53a47ce4`. Existing verification reports retain
their candidate-specific meaning. MAINT human UAT/acceptance remain pending.

The canonical initiative remains started, delivery pushed, with current
`implementation_authority: design_only`. This narrows authority for the new
planning slice; it does not rewrite earlier unit approvals or grant acceptance.
No product implementation, merge or release is authorized. The later explicit
iteration authority covered the now-completed Sol/Astra/Opus rounds1–4 only.
Round5 remains complete with changes requested and Astra blocked. The maintainer
now explicitly authorizes the compatibility correction and four-pass bounded
council cycle. The revised REM/annex await independent review; no product authority.

## Preserved local state

The two edited Chat example YAML files remain uncommitted and unstaged;
`.friday-old/` and ignored exports remain untouched. Historical receipts retain
their original branch/source identities. Do not broad-stage or clean this checkout.

**Next gate:** One explicit read-only Sol/Astra/Opus council round is authorized for draft CD-CMD-INGEST-GATE-A-001, unchanged directive bytes e44d4e4b from 494eed4f. Review all HRC-01–16/HR-01–12, especially zero production-code/config/store/environment edits, code only under tests/readiness/ingest/, generated state under .friday_test/, and shared LM Studio only in the confirmed production-offline/restart/log-separation window. Target coverage and overall>=9.5 from every seat, no mandatory findings. Reconcile all three reports; no automatic loop, harness construction, stage/model activation or delivery authority.

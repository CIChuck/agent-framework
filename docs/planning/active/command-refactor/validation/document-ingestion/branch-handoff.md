# INGEST-001 — scoped branch handoff

Status: **planning/design only; no construction approval**.
Working branch: `feature/cmd-ingest-001`. Created from `df62b77d551491cfb33ad2492c711036b09c9d4c` on 2026-11-10.

[Parent PR #15](https://github.com/CIChuck/agent-framework/pull/15) publishes
`feature/command-retirement` against `master`. It is open, not merged or accepted
by this handoff. The new branch starts from its submitted head so verified
command/Memory behavior is present without copying or rewriting history.
While the parent is open, review future INGEST-only deltas against that parent
head/branch; after merge, reconcile the actual merge strategy before targeting
`master`. Do not assume a squash merge preserves parent commit ancestry.
No second PR or merge is requested by this branch creation.

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
No product implementation, council/sub-agent, merge or release is launched.

## Preserved local state

The two edited Chat example YAML files remain uncommitted and unstaged;
`.friday-old/` and ignored exports remain untouched. Historical receipts retain
their original branch/source identities. Do not broad-stage or clean this checkout.

**Next gate:** Review INGEST-001 document/readiness and exact construction scope on feature/cmd-ingest-001; parent PR #15 targets master. MAINT-001 human UAT/acceptance pending. Delivery pushed.

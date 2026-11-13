# INGEST design council — round 2 reconciliation

**CHANGES_REQUESTED.** The all-seat9.5/no-mandatory-finding target is not met.

| Reviewer | Reported outcome | Advisory score |
| --- | --- | ---: |
| [GPT-6.1 Sol](sol-report.md) | VERIFIED | 9.5/10 |
| [GPT-6 Astra](astra-report.md) | CHANGES_REQUESTED | 9.0/10 |
| [Claude Opus5.5](opus-report.md) | CHANGES_REQUESTED; conduct qualified | 8.4/10 |

Candidate `2956b861de75fcf7ebf463c82f5f470cf6fa7b40`, correction base
`4f9cb13a7a868ec28305a6fe6445007cd3727532`; branch `feature/cmd-ingest-001`.
All seats reviewed the correction first and then the full proposed design.
Every report assesses24 criteria. Different grades are retained, not averaged.
Sol's result applies to that candidate and does not close another seat's finding.

## Open findings

1. **Existing-store policy (Opus M-1):** testing with fresh stores does not alone
   authorize changing behavior for every existing install. Define the upgrade
   policy, exact fresh-root request and root-state × operation matrix. A precise
   maintainer preference was requested; no answer is inferred from silence.
2. **Identity at every storage/assembly seam (Astra001 and Opus M-2):** maintained
   snapshot/restore and pruner clients bypass the proposed vector adapter.
   Recovery needs identity-preserving snapshots and same-space admission before
   mutation, or an explicit product refusal. Runtime/Core factory composition
   must resolve the same capabilities. Source inspection shows the current CLI
   container delegates to RuntimeKernel; it is not another independent client
   constructor, but its exposed readiness contract still needs coverage.

Useful advisories address lazy/read-only startup; destination/incarnation-specific
storage receipts; unwired Chat smart_read storage; existing import edges; CSV/TSV
header carry; hosted-model identity/counter limits; current roster links and web
scope; exact sidecar root and graph recall failures; inactive migration code;
and exact option-name parsing. They are included in the authorized correction
without inventing new fetchers, activating automatic storage or redesigning recovery.

## Conduct and proof limits

Opus again discloses a Git command outside its environment wrapper, after its
closing audit. A later PASS proves the frozen state still matches; it does not
prove the missed command used the required environment. The controller retains
the technical CHANGES_REQUESTED/8.4 report as qualified evidence and makes no
clean formal command-discipline claim. No cleanup or replacement seat is launched.
Its harness-owned tool-results artifact and external Git metadata changes remain
disclosed; the controller does not attribute or modify them.

All three start/end checks, Opus's post-deviation check and the controller's
[final frozen check](controller-frozen-integrity.json) pass:17,561 protected
entries, six metadata records, exact HEAD/branch/index/status/staging.
The logical index is `587b8099a2c6a1be5adc8bfe021bbc9cd6c6ebdcbf54a78d543d57007125ebe3`.
Raw report copies are byte-identical. [Reconciliation JSON](reconciliation.json)
pins reports/receipts and preserves all criterion outcomes. The exact request,
helper, metadata and compressed manifest are archived without rebinding original
absolute paths; a new candidate requires a new review request.

This is document/design review only. Source counterexamples were inspected,
not executed as new runtime regressions. Admin checks passed; no product tests,
builds, installs, provider calls or store operations were run. Historical baseline
failures remain failed/unwaived. Personal backup content is not adopted as
controller correctness evidence; maintained recovery/coordinator source suffices.

## Next gate

Correct these documents within the recorded iteration authority, settle the
existing-store preference, then freeze a new candidate for fresh full round3.
Rounds3 and4 remain within the budget. Every seat must honestly return VERIFIED
with score>=9.5 and no mandatory findings before the document gate can pass.
Gate-A execution, construction, human acceptance and delivery remain separate.

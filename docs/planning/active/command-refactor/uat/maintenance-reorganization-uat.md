# MAINT-001 — targeted maintenance UAT

Status: **READY TO RUN — all cases NOT RUN**. Independent implementation
verification is complete: Astra9.5, Sol9.6, no mandatory findings.
[Verified build, disposable setup and launch](../validation/maintenance/implementation/acceptance-handoff.md).
No human pass or acceptance is recorded.

Run each case separately. Begin with disposable state and record the before
records/statuses. For skip/standalone comparisons, use equivalent fresh copies
of that starting dataset; earlier execute cases change eligibility. Do not use
personal memory for the first pass. Provider calls occur only when the operator
launches the real runtime and invokes them.

| ID | Individual action | Expected observation | Result |
| --- | --- | --- | --- |
| MAINT-UAT-01 | `/help reorganize`, then `/reorganize` and `/reorganize --full` previews | Explicit full is documented; implicit/explicit previews agree. No provider work/recovery bundle; dependent synthesis/generated scope is deferred. | NOT RUN |
| MAINT-UAT-02 | Try duplicate/conflicting modes, e.g. `/reorganize --full --verify` and `/reorganize --full --full` | Clear refusal before mutation; session remains usable. | NOT RUN |
| MAINT-UAT-03 | On a populated disposable fixture, `/reorganize --full --execute` | Dedupe → prune → verify_pending → synthesize → verify_generated → lifecycle. Distinct progress labels; no second command needed to use newly verified sources. | NOT RUN |
| MAINT-UAT-04 | Compare `/insights`, `/meta` and known record statuses before/after case03 | Sources that became verified can contribute in this run. Only newly created insights enter generated verification. Rejected/uncertain sources remain ineligible. Mark BLOCKED if the dataset/provider produces no eligible source or new output. | NOT RUN |
| MAINT-UAT-05 | Inspect mixed-verdict stage output in a fixture with known outcomes | Selected/verified/rejected/uncertain totals agree. A completed stage need not approve every record. Errors remain separate from verdicts. | NOT RUN |
| MAINT-UAT-06 | Execute verification with no eligible pending candidates | Known zero counts; no verification model call. Empty output is not populated rendering proof. | NOT RUN |
| MAINT-UAT-07a | `/reorganize --full --execute --skip-verify` on its own fixture | Both verification stages are skipped; no fabricated verdict counts. | NOT RUN |
| MAINT-UAT-07b | `/reorganize --full --execute --skip-synthesis` on its own fixture | Synthesis and generated verification skipped; pending verification remains. | NOT RUN |
| MAINT-UAT-07c | `/reorganize --full --execute --skip-lifecycle` on its own fixture | Lifecycle skipped; preceding stages retain their order. | NOT RUN |
| MAINT-UAT-08a | `/reorganize --verify --execute` | Standalone pending verification; no automatic synthesis. | NOT RUN |
| MAINT-UAT-08b | `/reorganize --synthesize --execute` on eligible sources | Standalone synthesis retained; full-run stage sequence is not implicitly added. | NOT RUN |
| MAINT-UAT-09 | `/reorganize --full --execute --force-reembed` on a fixture with configured embeddings | Reembedding runs first; normal order follows. Record latency separately from the no-reembed run. | NOT RUN |
| MAINT-UAT-10 | Developer-assisted supported failure after generated verification | Whole-run rollback restores prior verdict metadata and removes new insights. Displayed counts clearly say attempted/rolled back. No public fault-injection flag exists. | NOT RUN |
| MAINT-UAT-11 | Developer-assisted bounded cancellation/restart fixture; separately observe ordinary Ctrl-C | Atomic stage drains safely; no next stage after cancellation. Recovery status is actionable; interrupted v1/new-stage recovery succeeds. Ctrl-C alone does not prove every atomic boundary. | NOT RUN |
| MAINT-UAT-12 | Inspect look/feel throughout the preceding cases and run another harmless command afterward | Readable progress/counts, useful errors, responsive terminal, understandable delays, and usable session after success/refusal. Record actual times and perceived stalls. | NOT RUN |

For every case record PASS / FAIL / BLOCKED, source/build, starting fixture,
configuration choice, run ID, observed order/counts, elapsed time and output.
Never include credentials. A blocked prerequisite is not a pass.

Automated proof already covers deterministic counts, same-run synthesis, exact
empty/migration-only scope, all skip combinations, cancellation/rollback and
installed v1 recovery. Human cases assess usability and configured live-provider
behavior on macOS arm64 / Python3.13.10. Existing root debt remains unwaived.

UAT completion and bounded maintainer acceptance are separate decisions.

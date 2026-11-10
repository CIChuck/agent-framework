# MAINT-001 — targeted maintenance UAT

Status: NOT RUN. Wait for the independent implementation handoff and its exact
verified launch command. Use disposable stores and explicit test configuration;
do not start with personal memory. Provider/network execution needs the user's
separate direction. Automated proof uses deterministic local providers.

- [ ] Preview implicit full and explicit `--full`; confirm identical plans, no
  provider activity or recovery bundle, and deferred dependent scopes.
- [ ] Execute a disposable full run; observe pending verification before
  synthesis, then generated verification, with distinct stage labels.
- [ ] Confirm a newly verified source contributes in the same run.
- [ ] Inspect mixed final verdict counts; distinguish uncertain/rejected from
  malformed-provider failure.
- [ ] Confirm no-candidate verification displays known zeros and no model work.
- [ ] Exercise each skip flag; both verification stages follow skip-verify,
  and skip-synthesis also skips generated verification.
- [ ] Exercise standalone verify/synthesize and first-position force-reembed.
- [ ] Try conflicting/duplicate flags; check help, error clarity and responsiveness.
- [ ] Induce a supported disposable failure after generated verification;
  confirm attempted/rolled-back labels and restored records/transcript.
- [ ] Interrupt at a supported test boundary; confirm safe cancellation,
  actionable recovery status, and later successful recovery.
- [ ] Review look/feel, stage progress, elapsed times and terminal responsiveness.

Record exact build, configuration, run IDs, observed counts/times and any
failures. No automatic pass or acceptance follows from this checklist.

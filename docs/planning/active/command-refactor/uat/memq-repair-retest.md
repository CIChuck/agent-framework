# MEMQ combined repair retest

Status: **PASS — maintainer-reported; CLOSED 2026-11-10**.
Chuck Russell reports this combined repair retest was successful and directs
closure. [Acceptance](../approval/memory-queries-acceptance.md). Earlier reported
failures and original UAT notes remain preserved; no per-command logs/timings
were supplied with this result. The procedure below is retained as a runbook.
The separate explicit `--full` command-syntax issue is open as FU-011.

1. Entity lookup: use a stored label visible in `/entities nodes`. Compare
   `/entities chuck` with `/entities "chuck"`. For the supplied known label compare
   `/entities Peano Arithmetic (PA)`, `/entities "Peano Arithmetic (PA)"` and
   `/entities 'Peano Arithmetic (PA)'`. Each quoted/unquoted pair should return
   identical node/relationship output. `Peano Arithmetic` alone does not select
   the longer stored label. Existing relationship filtering remains unchanged.
   Lowercase unquoted `nodes` lists nodes; quoted `"nodes"` looks up that label.
2. Ingestion: use fresh disposable text files at paths without spaces (the path
   parser is unchanged). Run `/ingest /path/single.txt` with no description, then
   `/list-ingested`; repeat for a file large enough to create multiple chunks.
   Both should succeed and list persisted counts with an empty display description.
   Also try an explicit description. Re-ingestion adds records as before, so use
   fresh files or account for the additional count. Existing records are not migrated.
3. Verification: run `/reorganize --verify --execute` to isolate the previously
   failing verification step. This is maintenance execution: normal recovery
   snapshots are created and successful verification may update metadata. Keep
   the new run ID and complete step/error lines. Errors should contain safe
   role/configured-model/schema/finish-reason/field-type details, without values.
   The maintainer now reports the combined retest successful; no causal claim is made about the earlier verification-response error.

## Closure observations

The maintainer reports full reorganization on exit produces positive `/meta`
results and accepts the main MEMQ UAT. The verify-only procedure does not itself
synthesize meta memories. Earlier warnings to keep MEMQ UAT blocked are superseded
by this acceptance. The separate inability to use `/reorganize --full --execute`
is FU-011; current full execution syntax is `/reorganize --execute`.
No model/configuration, quarantine, order or verification policy changed here.

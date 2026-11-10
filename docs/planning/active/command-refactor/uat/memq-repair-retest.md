# MEMQ combined repair retest

Status: awaiting independent review of the shared quote/ingestion candidate.
All human results remain pending. Preserve the maintainer's original UAT plan and
reported failures. This companion is in the same UAT folder; no earlier result
has been overwritten. Restart Friday Chat through the normal workflow after the
reviewed candidate is handed back. Existing YAML and personal stores are unchanged.

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
   The actual verification response has not yet been functionally repaired.

After successful verification, reassess full reorganization/synthesis before
populated `/meta` UAT. This verify-only run does not synthesize meta memories.
Keep remaining dependent UAT stopped if verification still fails. No claim is
made that all three production issues or all20 UAT cases have passed.

The configured verification models remain OpenRouter Gemini2.5 Flash for classifier/
researcher and Gemini3.5 Flash Lite for judge. No token/model/config/pipeline change.
The agent's checks use deterministic local embeddings and private stores only;
these operator commands may use the configured live services.

# MEMQ UAT verification diagnostics — corrected candidate

Status: **correction1 complete; fresh independent review pending**.
[Correction scope and checks](correction1/README.md) address MEMQ-VD-REV-002.
The [initial review](review-round1/report.md) remains BLOCKED for reviewer isolation;
it is not carried forward as verification. See its [preserved disclosure](review-round1/reviewer-temp-disclosure.json).
Current source validates diagnostic paths at their schema position. Unknown keys
are redacted even when their names are valid fields elsewhere in the schema.
All prior limits and actual-production uncertainty remain.

# Historical initial diagnostic candidate — 4ffde1df

Initial candidate status: **BLOCKED review; superseded by correction1**.
[Authority](../../../remediation/REM-CMD-MEMQ-UAT-002-verification-diagnostics.md)
records Chuck Russell’s current proceed instruction. Base f530e755. The earlier
Chat-only quote/ingest proposal stays held; this subunit changes only diagnostics.

Shared Friday Memory retains optional completion model/finish metadata, exposes
safe immutable response diagnostics and offers strict enclosing-object parsing.
Legacy parser default remains unchanged. Chat attaches maintenance role and
surfaces shared safe context through existing failed-step results and rollback
journals. Explicit length termination is distinct from syntax/schema failure.
Raw provider input, reasoning and unknown field names are excluded, including
from ordinary formatted validation exception traces.

## Actual checks

- Focused response/parser/metadata/privacy/rollback tests:71 passed.
- Final canonical source lanes: Commands/cohort599, Chat1410 with5 existing skips,
  CLI155, relevant Memory155. Chat used private committed example fixtures through
  two test-module path globals; all product module origins remained canonical at
  collection, finish and after teardown. One existing legacy-client warning.
- Unmodified baseline source with current user examples reproduces both failures
  seen in the unadjusted Chat lane: model-library example mismatch and UAT tool
  adapter type mismatch. That raw lane remains failed (1408 pass/2 fail/5 skip),
  separately reported rather than converted into a pass. User YAML is unchanged.
- Changed-source Ruff and mypy4 pass; new files format cleanly. The pinned format
  debt gate and a baseline-relative inventory for this subunit find no new debt.
  Existing mutation.py7/test_llm_completion.py17 format fragments remain unwaived;
  pre-existing Chat4-file/root debt is not repaired or claimed passing.
- Both Memory and Chat wheels built offline, installed in a private copied prefix,
  pip check passed and the exact138-name/version dependency closure is retained.
  Four isolated normal/-O headless/maintenance probes pass; all Friday origins
  are inside that prefix. All4 changed runtime source members equal wheel bytes.
  The headless probe forbids Chat/Commands/TUI imports. No provider/store was used.
- Scope audit finds only approved existing definitions changed; all old tests’
  ASTs are retained. Seven protected dirty/export/external identities match.

## Exclusions and limits

The first focused attempt failed two new tests because their synthetic request
had an empty message list; corrected tests use a valid request (no product fix).
The first guarded suite launch could not import the private origin plugin; its
runner logs are preserved, excluded, and superseded after copying that plugin to
its private import directory. Those setup errors are not product failures.

An early Ruff invocation omitted the private-cache override and wrote4 repository
cache files. They are preserved without cleanup/restoration and explicitly
recorded in early-ruff-cache-disclosure.json. Subsequent checks used private
caches and were rerun. No claim of perfect builder cache isolation is made.
No user config/store, supplied evidence or accepted prior report was altered.
Reviewers must still use exclusively their own fresh scratch.

This does not identify the actual failed verification role/field or prove the
production response was truncated. It enables the next diagnostic observation.
No model/config/budget, batching, pipeline, quarantine, coverage or rollback
policy changes. Quote/ingest repairs and populated-meta human UAT remain pending.

[Exact evidence](evidence.json) and [installed probe](installed_diagnostic_probe.py).
Fresh read-only review is required before diagnostic handoff; no acceptance or
external delivery is granted.

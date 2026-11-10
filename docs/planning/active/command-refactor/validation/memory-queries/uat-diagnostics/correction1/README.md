# Verification diagnostics — correction cycle 1

Authority remains the approved REM-CMD-MEMQ-UAT-002. This is its first bounded
correction cycle, within the existing four-source-path/test allowlist.

The [round1 report](../review-round1/report.md) is **BLOCKED**, retained verbatim.
MEMQ-VD-REV-001 is a reviewer scratch-boundary breach, not a usable verification.
The zero-byte sibling creation/removal is disclosed and not waived. Repository
and supplied-input identities matched; all reviewer ledger files match. The new
candidate receives a new fresh-context review, not a continuation of that seat.

MEMQ-VD-REV-002 is the product finding: a global union of JSON-schema field names
allowed unknown keys at incorrect schema positions to appear in diagnostics.
Only response_diagnostics.py changes at runtime in this correction. Its path
walker now follows the current schema position, local references and array items.
Map keys and unknown/ambiguous paths are redacted; known value fields remain.
No response validation, routing, metadata, parser, pipeline or recovery change.

Required correction checks:

- CR-VD-01: root extras confidence/status/memory_id/collection and nested extra
  decisions are redacted; legitimate decisions.0.confidence remains visible.
  Typed dictionary keys are redacted while known value-field paths remain.
- CR-VD-02: bounded VD-01..08 remain satisfied; old BLOCKED review/process deviations
  are preserved; new scratch isolation and all protected state match at both ends.

Builder: focused77, relevant Memory161, Commands/cohort599, controlled Chat1410
with5 existing skips, CLI155. Ruff, mypy4, new-file format and both no-new-debt
inventories pass. Both wheels rebuilt offline;138-distribution closure retained;
4 isolated installed normal/-O probes pass, including all5 collision cases for
all3 maintenance roles. Product origins are canonical at3 source boundaries and
installed origins stay inside the private prefix. The source fixture-plugin lane
uses private committed examples; the raw Chat2 dirty-example failures remain
failed/unwaived from round1 and were inspected, not rerun in this correction.

[Exact current receipts](evidence.json); earlier [77 receipt pairs](../evidence.json)
remain immutable. No live provider/store, YAML, quote/ingest repair or acceptance.
Independent review is pending. Production verifier role/field is still unknown.

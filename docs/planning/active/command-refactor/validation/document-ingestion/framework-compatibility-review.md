# INGEST-001 — framework compatibility review

**CHANGES_REQUESTED.** The framework-wide council on `06f294d7` did not meet the
all-seat9.5 design gate: Sol8.6 and Opus7.2 request changes; Astra is procedurally
BLOCKED, with a provisional8.4 that cannot count as formal signoff.

The [consolidated report](council-round5/report.md) maps the overlapping source
findings into nine bounded themes: startup logging, active MCP snapshot
ingestion, legacy backup restore, direct SQLite analysis, implicit Chroma
embedding fallback, consolidation acknowledgement, lifecycle result reporting,
recall error propagation and Runtime profile composition.

The embedding pool/backward-compatibility architecture remains the premise.
These source-backed gaps need explicit dispositions and cross-subsystem proofs
before implementation. They are not executed evidence that new code fails; no
INGEST code has been generated and no product/model/store tests ran here.

[Exact artifacts and advisory dispositions](council-round5/reconciliation.json)
preserve every raw report and its limitations. The module CLI already refuses
destructive restore/synthesis; public legacy APIs still need coverage. No
subsystem rewrite, data reset or migration is implied.

The current REM and Tools companion remain unchanged. All reviewers are done;
no automatic remediation, replacement review or new council is started.
Next: review the bounded document corrections, then separately authorize fresh
review. Gate-A, construction, human acceptance and delivery remain ungranted.

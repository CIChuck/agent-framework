# MEMQ D2 correction2 — exact frozen-input restoration

Status: implemented; fresh council pending. Execution phase: validation.
Validation state: pending. Source remains `3ed1d58a`.

[REM-CMD-MEMQ-D2-002](../../../../../remediation/REM-CMD-MEMQ-D2-002-restore-frozen-backlog.md)
addresses MEMQ-D2-CLAUDE-001 from [round2](../council-round2/report.md).
The CMD-F05 backlog file is restored exactly to directive-approved SHA256
`b8021069f2752074ac7fb6a25d9d41055749b161d7cd18b0c49f14eded35daa8`.
All30 normative directive input hashes now match. Correction1 introduced one
unapproved pin change; its broader CMD-F05 allowance is withdrawn, and its
incomplete preservation claim stays visible in historical evidence.

FU-009 and the explicit-description UAT workaround are preserved. The only new
UAT change removes its inaccurate claim that CMD-F05 records that defect.
Every case remains NOT RUN; no ingest repair or waiver is included.
The ASTRA-001 status correction remains, with current gates reconciled.

All source/tests/fixtures/metadata/lock and technical documents are unchanged.
Preservation checks cover both dirty examples, ignored exports, external
locator, accepted evidence and supplied inputs. All122 previous embedded/raw
pairs and10 round2 reconciliation pairs match. Runtime checks were inspected,
not rerun by this controller; this documentation profile does not inherit prior
verdicts or waive any baseline failure. Fresh admin/semantic/pin/identity/pair
controls and exact commands are in [evidence](evidence.json).

Next: fresh Sol/Astra/Claude restoration delta FIRST, then full bounded D2
aggregate with retained D1. D3 installed proof and human UAT remain future.
After this second unsuccessful correction cycle, remaining mandatory findings
must be returned to the maintainer. No acceptance or external delivery.

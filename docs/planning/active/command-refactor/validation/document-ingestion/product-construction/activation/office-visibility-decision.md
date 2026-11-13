# Maintainer amendment — reject affected XLSX workbooks

2026-11-13. Chuck Russell: **“2. lets eject affected workbooks with a clear explanation.”**
Context: the proposed alternative to reliable exclusion of hidden Excel rows or
columns was whole-workbook refusal. “Eject” is recorded as **reject**.

## Approved bounded behavior

If an **included worksheet** has hidden rows or hidden columns, reject the whole
workbook before Docling conversion, chunking, embedding or Memory writes. Do not
partially ingest visible cells, report success, modify the source, unhide/delete
cells, or introduce a second text extractor. Existing default exclusion of hidden
worksheets remains; hidden dimensions in an excluded worksheet do not alone
trigger refusal. PPTX, PDF, DOCX, saved-formula and other content rules are unchanged.

The shared capability returns stable `unsupported_workbook_visibility`. Sideband
reasons identify hidden rows, hidden columns or both, with affected sheet names
and counts where structural inspection knows them; include no hidden cell values.
For `/ingest`, the clear error must say no content was ingested and explain how
to proceed, for example:

> Cannot ingest budget.xlsx: Forecast contains hidden rows or columns. This version rejects workbooks with hidden rows or columns. Save a copy with the intended content visible or removed, then retry. Nothing was ingested.

The read-only command reports the same unsupported-content reason without claiming
an ingestion attempt. Any separately activated Tools selection applies this rule
to its included worksheets. No new selection command or Tools routing is activated.

## Requirement reconciliation and proof

This approved narrowing supersedes only the REM section B/XLSX promise to exclude
hidden rows/columns while continuing ingestion and the corresponding RD-02 demand
to qualify that exclusion before coding. Reliable row/column-to-Docling filtering
is no longer required for these rejected cases. The already measured strict
admission behavior supplies the starting implementation policy; it is not
relabeled as successful exclusion or newly executed product proof.

I3 acceptance must preserve visible-only workbook successes, including late-sheet
markers, and test row-only, column-only and combined refusal through the real
command. Assert the stable error/actionable explanation and zero conversion,
embedding and storage calls. The source is unchanged. Tests use small synthetic
workbooks; no model/provider call or new standalone Docling campaign is needed.

This is a requirement amendment and future acceptance instruction, not product
implementation, construction approval or a new council authorization. The earlier
frozen review remains scoped to its exact original inputs. Carry this amendment
into the final canonical impact/directive approval binding; historical approved
assessment v0.6 remains unchanged until its required final revision.

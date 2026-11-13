# INGEST — focused council construction handoff

This is a disposition of non-blocking council advisories, not a new normative
product specification, an expanded allowlist or construction approval. The
reviewed [directive](../../../../../../directives/CD-CMD-INGEST-001-product.md)
v0.7 at `0144c539` remains unchanged. Its A1–A5 gates control. All owners below
are proposed implementation owners; exact appendices require approval before
generation. The council loop is closed; no further round is inferred.

| Existing gate / owner | Concrete decision or artifact to carry forward | Required future acceptance |
| --- | --- | --- |
| A2 — Chat request owner and Tools worker | Bind the actual await/cancel/join and request tracking/drain callbacks to command return, output eligibility and real application shutdown. Resolve the completion-to-render boundary explicitly, including a second cancellation during shielded cleanup. Use permitted seams; stop for scope reconciliation if they cannot meet the requirement. | I3-C3/C4 exercise the real application run/shutdown path, not only a helper, with responsive loop, no late display/orphan, and no Memory admission/provider/store calls for /read. |
| A1 RD-03 and A2 — Tools worker/caller | Select the bounded worker type and state what happens when native conversion overruns its qualified ceiling, while preserving join/quiescence and truthful timeout reporting. No immediate native-kill guarantee is inferred. Define synchronous SmartFileReader document calls explicitly without breaking retained text/table APIs or blocking an event loop. | Slow/timeout and before/during/after-completion cancel cases; cleanup/shutdown proves the approved worker semantics under the resource envelope. |
| A2 — Core contracts, Tools planner and Memory entry | Define the retained converted-document handle/identity/lifetime and neutral plan transfer. Memory invokes injected Tools planning; counting/preparation is injected. Conversion and planning share the ingestion attempt's cancellation scope, with no second conversion or chunk split. | Genuine headless document-to-disposable-store witness without Chat, exact one-plan chunks and receipts. |
| A2 — LLM capabilities and composition roots | Bind each model capability/tokenizer asset to a shipping/install path or approved provisioned root with identity, hash, license and headless availability. Colocate source/attempt/job/plan/receipt contracts so ownership and failure cases can be reviewed together. | Clean headless and document profiles, model-matched counting and qualified capacity/preparation checks. |
| A1 impact reconciliation and A4 — assessment author / maintainer | Revise the same canonical package-impact path after qualification as required by the directive. State plainly that /read has no Memory lease and that Memory calls the injected Tools planner. Preserve approved v0.6 bytes in Git; bind the exact revised hash to maintainer satisfaction. | Approved per-package impact and exact directive/appendix binding before product generation. |
| A2/A3 — existing-consumer owners | Retain paired old/new preparation/vector witnesses, explicit-default origin cases, unsplit structured records and actual small/large/force_chunked/cache-disabled-to-enabled paths. Storage receipts must bind the destination namespace/incarnation; a conversion cache hit is not storage success. | I1 unchanged-flow proof, coordinated I2 admission switch and I3 cache/one-plan cases; all unwaived unchanged-scope regressions block the relevant exit. |

The next preparation work is the directive's existing Q/A1 qualification and
exact A2/A3 records, retaining completed Docling findings rather than reopening
vendor efficacy testing. No model switch, reset/migration, production operation
or live validation window is authorized by this handoff. The initiative stays
started/local. Whole Gate-A readiness, maintainer A4 approval and bounded A5
execution remain open; no code generation follows the council verdict alone.

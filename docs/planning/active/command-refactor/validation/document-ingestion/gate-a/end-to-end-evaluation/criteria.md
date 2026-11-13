# Isolated end-to-end evaluation criteria

The fresh validator assesses this bounded test flow and its actual evidence,
not production `/ingest` integration or whole-framework readiness. Follow the
[scope amendment](scope-amendment.md), with production and supplied inputs
read-only. No live endpoint replay is authorized for the reviewer; inspect the
recorded real transport proof and reproduce offline controls in new scratch.

| ID | Required evidence |
| --- | --- |
| EE-01 | Only test source and planning artifacts change. Production packages, configuration, dependency lock, working environment and stores remain preserved. Private source/package origins bind to recorded committed code. |
| EE-02 | Genuine PDF, DOCX, XLSX and PPTX, including OCR, convert through actual Docling. Structural/corrupt refusals remain excluded. Actual document chunks demonstrate the default 512-token budget and a smaller override with content/source oracles. |
| EE-03 | Actual Friday-LLM brokers all embedding requests to the exact already-loaded Nomic instance. Task prefixes, local counting, loaded context and before/after model-state observations are explicit. No direct HTTP embedding bypass or synthetic live-proof credit. |
| EE-04 | Real transport responses are checked for model, count, indices, finite/nonzero numeric vectors and expected 768 dimensions. Request, vector and prepared-token budgets reserve before transport; retries are disabled. |
| EE-05 | Shared Memory Chroma stores genuine extracted chunks, exact content hashes and provenance in fresh per-mode stores. Absent descriptions remain absent. Refused sources never occur in the corpus, model inputs or stored rows. |
| EE-06 | Actual query embeddings retrieve expected source chunks across the four formats and override collection. A separate process reopens the physical store with networking denied and verifies text/provenance and identical retrieval IDs without embedding. Retrieval consistency is distinguished from semantic-quality evaluation. |
| EE-07 | Per-run identity and saved evidence bind source, corpus, transport, storage and reopen results. Failure, missing evidence, source change and artifact modification refuse reporting. Python-visible guards, private paths, safe observed LM Studio settings and window expiry are enforced, with native limits disclosed. |
| EE-08 | Committed normal/optimized offline tests, focused Ruff/format and private mypy pass. Manual commands and actual package versions, request counts, results, failed setup attempts and remaining integration limits are documented accurately. |

Return VERIFIED, CHANGES_REQUESTED or BLOCKED with the complete matrix,
commands/exits, reproduced versus inspected evidence, preservation checks and
honest component score. A bounded result supplies no whole-readiness 9.5 result,
production construction, human acceptance or delivery authority.

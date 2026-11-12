# Isolated end-to-end ingestion readiness — scope amendment

Chuck directs: “Need to do a complete end-to-end test here soon. Need to get back
to enhancing the ingest command.” He confirms production is stopped and Nomic is
loaded on the reserved test server. This controller amendment makes that explicit
request concrete within the approved test-harness work; it is not a new claimed
user hash approval, product acceptance or authority to change production.

Run genuine documents through Docling, default document/512-token chunking, actual
Friday-LLM to the already-loaded Nomic, shared Memory Chroma storage and retrieval.
Use fresh isolated source exports/packages/configuration/inputs/outputs and stores.
Versioned code may add `tests/readiness/ingest/e2e.py` and
`tests/readiness/ingest/tests/test_e2e.py`,
update the local README and add that regression selector in stages.py. Retain
behavior.py's independently verified bytes. No product source, working .venv,
root dependency/lock, dirty YAML, personal data, graph/WAL or production store edit.

This explicitly adds disposable Chroma writes to the earlier document-only scope.
Use only fresh per-mode store paths below the owned `.friday_test` run; never
reset/delete an existing store or scan personal documents. Existing product
/ingest integration remains later work. No new web-to-memory route is implied.

Use standard private package setup, source from a recorded commit and the existing
Docling stack; no custom metadata/resolver expansion. Normal `uv build` may build
only the committed Core, Telemetry, LLM and Memory packages in private exports;
third-party dependencies remain wheel-only. The actual broker must be
friday_llm.LiteLLMEmbeddingService, and storage the public shared Memory adapter.
A test-only preparation wrapper may supply Nomic task prefixes; do not change
production embedding conventions or re-embed legacy stores. Query with the public
precomputed-query-vector seam, preserving correct document/query preparation.

The endpoint is exact loopback127.0.0.1:1234; only native read-only model status
and OpenAI-compatible embedding requests are permitted. No model management,
server restart, settings changes, provider credentials or public-service request.
Read-only status confirms the selected Nomic's configured/max context2048; CLI
confirms ttlMs=null; selected application settings confirm JIT loading=false.
Auto-eviction is tied to JIT loading, so no new load can be triggered by these
requests. Preserve raw facts separately from operator confirmation. Recheck
loaded model/context and loaded-instance fingerprint around requests; abort on
change. No global auto-eviction-off claim is made.

Retain64 total request,256 vector and131072 prepared-token ceilings, the current
operator window expiry, timeout/RSS/disk/cache limits and Python-visible guard
with honest native limits. Count real transport attempts, disable retries, allow
only the selected origin/routes, private cache/config/temp paths and no ambient
.env/provider settings. Post-install Certifi>=2026.10.19 remains required.

Check actual response count/order, finite uniform expected dimensions, chunk/source
text and provenance through storage, persistence/reopen and retrieval across all
four formats including OCR. Refused/empty/corrupt content must never reach model
or store. Positive default512 and a smaller-budget override, plus failure-before-
write controls, should be covered without synthetic embeddings earning live credit.
Full behavior, live-model and storage proof remain separately attributed.

Freeze reusable test code/results and obtain a fresh bounded independent review.
No9.5 whole-readiness, production construction, acceptance or delivery is inferred.

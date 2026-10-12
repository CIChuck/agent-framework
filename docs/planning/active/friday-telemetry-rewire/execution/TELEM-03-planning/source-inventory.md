# TELEM-03 static source inventory

Status: preparation evidence; no behavioral validation. Date: 2026-10-06.
Revision: 4ca9baecdcdcf26fc5e8055b326c3a54cda36cb7.
[Machine-readable hashes/calls/signatures](source-inventory.json) are extracted
with AST parsing from the isolated tracked snapshot before any TELEM-03 edit.

| Surface | Current construction/metrics gap | Proposed bounded treatment |
| --- | --- | --- |
| Typed completion / typed stream | service.py chat_completion_request and chat_completion_events bypass the legacy tracker | Safe request metrics around validation, dispatch, parsing and streaming finalization |
| Legacy completion / text stream | LLMTelemetryHelper exports raw model/context/response/error fields; word count used as token approximation; sink calls unguarded | Safe schema replaces service emissions; public standalone legacy helper unchanged |
| Retry/circuit | _call_with_retry / _call_stream_with_retry count locally; successful retry count lost | One ID/event per actual dispatch, zero on preflight circuit rejection; preserve policy |
| Embedding documents/query | Helper uses zero defaults; cache/empty input bypass metrics; batches lack durable identity | Logical request, batch and attempt IDs with presence/partial coverage |
| Pricing | Historical early-2025 table, custom overrides, supplied table, provider/base/prefix matching and unknown fallback | Add typed provenance while preserving old numeric API; no rate refresh |
| Primary Chat | build_framework_chat_model canonical, typed-config and legacy-fallback services | Same observer, primary construction role |
| Primary embeddings | build_framework_embedding_service canonical and legacy | Same observer, embedding role |
| Maintenance default/four roles | _build_legacy_primary_llm_service and _build_role_llm_service | Same observer; default and synthesizer/classifier/researcher/judge labels |
| Memory extraction | _build_extraction_llm_service canonical/override/default alias in maintenance factory | Injection; preserve default-service identity and actual construction role |
| Passage router | _build_passage_router canonical/legacy from memory factory | Injection only, passage_router; no memory-operation tracing |
| Compaction | maintenance factory canonical compaction service or researcher/default alias | Injection; preserve alias and selection |
| SmartFileRead | tool registry → _instantiate_tool → _build_smart_file_llm_service for summarizer/synthesizer | Service injection only; tool semantics unchanged |
| Explicit maintenance registry | reorganization/mutation.py build_explicit_maintenance_provider_registry constructs canonical/legacy LLMs and embeddings | Injection via runtime; no readiness invocation or recovery/mutation change |
| Chat observer | Only lifecycle/MCP schemas accepted; rejects raw LLM event names | Add explicit new event union without relaxing old rejection rules |
| Workflow adapter | Builds WorkflowEngine/ScratchPadStore; no direct LiteLLM construction in Chat workflow factory | No unrelated workflow edit; LLM service metrics apply wherever injected service is used |

Source concerns are inspection findings, not executed reproductions: legacy helper
classifies using str(error), uses dynamic spans and retains per-token timing lists;
its Exception-only context manager can miss cancellation and finally emissions can
mask a primary failure. Typed streaming emits usage before application zero defaults;
usage chunks can arrive after finish and must be inspected through natural exhaustion.
No raw legacy helper is connected to the accepted Chat observer in this proposal.

Role attribution deliberately describes construction. A legacy extraction/default
alias or compaction/researcher alias is not recreated or relabelled to manufacture
operation provenance. Turn/operation parent correlation belongs to TELEM-04.

Read-only rg searches covered LiteLLMService/LiteLLMEmbeddingService construction
throughout Friday Chat source. The two locations are adapters.py and
reorganization/mutation.py; runtime.py assembles their factories. New construction
sites outside this inventory require scope reconciliation before code generation.

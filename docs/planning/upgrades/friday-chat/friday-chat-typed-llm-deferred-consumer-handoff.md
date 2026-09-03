# Friday Chat Typed LLM Deferred Consumer Handoff

- Status: Active follow-up inventory
- Date: 2026-08-28
- Primary migration release: `friday-chat==0.1.0a1`
- Upstream dependency: `friday-framework-llm==0.1.0a1`
- Framework-wide successor: [Friday Framework typed LLM adoption plan](../friday-packages/friday-framework-typed-llm-adoption-plan.md)

## Boundary

Friday Chat `0.1.0a1` migrates only `FridayChatConfig.llm` and
`FrameworkChatModel` to Friday LLM's typed request and event APIs. The consumers
below remain on legacy Friday LLM calls. They are regression-tested in this
release but require separate design and implementation authority before their
configuration or behavior changes.

The primary typed service is not reused as their fallback. Friday Chat builds a
separate legacy primary service for maintenance, extraction, and compaction so
explicit primary targets and generation controls do not silently migrate these
consumers.

## Consumer Inventory And Sequence

| Sequence | Consumer | Current construction/config | Current API | Future migration requirement | Main risk and test surface |
| --- | --- | --- | --- | --- | --- |
| 1 | Entity/fact extraction | `_build_extraction_llm_service()`; `extraction:` with fallback connection data from `llm:` | Legacy `chat_completion()` through `MemoryExtractor` | Add a strict typed extraction config with explicit independent targets and deterministic structured-output policy. | Extraction output, retry, rejection, background cancellation, and stable commit tests. |
| 2 | Maintenance roles | `_build_role_llm_service()` and explicit maintenance provider registry; `maintenance.llm.{synthesizer,classifier,researcher,judge}` | Legacy `chat_completion()` and structured JSON adapters | Define one shared typed role-provider model without inheriting primary generation accidentally. | Provider probes, JSON validation, synthesis abstention, reorganization rollback, and role fallback tests. |
| 3 | In-session compaction | `InSessionCompactor`; `memory.compaction` with researcher or legacy-primary fallback | Legacy LLM client contract | Decide whether compaction owns a role target or explicitly reuses a typed maintenance role; define reasoning-storage policy. | Context budget, cancellation, sensitive reasoning, and compaction persistence tests. |
| 4 | Passage routing | `_build_passage_router()`; `memory.passage_router` with extraction/primary connection fallback | Legacy `LiteLLMService` | Add explicit router target and bounded low-variance generation defaults. | Route-decision determinism, fallback, latency, and no-I/O disabled-path tests. |
| 5 | Smart-file summarization | `_build_smart_file_llm_service()`; `smart_file.llm.summarizer` with primary connection fallback | Legacy completion through large-file processor | Add a typed summarizer provider model and document whether primary credentials may still be inherited. | Large-file chunking, provider-free fallback, prompt bounds, and memory-ingestion safety tests. |
| 6 | Reorganization mutation providers | `build_explicit_maintenance_provider_registry()` in `reorganization/mutation.py` | Legacy structured `chat_completion()` | Coordinate with maintenance-role migration and preserve the explicit no-primary-fallback safety contract. | Readiness probes, schema validation, abstention, mutation admission, rollback, and evidence-redaction tests. |

## Shared Contract Recommendation

Before migrating sequence item 1, define a Friday Chat-owned strict provider
configuration wrapper containing:

- connection and resilience fields;
- public Friday LLM `GenerationConfig`;
- explicit `TransportTarget` and `ModelTarget`;
- a closed union of public bounded provider-options types;
- role-specific defaults applied by an explicit resolver, never by inheriting
  populated Pydantic defaults accidentally.

Reuse that wrapper for extraction and maintenance roles only after their
different default, structured-output, persistence, and reasoning-sensitivity
requirements are written as tests. Do not use an untyped shared dictionary and
do not infer targets from model names.

## Stop Conditions

- A migration would change another framework package without separate authority.
- A consumer cannot preserve structured JSON, cancellation, retry, or durable
  mutation semantics through the typed API.
- Reasoning content could enter extraction, memory, transcript, diagnostics, or
  release evidence without an explicit approved policy.
- A shared config would silently inherit primary generation or target values.
- The required provider-options type is not a stable public Friday LLM export.

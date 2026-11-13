# Bounded document/source-feasibility review checklist

This is a source-reading aid, not an expanded implementation allowlist, an
implementation specification or proof of a verdict. Review the actual affected
contracts and coupled error/state transitions below. Unchanged algorithm internals
need inspection where they interact with these boundaries; this is not an audit
of every unrelated method in the repository. Do not import or execute product code.

First read all pinned normative parents and the conditional drafts/maps in full.
Record permitted historical measurement claims as inspected; independently
stream/hash archives if required, without opening stored databases or replaying
providers. Hash evidence is integrity, not behavioral proof. No previous reviewer
report, own memory or controller conclusion supplies review evidence.

| Group | Required current source boundaries | Contract questions |
| --- | --- | --- |
| Selection and roles | LLM embeddings.py/model_library.py; Core profiles.py/interfaces/memory.py; Chat adapters.py and reorganization/mutation.py; Runtime di.py/config.py; CLI container.py/profiles.py | Actual pool/non-pool/default/hint/origin selection, query/document calls, preparation/cache/batch/retry/cardinality and dimensions; all B01–08 and Q identity/counter/parity requirements. |
| Stores and graph | Memory adapters/vector.py/simple_vector.py/graph.py/null_graph.py, models/graph.py, retrieval/collection_manager.py/graph_scorer.py and controller/memory_controller.py | Every direct opener and query/write/envelope route, sync/async public injected scoring versus maintained unscored recall, absent-component fallbacks, typed refusal propagation and metadata reads. |
| Extraction, tasks and effects | Memory context/extractor.py/extraction_filter.py/consolidator.py/assembler.py, lifecycle/promotion.py; Chat extraction/close/result projection; Agent archive caller and Runtime shutdown | Stable-ID acknowledgement only after real storage, inner versus outer task ownership/status, logger sink lifecycle, vectorless-edge fallback, retries/partial counts and caller-visible terminal failures. Agent source stays unchanged. |
| MCP and indirect consumers | Memory ingestion/mcp.py, Chat memory_mcp.py, maintained TurnProcessor/Runtime observer call path; Memory multi_agent controller/coordinator/journal and MEMQ adapters; Tools memory wrappers | Active versus public/absent paths, exact pending ID/receipts/ownership and existing reasons, shared physical space versus authorization visibility, truthful partial promotion and offline reads. No protocol or automatic activation expansion. |
| Maintenance and recovery | Memory maintenance recovery.py/recovery_models.py/mutation.py/pruner.py/synthesizer.py/fact_checker.py/backup.py/analyzer.py/__main__.py plus pipeline/reorganizer/provider_contracts; Chat reorganization contracts/artifacts/coordinator and mutation | Actual client fallback loops, empty dimensions, provider readiness after admission, identity/versioned handoff/fingerprint and rollback, marker exclusion with retained backup baselines; FU013/014 and ordering/algorithms remain outside repair. |
| Files and common ingestion | Chat commands/files.py/registry.py and ingestion adapter; Tools filesystem/smart_read.py and reader factory/readers; Memory ingestion/large_file_processor.py/tool_ingester.py and public ingestion APIs | Raw command tail and retained handlers/line semantics, placeholder source, source/derived record sequence, cache/storage paths, actual versus absent routes, no second split and scoped future shared entry. DI22 complete role matrix includes I3-created paths. |
| Profiles, imports and documentation | All17 workspace package metadata; Runtime tool_loading.py; three actual command registry owners/CLI placeholders; named guide and README contract plans | Eight implementation owners versus indirect consumers, no new backend cycles, narrow counters versus document extras, source-unchanged dynamic imports, actual default discovery and substantive authored-doc obligations. |
| Static evidence and migration | Original compressed test inventory/seed, helper inventory and fixture supplement; actual retained source/test AST and fixture references | All36 original DI definitions,14FC/19nodes,12exits, disjoint fixtures/helpers and exclusions, exact test exceptions, original source hashes, offline/live selection. No execution or test-count inflation. |

A future exact A2 signature/file map or A3 test map remains a legitimate activation
gate. Check it is complete and feasible as a design obligation; do not demand the
unapproved implementation now. In your own ledger, list read files/sections,
criterion joins, concrete limitations and any unresolved design question. A mere
file name or digest does not count as having read its relevant implementation.

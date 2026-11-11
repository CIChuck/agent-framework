# INGEST-001 — initial source-linked readiness worklist

Status: **A0 worklist; no deployment or consumer is qualified by this table**.
The [readiness plan](readiness-plan.md) and exact reviewed
[compatibility annex](../../../embedding-compatibility-contract.md) control.
This starts the required inventory; A0 expands every listed family into individual
call sites and discovers/configures dynamic consumers. It is not a completeness
claim or permission to change all listed source. All 17 package dispositions remain
in the approved [assessment](../../../package-impact-assessment.md).

All source paths below are repository-relative. Their existence is checked as
planning evidence. Role and active/public/absent classifications follow the
normative annex; no existing defect is treated as a positive witness.

## Baseline configuration families

| ID | Source/configuration family | Facts and unresolved qualification |
| --- | --- | --- |
| B01 | Chat packaged `config_templates/config.example.yaml` and `models-config.example.yaml` | Pool memory defaults and explicit maintenance service; Nomic revision is a placeholder. Preserve selection; actual deployment identity/counter facts are pending. |
| B02 | Chat maintained non-pool `embedding` path in `adapters.py` | Preserve configured model/endpoint and existing hosted default. Mutable alias alone does not qualify; no replacement is inferred. |
| B03 | Sanitized Chat compatibility fixture | Freeze existing alias/endpoint/extraction choice from committed test inputs; no dirty user YAML. Missing revision remains unresolved. |
| B04 | Runtime catalog/pool assembly in `di.py` | Preserve default Memory binding and optional distinct extraction service; each selected capability must qualify independently. |
| B05 | Runtime legacy `embedding`/service shapes in `packages/friday-runtime/src/friday_runtime/config.py`/`di.py` | Omitted new fields still need artifact-bound readiness without configuration churn or hidden fallback. |
| B06 | CLI `container.py` and `profiles.py` | Preserve direct/env/default origin and Runtime delegation. No new launcher/client. |
| B07 | Chat `reorganization/mutation.py` inline maintenance embedding | Separate existing model/endpoint may share a namespace only with compatible space identity. No sequencing/prompt redesign. |
| B08 | Memory `MaintenanceConfig.embedding` and public injected embedders | Preserve provider interface and all callable shapes; no Chroma default embedder substitution. |

Packaged examples and source describe configuration shapes, not the user's live
selection. None of these rows authorizes a model call. New optional fields are
omitted in baseline qualification fixtures. Actual B/N compatibility must succeed
under qualified readiness; merely parsing and then refusing is not compatibility.

## Caller and consumer families to expand in A0

| ID | Current source anchors | Role/policy and proof binding |
| --- | --- | --- |
| C01 | `packages/friday-llm/src/friday_llm/model_library.py`, `embeddings.py` | Resolve service/capability/preparation; document/query roles and batch/index/dimension/token checks. B01–08, DI-17/18/21–24/33, FC-10/12/14. |
| C02 | `packages/friday-chat/src/friday_chat/adapters.py`, `commands/registry.py`, `commands/files.py` | Current command reading/character slicing and shared-entry target; source document/512 plan, zero ingestion after extraction refusal. DI-01–19/26/33/34. Future command implementation proof is separate from Gate-A upstream probes. |
| C03 | `packages/friday-tools/src/friday_tools/filesystem/smart_read.py`, `packages/friday-memory/src/friday_memory/ingestion/large_file_processor.py` | Explicit text small/large/cache/source-derived handoffs. No automatic storage activation or double chunking. TOOLS-DOC's document routing remains separate. |
| C04 | `packages/friday-memory/src/friday_memory/ingestion/mcp.py`, `packages/friday-chat/src/friday_chat/memory_mcp.py` | Active MCP snapshot/publication path; unsplit snapshot, pending-ID/receipt semantics and existing reasons. FC-02/13. |
| C05 | `packages/friday-memory/src/friday_memory/context/extractor.py`, `packages/friday-chat/src/friday_chat/adapters.py` | Relationship/insight/summary embedding/storage and truthful acknowledgement; unsplit records, stable-ID retry. FC-01/06/14. |
| C06 | `packages/friday-memory/src/friday_memory/context/assembler.py`, `packages/friday-agent/src/friday_agent/base.py` | Actual owned inner background task, observed terminal status/wait and shutdown. Wrapper return is not completion. FC-06/12/13. |
| C07 | `packages/friday-memory/src/friday_memory/context/consolidator.py` | Public consolidation stored-batch acknowledgement and retry; classify maintained callers separately. FC-06. |
| C08 | `packages/friday-memory/src/friday_memory/adapters/vector.py`, `packages/friday-memory/src/friday_memory/retrieval/collection_manager.py` | Direct clients, query/document/precomputed vectors, namespace/open intent, result/errors and store-only metadata. DI-22/29/33, FC-08/13/14. |
| C09 | `packages/friday-memory/src/friday_memory/adapters/graph.py`, `packages/friday-memory/src/friday_memory/adapters/null_graph.py` | Stored graph vector envelopes and identity-safe comparisons; no migration/backfill. DI-22/29/33, FC-08. |
| C10 | `packages/friday-memory/src/friday_memory/retrieval/graph_scorer.py`, `packages/friday-memory/src/friday_memory/controller/memory_controller.py` | Scorers public-injectable, actual Chat/Runtime maintained recall stays unscored. Distinguish absent fallback components from invalid present vectors. FC-08. |
| C11 | `packages/friday-memory/src/friday_memory/retrieval/factor_computer.py`, `packages/friday-memory/src/friday_memory/retrieval/access_buffer.py`, `packages/friday-memory/src/friday_memory/maintenance/incremental.py` | Store-only/indirect metadata consumers and guarded recall effects; no invented inference or new scoring wiring. FC-08/13. |
| C12 | `packages/friday-memory/src/friday_memory/maintenance/pruner.py`, `packages/friday-memory/src/friday_memory/maintenance/synthesizer.py`, `packages/friday-memory/src/friday_memory/maintenance/fact_checker.py`, `packages/friday-memory/src/friday_memory/maintenance/__main__.py` | Every direct opener and callable shape; no fallback destination/default embedder. Existing synthesis records unsplit; authority and role checks precede effects. FC-05/11/14. |
| C13 | `packages/friday-memory/src/friday_memory/maintenance/mutation.py`, `packages/friday-memory/src/friday_memory/maintenance/recovery.py`, `packages/friday-chat/src/friday_chat/reorganization/mutation.py` | Empty-store dimensions, guarded direct clients, provider readiness, versioned binding/fingerprints and same-namespace recovery. No maintenance-order redesign. DI-27/29/32/33, FC-11. |
| C14 | `packages/friday-memory/src/friday_memory/maintenance/backup.py`, `packages/friday-memory/src/friday_memory/maintenance/analyzer.py` | Public physical backup and read-only SQLite consumers; protect live binding, preserve working baselines and leave FU-014 unwaived. FC-03/04. |
| C15 | `packages/friday-memory/src/friday_memory/lifecycle/promotion.py`, `packages/friday-memory/src/friday_memory/lifecycle/decay.py`, `packages/friday-memory/src/friday_memory/lifecycle/migration.py`, `packages/friday-tools/src/friday_tools/memory/lifecycle.py` | Indirect vectors and honest mutation/tool counts. Classify inactive migration explicitly; no second chunking or opportunistic repair. FC-07/13/14. |
| C16 | `packages/friday-memory/src/friday_memory/multi_agent/controller.py`, `packages/friday-memory/src/friday_memory/multi_agent/coordinator.py`, `packages/friday-memory/src/friday_memory/multi_agent/journal.py` | Memory-owned shared physical space with retained visibility and truthful partial outcomes; no coordinator/journal rewrite inferred. FC-13/14. |
| C17 | `packages/friday-runtime/src/friday_runtime/di.py`, `packages/friday-runtime/src/friday_runtime/config.py`, `packages/friday-runtime/src/friday_runtime/tool_loading.py` | Pool/non-pool composition, explicit path origin, admission before resourceful startup, ephemeral isolation and actual optional import discovery. FC-01/02/06/09/10/12/13. |
| C18 | `packages/friday-core/src/friday_core/profiles.py`, `packages/friday-cli/src/friday_cli/container.py`, `packages/friday-cli/src/friday_cli/profiles.py` | Existing public factories/re-exports/constructors preserve injection and origin; no backend fallback or new CLI command. FC-09/10/12. |
| C19 | Chat metadata commands, Agent public memory tools and source-unchanged Telemetry/Transcript/MCP/Optimization/Finance/Speech/Sandbox/Moltbook consumers | Expand exact call/import/test paths from the approved 17-package inventory. Classify declared-only/inactive edges honestly; require explicit offline Finance registration without Docling. DI-34, FC-12/13. |
| C20 | `packages/friday-memory/src/friday_memory/ingestion/tool_ingester.py`, `packages/friday-memory/src/friday_memory/ingestion/pipeline.py`; absent maintained URL/generic automatic-tool ingestion | Public ToolOutputIngester proof cannot establish absent wiring; classify the legacy DocumentIngestionPipeline separately and prevent a second chunker. Freeze exact current callable paths in A0; do not add a route to make a test pass. DI-16/19/34 and companion TD obligations. |

The known direct clients are a lower bound. Search maintained `packages/*/src`
with explicit exclusions for user config/state, classify all new matches and
record any configuration-driven blind spots. New owner/source paths return for
scope reconciliation; this worklist alone authorizes no edits.

## Required per-call trace fields

Each expanded row must bind caller symbol/path/source hash; active/public/absent
status; B family and exact service/profile; resolved model/counter/preparation;
raw destination value/origin and normalized physical layout; open intent and
namespace/incarnation identity; source-versus-derived/unsplit policy; positive B,
positive N and refusal R nodes; installed normal/optimized lane; origin checks;
negative witness and approved oracle exception; and evidence/qualification status.

At readiness, distinguish inspected source and upstream probe facts from planned
construction nodes. Do not invent a passing test for an interface not yet built.
At construction, update the initial case/fixture inventory and migration map
before replacing old coverage. Root `tests/integration/`, Transcript/Finance
`tests/` and any new Optimization witness need explicit selectors; classify every
non-default module offline/live. Finance's live provider module remains excluded
without separate authority and earns no executed-coverage credit.

## Present qualifications and stop conditions

All deployment rows are **pending**. The packaged Nomic revision placeholder,
mutable hosted aliases and an unselected replacement cannot produce readiness
records. A3 needs explicit operator facts before calls; Qwen remains illustrative.
One qualified model does not qualify another profile or all consumers. Unknown
identity/counting or unsupported format/coverage stops the dependent gate.

The eventual readiness report must freeze this matrix at call-site granularity
and identify remaining proof for the exact construction directive. This file is
a planning worklist, not execution evidence, complete source audit, independent
validation, or a product/TOOLS-DOC completion claim.

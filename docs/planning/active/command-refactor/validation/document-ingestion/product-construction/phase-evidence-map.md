# INGEST — phase and evidence dependency map

Version 0.2; conditional document contract. This map corrects the proof order;
it does not waive a parent DI/FC obligation or authorize implementation.
The [machine-readable join](phase-evidence-map.json) retains every original
DI-01–36 definition and digest, all FC-01–14 dispositions, proposed witness IDs,
source owners and prerequisite edges. Proposed case names are not existing,
collected or executed tests; exact A2/A3 bindings are required before generation.

## Ordering and authority

**Q → I1 → I2 → I3 → AG → UAT.** Q establishes upstream/deployment feasibility
and unchanged-baseline behavior under separately authorized effects. A1 requires
Q's RD dispositions, not the downstream product acceptance column. Inert proposed
metadata and co-installed upstream distributions are not new product extras.

Before each I slice, record A1–A5 and its approved exact contracts/files/test-map
appendices. After its implementation, independently verify only its scoped exits.
These are coherent intermediate candidates, not whole-feature compatibility or
release claims. New failures in unchanged scope must be reported; temporary
incompleteness of a clearly later deliverable is not falsely certified as passing.
No successful public consumer is replaced with a mock-only final proof.

| Stage | Candidate/artifact and permitted evidence | What it cannot certify |
| --- | --- | --- |
| Q | Exact upstream private stack/assets, actual qualified deployment and baseline Friday code/wheels; planned metadata/API/path/test/docs matrices and standalone behavior/resource probes. | New product extras, integrated guards, shared plans, installed candidate routes or authored final guides. |
| I1 | Its approved frozen Core/LLM/Memory foundation implementation plus Q facts. | Chat aggregate, Runtime consumer wiring, common document plan and smart_read/public command integration. |
| I2 | Approved existing consumer/Chat-recovery integration plus verified I1. | New converter/common document plan, `/ingest` integration, document extras or whole-suite migration acceptance. |
| I3 | Approved extraction/plan/command/cache/worker and document-metadata implementation plus I1/I2. | Final independent code council, human UAT, acceptance or another unit's Tools routing. |
| AG | Full frozen source/artifacts/evidence; all original technical DI/FC checks and complete map/docs review; required separately authorized DI-12 three-seat code council. | Human UAT as already run, maintainer acceptance or delivery. |
| UAT | Explicit human runs on the verified installed disposable setup, after AG. | Automatic acceptance/production rollout/model selection or delivery. |

Full requirement **accounting** is checked at AG. DI-12 has ordered AG and UAT
substates; its human execution cannot be labelled complete until recorded.
Full DI-35/36 review covers all changed phases at AG, while I1/I2 review only
their own maps/content. This preserves required verification without a forward
phase dependency.

## Slice exits and concrete planned witnesses

Each following assertion joins implemented owner/files, its phase's input
candidate, prerequisite stages and planned witness in the JSON. A planned path
within a broad parent row still needs exact A2/A3 approval; no extra helper is
implicitly allowed. All existing named FC nodes remain required.

### I1 scoped exit

| Exit | Owners / implementation | Planned witness and scope |
| --- | --- | --- |
| I1-C1 | Core; `packages/friday-core/src/friday_core/ingestion.py` and the exact listed JSON paths. | `packages/friday-core/tests_core/test_interfaces.py::test_ingestion_contracts_are_immutable_and_backend_neutral` — Validate neutral values/protocol shape and old public interfaces; no Tools/Memory backend import and no actual smart_read/common plan claim. |
| I1-C2 | LLM, Memory metadata; `packages/friday-llm/src/friday_llm/embeddings.py` and the exact listed JSON paths. | `packages/friday-llm/tests_llm/test_embeddings.py::test_qualified_preparation_limits_and_indexed_batch_guards` — Implement/test actual LLM preparation/count/batch boundary on supplied text and qualified facts; narrow counter edge. No document splitting, Runtime assembly or full document DI17/24 closure. |
| I1-C3 | Memory; `packages/friday-memory/src/friday_memory/ingestion/embedding_space.py` and the exact listed JSON paths. | `packages/friday-memory/tests_memory/test_adapters/test_vector.py::test_direct_namespace_admission_contracts` — Direct factory/store admission and identity values, matching reopen and foreign/missing identity refusals; no Chat/Runtime startup claim. |
| I1-C4 | Memory; `packages/friday-memory/src/friday_memory/maintenance/recovery_models.py` and the exact listed JSON paths. | `packages/friday-memory/tests_memory/test_maintenance/test_recovery_participant.py::test_memory_v2_models_and_typed_loader_contract` — Memory-v2 model/loader, old v1 strictness and fingerprint inputs only; no actual Chat aggregate/rollback claim. I1 map and changed-contract notes accepted for I1 only. |

### I2 scoped exit

| Exit | Owners / implementation | Planned witness and scope |
| --- | --- | --- |
| I2-C1 | Memory, Chat, Runtime, Core profiles, CLI conditional; `packages/friday-runtime/src/friday_runtime/di.py` and the exact listed JSON paths. | `tests/integration/test_embedding_compatibility.py::test_existing_embedding_configuration_and_origin` — Actual existing pool/non-pool startup/admission, logging, ephemeral isolation and headless counter installs. CLI is source-unchanged if forwarding suffices; otherwise exact approved paths. Read-only text uses no embedding prerequisite. |
| I2-C2 | Memory, Chat, Runtime, listed Tools wrappers; `packages/friday-memory/src/friday_memory/context/assembler.py` and the exact listed JSON paths. | `tests/integration/test_embedding_compatibility.py::test_model_change_preserves_operational_contract` — Actual existing conversation/graph/recall/MCP/task/maintenance/lifecycle/inspection/multi-agent B/N/R and truthful effects. No common document chunk plan or unwired route credit. |
| I2-C3 | Memory, Chat; `packages/friday-memory/src/friday_memory/maintenance/recovery.py` and the exact listed JSON paths. | `tests/integration/test_embedding_compatibility.py::test_chat_v2_snapshot_roundtrip_and_same_namespace_rollback` — Actual Memory-v2 → Chat aggregate-v2 write/read/reparse → admitted same-namespace restore/automatic rollback; strict mixed/version/identity negatives. I2-only map/docs review. |

### I3 scoped exit

| Exit | Owners / implementation | Planned witness and scope |
| --- | --- | --- |
| I3-C1 | Tools; `packages/friday-tools/src/friday_tools/filesystem/readers/document_ingestion.py` and the exact listed JSON paths. | `packages/friday-tools/tests_tools/test_document_ingestion.py::test_genuine_format_scope_and_complete_success_admission` — Real native/OCR formats, order/coverage, selected-release structural mapping, no fallback or diagnostic content, resource admission and missing-assets independence. |
| I3-C2 | Memory, Tools, Core contracts; `packages/friday-memory/src/friday_memory/ingestion/document_ingestion.py` and the exact listed JSON paths. | `tests/integration/test_document_ingestion.py::test_headless_common_plan_and_destination_bound_receipts` — Real headless Memory factory → Core entry → smart_read text small/large/force_chunked/cache paths; raw chunks equal common plan, derived records unsplit, no Chat import and no second split. |
| I3-C3 | Commands, Chat, Memory; `packages/friday-commands/src/friday_commands/file_inputs.py` and the exact listed JSON paths. | `tests/integration/test_document_ingestion.py::test_registry_stores_extracted_document_chunks` — Actual raw-tail default-handler parsing and genuine registry document→common plan→stored chunks, metadata/descriptions and zero-ingestion failures; preserve unrelated/custom handlers. |
| I3-C4 | Tools worker, Memory text planning, LLM counter, caller request owner; `packages/friday-tools/src/friday_tools/filesystem/readers/document_ingestion.py` and the exact listed JSON paths. | `packages/friday-chat/tests_chat/test_document_ingestion.py::test_cancelled_ingestion_waits_for_quiescence_without_late_storage` — Actual responsive event loop/admission, owned workers/no provider-store capabilities, cancellation before/during/after completion, stale success refusal and idempotent quiescence. |
| I3-C5 | Tools, Chat, all affected test/document owners; `packages/friday-tools/pyproject.toml` and the exact listed JSON paths. | `tests/integration/test_document_ingestion.py::test_clean_installed_candidate_document_profiles` — Actual candidate extra names/edges, clean installs/Certifi/origins, all positive format/provenance/storage and negative controls; authored docs and complete implementation map. Earlier positive claims remain for exact source, final candidate reviewed at AG. |

## Full requirement first-availability join

This table lists first availability of the **complete original** scenario,
not scoped foundation credit. AG still verifies all technical proof against the
final candidate; a reused receipt requires valid source/contract attribution.
The full original definition/digest is in the JSON, not abbreviated away here.

| Requirement | Earliest complete evidence | Scoped earlier/later exit references |
| --- | --- | --- |
| DI-01 | I3 | I3-C1 |
| DI-02 | I3 | I3-C1 |
| DI-03 | I3 | I3-C1 |
| DI-04 | I3 | I3-C1 |
| DI-05 | I3 | I3-C3 |
| DI-06 | I3 | I3-C3 |
| DI-07 | I3 | I3-C3 |
| DI-08 | I3 | I3-C5 |
| DI-09 | I3 | I3-C5 |
| DI-10 | AG | I3-C5 |
| DI-11 | I3 | I3-C4 |
| DI-12 | UAT | Original requirement is checked directly in full at AG; no early exit substitutes. |
| DI-13 | I3 | I3-C1 |
| DI-14 | I3 | I3-C1 |
| DI-15 | I3 | I3-C5 |
| DI-16 | I3 | I3-C2, I3-C3 |
| DI-17 | I3 | I1-C2, I3-C2 |
| DI-18 | I2 | I1-C2, I2-C1 |
| DI-19 | I3 | I3-C2, I3-C3 |
| DI-20 | I3 | I3-C5 |
| DI-21 | I2 | I1-C3, I2-C1 |
| DI-22 | I2 | I1-C2, I2-C2 |
| DI-23 | I3 | I1-C1, I3-C2 |
| DI-24 | I3 | I1-C2 |
| DI-25 | I3 | I3-C1 |
| DI-26 | I3 | I3-C4 |
| DI-27 | I2 | I1-C4, I2-C3 |
| DI-28 | I2 | I2-C1, I2-C2, I2-C3 |
| DI-29 | I3 | I1-C3, I2-C1, I3-C3 |
| DI-30 | I3 | I3-C2 |
| DI-31 | I3 | I3-C2 |
| DI-32 | I2 | I1-C4, I2-C3 |
| DI-33 | I3 | I2-C1, I2-C2 |
| DI-34 | AG | I2-C1, I2-C2, I3-C5 |
| DI-35 | AG | I1-C1, I1-C2, I1-C3, I1-C4, I2-C1, I2-C2, I2-C3, I3-C5 |
| DI-36 | AG | I1-C4, I2-C3, I3-C5 |

DI-23: I1-C1 proves neutral entry contracts only; I3-C2 implements and exercises
actual Memory factory → entry → smart_read text small/large/force_chunked and
warm-cache storage. DI-32: I1-C4 proves Memory-v2 values/loaders only; I2-C3
executes actual Chat aggregate-v2 write/read/reparse and same-namespace rollback.
DI-17: supplied-text counter guard in I1-C2 is not document/table/slide chunking;
I3-C2 proves final real chunk budgets/content. DI-29's existing startup/text
portion is I2-C1; the actual document `/read` embedding-independence portion
waits for I3-C3. DI-33/34 require final common-entry and all-consumer dispositions,
not only the earlier existing-record round trip.

## FC, profiles and review sequencing

FC-01–14 remain fully required. I1 supplies underlying contracts; I2 exercises
existing logging/MCP/backup/analyzer/synthesis/tasks/lifecycle/recall/profile/
configuration/dimension/indirect operations; I3 adds common-entry/source-derived
and installed document interactions. All original named tests and B/N/R oracles
are retained for AG. Source-unchanged consumers still receive actual disposition.

RD-06 Q graph feasibility uses upstream artifacts and unchanged Friday code,
with proposed extra declarations labelled as proposals. I1 creates the narrow
LLM/Memory counter metadata; I2 tests actual headless candidate installs. I3
creates Tools' document extra/default Chat edge and proves clean document/bare
Tools/shared-extractor profiles. AG validates actual final installations and
security/origins. Separate TOOLS-DOC activation later proves factory/smart_read
four-format selections; neither an INGEST helper nor a profile import claims it.

DI-12 is mandatory: after the code/evidence freeze, obtain dispatch authority
and run fresh Sol/Astra/Opus code council. If authority is absent, stop at that
gate; do not omit the review. Human UAT follows verification and is recorded
separately. Current document review is not that future code council.

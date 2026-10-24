# TELEM-04 source inventory

Preparation base: e6209e3156216afde1655758e280690229f7d3e6.
[Exact AST definitions, APIs, hashes and target paths](source-inventory.json).
This is static inspection, not an executed behavioral baseline.

| Current boundary | Observation and proposed placement |
| --- | --- |
| TurnProcessor.process/process_streaming | No whole-turn telemetry identity; scope begins before circuit/selection and ends after full existing persistence or failure |
| _prepare_turn | Selection/rejections and retrieval precede the model; no exported raw query/tool names or memory payload |
| _complete_with_retries | Outer Chat retries/timeout are separate from shared LLM attempts; observe actual invocations without changing retry policy |
| _complete_tool_turn | Builds/redacts assistant history before follow-up calls; derive safe reasoning-preservation booleans from actual outbound messages |
| ToolLoop.run | Dispatches native/MCP calls; swallows KeyError in existing control flow; observe that failure and validate returned MCP status before counting success |
| _persist_turn | Memory store, transcript turn, optional raw context log and MCP-aware interaction occur sequentially; later failure can leave partial persistence, so no atomicity/success claim |
| FrameworkMemoryAdapter.ingest_document | Existing single/batch storage returns actual chunk count; observe without paths/content or extra calls |
| FrameworkMaintenanceAdapter._extract_turns | Per-item extraction, requeue on failures and special committed-under-cancellation semantics; preserve those facts and originating turn |
| BackgroundWorkCoordinator.schedule_after_turn | Generates a separate extraction work ID and schedules outside completed turn execution; explicit safe origin handoff is needed |
| PendingExtractionTurn/TurnResult | Add optional final safe metadata field with default None; raw persisted IDs and result fields remain unchanged |
| ChatTelemetryObserver | Strict accepted LLM/MCP/lifecycle projections,256 records/128 spans; add independently validated execution family and bounded fixed metrics |
| /debug and /timing | Existing successful-result fields are available, but failed turns have no TurnResult; render safe observer terminal summaries as well |

Shared LLM request/attempt/batch IDs already exist; the observer can link validated
request_start to an active scope without changing those accepted payloads. MCP
events have existing safe server/tool refs but no invocation ID; new linked
projections carry the current operation context without inventing old payload fields.
Accepted memory_mcp coordination, core MCP provenance and raw storage protocols are
read-only boundaries. Headless assembly and vendor callbacks are outside CD-004.

Nine prospective existing source targets pass genuine Ruff and Mypy. Three new
source and six new test paths are absent at this preparation baseline. No new
source/test or behavioral result is claimed by this inventory.

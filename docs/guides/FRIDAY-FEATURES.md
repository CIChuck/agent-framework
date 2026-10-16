---
title: Friday capability status
description: Implemented, limited, placeholder and queued capabilities with direct evidence and guide ownership.
framework_version: 0.1.0a3
last_reviewed: '2026-10-15'
status: current
audience: Technical end users and application integrators
doc_type: reference
---

# Friday capability status

This reference describes the reviewed **0.1.0a3 implementation**, not a roadmap
or a claim of production certification. Framework APIs and their Chat integration
can have different maturity. Installation/extras supply dependencies, not runtime
enablement. Use the [board](../planning/README.md) for current work authority.

## Application and composition

| Capability | Current status | Evidence / guide |
| --- | --- | --- |
| Maintained terminal application | `friday-chat`; explicit YAML; fake default and opt-in real model/memory/tool assembly | [CLI](09-cli-reference.md), [Chat assembly](../../packages/friday-chat/src/friday_chat/runtime.py) |
| `friday` executable from CLI component | Declared placeholder entry point, not a functioning application | [CLI main module](../../packages/friday-cli/src/friday_cli/main.py) |
| Headless lifecycle | `RuntimeConfig` and `RuntimeKernel` compose configured services/profiles | [Architecture](03-core-concepts.md) |
| Automatic Chat first-run setup | No `init`/`doctor` implementation or implicit OS-config lookup | [Desktop setup](16-desktop-deployment.md) |
| Root distribution | Metadata-only aggregate, no importable root module | [Package map](14-appendices.md#package-map) |

## Models and memory

| Capability | Current status | Evidence / guide |
| --- | --- | --- |
| Chat/embedding transport | LiteLLM-backed; pinned 1.100.1 | [LLM README](../../packages/friday-llm/README.md) |
| Canonical model library | Strict versioned endpoint/model profiles, env credential names and role bindings | [Configuration](10-configuration.md) |
| Typed requests/events | Distinct text/reasoning/tool/usage/finish surfaces; control support is profile-specific | [Advanced integration](11-advanced-topics.md) |
| Built-in normalized controls | LM Studio + OpenAI-compatible Chat Completions + Qwen3.8; not universal provider parity | [LLM README](../../packages/friday-llm/README.md) |
| Episodic/vector/graph memory | Implemented adapters/controllers; persistence and embeddings explicitly configured | [Memory](04-adaptive-memory.md) |
| Extraction/consolidation | Implemented, can call configured models; quality and completion evaluated separately | [Memory](04-adaptive-memory.md#from-a-turn-to-reusable-memory) |
| Context pruning | Formatting overhead reserved; prior-session history included and pruned first under pressure | [Budget guide](memory-management-guidelines.md) |
| Background compaction | Opt-in Chat monitor/compactor; cooldown, severity and result limits apply | [Budget guide](memory-management-guidelines.md#automatic-compaction-is-opt-in-in-chat) |
| Lifecycle and maintenance | Staged scoring, explicit mutation/recovery; capabilities/preflight can refuse operations | [Memory](04-adaptive-memory.md#maintenance-backups-and-recovery) |
| Transcript persistence/export | SQLite/JSONL stores and CSV/JSONL/Markdown views; raw content is sensitive | [Transcript example](04-adaptive-memory.md#durable-transcripts) |
| Pinecone/Neo4j/Ollama-specific adapter classes from old guides | Not shipped under those names; custom backend work is separate | [Architecture](03-core-concepts.md#protocols-and-concrete-implementations) |

## Agents, workflows and tools

| Capability | Current status | Evidence / guide |
| --- | --- | --- |
| Interactive agents | Implemented `InteractiveAgent`/`ReplAgentBase`; compatibility `CopilotAgent` name | [Agents](06-agents.md) |
| Framework orchestration | Single active agent, cached instances, explicit routing/delegation and configured factories | [Multi-agent guide](07-multi-agent.md) |
| Chat specialist-agent execution | Deterministic `FakeOrchestrator` in fake and real modes; not independent model agents | [Assembly](../../packages/friday-chat/src/friday_chat/runtime.py) |
| Autonomous agent | Placeholder; `run()` raises `NotImplementedError` | [Source](../../packages/friday-agent/src/friday_agent/autonomous.py) |
| Workflow hierarchy | Canonical workflow/pipeline/task models, loader/executor, contracts and dispatch state | [Workflows](08-workflows.md) |
| Chat workflow execution | Real mode uses flat engine plus deterministic agent adapter; canonical listing does not imply runnable bundles | [Adapter](../../packages/friday-chat/src/friday_chat/adapters.py) |
| Namespace-aware sharing | Additive wrapper, policy and promotion journal; host authentication/metadata protection still required | [Multi-agent memory](07-multi-agent.md#namespace-aware-memory) |
| Native tools | Function and typed class surfaces, explicit registry/selection; implementations and stubs coexist | [Tools](05-tools.md), [catalog](14-appendices.md#native-tool-source-catalog) |
| Shell/subprocess isolation | Host privileges/policy checks; not arbitrary-code containment | [Execution backends](11-advanced-topics.md#execution-backends) |
| Docker/mock backends | Explicit Docker provisioning; mock does not execute code | [Sandbox README](../../packages/friday-sandbox/README.md) |
| DSPy/knapsack optimizer | Optimization package skeleton only; no implemented training/compiler/evaluator API | [Optimization README](../../packages/friday-optimization/README.md) |

## MCP and observability

| Capability | Current status | Evidence / guide |
| --- | --- | --- |
| MCP modern tools | Explicit 2026-07-28 stdio/Streamable HTTP clients and modern server APIs | [MCP matrix](19-mcp-migration.md) |
| MCP compatibility | Explicit 2025-11-25 HTTP client; retained 2024-11-05 legacy APIs/default stdio | [MCP matrix](19-mcp-migration.md) |
| Integrated MCP | Disabled default; canonical filters, budgets, strict HTTPS trust/auth/network policy | [Client guide](17-mcp-client.md) |
| Catalog refresh | Programmatic generation-bound refresh; integrated stop/start rediscovery | [Refresh contract](17-mcp-client.md#explicit-manual-catalog-refresh) |
| MRTR/input-required | Unsupported continuation; explicit categorical failure, no callback/state forwarding | [Client results](17-mcp-client.md#dated-tool-results-and-optional-features) |
| Optional MCP roles | No modern Tasks, roots/sampling/elicitation, subscriptions or integrated resources/prompts; no OAuth discovery/login/refresh | [Client](17-mcp-client.md), [server](18-mcp-server.md) |
| Provider-neutral telemetry | Implemented interface/providers/factory/lifecycle and closed LLM/MCP/execution schemas | [Telemetry README](../../packages/friday-telemetry/README.md) |
| Chat diagnostics | Default-disabled bounded local debug observer, turn correlation and borrowed injection | [CLI/configuration](10-configuration.md#telemetry-configuration-and-langfuse) |
| Owned OpenTelemetry | Optional validated SDK/API 1.39.1, console/OTLP-gRPC, verified-TLS policy; no automatic global bridge | [Advanced telemetry](11-advanced-topics.md#telemetry-ownership-and-exporters) |
| Provider-neutral Langfuse | Queued, not the legacy callback/extra path | [Board](../planning/README.md) |
| Universal content sanitization | Not guaranteed; closed telemetry, raw transcripts, native helpers and checked MCP have different boundaries | [Security](security-configuration-guidelines.md) |

## Optional domain/audio integrations

| Capability | Current status | Evidence / guide |
| --- | --- | --- |
| Finance | Massive data wrapper; plan/freshness dependent; tier probing placeholder and limited exception normalization | [Finance README](../../packages/friday-finance/README.md) |
| Moltbook | Typed client with read/mutation operations; application supplies auth and action authority | [Moltbook README](../../packages/friday-moltbook/README.md) |
| Standalone TTS/wake word | ElevenLabs/Picovoice adapters with explicit provider/device setup | [Speech](speech.md) |
| Built-in STT | Picovoice transcription capture not wired; custom adapter required | [Speech](speech.md#current-capability-boundaries) |
| Chat provider audio | Deterministic `FakeSpeechAdapter` even in real mode | [Speech](speech.md) |

## Interpreting status

“Implemented” means the named source surface exists with the documented limits.
It does not certify every provider, public deployment or semantic output.
“Placeholder” means a declared API is not functional. “Queued” describes board
work without implementation authority. Guide review dates describe evidence
freshness and do not change those product/lifecycle states.

[Guide index](README.md) · [Capability status](FRIDAY-FEATURES.md)

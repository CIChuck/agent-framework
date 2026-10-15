---
title: Friday framework overview
description: Scope, architecture, capabilities and adoption boundaries for the alpha3 release.
framework_version: 0.1.0a3
last_reviewed: '2026-10-15'
status: current
audience: Technical end users and application integrators
doc_type: guide
---

# Friday framework overview

Friday is a modular Python framework for applications that combine language
models, conversational memory, tools and agent orchestration. Friday Chat is
the maintained terminal application built on those libraries. The release
reviewed here is **0.1.0a3**, an alpha requiring **Python 3.13.4 or newer**.

These guides describe the shipped implementation. A successful model response,
a stored memory or a completed workflow is evidence of that operation; judging
the response's correctness remains part of your application.

## What Friday provides

| Capability | Implemented surface | What you configure or supply |
| --- | --- | --- |
| Chat and embeddings | LiteLLM-backed services, typed requests and streaming events | Model endpoints, exact model identities, credentials and generation settings |
| Conversation history | Episodic stores and SQLite/JSONL transcripts | Session identity, persistence paths and retention |
| Semantic recall | Vector stores, collection management and retrieval scoring | Embedding model, compatible dimensions and collection policy |
| Entity relationships | Graph adapters, extraction and graph retrieval | Ontology, extraction service and application trust policy |
| Context assembly | Retrieval, pruning, prompt layout and optional compaction | Context/output budgets, history and supporting-context limits |
| Tools | Native functions/classes, registries, selection and execution loops | Explicit admission, permissions, environment and output handling |
| Multiple agents | Profiles, registries, mention routing, delegation and workflows | Concrete profiles, factories, service bindings and handoff rules |
| MCP | Local stdio and explicitly admitted HTTPS tools clients; separate server APIs | Dated protocol profiles, peer trust, authentication, filters and limits |
| Observability | Provider-neutral telemetry contracts, owned factories and bounded Chat diagnostics | Explicit enablement, provider ownership and exporter policy |

The [capability reference](FRIDAY-FEATURES.md) distinguishes working components
from placeholders and queued integrations. `AutonomousAgent` is a placeholder;
the Optimization package does not supply an implemented optimizer. The planned
provider-neutral Langfuse integration remains queued. Existing legacy Langfuse
callback support is a separate compatibility path.

## How a conversation uses the framework

1. The application loads its configuration and resolves model/embedding roles.
2. A user message enters the Chat turn processor or an application-owned agent.
3. Context assembly combines relevant history, semantic passages and graph
   information within the configured budget.
4. The model produces text and, when enabled and admitted, tool calls. The
   owning loop validates and executes tools and presents results to the model.
5. The application records the turn and may schedule extraction, consolidation
   or compaction. Those are separate operations with their own failure states.

Memory changes future **context**; it does not train or change model weights.
Retrieval can omit relevant evidence and extraction can produce incorrect facts.
Use provenance and source documents to evaluate important recalled information.

## Three memory roles

- **Episodic memory** retains conversation turns. In-memory history disappears
  with the process; durable transcript adapters persist according to their backend.
- **Semantic memory** stores text and metadata with embeddings for similarity
  search. Changing embedding models can require rebuilding compatible collections.
- **Associative memory** represents entities and relationships. Access scores
  influence retrieval and lifecycle behavior; frequency does not establish truth.

These roles are coordinated through `MemoryController`, with `ContextAssembler`
and `PromptArchitect` turning recall into model messages. Storage durability and
context inclusion are different: a stored item need not appear in every prompt.
See [adaptive memory](04-adaptive-memory.md).

## Choose an adoption path

| Goal | Start here |
| --- | --- |
| Explore the terminal UI without credentials | [Offline Chat quick start](02-getting-started.md#run-an-offline-chat-session) |
| Run Chat with your models and persistent memory | [Real-session setup](02-getting-started.md#prepare-a-real-session) and [configuration](10-configuration.md) |
| Embed one component | Its [package README](../../README.md#package-map) and the corresponding technical guide |
| Assemble a headless application | [Runtime composition](03-core-concepts.md#runtime-composition-and-ownership) |
| Connect external MCP tools | [MCP client setup](17-mcp-client.md) |
| Publish explicitly owned tools to MCP clients | [MCP server APIs](18-mcp-server.md) |

The root distribution is `friday-framework`; it is metadata-only and does not
provide a `friday_framework` Python module. Distribution names, import names
and executable names differ. [Package mapping](14-appendices.md#package-map)
lists all 16 workspace packages.

## Deployment and trust boundaries

Local model serving is a deployment choice. Extraction, embeddings, maintenance,
tools, speech and exporters have independent destinations, so selecting a local
chat model alone does not establish that all data stays on the machine.

Tool schemas and prompt-injection scanning do not grant permissions or provide
an operating-system isolation boundary. Namespace metadata is not a complete
tenant-security system. Authentication, consent, filesystem/network limits,
backup, access control and content retention belong to the deployed application.
The framework does not confer HIPAA, GDPR or SOC2 compliance.

Start with synthetic data and explicit paths; verify the capabilities you need
before adding provider-backed operations. The guides label offline examples,
configuration fragments and live examples so you can choose the appropriate
validation environment.

[Guide index](README.md) · [Capability status](FRIDAY-FEATURES.md)

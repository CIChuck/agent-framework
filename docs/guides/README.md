---
title: Friday technical guides
description: Navigation and reading paths for the reviewed alpha3 technical end-user documentation.
framework_version: 0.1.0a3
last_reviewed: '2026-10-15'
status: current
audience: Technical end users and application integrators
doc_type: navigation
---

# Friday technical guides

These 25 documents explain the current **Friday 0.1.0a3** implementation for
technical end users and application integrators. They require Python 3.13.4+.
Start with the task you want to complete, then follow the deeper reference.
The [repository/package READMEs](../../README.md) remain the installation and
component entry points.

## Reading paths

| Your task | Read next |
| --- | --- |
| Try Friday without keys or real stores | [Offline Chat](02-getting-started.md#run-an-offline-chat-session) |
| Configure real models/memory | [Configuration](10-configuration.md), then [memory](04-adaptive-memory.md) |
| Embed the framework | [Core concepts](03-core-concepts.md) and the relevant package README |
| Add native tools | [Tools](05-tools.md), [security](security-configuration-guidelines.md) |
| Design agents/workflows | [Agents](06-agents.md), [orchestration](07-multi-agent.md), [workflows](08-workflows.md) |
| Connect or expose MCP tools | [Client](17-mcp-client.md), [server](18-mcp-server.md), [migration](19-mcp-migration.md) |
| Tune context | [Memory management](memory-management-guidelines.md) |
| Operate/debug | [Desktop setup](16-desktop-deployment.md), [CLI](09-cli-reference.md), [troubleshooting](13-troubleshooting.md) |
| Check whether a feature actually ships | [Capability status](FRIDAY-FEATURES.md) |

## Numbered series

| Guide | Technical coverage |
| --- | --- |
| [Framework overview](01-executive-summary.md) | Scope, adoption choices, architecture and alpha boundaries |
| [Getting started](02-getting-started.md) | Installation, offline Chat and real-session preparation |
| [Core concepts](03-core-concepts.md) | Package contracts, composition, turn flow and ownership |
| [Adaptive memory](04-adaptive-memory.md) | Stores, extraction, recall, scoring and recovery |
| [Tools](05-tools.md) | Function/class APIs, registries, selection and execution |
| [Agents](06-agents.md) | Validated profiles, factories, model/tool bindings and lifecycle |
| [Multi-agent orchestration](07-multi-agent.md) | Framework routing, handoffs, namespace policy and Chat limits |
| [Workflows](08-workflows.md) | Canonical bundles, flat compatibility, approval and dispatch |
| [CLI reference](09-cli-reference.md) | Current process options, slash commands and side effects |
| [Configuration](10-configuration.md) | Chat versus Runtime schemas, canonical models and integrations |
| [Advanced integration](11-advanced-topics.md) | Adapters, performance, telemetry, backends and deployment |
| [Application patterns](12-use-cases.md) | Practical designs with explicit evidence and acceptance checks |
| [Troubleshooting](13-troubleshooting.md) | Boundary-specific diagnosis without deleting state |
| [Reference](14-appendices.md) | Distribution/import map, static tool catalog, APIs and glossary |
| [Contributing](15-contributing.md) | Workspace checks, governance and guide maintenance |
| [Desktop deployment](16-desktop-deployment.md) | Pinned uv install, persistent config/state and launch paths |
| [MCP client](17-mcp-client.md) | Dated peer config, admission, results, refresh and lifecycle |
| [MCP server](18-mcp-server.md) | Explicit modern tools registration and stdio/HTTP server policy |
| [MCP migration](19-mcp-migration.md) | Transport/profile matrix, explicit upgrades and rollback |


## Supplementary guides

- [Memory budgeting and maintenance](memory-management-guidelines.md)
- [Security configuration and output handling](security-configuration-guidelines.md)
- [Speech services and current Chat limits](speech.md)
- [Capability status](FRIDAY-FEATURES.md)
- [Detailed outline and subject ownership](OUTLINE.md)

## How to interpret examples and metadata

Complete offline examples use synthetic data and temporary/explicit paths. Live
examples identify credentials/endpoints/hardware and can incur provider calls
or write state. Configuration fragments name their owning schema. Fake adapters
validate control flow, not real provider behavior.

Every document records its framework version and actual review date in front
matter. `status: current` refers to the guide's implementation basis, not
production certification or maintainer acceptance. Shipped limitations and
queued features remain explicit. Current source/accepted contracts control over
historical plans. The guide upgrade does not change package behavior or republish
existing PyPI artifacts.

[Guide index](README.md) · [Capability status](FRIDAY-FEATURES.md)

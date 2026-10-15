---
title: Guide outline and subject ownership
description: Detailed section map and ownership rules for the current technical guide series.
framework_version: 0.1.0a3
last_reviewed: '2026-10-15'
status: current
audience: Technical end users and application integrators
doc_type: navigation
---

# Guide outline and subject ownership

The numbered series is organized around the current implementation rather
than a future architecture. Each subject has a primary guide; supplemental
documents go deeper without duplicating a second full CLI/config reference.
Use the [index](README.md) for task-oriented reading paths.

## Series and subject ownership

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


## Detailed section map

### [Framework overview](01-executive-summary.md)

- What Friday provides
- How a conversation uses the framework
- Three memory roles
- Choose an adoption path
- Deployment and trust boundaries

### [Getting started](02-getting-started.md)

- Prerequisites and installation
- Run an offline Chat session
- Prepare a real session
- Check persistence without relying on model recollection
- Use a component without Chat
- Where to go next

### [Core concepts](03-core-concepts.md)

- Architecture layers
- Protocols and concrete implementations
- Runtime composition and ownership
- A turn is a sequence of distinct operations
- Memory, orchestration and workflow state
- Observation and resource ownership
- Implementation references

### [Adaptive memory](04-adaptive-memory.md)

- Stores and controllers
- Durable transcripts
- Semantic search without a provider
- From a turn to reusable memory
- Recall and cross-session priming
- Context engineering
- Lifecycle stages and collection movement
- Provenance and namespace-aware memory
- Maintenance, backups and recovery
- Implementation references

### [Tools](05-tools.md)

- Two implementation surfaces
- Register an isolated function tool
- A typed tool
- Discovery and schema inspection
- Configure Chat tool admission
- Selection and context budgets
- Filesystem and shell policy
- External tools and outputs
- Implementation references

### [Agents](06-agents.md)

- Agent types
- A complete profile
- Profile fields and validation
- Registry and factories
- Tool autonomy and permissions
- Model and memory binding
- Lifecycle and failures
- Troubleshooting profiles
- Implementation references

### [Multi-agent orchestration](07-multi-agent.md)

- Framework and Chat surfaces
- Profiles, factories and session identity
- Routing and delegation
- Explicit handoffs
- Namespace-aware memory
- Sequential, parallel and hierarchical designs
- Operational checks
- Implementation references

### [Workflows](08-workflows.md)

- Choose the correct surface
- Canonical bundle layout
- Canonical contracts
- Flat compatibility workflow
- Execution, approval and failure
- Chat commands
- Implementation references

### [CLI reference](09-cli-reference.md)

- Process options
- Slash commands
- Session and inspection behavior
- Transcripts, exports and replay
- Tool commands
- Commands that change memory
- Orchestration and workflow limits
- Speech and security commands
- Implementation references

### [Configuration](10-configuration.md)

- Files and loaders
- Canonical model library
- Bind models to Chat roles
- Role-specific overrides and generation controls
- Chat sections and responsibilities
- Secrets and environment precedence
- Headless Runtime configuration
- MCP configuration
- Telemetry configuration and Langfuse
- Validate configuration changes

### [Advanced integration](11-advanced-topics.md)

- Route models by service role
- Typed model requests and streaming
- Implement an adapter deliberately
- Performance measurement
- Telemetry ownership and exporters
- Execution backends
- Deployment profiles and durable state
- MCP lifecycle and trust

### [Application patterns](12-use-cases.md)

- A complete offline component composition
- Research assistant with cross-session context
- Code assistance and review
- Document analysis and question answering
- Project and team knowledge
- Support and operations assistance
- Finance data assistance
- Sensitive-domain applications
- Speech and social integrations
- Evaluate the application you actually assembled

### [Troubleshooting](13-troubleshooting.md)

- Establish the baseline
- Installation and startup
- Configuration loading
- Models, reasoning and timeouts
- Memory and persistence
- Native tools and selection
- Integrated MCP diagnostics
- Agents and workflows
- Telemetry, logs and shutdown
- Report a reproducible issue

### [Reference](14-appendices.md)

- Package map
- Public API entry points
- Native tool source catalog
- Configuration and example conventions
- Migration reference
- Glossary

### [Contributing](15-contributing.md)

- Set up a development checkout
- Make a focused change
- Run appropriate checks
- Authority and review
- Maintain end-user documentation
- Submit useful review evidence

### [Desktop deployment](16-desktop-deployment.md)

- Choose an installation mode
- Stable paths
- Copy and edit configuration
- Launch explicitly
- Verify the installation in stages
- Upgrade and rollback
- Troubleshooting launch problems

### [MCP client](17-mcp-client.md)

- Install and choose a profile
- Configure a local server
- Discovery, turn budgets and results
- Inspect and troubleshoot
- Explicit HTTPS Streamable HTTP peers
- Offline programmatic round trip
- Implementation references

### [MCP server](18-mcp-server.md)

- Installation
- Register an async tool and serve stdio
- Use an explicit registry snapshot
- Serve one HTTP endpoint
- Discovery, limits and lifecycle
- Implementation references

### [MCP migration](19-mcp-migration.md)

- Choose a client configuration
- Admission, results and ownership
- Upgrade and rollback
- Alpha3 application checks
- Implementation references

## Supplement ownership

| Document | Owns | Defers to |
| --- | --- | --- |
| [Memory management](memory-management-guidelines.md) | Budget arithmetic, pruning, compaction and operational tuning | Memory guide for stores/controller architecture |
| [Security](security-configuration-guidelines.md) | Actual per-path output handling, scanner vocabulary and privacy limits | MCP guides for protocol trust/admission |
| [Speech](speech.md) | Standalone provider/config/harness behavior and Chat adapter limits | Configuration guide for general file/env loading |
| [Capability status](FRIDAY-FEATURES.md) | Implemented/limited/placeholder/queued distinction | Source, accepted contracts and current development board |

## Maintenance rules

Preserve filenames so incoming links remain stable. Update headings/anchors and
cross-links together. Keep commands and examples tied to the reviewed release;
do not reintroduce retired test-app entry points or future APIs as working
recipes. Update review metadata after checking the body, not as a date-only edit.
See [contributing](15-contributing.md#maintain-end-user-documentation).

[Guide index](README.md) · [Capability status](FRIDAY-FEATURES.md)

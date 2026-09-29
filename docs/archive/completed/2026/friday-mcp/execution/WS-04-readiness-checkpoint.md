# MCP-WS-04 Readiness Checkpoint

Date: 2026-09-28
Base: `acd1fd1e736a38134fac40d7fdb35cd1f32cf683`
Branch: `feature/friday-mcp-ws04-chat-budget`
Status: Reconciled within explicitly approved eight-feature scope

Maintainer said "proceed - lets build it" after WS-04's complete feature and
non-goal summary. Accepted WS-00 through WS-03 and fresh VAL-009 remain intact.
The construction directive records that approval and binds exact paths/checks.

Existing `ToolSelectionState` implements native/manual relevance selection,
count/schema-ratio limits, immutable evidence and existing commands. Processor
selects before memory retrieval and subtracts output/system/schema cost, but
has no canonical MCP metadata, result reservation or memory floor. Chat's
framework adapter constructs native tools synchronously and ignores MCP provider
config; direct Chat does not use RuntimeKernel. Memory already receives exact
`token_limit`, including zero. Reuse those boundaries instead of a memory change.

Add the public Chat bridge and only its runtime/app consumer wiring to reuse
accepted provider/default registry. No framework lifecycle/transport edits.
Metadata is a sidecar; plain native schemas stay compatible. Canonical MCP limits
already carry 2048 reserved result tokens and a configurable 4096 memory floor.
Required servers/provider includes are not per-turn mandatory sets; an explicit
Chat context list and exact manual selection define required selected tools.

No user-owned dirty paths are changed: `.DS_Store`, deleted `family-tree.md`,
`docker-bench-security/`, Chat pre-typed-LLM backup and sandbox Dockerfile.audit.
Base controller byte fingerprints match. Baseline commands/logs are running
under `/private/tmp/ws04-baseline`; the implementation report will include all
exact outcomes and separate unchanged broad typing/test debt. No product edit
occurred before this approved directive/checkpoint.

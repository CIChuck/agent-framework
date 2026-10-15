# Tool Manifest Continuity Remediation Tasks

---
title: Tool manifest continuity remediation tasks
initiative: friday-tool-manifest-continuity
document_type: task-list
status: draft
work_state: queued
created: 2026-09-30
updated: 2026-09-30
implementation_authority: not granted
---

The current `tools.context.required_tools` trial pins 14 explicitly named
native tools. It cannot pin an MCP server's future discoveries without knowing
their canonical names in advance. MCP admission and model-turn inclusion are
separate decisions: `tools.providers.mcp.include_tools` names tools that must
be registered at startup, while the per-turn selector may still omit admitted
tools from the API `tools` request and the textual `Available tools:` block.
`include_categories: [mcp]` can admit discovered tools without enumerating
names, but does not require all of them on every turn. Friday currently has no
configuration policy for that latter behavior.

The following tasks define a proposed remediation sequence. They do not grant
product-code implementation authority.

## TM-01: Establish a multi-turn MCP baseline

- Run a reproducible local MCP peer with a catalog discovered at startup, then
  vary user prompts across turns. Record the discovered, admitted, selected,
  API-bound, and prompt-visible canonical tool names separately.
- Exercise both explicit `include_tools` and category-based admission; record
  why optional tools are omitted, including relevance and each budget limit.
- Repeat the native 14-tool config trial so its result is not mistaken for MCP
  continuity evidence. Keep provider-backed prompt-cost and behavior evidence
  distinct from local selection tests.
- Completion evidence: a bounded, secret-free turn ledger and a demonstrated
  MCP name that is admitted at startup but absent on a later model turn, or
  evidence that current behavior already meets the intended contract.

## TM-02: Specify discovery-aware inclusion

- Define a config policy that can require all admitted, verified MCP tools on
  each turn without enumerating their names in YAML. Distinguish it from
  `include_tools`, `include_categories`, and the static `required_tools` list.
- State when the required set is captured (startup discovery, session start,
  or each turn), and what happens after peer failure, catalog replacement, or
  a new session. The policy must use the same checked definitions for the API
  request, textual manifest, and diagnostics.
- Preserve MCP admission, schema/metadata verification, collision handling,
  and tool authorization. Discovery alone must not bypass those gates.
- Completion evidence: a reviewed behavior contract and config example using
  a peer whose tool names are unknown before startup.

## TM-03: Resolve count and context-budget conflicts

- Decide whether a discovered-required set that exceeds `max_tools`, optional
  `max_mcp_tools`, schema-token ceiling, result reservation, or memory floor
  rejects the turn or follows an explicit priority/degradation rule. Define
  diagnostics that identify the limit without exposing untrusted peer text.
- Validate static contradictions early: the current parser accepts more
  `required_tools` names than `max_tools`, while turn selection fails later.
  Specify the corresponding check for any discovery-aware policy once the
  catalog is known.
- Completion evidence: approved failure/degradation rules and examples for a
  fitting catalog, an oversized catalog, and a required tool that disappears.

## TM-04: Implement the approved runtime and configuration contract

- After explicit construction authority, add the selected config shape and
  discovery-aware selection behavior. Keep `/inject-tools` and `/clear-tools`
  semantics explicit when configured required sets and manual selections meet.
- Reuse one checked selection snapshot for prompt text, API schemas, budget
  accounting, and diagnostics. Do not silently evict required MCP tools.
- Completion evidence: focused config and turn-selection tests, including
  unknown-before-startup names, registry changes, unavailable peers, malformed
  schemas, and count/token/memory-limit failures.

## TM-05: Validate continuity and operational cost

- Independently verify the implementation against the approved contract and
  a frozen candidate. Repeat the TM-01 conversation with different prompts and
  compare selected names, schema identity, and textual manifest on each turn.
- Measure actual provider request size and context use with the discovered
  catalog. Record whether stable inclusion improves tool availability; do not
  infer model-quality gains from manifest stability alone.
- Completion evidence: a review verdict, reproducible commands, bounded
  evidence, and any remaining limits or regressions.

## Decisions needed before implementation

1. Should every admitted MCP tool be required, or only tools admitted by a
   separate discovery-aware rule?
2. Is the discovered-required set frozen for a session or re-evaluated on each
   turn when availability changes?
3. When the full set cannot fit, should the turn fail or should an explicitly
   ordered subset remain available?

Source boundaries: [MCP client guide](../../../guides/17-mcp-client.md),
[per-turn selector](../../../../packages/friday-chat/src/friday_chat/tools/selection.py),
[turn assembly](../../../../packages/friday-chat/src/friday_chat/turns/processor.py),
and [MCP registry bridge](../../../../packages/friday-chat/src/friday_chat/tools/mcp.py).

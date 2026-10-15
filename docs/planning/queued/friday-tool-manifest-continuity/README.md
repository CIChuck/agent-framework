# Friday Tool Manifest Continuity Remediation

---
title: Friday tool manifest continuity remediation
initiative: friday-tool-manifest-continuity
document_type: initiative-index
status: draft
work_state: queued
condition: normal
created: 2026-09-30
updated: 2026-09-30
next_gate: validate the native-tool trial and review discovery-aware MCP remediation tasks
implementation_authority: not granted
---

## Symptom and evidence

The tool list visible to the model appears to move in and out of context across
user turns in one Friday conversation. This is an observed continuity problem,
not yet evidence that the registered catalog changes or that model quality has
degraded.

Read-only inspection on 2026-09-30 of the local Friday transcript export found
the `Available tools:` block changing within one session:

| Stored turn | Visible tool count | Observation |
| ---: | ---: | --- |
| 3 | 14 | Full native list |
| 4 | 1 | `serper_search` only |
| 5 | 14 | Full native list returns |
| 13 | 5 | Selected subset |
| 14 | 14 | Full native list returns |
| 15 | 3 | `file_write`, `file_read`, `directory_list` |

These counts were extracted from `context_log.raw_prompt` in the local
`.friday/exports/friday_transcripts.sqlite` without copying user messages,
tool arguments, or prompt text into this packet. The export is local evidence,
not a committed validation fixture.

Current source explains the pattern:

- `TurnProcessor._prepare_turn()` calls `select_for_turn(user_message)` for
  every user turn and builds a new prompt and model request from that selection.
- Automatic selection keeps tools scoring at or above the configured relevance
  threshold; when none qualify, it considers the full registered list. It then
  applies count, schema-token, result-reservation, and memory-floor limits.
- The example configuration sets `recommendation_threshold: 0.5` and
  `include_in_context: true`, so the selected set also appears as an
  `Available tools:` text block. At the time of the saved session, no required
  set was configured.
- Existing `tools.context.required_tools` can require named tools on each turn,
  and `/inject-tools` can keep an exact manual set until `/clear-tools`.
  Required tools still have to pass the budget and registry checks.
- Within one turn, the selected definitions are reused for each tool
  continuation. The observed change is between user turns.

On 2026-09-30, the maintainer directed a config-only trial: the repository
example now lists all 14 of its current registry tools under
`tools.context.required_tools`. The separate, pre-existing removal of three
finance registry entries was preserved. A read-only load using the supplied
environment script resolved all 14 tools; two different user messages each
selected the same 14, with an estimated 2,747 schema tokens against an
11,875-token tool ceiling. This establishes configuration acceptance, not yet
provider-backed conversation behavior or historical quality impact.

The registered catalog, the selected API `tools` schemas, and the textual
`Available tools:` block are distinct surfaces. This remediation must verify
their identities separately. A tool registered in Friday can be unavailable to
the model on a turn when its schema is not selected.

The config-only trial does not resolve dynamic MCP discovery. Static
`required_tools` names cannot cover tools whose names are unknown until a peer
is discovered. Category-based MCP admission can register those tools, but the
per-turn selector may still omit them. The proposed [remediation tasks](remediation-tasks.md)
define the discovery-aware contract and validation needed to close that gap.

## Current configuration trial and remaining contract

The maintainer selected every currently declared native tool as the stable
configured set. Validate this config-only behavior across a real multi-turn
Friday conversation. Separately, define a bounded discovery-aware contract
for MCP tools; static required names do not meet that need. Future registry
additions are not automatically added to the explicit required list.

The design must preserve these existing boundaries:

- Only registered and currently authorized tools may be sent to the model.
  Session continuity cannot bypass MCP metadata/schema checks or future tool
  governance policy.
- Tool schema count, token budget, result reservation, and memory retrieval
  floor remain enforceable. A required set that cannot fit must fail visibly or
  follow a specifically approved degradation rule; silent eviction is not a
  continuity guarantee.
- `/inject-tools` manual selection remains exact until `/clear-tools`, as
  existing tests require. Registry replacement, MCP availability changes, and
  a new session need explicit invalidation behavior.
- The textual list, the selected API schemas, and tool-budget diagnostics must
  agree for each model request. No raw schema or sensitive prompt logging is
  required to prove this; names, hashes, counts, and rejection reasons suffice.

Pinning all current tools changes context cost but fits the measured local
budget. The review should measure live prompt cost and availability before
deciding whether any adaptive selection or new pinning logic remains useful.

## Bounded work to authorize later

1. Repeat the 14-to-1-to-14 conversation shape with the configured required
   set, capturing selected names, API schema identity, textual manifest
   identity, and budget/rejection reasons at each turn.
2. Measure prompt-token cost and tool availability in a provider-backed
   conversation; do not infer model-quality improvement merely from stable
   manifests.
3. If a gap remains, approve explicit invalidation and budget rules for manual
   selection, MCP peers, registry changes, and new sessions before any product
   code changes.
4. Add multi-turn regression coverage for the approved behavior, comparing
   prompt-visible names with schemas actually sent to the provider.

## Open decisions

- Should future registry additions join the required set automatically, or
  only through an explicit YAML edit?
- Is explicit configured pinning sufficient after provider-backed validation?
- When a core set exceeds budget, should Friday reject the turn, ask for an
  explicit selection, or apply a documented priority rule?
- Should `include_in_context` continue duplicating selected tool names when
  provider-native `tools` schemas are present?

## Related authority and source

- [Development task lifecycle](../../../reference/policies/development-task-lifecycle.md)
- [Accepted MCP context-budget directive](../../../archive/completed/2026/friday-mcp/directives/ws-04-friday-chat-context-budget.md)
- [Tool governance draft](../tool-governance/README.md)
- [Tool-selection implementation](../../../../packages/friday-chat/src/friday_chat/tools/selection.py)
- [Turn assembly](../../../../packages/friday-chat/src/friday_chat/turns/processor.py)
- [Current multi-turn selection tests](../../../../packages/friday-chat/tests_chat/test_tool_selection_budget.py)

This packet is a reviewable proposal. The board keeps implementation authority
at `not_granted` until the maintainer approves a bounded construction directive.

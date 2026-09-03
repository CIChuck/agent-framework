# Documentation Classification And Path Migration Ledger

---
title: Documentation Classification And Path Migration Ledger
initiative: documentation-governance
document_type: migration-ledger
status: active
created: 2026-09-03
updated: 2026-09-03
baseline_commit: 482b857507409fb73556e273f96acdce1c398480
---

## Rules

- This ledger records proposed destinations before files move.
- A path move does not change approval or implementation authority.
- `hold` means the destination or authority is ambiguous and the file must not
  move until the ambiguity is resolved.
- Existing document bodies are preserved. Packet indexes may explain stale
  embedded status language without silently rewriting historical evidence.
- All `docs/guides/` paths are excluded and must remain unchanged.
- Untracked user documents and backups are not part of this ledger.

## Planning Index And Governance

| Existing path | Classification | Proposed destination | Reason |
| --- | --- | --- | --- |
| `docs/planning/README.md` | replace as stale navigation | same path | Become the current-work dashboard; existing links and release state are obsolete |
| `docs/planning/active/documentation-governance/README.md` | active authority | unchanged | Controls this remediation |
| `docs/planning/active/documentation-governance/current-state-authority-manifest.md` | active authority | unchanged | Preserves the pre-migration development stop point |
| `docs/planning/active/documentation-governance/classification-ledger.md` | active execution record | unchanged | Records every proposed planning move |

## Completed Friday Chat V2 Packet

The maintainer's spelling correction is accepted. These files first resolve from
the tracked `friday-chat-v2-aechive` path to the working-tree
`friday-chat-v2-archive` path, then move as one packet.

Final packet: `docs/archive/completed/2026/friday-chat-v2/`

| Existing file | Final file |
| --- | --- |
| `friday-chat-v2-behavioral-contracts.md` | `friday-chat-v2-behavioral-contracts.md` |
| `friday-chat-v2-build-plan.md` | `friday-chat-v2-build-plan.md` |
| `friday-chat-v2-code-generation-task-list.md` | `friday-chat-v2-code-generation-task-list.md` |
| `friday-chat-v2-compatibility-testing-protocol.md` | `friday-chat-v2-compatibility-testing-protocol.md` |
| `friday-chat-v2-parity-matrix.md` | `friday-chat-v2-parity-matrix.md` |
| `friday-chat-v2-startup-config-remediation-plan.md` | `friday-chat-v2-startup-config-remediation-plan.md` |
| `friday-chat-v2-turn-integration-remediation-plan.md` | `friday-chat-v2-turn-integration-remediation-plan.md` |
| `docs/planning/build-plans/deprecated/friday-v2-feature-inventory.md` | `friday-v2-feature-inventory.md` |

The packet needs an archive `README.md` identifying it as historical contract
and closeout evidence. The behavioral contract remains evidence of required
Friday Chat behavior unless a current contract explicitly supersedes it.

## Completed Remediation Packets

| Existing path | Classification | Proposed destination |
| --- | --- | --- |
| `docs/planning/build-plans/chat-command-remediation` | completed plan | `docs/archive/completed/2026/friday-chat-command-remediation/plan.md` |
| `docs/planning/build-plans/construction-directives/friday-chat-command-remediation-1-construction-directive.md` | executed directive | `docs/archive/completed/2026/friday-chat-command-remediation/construction-directive.md` |
| `docs/planning/build-plans/reorg-remediation-plan-1.md` | completed plan with stale pre-execution status | `docs/archive/completed/2026/reorganization-remediation-1/plan.md` |
| `docs/planning/build-plans/construction-directives/reorg-remediation-1-construction-directive.md` | executed directive | `docs/archive/completed/2026/reorganization-remediation-1/construction-directive.md` |

Each packet gets a `README.md` that names its implementation commit and explains
any stale status retained in the historical plan body.

## Typed LLM And Release Packets

### Completed `0.1.0a2` typed-LLM initiative

Final packet: `docs/archive/completed/2026/typed-llm-0.1.0a2/`

| Existing path | Proposed destination |
| --- | --- |
| `docs/planning/upgrades/friday-llm/friday-llm-reasoning-and-sampling-controls-requirement.md` | `friday-llm/reasoning-and-sampling-controls-requirement.md` |
| `docs/planning/upgrades/friday-llm/friday-llm-reasoning-controls-tactical-implementation-plan.md` | `friday-llm/tactical-implementation-plan.md` |
| `docs/planning/upgrades/friday-chat/friday-chat-typed-llm-config-migration-tactical-plan.md` | `friday-chat/config-migration-tactical-plan.md` |
| `docs/planning/upgrades/friday-chat/friday-chat-typed-llm-deferred-consumer-handoff.md` | `friday-chat/deferred-consumer-handoff.md` |
| `docs/planning/upgrades/friday-packages/friday-framework-typed-llm-adoption-plan.md` | `framework/adoption-plan.md` |
| `docs/planning/upgrades/friday-packages/friday-framework-typed-llm-execution-log.md` | `framework/execution-log.md` |

The deferred-consumer handoff is historical: its listed consumers were completed
by the succeeding framework-wide adoption plan. The packet index must state this
without changing the original handoff record.

### Durable current model-library contract

| Existing path | Classification | Proposed destination |
| --- | --- | --- |
| `docs/planning/upgrades/friday-packages/friday-model-library-technical-spec.md` | implemented technical reference | `docs/reference/llm/model-library-technical-spec.md` |

### Release records

| Existing path | Classification | Proposed destination |
| --- | --- | --- |
| `docs/planning/upgrades/friday-packages/friday-package-cohort-0.1.0a1-plan.md` | completed release plan | `docs/archive/completed/2026/friday-package-cohort-0.1.0a1/plan.md` |
| `docs/planning/upgrades/friday-packages/friday-package-cohort-0.1.0a2-artifact-sha256.txt` | durable release evidence | `docs/reference/releases/friday-package-cohort-0.1.0a2-artifact-sha256.txt` |

Existing release evidence under `docs/reference/releases/` remains in place.

### Deferred reasoning work

| Existing path | Classification | Proposed destination |
| --- | --- | --- |
| `docs/planning/upgrades/friday-llm/friday-llm-model-aware-reasoning-control-deferred-feature.md` | deferred, not authorized | `docs/planning/deferred/model-aware-reasoning-control/README.md` |

## Friday MCP Packet

The complete MCP packet remains Draft and moves without gaining implementation
authority.

Final packet: `docs/planning/queued/friday-mcp/`

| Existing path | Proposed destination |
| --- | --- |
| `docs/planning/build-plans/friday-framework-mcp-enhancements.md` | `build-plan.md` |
| `docs/planning/build-plans/friday-mcp-thoughts.md` | `design-notes.md` |
| `docs/planning/build-plans/tactical-implementation/friday-framework-mcp-tactical-implementation-plan.md` | `tactical-plan.md` |
| `docs/planning/build-plans/construction-directives/friday-framework-mcp-ws-00-contract-policy-foundation.md` | `directives/ws-00-contract-policy-foundation.md` |
| `docs/planning/build-plans/construction-directives/friday-framework-mcp-ws-01-configuration-model-validation.md` | `directives/ws-01-configuration-model-validation.md` |
| `docs/planning/build-plans/construction-directives/friday-framework-mcp-ws-02-runtime-lifecycle-provider-loading.md` | `directives/ws-02-runtime-lifecycle-provider-loading.md` |
| `docs/planning/build-plans/construction-directives/friday-framework-mcp-ws-03-tool-naming-metadata-registry.md` | `directives/ws-03-tool-naming-metadata-registry.md` |
| `docs/planning/build-plans/construction-directives/friday-framework-mcp-ws-04-friday-chat-context-budget.md` | `directives/ws-04-friday-chat-context-budget.md` |
| `docs/planning/build-plans/construction-directives/friday-framework-mcp-ws-05-execution-provenance-transcript.md` | `directives/ws-05-execution-provenance-transcript.md` |
| `docs/planning/build-plans/construction-directives/friday-framework-mcp-ws-06-memory-compatibility-ingestion.md` | `directives/ws-06-memory-compatibility-ingestion.md` |
| `docs/planning/build-plans/construction-directives/friday-framework-mcp-ws-07-telemetry-diagnostics-health.md` | `directives/ws-07-telemetry-diagnostics-health.md` |
| `docs/planning/build-plans/construction-directives/friday-framework-mcp-ws-08-documentation-guide-closeout.md` | `directives/ws-08-documentation-guide-closeout.md` |
| `docs/planning/build-plans/construction-directives/friday-framework-mcp-ws-09-optional-external-config-include.md` | `directives/ws-09-optional-external-config-include.md` |

A new packet `README.md` will state that review and approval are the next gate;
`MCP-WS-00` is first only after that approval.

## Current And Proposed Work

| Existing path | Classification | Proposed destination |
| --- | --- | --- |
| `docs/planning/build-plans/mitigation-plan-1.md` | implemented, blocked on one live acceptance criterion | `docs/planning/blocked/nonblocking-chat-input/plan.md` |
| `docs/planning/build-plans/friday-chat-v2-framework-upgrade-log.md` | mixed follow-up inventory with unresolved proposed items | `docs/planning/backlog/friday-chat-framework-followups/upgrade-log.md` |
| `docs/planning/build-plans/friday-framework-enhancements.md` | planned; implementation authority not evidenced | `docs/planning/queued/framework-validation-and-contracts/README.md` |
| `docs/planning/build-plans/friday-framework-friday-md-file.md` | draft | `docs/planning/queued/friday-startup-context/README.md` |
| `docs/planning/build-plans/friday-framework-web-chat.md` | draft | `docs/planning/queued/friday-web-chat/README.md` |
| `docs/planning/build-plans/tool-governance.md` | draft | `docs/planning/queued/tool-governance/README.md` |
| `docs/planning/security/prompt-injection-mitigation-build-plan.md` | ready for implementation; no execution record found | `docs/planning/queued/prompt-injection-mitigation/README.md` |
| `docs/planning/backlog/agent-scoped-memory-context.md` | backlog | `docs/planning/backlog/agent-scoped-memory-context/README.md` |

The Friday Chat unclosed-client-session defect receives a small active packet
index that links to the existing behavioral contract. It does not receive
implementation authority from this documentation-only branch.

## Tooling And Product Backlog

| Existing path | Classification | Proposed destination |
| --- | --- | --- |
| `docs/planning/build-plans/to-do/claude-agent-sdk-tool-build-plan.md` | approved plan, not executed | `docs/planning/queued/claude-agent-sdk-tools/build-plan.md` |
| `docs/planning/build-plans/to-do/friday-evaluates-deeply.md` | review input for Claude plan | `docs/planning/queued/claude-agent-sdk-tools/analysis.md` |
| `docs/planning/build-plans/to-do/friday-thoughts.md` | review input for Claude plan | `docs/planning/queued/claude-agent-sdk-tools/friday-review.md` |
| `docs/planning/build-plans/to-do/friday-needs-tools.md` | backlog requirements note | `docs/planning/backlog/tool-capabilities/directory-listing.md` |
| `docs/planning/build-plans/to-do/friday-speech-build-plan.md` | unapproved draft | `docs/planning/queued/friday-speech/README.md` |
| `docs/planning/build-plans/to-do/roadmap.md` | informal backlog | `docs/planning/backlog/strategic-roadmap/README.md` |

## Superseded Planning Material

| Existing path | Classification | Proposed destination |
| --- | --- | --- |
| `docs/planning/build-plans/deprecated/context-pipeline-key-facts-build-plan.md` | explicitly deprecated | `docs/archive/superseded/context-pipeline-key-facts/build-plan.md` |
| `docs/planning/build-plans/deprecated/copilot-promotion-build-plan.md` | superseded by Friday Chat V2 | `docs/archive/superseded/copilot-promotion/build-plan.md` |
| `docs/planning/build-plans/deprecated/friday-performance-optimization-build-plan.md` | explicitly deprecated | `docs/archive/superseded/friday-performance-optimization/build-plan.md` |
| `docs/planning/build-plans/deprecated/new-memory-features.md` | historical idea notes | `docs/archive/superseded/new-memory-features/notes.md` |
| `docs/planning/build-plans/friday-framework-pypi-preparation.md` | draft overtaken by released package cohorts | `docs/archive/superseded/friday-framework-pypi-preparation/build-plan.md` |
| `docs/planning/build-plans/friday-framework-uvx-distro.md` | draft partly overtaken by current Friday Chat distribution; remaining web work has its own plan | `docs/archive/superseded/friday-framework-uvx-distribution/build-plan.md` |

Archive packet indexes will name the known successor or state that no current
successor has been identified.

## Architecture And Reference Classification

As-built source and current package layout resolved the following classifications:

| Existing path or group | Classification | Destination |
| --- | --- | --- |
| `docs/planning/prds/friday-os-prd-v1.md`, `friday-os-prd-v2.md`, and `friday-engine-prd-v4.md` | earlier product concepts using a package model that does not match the published workspace | `docs/archive/superseded/friday-os-product-concepts/` |
| `docs/architecture/SEKG/` | approved for design, not implementation | `docs/planning/queued/self-evolving-knowledge-graph/` |
| `docs/architecture/agents/HIL/` | design packet with open critical blockers | `docs/planning/blocked/human-in-the-loop/` |
| `docs/architecture/agents/phase-5-*.md` | implemented historical phase designs; corresponding runtime and experiment surfaces exist | `docs/archive/completed/2026/runtime-phase-5/` |
| `docs/reference/providers/massive/` | raw provider and design source inputs, including empty placeholders | `docs/archive/source-materials/providers/massive/` |
| `docs/reference/specs/friday-api-prd.md` | unimplemented product proposal | `docs/planning/queued/friday-api/README.md` |
| `docs/reference/specs/friday-tui-prd.md` | unimplemented product proposal | `docs/planning/queued/friday-tui/README.md` |
| `docs/reference/specs/Friday Lab Environment.md` | testing and evaluation reference | `docs/reference/testing/friday-lab-environment.md` |

## Authority Hold

The following collection will not move until each remaining document's current
role is confirmed:

| Existing path or group | Reason for hold |
| --- | --- |
| `docs/reference/specs/` | Mixes potentially durable specifications with old batches, draft images, and presentations |

## Existing Archive

The existing archive remains in place during planning migration. DG-06 will add
an index and classify its top-level collections. Large historical collections
will not be flattened merely for cosmetic uniformity because their directory
structure carries provenance.

## Maintainer-Approved Review Documents

The maintainer authorized both previously untracked reviews for inclusion and
classification on 2026-09-03.

| Existing path | Classification | Proposed destination |
| --- | --- | --- |
| `docs/reference/memory/review-pass-1.md` | completed as-built review and normative input to a future Memory V2 plan; implementation not authorized | `docs/planning/queued/memory-v2/package-review-pass-1.md` |
| `docs/reference/security/review-8-10.md` | completed as-built security review and remediation input to tool governance | `docs/planning/queued/tool-governance/as-built-security-review.md` |

The ignored recovery-code export was removed without being opened after the
maintainer confirmed that removal was authorized. It was never tracked and has
no migration destination.

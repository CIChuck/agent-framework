# HIL — Human-in-the-Loop Design

**Lifecycle:** Blocked pending resolution of `patch-list-2.md`
**Implementation authority:** Not granted

**Status:** Design
**Author:** Chuck Russell
**Date:** 2026-03-29

---

## Overview

HIL (Human-in-the-Loop) provides configurable human approval gates that intercept tool calls before they execute in the Friday Framework's ReAct loop. It is designed as a **standalone package** (`friday-hil`) that evolves independently toward Beads (task queue) and Dolt (version-controlled audit database) integration.

## Documents

| Document | Description |
|----------|-------------|
| [design.md](./design.md) | Full architecture, component specs, integration points |
| [config-reference.md](./config-reference.md) | Complete `hil:` config schema with all options |
| [build-plan.md](./build-plan.md) | Phased implementation plan — 22 phases with scope guards and verification steps |
| [test-plan.md](./test-plan.md) | 4-level test plan — unit, agent integration, friday.py session, end-to-end experiment |
| [patch-list-2.md](./patch-list-2.md) | Remaining high-priority blockers after the first doc revision pass |


## Quick Summary

- **Package:** `packages/friday-hil/`
- **Protocol:** `HILInterface` defined in `friday-core/interfaces/hil.py`
- **Scope:** Intercepts tool calls in both `MemoryChatSession._process_with_tools()` and `AgentBase._execute_tool_call()`
- **Modes:** `yolo` (no prompts), `strict` (always prompt), `ask_once` (prompt once per unique call; coarse-grained first-word trust for configured `ask_once_commands`)
- **Evolution:** SQLite audit log → Dolt (connection-string swap); direct execution → Beads task dispatch

## Related

- PRD: `tests/integration/memory/scratchpad/PRD_HIL_Beads_Dolt_Integration.md`
- Workflow HITL: `friday_agent.workflows.models` (`HITLPolicy`, `HITLRequest`, `HITLDecision`, `HITLAuthorityPolicy`) — governs task/state transitions. Tool-call HIL operates on a separate control plane. See [design.md § Relationship to Workflow HITL](./design.md#relationship-to-workflow-hitl) for the scope boundary.

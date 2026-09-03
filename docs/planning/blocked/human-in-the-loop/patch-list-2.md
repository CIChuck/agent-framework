# HIL Doc Patch List 2

**Status:** Open
**Date:** 2026-04-01
**Scope:** Remaining high-priority blockers after the first HIL doc revision pass

---

## Purpose

This document captures the remaining high-priority issues in the HIL design set that still block or materially mislead implementation. These are narrower than the first patch list and focus on unresolved architectural and contract inconsistencies.

---

## Patch 1 — Resolve the Runtime Boot / Session-ID Contradiction

**Priority:** Critical

### Problem

The docs currently specify:

- `HILController.__init__(config, session_id)`
- `DIContainer.boot()` creates the HIL controller
- `RuntimeKernel.create_session()` is what creates session IDs

That means the runtime-managed path tries to construct a session-bound controller before any session exists.

### Required doc change

Choose one runtime model and apply it consistently:

1. **Session-scoped controller**
   - HIL controller is created only after a runtime session exists
   - runtime agent creation must depend on a bound session
   - docs must state where the controller is recreated or rebound per session

2. **Process-scoped controller**
   - `HILController` no longer requires `session_id` at construction
   - session ID is passed into `check_approval()` / audit writes
   - docs must update the interface, controller, audit writer, and all integration points

### Files to patch

- `design.md`
- `build-plan.md`
- `test-plan.md`

### Acceptance criteria

- The runtime-managed path can be implemented in the order the docs describe
- No step requires a session ID before one exists
- Session ownership of trust state and audit rows is explicit

---

## Patch 2 — Add an Explicit Runtime Config Contract for HIL

**Priority:** Critical

### Problem

The revised docs say `DIContainer` creates HIL from runtime config, but `RuntimeConfig` currently has no `hil` section and rejects unknown top-level keys. The design set therefore depends on a config surface that is not specified.

### Required doc change

- Add a runtime config contract for HIL, or explicitly defer runtime-managed HIL until that config surface exists.
- If added now, define:
  - top-level section name
  - allowed keys
  - mapping into `RuntimeConfig`
  - validation behavior for unknown keys
  - default disabled behavior
- Update runtime build phases to include:
  - `RuntimeConfig` changes
  - config validation updates
  - tests for parsing and unknown-key behavior

### Files to patch

- `design.md`
- `build-plan.md`
- `config-reference.md` if it is intended to apply to runtime YAML too

### Acceptance criteria

- The runtime-managed HIL path has a documented config source
- The config model and parser are part of the implementation plan
- Unknown-key policy remains coherent with repository policy

---

## Patch 3 — Remove Remaining Architectural Contradictions From `build-plan.md`

**Priority:** Critical

### Problem

The build plan still contains mutually inconsistent statements about:

- ABCs vs Protocols
- app-layer-only wiring vs runtime factory wiring
- a single shared controller across direct chat and orchestrated agents

Later sections are more accurate, but the earlier contradictory sections still make the document unsafe to follow linearly.

### Required doc change

- Rewrite the top-level dependency architecture section so it matches the current intended implementation model.
- Remove or update stale language such as:
  - `HILDecision ABCs`
  - `wired together in friday.py / app layer`
  - `Single HILController instance shared across MemoryChatSession and AgentOrchestrator`
- Ensure the build plan has exactly one authoritative wiring story.

### Files to patch

- `build-plan.md`
- `README.md` if its summary still overstates shared-controller behavior

### Acceptance criteria

- A reader can follow the plan from top to bottom without changing mental models midstream
- The top-level architecture summary matches the detailed implementation phases

---

## Patch 4 — Reconcile the “Shared Trust Store” Claim With the Revised Wiring Model

**Priority:** High

### Problem

The docs still promise one shared session trust store across direct chat and orchestrated execution, but the revised architecture now separates:

- manual direct-chat HIL in `friday.py`
- runtime-managed HIL for orchestrated agents

The docs no longer explain how those two paths share state, or whether they still do.

### Required doc change

Choose one explicit statement:

1. **Shared trust remains a requirement**
   - document the shared owner of session trust state
   - show how both direct chat and runtime-managed agents bind to the same controller/session store

2. **Shared trust is deferred**
   - narrow v0.1 scope so direct-chat and runtime-managed HIL maintain separate trust state
   - remove the shared-trust claim from goals and summaries

### Files to patch

- `README.md`
- `design.md`
- `build-plan.md`
- `test-plan.md`

### Acceptance criteria

- The docs make one unambiguous claim about trust-store sharing
- The test plan matches that claim

---

## Patch 5 — Fix the Level 3 `MemoryChatSession` Fixture Example

**Priority:** High

### Problem

The Level 3 fixture sketch still does not match the real constructor surface for `MemoryChatSession`. In particular, the sample omits `llm`, which the real constructor requires.

### Required doc change

- Update the fixture example to include the actual required parameters:
  - `llm`
  - `controller`
  - `assembler`
  - `architect`
  - `system_prompt`
  - `session_id`
  - `user_id`
- Keep the fixture minimal, but syntactically plausible against the current constructor.

### Files to patch

- `test-plan.md`

### Acceptance criteria

- The sample fixture can be translated directly into a runnable test
- The test plan no longer requires reverse-engineering the constructor before implementation

---

## Patch 6 — Remove the Dead `autonomous_fallback` Example From the Main Rollout Path

**Priority:** High

### Problem

The config reference now correctly marks `autonomous_fallback` as reserved for v0.2 and not parsed in v0.1, but the build plan still instructs implementers to add it to the main sample `hil:` block in `tests/integration/memory/config.yaml`.

That leaves a dead key in the primary rollout path and reintroduces schema drift.

### Required doc change

- Remove `autonomous_fallback` from the v0.1 config patch step in the build plan.
- If the key should remain visible, move it into a commented “future v0.2 example” block only.

### Files to patch

- `build-plan.md`

### Acceptance criteria

- The main v0.1 sample config contains only parsed, documented keys
- There is no dead config in the primary implementation path

---

## Recommended Edit Order

1. Patch 1
2. Patch 2
3. Patch 3
4. Patch 4
5. Patch 5
6. Patch 6

---

## Definition of Done

The remaining blockers are resolved when:

- runtime-managed HIL has a coherent session model
- runtime config has an explicit HIL contract, or runtime-managed HIL is deferred
- the build plan contains one consistent architecture story
- trust-store sharing is either fully specified or explicitly removed from v0.1 scope
- Level 3 fixture examples are runnable against the current code
- the v0.1 sample config contains no reserved-only keys

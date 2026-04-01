# HIL Doc Patch List

**Status:** Open
**Date:** 2026-03-31
**Source:** Review of the HIL design set against current repository architecture and repository engineering policy

---

## Purpose

This document translates the current HIL doc review into a concrete patch list for the documents in this folder. It is focused on correcting implementation-contract drift, internal inconsistencies, and repository-shape mismatches before HIL implementation begins.

---

## Patch 1 — Re-anchor Agent Injection at the Real Factory Boundary

**Priority:** Critical

### Problem

The docs currently describe HIL propagation as if `AgentOrchestrator._ensure_agent()` directly constructs agent instances and can inject `hil_controller` there.

That is not how the current repository works:

- `AgentOrchestrator._ensure_agent()` calls `AgentRegistry.create_agent(name)`
- `AgentRegistry` uses a configured factory of type `Callable[[AgentProfile], AgentBase]`
- `RuntimeKernel` owns the default registry factory via `_create_agent()`

The current HIL docs therefore identify the wrong integration seam for orchestrated-agent wiring.

### Required doc changes

- In `design.md`, replace the current `AgentOrchestrator` injection narrative with the actual creation path:
  `RuntimeKernel` or app-layer registry factory owns HIL injection, and `AgentOrchestrator` simply consumes already-wired agents from `AgentRegistry`.
- In `build-plan.md`, replace Phase 10's current `_ensure_agent()` injection step with a plan that updates the real construction boundary.
- Explicitly document two valid wiring modes:
  - `RuntimeKernel`-managed agent creation for runtime/experiment flows
  - manual DI for `friday.py`
- Add migration notes for affected packages:
  - `friday-core`
  - `friday-agent`
  - `friday-runtime`
  - `tests/integration/memory/friday.py`

### Files to patch

- `design.md`
- `build-plan.md`
- `README.md` quick summary if it still says `AgentOrchestrator` passes HIL directly to agents

### Acceptance criteria

- No HIL doc claims that `_ensure_agent()` directly instantiates agents
- The build plan can be executed against the repo without discovering a missing constructor seam mid-implementation
- Runtime-managed and manual-DI paths are both named explicitly

---

## Patch 2 — Rewrite `friday.py` Integration Steps Against the File as It Exists

**Priority:** Critical

### Problem

The `friday.py` integration steps assume:

- `session_id` exists near the initial config extraction block
- there is an `AgentOrchestrator(...)` construction site in `main()`

Neither assumption is currently true.

In the current file:

- `tools_config` is read long before `session_id` is created
- `session_id` is created close to transcript-session initialization
- `MemoryChatSession(...)` is constructed in `main()`
- an orchestrator is not constructed there today

### Required doc changes

- In `design.md`, rewrite Section 7.3 so HIL initialization is placed after `session_id` creation or is otherwise explicitly designed to avoid requiring it earlier.
- In `build-plan.md`, rewrite Phases 12–15 to match the current `friday.py` structure.
- Remove any instruction that tells the implementer to modify a nonexistent `AgentOrchestrator(...)` call in `main()`.
- If HIL needs orchestrator support in `friday.py`, add a preceding patch step that first introduces orchestrator construction, session binding, and ownership of that object.
- If HIL does not require orchestrator support in `friday.py` v0.1, say so explicitly and limit `friday.py` scope to direct-chat interception plus `/hil` commands.

### Files to patch

- `design.md`
- `build-plan.md`
- `test-plan.md` wherever Level 3 assumes a different `friday.py` wiring model

### Acceptance criteria

- Every `friday.py` step in the docs maps to code that actually exists today
- The order of steps is executable without inventing missing local state
- The doc clearly distinguishes direct-chat HIL from orchestrated-agent HIL

---

## Patch 3 — Choose One `ask_once` Semantic Model and Apply It Everywhere

**Priority:** Critical

### Problem

The docs currently describe contradictory `ask_once` behavior:

- one description says approval option `1` or `3` populates `ask_once` session trust
- another says only option `3` persists trust
- one description says `ask_once` mode prompts every tool once
- another decision chain only gives coarse-grained fast-path behavior to `ask_once_commands`

This is a user-visible behavioral contract and must not remain ambiguous.

### Required doc changes

- Pick one precise model for:
  - what option `1` does
  - what option `3` does
  - whether `ask_once` mode applies to all tools or only configured command classes
  - how exact-hash trust interacts with first-word trust
  - whether `strict` mode can still benefit from prior option `3` approvals
- Update:
  - decision chain
  - mode comparison table
  - config comments for `ask_once_commands`
  - controller pseudocode
  - tests covering `ask_once`
- Add at least two explicit examples:
  - same command, same args, second execution
  - same command first-word, different args, second execution

### Files to patch

- `design.md`
- `config-reference.md`
- `build-plan.md`
- `test-plan.md`

### Acceptance criteria

- All four docs describe identical `ask_once` behavior
- A reader can predict second-call behavior without inference
- The decision chain and test plan assert the same semantics

---

## Patch 4 — Align the Typed Config Contract With the Published YAML Schema

**Priority:** High

### Problem

The config reference publishes `autonomous_fallback`, but the authoritative `HILConfig` spec does not include or parse it.

That creates a contract split between:

- the YAML users are told they can write
- the typed config model implementers are told to build

### Required doc changes

- Decide whether `autonomous_fallback` belongs in v0.1.
- If yes:
  - add it to the typed `HILConfig` spec
  - define its model shape explicitly
  - define whether it is parsed-only or partially enforced in v0.1
- If no:
  - remove it from the v0.1 schema
  - move it into a “Reserved for v0.2” section that is explicitly non-contractual

### Files to patch

- `config-reference.md`
- `build-plan.md`
- `design.md` if it mentions the field as part of v0.1 contract

### Acceptance criteria

- Every YAML key in the published schema exists in the typed contract, or is clearly marked out of scope for the current version
- No v0.1 implementation step is forced to guess whether to parse the field

---

## Patch 5 — Repair the Level 3 Test Plan to Match the Real `MemoryChatSession` Signature

**Priority:** High

### Problem

The Level 3 fixture sketch uses constructor arguments that do not match the actual `MemoryChatSession` signature in `tests/integration/memory/friday.py`.

As written, the test plan is not executable and would mislead the implementer.

### Required doc changes

- Rewrite the Level 3 fixture section to match the current constructor:
  - `controller`
  - `assembler`
  - `architect`
  - `system_prompt`
  - `session_id`
  - `user_id`
  - any other required dependencies that cannot be omitted
- Remove stale names such as:
  - `memory_controller`
  - `context_assembler`
  - `tool_registry` as a direct constructor argument
- Add a note that Level 3 should use minimal mocks for the actual required constructor surface rather than a simplified pseudo-constructor.

### Files to patch

- `test-plan.md`

### Acceptance criteria

- The sample Level 3 fixture code is syntactically plausible against the current constructor
- A contributor can build the test module without first reverse-engineering the session signature

---

## Patch 6 — Strengthen the Cross-Package HIL Contract Style

**Priority:** High

### Problem

The docs currently mix ABC language with structural-typing language:

- `HILInterface` / `HILDecision` are specified as ABCs
- the build plan later says `MockHILController` should satisfy the interface “without subclassing it” via structural typing

That is a contract-style mismatch. It also undershoots repository policy, which prefers explicit typed contracts at boundaries and favors `Protocol` or typed models over ad hoc duck typing.

### Required doc changes

- Decide whether the HIL boundary uses:
  - ABCs
  - `Protocol`
  - Pydantic/dataclass request-response models plus a protocol/ABC service interface
- Apply that choice consistently across:
  - interface spec
  - concrete decision type
  - testing guidance
  - build plan language
- If retaining ABCs:
  - stop describing the test double as “structural typing”
  - either subclass the contract explicitly in examples or describe it as a compatible test double informally
- If moving to `Protocol`:
  - update the interface definition and justify the choice as the stable package boundary

### Files to patch

- `design.md`
- `build-plan.md`
- `test-plan.md`
- `README.md` quick summary if it names the protocol surface

### Acceptance criteria

- The HIL boundary contract style is consistent across all docs
- The contract clearly complies with repository policy for cross-package interfaces

---

## Patch 7 — Add Explicit Interaction With Existing Workflow HITL

**Priority:** Medium

### Problem

The repo already has workflow-level HITL and approval constructs in `friday-agent.workflows`. The HIL docs currently describe tool-call approval in isolation and do not explain how it coexists with task/workflow approval gates.

That omission risks two parallel approval systems with no documented precedence or operator model.

### Required doc changes

- Add a “Relationship to Existing Workflow HITL” section.
- State that tool-call HIL and workflow HITL are separate control planes unless intentionally unified later.
- Document precedence and scope:
  - workflow HITL governs task execution and task state transitions
  - HIL governs tool execution attempts inside direct chat and agent REPL loops
- Explicitly defer any unification work to a later phase unless it is in scope now.

### Files to patch

- `design.md`
- `README.md`

### Acceptance criteria

- A reader can tell whether HIL replaces, complements, or ignores workflow HITL
- There is no ambiguity about which mechanism is responsible for which approval decision

---

## Patch 8 — Normalize Validation and Migration Notes for Boundary Changes

**Priority:** Medium

### Problem

The repository policy treats design docs as implementation contracts and requires boundary changes to include affected packages, validation evidence, and migration notes. The HIL docs partly do this, but not consistently for all touched boundaries.

### Required doc changes

- For each boundary-changing phase, add:
  - contract change summary
  - affected packages
  - required validation commands
  - migration/backward-compatibility notes
- Ensure the plan names the boundary impact for:
  - `friday-core`
  - `friday-agent`
  - `friday-runtime`
  - `tests/integration/memory/friday.py`
  - experiments, where applicable

### Files to patch

- `build-plan.md`

### Acceptance criteria

- Boundary-affecting phases conform to repository policy expectations
- The plan tells implementers what to validate after each public-contract change

---

## Recommended Edit Order

1. Patch 1
2. Patch 2
3. Patch 3
4. Patch 4
5. Patch 6
6. Patch 5
7. Patch 7
8. Patch 8

This order fixes architecture and contract drift first, then repairs downstream plan and test details.

---

## Definition of Done

The HIL docs are ready for implementation when all of the following are true:

- the documented integration seams match the current repository
- direct-chat and orchestrated-agent wiring paths are both explicit
- `ask_once` behavior is described identically in every HIL doc
- the YAML schema and typed config contract agree
- Level 3 and Level 4 tests are runnable from the documented constructor/runtime surfaces
- the HIL docs state how this system relates to existing workflow HITL
- the build plan satisfies repository policy for boundary changes

---
title: Multi-agent orchestration
description: Route, delegate and share evidence with explicit session, factory and namespace boundaries.
framework_version: 0.1.0a3
last_reviewed: '2026-10-15'
status: current
audience: Technical end users and application integrators
doc_type: guide
---

# Multi-agent orchestration

Friday's framework orchestrator coordinates registered agents within a process.
It has one active agent at a time, caches created instances and supports explicit
mention routing and delegation. It is not a distributed scheduler or a pool of
independent autonomous workers.

## Framework and Chat surfaces

| Surface | Current behavior |
| --- | --- |
| `friday_agent.AgentOrchestrator` | Uses a real `AgentRegistry` and caller-configured factories; awaits each agent's `run()` |
| `RuntimeKernel` | Assembles configured services/profiles for headless use |
| Friday Chat orchestration | Uses `FakeOrchestrator` in both fake and real runtime assembly in alpha3 |
| Friday Chat workflow commands in real mode | Use the framework's flat workflow engine with that same deterministic orchestration adapter |

Consequently, Chat's `/agents`, `/switch`, `@mentions` and `/delegate` expose
deterministic routing behavior today. `--runtime real` makes Chat's selected
model/memory/tool integrations real; it does **not** turn delegated specialist
tasks into independent model-backed agents. Use the framework APIs in your
own composition when that is required.

## Profiles, factories and session identity

Define and validate each profile using [the agent guide](06-agents.md). Register
profiles, configure a factory and construct `AgentOrchestrator(registry,
default_agent=...)`. The constructor requires a configured global registry
factory. A profile/capability declaration alone is not an instantiated agent.

Bind the intended session using `await orchestrator.set_session(session_id,
user_id=...)`. Session identity controls conversation continuity; application
authentication and namespace policy are separate concerns. Share a memory
controller only when the agents are intended to operate over that data.

This **offline Python example** demonstrates route resolution only. Its factory
deliberately refuses execution; no models or stores are created:

```python
from friday_agent import AgentBase, AgentOrchestrator, AgentProfile, AgentRegistry

def no_execution(profile: AgentProfile) -> AgentBase:
    raise RuntimeError("This example resolves routes only.")

registry = AgentRegistry()
for name in ("assistant", "researcher"):
    registry.register(AgentProfile(
        name=name, role="Demo", goal="Inspect routing",
        system_prompt_template="You are {name}.",
    ))
registry.set_factory(no_execution)
orchestrator = AgentOrchestrator(registry, default_agent="assistant")
decision = orchestrator.route("@researcher Review the supplied source")
print(decision.target_agent, decision.source, decision.message)
```

Expected output: `researcher explicit Review the supplied source`.
`route()` does not mutate active-agent state. `process()` resolves the route,
creates/restores the target and awaits execution; it needs a functional factory.

## Routing and delegation

The framework's order is an explicit `@agent message`, then the active agent,
then the configured default when automatic initialization is enabled. Unknown
explicit targets fail with `OrchestratorError`. Mentions must match the routing
grammar; use simple alphanumeric/underscore profile names for mention routing.

| API | Effect |
| --- | --- |
| `route(user_input)` | Return a `RoutingDecision` without creating an agent |
| `await process(user_input)` | Resolve route and run the selected agent |
| `await switch_agent(name)` | Ensure/cache the named agent and make it active |
| `await delegate(name, task, return_to_current=True, ...)` | Run a target and normally return control after successful completion |
| `get_status()`, `get_agent_info(name)` | Inspect current routing/cache/profile state |
| `get_delegation_history()` | Inspect recorded delegation history; it may include task previews/handoff data |
| `await shutdown()` | Settle orchestrator-owned agents through its lifecycle |

Do not share a mutable single-active orchestrator across concurrent requests
without application-level coordination. The default implementation does not
provide isolated per-request active-agent state. If a delegated call raises,
inspect the active agent and owned work before assuming control was restored;
the successful return path is not an exception-safe rollback guarantee.

## Explicit handoffs

Give each delegated task a bounded objective, allowed inputs/tools, expected
output, evidence requirements and completion criteria. Pass exact artifacts or
structured handoff data when the next task needs them. Similarity retrieval
can supply background, but cannot guarantee recovery of an exact predecessor
result or every relevant source.

The framework accepts `handoff_payload` and optional `skill_ref`; workflows add
typed handoff/artifact contracts. Skill resolution chooses a declared matching
agent, preferring an eligible requested agent or a deterministic sorted match.
It does not install a skill, authorize a tool or validate the result's quality.

For a research/review sequence, give the reviewer the source bundle and draft
artifact rather than only the researcher's conclusion. A completed review call
is not human acceptance of its findings.

## Namespace-aware memory

`MultiAgentMemoryController` wraps an existing controller with `session_id`,
`agent_id`, `namespace`, optional `NamespacePolicyEngine` and optional
`PromotionCoordinator`. It supports private writes, filtered recall and explicit
shared promotion/write operations.

This **offline Python example** checks the default policy without opening stores:

```python
import asyncio
from friday_memory import NamespacePolicyEngine

async def main() -> None:
    policy = NamespacePolicyEngine("session-1", "researcher", "research")
    print(await policy.can_read("researcher", "research", "session-1"))
    print(await policy.can_read("reviewer", "research", "session-1"))
    print(await policy.can_write_shared("researcher", "session-1", None))

asyncio.run(main())
```

Expected output: `True`, `False`, `False`.

The default policy checks in-process identity/session/namespace and capability
time validity. It is not a complete security boundary: it does not authenticate
a network caller or cryptographically bind capabilities. Callers also supply
metadata to memory writes; do not let untrusted callers override authoritative
visibility/namespace fields. Enforce identity, metadata and tenant separation
at the application/store boundary.

`PromotionCoordinator` journals proposals and staged writes. If arbitration is
configured, it consults the decision; without one it must not be described as
an automatic human approval gate. A partial graph/vector commit is a recovery
state, not fully available shared memory. Inspect journal/forensics and use
the explicit recovery contract before retrying.

## Sequential, parallel and hierarchical designs

Use sequential delegation when each task depends on an earlier result. Use
[workflow dependencies](08-workflows.md) to express the sequence and required
artifacts. For parallel application work, isolate mutable agent/session state
and explicitly merge results; `asyncio.gather()` around one active orchestrator
does not create a safe worker pool.

Hierarchical workflow/pipeline/task models exist, but their execution and lease
contracts do not supply an external job queue or distributed exactly-once
execution. Design worker ownership, timeout, retry and idempotency at the host
boundary before deploying across processes.

## Operational checks

- Verify registered profiles, configured factories and model-role bindings.
- Record the active session and agent with each application-owned result.
- Distinguish no recall, filtered recall and a failed/pending memory write.
- Bound delegation depth, latency and permitted side effects in your host.
- Keep task previews, handoff content and generic logs out of public diagnostics.
- Validate a failing or timed-out external mutation before explicitly retrying it.

## Implementation references

- [Framework orchestrator](../../packages/friday-agent/src/friday_agent/orchestrator.py)
- [Registry and skill lookup](../../packages/friday-agent/src/friday_agent/registry.py)
- [Namespace controller/policy/coordinator](../../packages/friday-memory/src/friday_memory/multi_agent)
- [Chat assembly and deterministic adapter](../../packages/friday-chat/src/friday_chat/runtime.py)
- [Chat workflow adapter](../../packages/friday-chat/src/friday_chat/adapters.py)

[Guide index](README.md) · [Capability status](FRIDAY-FEATURES.md)

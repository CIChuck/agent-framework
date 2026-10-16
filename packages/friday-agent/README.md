# Friday Agent

Agent profiles, registries, interactive agents, multi-agent routing, and workflow execution. Use this package to define agent behavior; use Friday Runtime to assemble its LLM, memory and tool dependencies.

**Distribution:** [friday-framework-agent](https://pypi.org/project/friday-framework-agent/) · **Import:** `friday_agent`
**Python:** 3.13.4+ · **Status:** alpha · **License:** MIT

## Installation

```bash
python -m pip install "friday-framework-agent==0.1.0a4"
```

Friday distributions use the same release version; keep internal Friday dependencies aligned.

## Quick start: register an agent profile

This example is local and makes no model requests. A profile describes an agent; registering it does not create a running agent.

```python
from friday_agent import AgentProfile, AgentRegistry

profile = AgentProfile(
    name="assistant",
    role="Project assistant",
    goal="Answer questions about the project",
    system_prompt_template="You are {name}, a {role}. Your goal: {goal}",
    tools=[],
)
registry = AgentRegistry()
registry.register(profile)
print(registry.list_agents())
```

## Using agents in an application

- `InteractiveAgent` runs the interactive reasoning/tool loop. `CopilotAgent` is a compatibility alias.
- `AgentLoader` loads profiles; `AgentRegistry` resolves names and creates agents through an application-supplied factory.
- `AgentOrchestrator` routes work; `WorkflowEngine` executes task graphs.
- Agent execution requires a configured LLM, memory/context services, and a tool registry. A profile alone supplies none of those services.

For full composition, configure `RuntimeConfig`, start `RuntimeKernel`, then spawn a **registered** agent name. Tool names in a profile must exist in the selected registry. Keep credentials in the owning application, outside profiles.

## Development

Work from the monorepo root after the [shared contributor setup](https://github.com/CIChuck/agent-framework/blob/master/README.md#development).
Run the focused suite:

```bash
uv run --no-sync pytest packages/friday-agent/tests_agent -q
```

## Documentation and support

[Runtime composition](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-runtime/README.md) · [Agent guide](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/06-agents.md) · [Workflows](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/08-workflows.md) · [Source](https://github.com/CIChuck/agent-framework/tree/master/packages/friday-agent/src/friday_agent) · [Issues](https://github.com/CIChuck/agent-framework/issues) · [Contributing](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/15-contributing.md)

## License

[MIT](https://github.com/CIChuck/agent-framework/blob/master/LICENSE).

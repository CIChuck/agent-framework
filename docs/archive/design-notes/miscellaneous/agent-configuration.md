# Design: Data-Driven Agent Configuration

**Status:** Exploratory
**Context:** Enabling agents to be defined purely via YAML configuration files, decoupling behavior from code.

## 1. Concept: The Agent Manifest

We move away from defining agents in Python code. Instead, an agent is defined by a **Manifest** (YAML) that specifies its Identity, Capabilities, and Constraints.

### 1.1 The Schema (`agent.schema.yaml`)

```yaml
# identity: Who am I?
name: "ResearchBot"
role: "Senior Research Analyst"
goal: "Find and synthesize information from the web."
backstory: |
  You are a meticulous researcher who verifies every fact.
  You prefer primary sources over summaries.

# capabilities: What can I do?
tools:
  - "web_search"
  - "read_page"
  - "scratchpad_write"

# workflow: How do I collaborate?
inputs:
  - name: "topic_string"
    type: "string"
    description: "The main topic to research."

outputs:
  - name: "research_summary"
    type: "file" # Options: file, memory, message
    path_template: "research/{topic}_summary.md"
    description: "A markdown summary of findings."

# architecture: How do I think?
model: "gpt-4-turbo"
temperature: 0.3
max_tokens: 4000

# memory: What do I remember?
memory:
  mode: "vector_only"  # Options: full, episodic_only, vector_only
  namespace: "research_team" # Shared namespace or private

# registry: How am I found?
tags:
  - "research"
  - "web"
  - "synthesis"
```

## 2. Component: `AgentLoader`

We introduce a loader component in `packages/friday-agent` responsible for hydration.

```python
class AgentLoader:
    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    def load_from_directory(self, path: Path) -> None:
        """Scan directory for .yaml files and register agents."""
        for file in path.glob("*.yaml"):
            config = self._parse_yaml(file)
            self._register_agent(config)

    def _register_agent(self, config: AgentConfig) -> None:
        # Convert Config -> Profile
        profile = AgentProfile(
            name=config.name,
            role=config.role,
            goal=config.goal,
            system_prompt_template=config.backstory,
            tools=config.tools,
            temperature=config.temperature
        )
        
        # Register with Metadata
        self.registry.register(
            profile=profile, 
            tags=config.tags, 
            memory_mode=config.memory.mode
        )
```

## 3. Integration with Ecosystem

### 3.1 Registry Population
At startup (e.g., in `FridayContainer.initialize`), the system points `AgentLoader` to a configuration directory (e.g., `agents/`). The Registry is automatically populated with all defined agents.

### 3.2 Orchestrator Usage
The Orchestrator doesn't care *how* the agent was defined. It just queries the Registry:
> "Find me an agent with tag 'research'."

The Registry returns the `AgentMetadata` (hydrated from YAML), and the Orchestrator passes it to the Container to instantiate the `TeamAgent`.

### 3.3 Memory Configuration
The `memory` section in the YAML directly controls the `memory_mode` argument passed to `FridayContainer.get_team_agent`, triggering the correct Null/Real adapter injection.

## 4. Benefits

1.  **Hot-Reloading:** We can tweak agent prompts or tools by editing a text file, potentially even reloading the registry at runtime without restarting the orchestrator.
2.  **Sharing:** Agent manifests can be shared, versioned, and downloaded (like prompts).
3.  **Safety:** Guardrails (e.g., allowed tools) are explicit in the config, not hidden in Python logic.

# Phase 5-B: Declarative Runtime Tool Loading and Provider-Aware Tool Registry

**Status:** Proposed  
**Date:** 2026-03-16  
**Audience:** Runtime architects, agent-framework maintainers, tool/runtime integrators

---

## 1. Problem Statement

The runtime can execute agents and workflows, but tool availability is still too implicit and too narrow.

Today, the runtime DI path in `friday-runtime` creates a `DefaultToolRegistry` and loads only decorated built-in tools. That is sufficient for memory helpers and simple internal tools, but it does not make externally defined tool surfaces such as `friday-tools` instances available by configuration.

This creates four practical problems:

1. Runtime tool availability is not declarative.
2. Experiments and workflows that need web, filesystem, or external tools require Python-side registry patching.
3. The framework has no first-class configuration contract for choosing which tool providers and categories are active in a given runtime.
4. The current runtime path does not provide a coherent extension model for future MCP-backed or externally hosted tool providers.

The result is that tool-enabled workflows are possible, but the framework contract is weaker than the rest of the runtime configuration model introduced in earlier phases.

---

## 2. Phase Objective

Phase 5-B establishes runtime-owned declarative tool loading in DI.

This phase introduces:

1. A runtime `tools` configuration section.
2. Provider-aware tool loading, not just built-in decorated tools.
3. Category-aware tool enablement and filtering.
4. A normalized runtime registry assembly path that can load built-ins, `friday-tools`, and future external providers through one contract.

This phase does not implement workflow experiments itself. It establishes the runtime tool-loading contract that those experiments and production workflows will consume.

---

## 3. Architecture Decisions

## 3.1 Tool Loading Belongs to Runtime DI

Tool loading should be a runtime concern, not an experiment-local bootstrap concern.

`RuntimeConfig` should declare which tool providers and categories are enabled. `DIContainer` should build the tool registry accordingly. Experiments and workflows should consume that runtime contract rather than patching registries in Python.

This keeps the runtime aligned with the broader configuration direction already used for prompting, transcript, LLM pools, embedding pools, and artifact policy.

## 3.2 The Registry Is a Unified Runtime Surface

The registry exposed to agents remains a single runtime tool registry.

The framework should not expose separate per-provider registries to agent execution. Instead, runtime should:

1. load tools from multiple sources,
2. normalize them into one registry,
3. enforce provider/category filters before agent execution.

This keeps agent prompting and tool resolution simple while allowing runtime to remain modular.

## 3.3 Providers and Categories Are Both First-Class

Tool loading needs two axes of control:

1. **Provider**: where the tool comes from
   - built-in decorated tools
   - `friday-tools` packaged tools
   - future MCP-backed tools
   - future external catalogs
2. **Category**: what kind of capability the tool exposes
   - memory
   - filesystem
   - web
   - code execution
   - finance
   - utility

Provider-only control is too coarse, and category-only control is too ambiguous. The runtime contract should support both.

## 3.4 Agent Config Still Selects From the Runtime Pool

Runtime config defines the available tool universe. Agent profiles still define which tools an agent can use.

This preserves the existing boundary:

1. runtime decides what is loadable and safe to expose,
2. agent config decides what is in-scope for that agent,
3. workflow execution decides which agent runs and when.

The runtime should not silently inject undeclared tool access into an agent profile.

---

## 4. Current-State Gap

The current DI path creates a registry like this:

1. instantiate `DefaultToolRegistry`
2. call `load_decorated_tools()`
3. bind dependencies for a small set of built-in tools

That leaves several gaps:

1. `friday-tools` instances such as `web_search`, `web_reader`, and `file_write` are not declaratively loaded.
2. Experiments that need those tools must register them manually.
3. There is no runtime schema for enabling or disabling tools by provider or category.
4. There is no normalized provider-loader abstraction in DI.

This phase closes that gap.

---

## 5. Target Model

## 5.1 Runtime Tool Configuration

Runtime gains a first-class `tools` section.

The intent is:

1. runtime config declares which providers are enabled,
2. runtime config declares which categories are allowed or denied,
3. runtime config may explicitly enable or disable named tools,
4. DI builds a final registry from that policy.

## 5.2 Provider-Aware Loading

Each provider contributes tool definitions through a dedicated loader path.

Examples:

1. `builtin`
   Loads decorated framework tools already defined in runtime packages.
2. `friday_tools`
   Loads named packaged tool instances such as `web_search`, `web_reader`, `file_write`, and other curated tool adapters.
3. `mcp`
   Future phase. Loads tools exposed by MCP integrations.
4. `external`
   Future phase. Placeholder for remote catalogs or plugin sources.

The first implementation slice should fully support `builtin` and `friday_tools`, while designing clean interfaces for later providers.

## 5.3 Final Registry Construction

The runtime registry assembly path should follow this order:

1. load providers declared in config,
2. gather candidate tools,
3. apply category filters,
4. apply explicit include/exclude rules,
5. register the resulting set,
6. bind runtime dependencies where needed.

The final registry is then handed to agents and workflows.

---

## 6. Configuration Direction

The runtime config should use a richer provider/category model rather than a flat list of tool names.

Illustrative direction:

```yaml
tools:
  default_policy: selected
  providers:
    builtin:
      enabled: true
      include_categories:
        - memory
        - utility
      exclude_tools: []
    friday_tools:
      enabled: true
      include_categories:
        - web
        - filesystem
      include_tools:
        - web_search
        - web_reader
        - file_write
      exclude_tools: []
    mcp:
      enabled: false
      servers: []
  global_include_tools: []
  global_exclude_tools: []
```

This shape is intentionally richer than:

```yaml
tools:
  enabled:
    - web_search
    - web_reader
    - file_write
```

because the framework needs provider and category controls, not just a single named-list.

## 6.1 Expected Semantics

The intended semantics are:

1. `default_policy`
   Controls whether a provider loads all available tools by default or only explicitly selected tools.
2. `providers.<provider>.enabled`
   Turns a provider on or off.
3. `include_categories`
   Restricts a provider to specific capability classes.
4. `include_tools`
   Explicitly whitelists named tools from that provider.
5. `exclude_tools`
   Explicitly removes named tools even if category/provider rules would otherwise include them.
6. `global_include_tools` / `global_exclude_tools`
   Runtime-wide final overrides after provider-local filtering.

## 6.2 Validation Direction

Runtime config validation should reject:

1. unknown provider names,
2. unknown categories when categories are validated against a known set,
3. contradictory include/exclude combinations where behavior would be ambiguous,
4. provider sections that declare provider-specific fields without enabling the provider.

---

## 7. Integration Boundaries

## 7.1 DI Responsibilities

`DIContainer` should:

1. parse the runtime `tools` section,
2. invoke provider-specific loaders,
3. assemble the registry,
4. bind runtime services and dependencies into tools that need them.

`DIContainer` should not embed large provider-specific registration logic inline. Provider loaders should be factored into dedicated helpers or modules.

## 7.2 Agent Responsibilities

Agents should continue to:

1. resolve tool schemas from the injected registry,
2. restrict use to tools declared in their profile,
3. execute tools through the existing tool execution path.

No new prompt contract is introduced here beyond making the tools available declaratively.

## 7.3 Workflow Responsibilities

Workflows should not know how tools are loaded. They should only depend on:

1. agent capabilities,
2. runtime-configured tool availability,
3. agent profiles naming tools that exist in the runtime registry.

This keeps workflow definitions portable and keeps tool bootstrap inside runtime.

---

## 8. Feature Set for Phase 5-B

In scope:

1. Runtime config schema for declarative tool loading.
2. DI-based provider-aware registry assembly.
3. Built-in decorated tool loading through the new config path.
4. `friday-tools` packaged tool loading through the new config path.
5. Category and named-tool filters.
6. Dependency binding for loaded tools where required.
7. Targeted runtime tests and config validation tests.

Out of scope:

1. Full MCP tool loading implementation.
2. External plugin marketplace or remote catalog support.
3. Tool permission policies beyond provider/category/name filtering.
4. Workflow experiment implementation itself.
5. Prompt-contract changes unrelated to tool availability.

---

## 9. Implementation Tasks

The following code-generation tasks are required to complete Phase 5-B.

## 9.1 Runtime Config Model

1. Add `tools` config models to `friday-runtime`.
2. Add nested-to-flat compatibility handling if the runtime config surface still requires flat compatibility fields.
3. Add YAML parsing and validation for provider/category/tool selection.
4. Add default values that preserve current behavior when no `tools` section is present.

## 9.2 Tool Provider Loader Abstractions

1. Introduce a provider loader interface or helper contract.
2. Add a loader for built-in decorated tools.
3. Add a loader for curated `friday-tools` packaged tools.
4. Design, but do not fully implement, the extension hook for future MCP/external providers.

## 9.3 DI Refactor

1. Refactor `_create_tool_registry()` in `DIContainer` to use provider loaders.
2. Apply provider/category/tool filters before final registration.
3. Preserve existing dependency binding for memory-related built-ins.
4. Add dependency binding support for packaged tools that need runtime services or sandbox context.

## 9.4 Tool Catalog Mapping

1. Define a normalized mapping from runtime config names to concrete tool implementations.
2. Ensure curated `friday-tools` instances are addressable by stable names.
3. Ensure duplicate names across providers are handled deterministically.
4. Define error behavior for requested tools that cannot be resolved.

## 9.5 Tests

1. Runtime config parsing tests for `tools`.
2. DI tests for provider-aware registry assembly.
3. Regression tests confirming current built-in tools still load under the default policy.
4. Tests confirming `friday-tools` instances such as `web_search`, `web_reader`, and `file_write` can be enabled declaratively.
5. Tests confirming category filtering and explicit include/exclude behavior.
6. Tests confirming invalid provider/category/tool config is rejected.

## 9.6 Follow-On Consumer Work

These are not part of Phase 5-B implementation itself, but they are the immediate consumers:

1. non-deterministic workflow artifact smoke experiment,
2. richer workflow experiments using web and filesystem tools,
3. future MCP-backed tool integration experiments.

---

## 10. Open Design Questions

These questions should be resolved during implementation review, but they do not block the design document itself.

1. Should categories be validated against a fixed enum or treated as provider-owned free-form strings?
2. Should provider-local `include_tools` imply category bypass, or still require the tool to belong to an included category?
3. How should name collisions be resolved if multiple providers export the same tool name?
4. Should runtime support per-agent overrides later, or remain runtime-global only in this phase?
5. How should MCP server configuration be represented when that provider is implemented in a later phase?

---

## 11. Expected Outcome

Phase 5-B makes tool loading a first-class runtime contract.

After this phase:

1. experiments and workflows no longer need Python-side registry patching to use common packaged tools,
2. runtime configuration will declare the active tool universe explicitly,
3. the tool registry will be provider-aware and category-aware,
4. future workflow and artifact experiments can rely on the same runtime tool-loading contract as production execution.

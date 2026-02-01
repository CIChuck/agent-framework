# Friday Agent Framework - Comprehensive User Guide
## Outline & Section Descriptions

**Document Version:** 1.0
**Framework Version:** v0.1.0
**Target Audience:** Technical executives, developers, AI practitioners
**Last Updated:** 2026-01-24

---

## 1. EXECUTIVE SUMMARY: Why Friday Exists

**Purpose:** Introduce Friday's core value proposition and establish the context for why it was built.

This section opens with the fundamental problem facing AI development today: most chatbots and AI assistants are stateless, session-bound entities that cannot truly learn or remember. They lack the ability to build understanding over time, access relevant historical context, or maintain coherent multi-session relationships with users. Every conversation starts from zero, requiring users to repeatedly explain context, preferences, and background information.

Friday Framework was built to solve this exact problem by providing a production-ready, modular Python framework that gives AI agents genuine memory, learning capabilities, and the ability to work collaboratively in multi-agent teams. Unlike wrapper libraries that simply add persistence to existing APIs, Friday implements a sophisticated three-tier memory architecture (episodic, semantic, associative) with intelligent lifecycle management, Hebbian learning, and context engineering principles drawn from cognitive science research. This section will establish Friday as an enterprise-grade solution for building AI agents that genuinely improve over time, remember what matters, and collaborate effectively across complex workflows.

---

## 2. GETTING STARTED

**Purpose:** Provide a fast-path for users to get Friday running and experience its core capabilities.

### 2.1 Prerequisites & Installation
This subsection covers the technical requirements for running Friday: Python 3.10+, system dependencies (SQLite, optional Docker), and the installation process using `uv` (the modern Python package manager). We'll explain the monorepo structure and how the packages work together, including the optional installation of specific components (e.g., installing only `friday-memory` if you just need the memory system). The installation guide will include both development setups (from source) and future production installation via PyPI.

### 2.2 Quick Start: Your First Friday Agent
This provides a minimal working example that creates a basic Friday agent, runs a conversation, and demonstrates memory persistence across sessions. The code example will be under 50 lines and show the "hello world" experience: create an agent, have a conversation, exit, restart, and see that Friday remembers the prior conversation. This section establishes the fundamental developer experience and shows how Friday's memory "just works" without complex configuration.

### 2.3 Configuration Basics
A gentle introduction to Friday's YAML-based configuration system, covering the essential settings needed to get started: LLM provider (OpenAI, Anthropic, or local Ollama), API keys via environment variables, and basic memory settings. This section introduces the `config.yaml` structure without overwhelming readers with the full configuration reference (which comes later). We'll show how to switch between cloud and local models with a single configuration change, demonstrating Friday's provider-agnostic architecture.

---

## 3. CORE CONCEPTS & ARCHITECTURE

**Purpose:** Build a mental model of how Friday works at a high level before diving into specific features.

### 3.1 The Intelligence Plane & Control Plane Architecture
This section introduces Friday's conceptual architecture: the Intelligence Plane (intelligence layer with memory and reasoning) and the Control Plane (execution layer with tools and actions). We'll explain how Friday differs from typical LLM wrappers by separating concerns: memory management lives in `friday-memory`, LLM interaction in `friday-llm`, tool execution in `friday-tools`, and agent coordination in `friday-agent`. This modular separation enables independent scaling, testing, and deployment of each component. The section includes a clear architectural diagram showing how data flows from user input → context assembly → LLM inference → tool execution → memory storage → response.

### 3.2 Protocol-First Design Philosophy
An explanation of Friday's abstract protocol layer (`friday-core`) and why it matters. Every major component (LLM client, memory stores, tools, telemetry) is defined as an abstract protocol/interface, enabling complete implementation swappability without code changes. This section explains the benefits: zero vendor lock-in, easy testing with mocks, ability to bring your own implementations, and future-proof architecture. We'll show concrete examples like swapping ChromaDB for Pinecone or replacing LiteLLM with a custom LLM client by implementing the `LLMClient` protocol.

### 3.3 Monorepo Package Structure
A tour of the eight core packages (`friday-core`, `friday-memory`, `friday-llm`, `friday-agent`, `friday-tools`, `friday-sandbox`, `friday-transcript`, `friday-mcp`) with dependency flow visualization. This section clarifies which packages depend on which, why the dependency graph flows in one direction, and how this enables independent package evolution. We'll explain when you'd use specific packages in isolation (e.g., using only `friday-memory` for a custom agent, or `friday-tools` in a non-Friday system) versus using the full stack for comprehensive agent capabilities.

### 3.4 The Memory Loop: Context → Action → Learning
The conceptual flow of a Friday agent's operation cycle: (1) Context Assembly - gathering relevant memories and history, (2) Prompt Architecture - structuring the LLM prompt with optimized token budgeting, (3) LLM Inference - generating responses with optional tool calls, (4) Tool Execution - performing actions in the real world, (5) Memory Extraction - identifying entities, relationships, and insights from the interaction, (6) Memory Storage - persisting learnings to the three-tier memory system. This section establishes the "cognitive loop" that makes Friday agents genuinely adaptive rather than reactive.

---

## 4. ADAPTIVE MEMORY: The Heart of Friday

**Purpose:** Deep dive into Friday's memory architecture, the most distinctive technical capability.

### 4.1 Three-Tier Memory Architecture

#### 4.1.1 Episodic Memory (Conversation History)
Episodic memory represents the raw, chronological record of conversations stored in SQLite via the Transcript system. This subsection explains how turns are captured with full metadata (timestamps, token usage, tool calls, latency), how conversation history is retrieved for recent turns, and how episodic memory feeds into the Context Assembler for maintaining conversation coherence. We'll cover the `InteractionTurn` data model and how it preserves the complete interaction trace including tool execution results and provenance metadata.

#### 4.1.2 Semantic Memory (Vector Store)
Semantic memory uses ChromaDB for embedding-based similarity search of insights, facts, and summaries extracted from conversations. This section explains the multi-collection architecture: `memories_short_term` for recent but unproven memories, `memories_long_term` for verified and frequently-accessed information, and `memories_decayed` for low-value memories that have faded but remain recoverable. We'll explain how embedding models transform text into vector representations, how similarity search works, and why semantic search complements graph relationships for comprehensive memory retrieval.

#### 4.1.3 Associative Memory (Knowledge Graph)
Associative memory uses NetworkX (with JSON persistence) to model entities (people, projects, technologies, concepts) and their relationships as a directed graph with semantic edges (USES, AUTHORED, DISLIKES, COLLABORATES_WITH). This section explains Hebbian learning via `hit_count` tracking (frequently-accessed entities become more important), how relationship paths enable multi-hop reasoning ("What projects has Alice worked on with Python?"), and how the graph complements vector search by providing structure to unstructured conversations. We'll show example graph queries and explain the `GraphPathScorer` for intelligent path filtering.

### 4.2 Memory Lifecycle Management

#### 4.2.1 The Four Stages: Episodic → Short-Term → Long-Term → Decayed
A detailed explanation of memory staging and how memories progress (or regress) through lifecycle stages based on usage and importance. This section introduces the state machine: newly extracted memories start in short-term, get promoted to long-term based on access patterns and age, decay to the decayed stage when unused, and can be reactivated when accessed again. We'll explain the decay formula (exponential decay with configurable lambda), promotion scoring (multi-factor: age, access, confidence, connections), and the philosophy behind soft-deletion (memories are never permanently lost unless explicitly confirmed by maintenance operations).

#### 4.2.2 Promotion: Short-Term → Long-Term
Deep dive into the promotion scoring algorithm: how age factor (time in short-term), access factor (retrieval frequency), confidence factor (extraction quality), and connection factor (graph relationships) combine to produce a promotion score between 0-1. We'll explain the default threshold (0.7) and 24-hour minimum age requirement, showing examples of memories that would/wouldn't be promoted. This section demonstrates how Friday learns what's important rather than treating all memories equally.

#### 4.2.3 Decay: Long-Term → Decayed
Explanation of the decay algorithm using exponential decay based on time since last access. We'll show the mathematical formula, default decay constants (λ=0.01 means ~79% score after 24 hours, ~19% after 1 week), and why decay mimics human memory forgetting curves. This section explains how unused memories naturally fade, preventing context pollution while remaining recoverable if they become relevant again. We'll cover configurable decay rates for different memory types and use cases (e.g., faster decay for temporary task information, slower decay for learned preferences).

#### 4.2.4 Reactivation: Decayed → Long-Term
The unique "soft-delete" pattern where accessing a decayed memory automatically reactivates it back to long-term status. This section explains why this matters: Friday can "remember" things it had forgotten when they become contextually relevant again, mimicking human memory reconsolidation. We'll show examples of reactivation in practice (user references an old project they haven't mentioned in months, Friday retrieves it from decayed state and restores it to active memory).

### 4.3 Context Engineering & Token Budgeting

#### 4.3.1 The Knapsack Problem: Optimal Memory Packing
Detailed explanation of Friday's context assembly algorithm using the knapsack optimization approach. Given a fixed context window (e.g., 8K tokens for GPT-4), how does Friday select the optimal subset of memories to include? This section explains the multi-factor scoring (relevance × importance × recency), token cost estimation, and the knapsack solver that maximizes information density within budget constraints. We'll show how this beats naive approaches (most recent N memories, top N by similarity) with concrete token count examples.

#### 4.3.2 Lost-in-the-Middle Mitigation
Explanation of the research-backed "lost in the middle" problem where LLMs pay less attention to content in the middle of long contexts, and how Friday solves it with tail injection. The PromptArchitect places supporting context (retrieved memories, primed knowledge) immediately before the user's query rather than at the document start, leveraging the recency effect for maximum attention. This section includes citation to the original research and shows before/after examples of prompt structure with measured performance improvements.

#### 4.3.3 Context Payload Structure
Technical breakdown of the `ContextPayload` data structure returned by the ContextAssembler: system prompt, conversation history (episodic), retrieved insights (semantic), loaded entities (associative), injected tools, and scoped variables. We'll explain how each component fits the token budget, why order matters (system → history → context → query), and how the PromptArchitect formats this payload into actual LLM message structures. This section bridges the conceptual memory system with the practical prompt engineering.

### 4.4 Memory Extraction Pipeline

#### 4.4.1 Entity & Relationship Extraction
Detailed look at the extraction pipeline that converts raw conversation into structured memories. After each turn, Friday's `MemoryExtractor` sends the conversation to a dedicated extraction LLM (often a cheaper model like GPT-4o-mini or Claude Haiku) to identify entities (with types and descriptions) and relationships (with semantic verbs and context). This section explains the extraction prompt structure, output format (structured JSON), and how extraction failures are handled gracefully without blocking conversation flow.

#### 4.4.2 Insight Generation
Beyond entities and relationships, Friday generates "insights" - semantic summaries of important information, user preferences, decisions made, and lessons learned. This subsection explains how insights differ from raw summaries (insights are actionable, preference-revealing, decision-capturing), the insight scoring system for filtering noise, and how insights populate the vector store for semantic retrieval. We'll show examples of high-quality insights ("User prefers TypeScript over JavaScript for production code") versus low-value ones ("User said hello").

#### 4.4.3 Configurable Extraction Models
Friday supports separate extraction models from the main LLM, enabling cost optimization (use GPT-4o for reasoning, GPT-4o-mini for extraction) or capability matching (use Claude for conversation, Gemini for entity extraction). This section explains the `extraction_llm` configuration, when to use the same vs. different models, and the tradeoffs (cost vs. quality vs. consistency). We'll include recommended configurations for different budget levels and use cases.

### 4.5 Session Priming & Cross-Session Continuity

#### 4.5.1 Automatic Context Priming
When starting a new session, Friday automatically "primes" context by loading the most important entities (by Hebbian hit_count), recent insights, and conversation summaries from prior sessions. This section explains the priming algorithm, configurable priming depth (how many entities/insights to load), and recency filtering (optionally limit to last N days). We'll demonstrate how priming enables seamless continuation across days, weeks, or months without explicit "remember when..." prompts from users.

#### 4.5.2 Memory Namespaces (Multi-User/Multi-Project)
Friday supports memory namespaces to isolate memories per user, per project, or per agent team. This subsection explains how namespaces work (via metadata filtering in stores), when to use them (shared Friday instance with multiple users, or single user with multiple project contexts), and how to configure namespace isolation. We'll show examples of namespace-based queries and explain the shared vs. isolated memory tradeoffs.

---

## 5. TOOLS: Friday's Connection to the World

**Purpose:** Comprehensive guide to Friday's tool system and how agents interact with external systems.

### 5.1 Tool Architecture & Design

#### 5.1.1 The BaseTool Protocol
Technical explanation of the `BaseTool` abstract class that all tools inherit from. This section covers the required attributes (name, description, category, tags), the `parameters_schema` property (auto-generated from Pydantic models), and the async `execute()` method signature. We'll explain the tool lifecycle: registration → schema generation → LLM selection → parameter validation → execution → result formatting → memory logging. The standardized `ToolResult` structure ensures consistent handling across all tools.

#### 5.1.2 Tool Schemas for LLMs
Friday generates tool schemas in both OpenAI function-calling format and Anthropic tool-use format automatically from Pydantic parameter models. This section explains how the schema generation works, why Pydantic ensures type safety and validation, and how Friday handles schema differences between LLM providers transparently. We'll show side-by-side examples of the same tool represented in different schema formats and how the `ToolManifest` class manages cross-provider compatibility.

#### 5.1.3 Tool Result Standardization
Deep dive into the `ToolResult` data structure: `content` (human-readable string), `data` (structured response for programmatic access), `metadata` (execution details like latency and status), and optional `error` field. This section explains why standardization matters (consistent LLM parsing, logging, debugging), how tools should format results for best LLM comprehension, and best practices for error handling in tools (fail gracefully, return actionable error messages, preserve partial results when possible).

### 5.2 Built-in Tool Catalog (50+ Tools)

#### 5.2.1 Filesystem Tools
Reference documentation for the 8+ filesystem tools: `read_file` (with smart encoding detection and line limiting), `write_file`, `append_file`, `list_directory` (recursive with glob patterns), `search_files` (content search with regex), `get_file_info` (metadata like size and timestamps), `delete_file`, and `move_file`. Each tool entry includes: purpose, parameters with types, example usage, return format, and common error cases. We'll explain the smart file readers for PDF, DOCX, Excel, and CSV files.

#### 5.2.2 Shell & System Tools
Documentation for command execution tools: `execute_command` (run arbitrary shell commands with timeout and working directory), `run_script` (execute scripts with interpreter detection), and system health tools (`check_health`, `get_system_info`). This section emphasizes security considerations (command injection risks, working directory isolation, timeout enforcement) and when to use shell tools vs. specialized tools (prefer `git_status` over `execute_command("git status")`).

#### 5.2.3 Web & Network Tools
Coverage of HTTP and web interaction tools: `http_request` (flexible HTTP client with headers, auth, and timeout), `web_search` (search engine integration), `scrape_page` (HTML parsing and content extraction), and `download_file` (streaming downloads with progress). We'll explain rate limiting, user-agent configuration, authentication patterns (API keys, OAuth), and best practices for web scraping (respect robots.txt, implement backoff).

#### 5.2.4 Git Tools
Comprehensive guide to the 6+ Git tools for version control operations: `git_status`, `git_commit` (with message formatting), `git_push`/`git_pull`, `git_diff` (with file filtering and unified diff format), `git_log` (with customizable format and depth), `git_branches`, and `git_checkout`. This section emphasizes Git workflow integration: how Friday can autonomously manage commits during code generation, how to review diffs before committing, and safety guardrails (never force-push to protected branches).

#### 5.2.5 Data Manipulation Tools
Documentation for data parsing and transformation tools: `parse_json`, `parse_yaml`, `parse_xml`, `csv_operations` (read/write/query CSV data), `jq_query` (JSONPath/jq-style queries), `xml_query` (XPath support), and `format_data` (pretty-printing with syntax highlighting). These tools enable Friday to work with structured data from APIs, configuration files, and databases without relying solely on LLM reasoning about raw text.

#### 5.2.6 Text Processing Tools
Reference for text manipulation tools: `regex_search`, `regex_replace`, `text_transform` (case conversion, trimming, line operations), and `format_text` (markdown, code, and template rendering). We'll explain when to use text tools vs. relying on LLM text generation (tools are faster, cheaper, and more reliable for deterministic operations like extracting all email addresses from a document).

#### 5.2.7 Code Execution Tools
Deep dive into the sandboxed code execution tools: `run_python` (execute Python code in isolated subprocess), `analyze_code` (static analysis with linting), `format_code` (auto-formatting with Black/Prettier), and `lint_code` (run linters like Ruff/ESLint). This section covers the safety model (subprocess isolation, resource limits, timeout enforcement) and future Docker-based sandboxing for untrusted code. We'll explain when code execution is appropriate vs. risky (user explicitly requests computation vs. autonomous execution).

### 5.3 Creating Custom Tools

#### 5.3.1 Function-Based Tools (@tool Decorator)
The fastest way to create tools: decorate a Python function with `@tool` and Friday auto-generates schemas from type hints and docstrings. This section provides a step-by-step guide with examples: simple tool (single parameter, string return), tool with multiple parameters (Pydantic model), tool with complex return type (ToolResult with metadata), and async tool (for I/O operations). We'll explain docstring formatting for good LLM descriptions and parameter documentation.

#### 5.3.2 Class-Based Tools (BaseTool Subclass)
For more control, implement the `BaseTool` protocol directly. This section shows how to create a class-based tool with custom parameter validation, initialization logic (API clients, configuration loading), streaming results, and stateful operations (maintaining connections across multiple calls). We'll include a complete example: a database query tool that manages connection pooling and result pagination.

#### 5.3.3 Tool Categories & Discovery
Explanation of Friday's tool categorization system (filesystem, shell, web, git, data, text, code, math, integrations) and how categories enable focused tool selection. We'll show how to assign categories and tags to custom tools, how the tool registry uses categories for filtering, and how LLM prompts can be optimized with category-specific tool subsets ("only offer web tools for this research task").

#### 5.3.4 Tool Registration & Lifecycle
Technical details on tool registration with the `DefaultToolRegistry`: singleton pattern, lazy loading, hot-reloading for development, and tool versioning. This section explains how agents discover tools at runtime, how the orchestrator manages tool permissions per agent, and how to debug tool execution failures using the transcript system's detailed tool call logs.

### 5.4 Dynamic Tool Selection & Context Injection

#### 5.4.1 Context-Aware Tool Recommendations
Friday can dynamically recommend relevant tools based on user query analysis. This section explains the recommendation algorithm: semantic similarity between query and tool descriptions, category matching (web tools for URLs, git tools for repository mentions), and historical usage patterns (if user often runs tests, suggest testing tools). We'll show how the `/recommend-tools` CLI command enables testing the recommendation system.

#### 5.4.2 Tool Token Budget Management
When including tool schemas in the LLM prompt, they consume valuable tokens. This subsection explains Friday's token budget management for tools: how the PromptArchitect estimates schema sizes, selects the most relevant tools within budget, and falls back to tool categories when individual schemas exceed budget. We'll show examples of token-optimized tool injection (include 5 specific tools vs. listing all 50).

#### 5.4.3 Per-Task Tool Injection
For specific workflows or agents, tools can be explicitly injected into context. This section shows how to use the `/inject-tools` CLI command for testing, how to configure per-agent tool allowlists in agent YAML definitions, and how workflow tasks can specify required tools. We'll explain the security implications of tool access control (don't give web scraping tools to untrusted agents).

---

## 6. AGENTS: Configuration & Capabilities

**Purpose:** Complete guide to creating, configuring, and deploying Friday agents.

### 6.1 Agent Types & Patterns

#### 6.1.1 CopilotAgent: Interactive Re-Act Pattern
Deep dive into Friday's flagship agent implementation. CopilotAgent uses the Reasoning and Acting (Re-Act) pattern: (1) Observe - review context and user query, (2) Think - reason about next action, (3) Act - call tools if needed, (4) Observe results - integrate tool outputs, (5) Repeat until task complete (max 10 iterations). This section explains the Re-Act loop implementation, how tool calls are managed, streaming support for real-time updates, and circuit breakers for preventing infinite loops or excessive API costs.

#### 6.1.2 AutonomousAgent: Event-Driven Execution (Planned)
Preview of the planned AutonomousAgent for background task execution. Unlike CopilotAgent which requires human-in-the-loop for each step, AutonomousAgent operates independently based on goals, schedules, or event triggers. This section explains the design concepts: goal-oriented planning, task decomposition, autonomous tool execution with confidence thresholds, checkpoint/rollback for error recovery, and notification patterns for human oversight. We'll clarify the current status (planned) and implementation timeline.

### 6.2 Agent Configuration with YAML

#### 6.2.1 Agent Profile Schema
Complete reference for the agent YAML schema used by `AgentLoader`. This section documents all available fields: identity (`name`, `role`, `goal`), capabilities (`tools`, `skills`, `constraints`), model configuration (`model`, `temperature`, `max_tokens`), memory settings (`mode`, `namespace`, `priming`), and metadata (`version`, `author`, `tags`). We'll provide annotated examples showing common configuration patterns and explain validation rules (required fields, type constraints, valid enums).

#### 6.2.2 Tool Permission Management
How to control which tools an agent can access via the `tools` configuration field. This section explains allowlist patterns (explicit tool names), category-based selection (`tools: ["filesystem.*"]` for all filesystem tools), wildcard usage, and the security model (deny-by-default, explicit grant). We'll show examples of specialized agents (read-only filesystem agent, git-only agent, unrestricted admin agent) and explain when to restrict tools (untrusted user input, cost control, safety boundaries).

#### 6.2.3 Model Selection Per Agent
Friday supports different LLM models per agent, enabling cost and capability optimization. This section explains when to use premium models (GPT-4, Claude 3.5 Sonnet) vs. budget models (GPT-4o-mini, Claude Haiku) vs. local models (Llama 3, Mistral). We'll provide decision frameworks: use premium for complex reasoning, budget for simple classification/extraction, local for privacy-sensitive data. Examples include a research agent (GPT-4 for analysis) delegating to a summarization agent (Haiku for cost efficiency).

#### 6.2.4 Memory Mode Configuration
Agents can be configured with different memory access patterns via the `mode` field: `full` (episodic + semantic + associative), `vector_only` (semantic search only), `graph_only` (entity/relationship access), `episodic_only` (conversation history), or `none` (stateless). This section explains when to use each mode (stateless for short-lived tasks, vector_only for research agents, full for personal assistants), the performance implications, and how namespace isolation works with modes.

### 6.3 Agent Lifecycle & State Management

#### 6.3.1 Agent Initialization & Loading
Technical explanation of agent instantiation: how `AgentLoader` reads YAML definitions, validates configurations, resolves dependencies (tools, models, memory), and constructs agent instances. This section covers lazy loading (agents only instantiated when needed), caching (reuse loaded agents), hot-reloading for development (watch YAML changes), and error handling (graceful degradation for missing tools or invalid configs).

#### 6.3.2 Session Management & Checkpointing
How agents maintain state across conversations: session ID tracking, conversation history management, checkpoint creation (snapshot agent state for rollback), and cleanup (releasing resources on session end). This section explains the session lifecycle: initialization → active turns → maintenance (optional) → shutdown, and how sessions persist across application restarts (load from transcript store).

#### 6.3.3 Agent Registry & Discovery
Friday's `AgentRegistry` enables dynamic agent discovery and instantiation. This section explains the registry pattern: agents register themselves with metadata (name, capabilities, tags), queries filter by criteria (find all agents with 'research' capability), and the orchestrator selects agents based on task requirements. We'll show examples of registry queries and explain the tag system for capability advertising.

---

## 7. MULTI-AGENT ORCHESTRATION: Team Collaboration

**Purpose:** Guide to building multi-agent systems with Friday's orchestration layer.

### 7.1 The "Shared Intelligence Plane, Multiple Control Planes" Architecture

#### 7.1.1 Shared Memory Model
Friday's multi-agent architecture uses a shared memory model: all agents in an orchestrated system access the same memory controller, enabling seamless context sharing. This section explains why shared memory matters (no context handoff overhead, agents build on each other's work, collective learning), how provenance tracking prevents attribution confusion (who learned what), and the tradeoffs vs. isolated-memory architectures (shared = collaboration, isolated = specialization).

#### 7.1.2 Provenance Tracking
Every memory entry includes `ProvenanceMetadata`: author (which agent created it), source (conversation, tool, inference), and timestamp. This section explains how provenance enables debugging (trace back why Friday believes something), quality filtering (trust high-confidence extractions more), and agent-specific learning (agent A's insights might be more valuable than agent B's for certain topics). We'll show examples of provenance queries and explain multi-agent attribution in collaborative tasks.

### 7.2 Agent Orchestrator

#### 7.2.1 Explicit Routing with @mentions
Friday supports explicit agent routing via `@agent_name` prefix in user messages. This section explains the routing mechanism: message parsing, agent lookup, context switching, and response attribution. We'll show examples of direct routing ("@researcher find papers on transformers", "@coder implement the algorithm", "@reviewer check the code") and explain when explicit routing is better than automatic selection (user knows exactly which agent they need).

#### 7.2.2 Task Delegation & Return
The `delegate()` API enables one agent to hand off a subtask to another agent and receive the result back. This section explains delegation patterns: synchronous (wait for result), asynchronous (continue work while delegate executes), and streaming (receive partial results). We'll show code examples of delegation in agent workflows and explain how the orchestrator manages context switching, maintains conversation coherence, and attributes contributions properly.

#### 7.2.3 Agent State Aggregation
When multiple agents collaborate, the orchestrator aggregates their outputs into coherent responses. This section explains the aggregation strategies: sequential (chain agents in order), parallel (multiple agents work simultaneously, merge results), and hierarchical (supervisor agent coordinates worker agents). We'll show examples of each pattern and explain when to use them (sequential for dependent tasks, parallel for independent subtasks, hierarchical for complex projects).

### 7.3 Multi-Agent Workflows & Patterns

#### 7.3.1 Research → Analysis → Reporting Pipeline
Example pattern: researcher agent gathers information, analyst agent processes it, reporter agent generates final document. This section walks through a complete implementation including agent definitions, handoff points, and quality gates. We'll explain how shared memory enables the pipeline (analyst automatically accesses researcher's findings), how provenance tracks contributions (final report cites sources from research phase), and how to add human-in-the-loop approval between stages.

#### 7.3.2 Peer Review & Validation Patterns
Example pattern: coder agent writes code, reviewer agent checks for bugs/style, tester agent runs test suite. This section shows how Friday agents can validate each other's work, improving output quality through automated peer review. We'll explain the validation protocol (clear acceptance criteria, structured feedback), how to prevent infinite revision loops (max 3 iterations), and how to escalate to human reviewers when agents can't reach consensus.

#### 7.3.3 Specialist vs. Generalist Agent Strategies
Guidance on agent team composition: when to use specialist agents (narrow tool access, domain-specific prompts, expert-level models) vs. generalist agents (broad tool access, general-purpose prompts, balanced models). This section provides decision frameworks based on task complexity, cost constraints, and quality requirements. We'll show example teams: "small generalist team" (2-3 capable agents) vs. "large specialist team" (10+ focused agents) and explain scaling considerations.

---

## 8. WORKFLOWS: Task Graphs & Automation

**Purpose:** Complete guide to Friday's dynamic workflow engine for complex multi-step automation.

### 8.1 Workflow Engine Architecture

#### 8.1.1 Task Graphs & Dependencies
Friday workflows are directed acyclic graphs (DAGs) of tasks with explicit dependencies. This section explains the task graph model: nodes are tasks (with agent assignment, inputs, outputs), edges are dependencies (task B requires task A's output), and the engine ensures topological execution order. We'll cover cycle detection (prevent circular dependencies), parallel execution (run independent tasks concurrently), and failure handling (stop on error vs. continue with remaining tasks).

#### 8.1.2 Variable Passing with $var Syntax
Tasks communicate via variables using the `$var` syntax in workflow YAML. This section explains variable scoping (workflow-level, task-level), input binding (`inputs: {topic: "$user_topic"}`), output publishing (`outputs: ["research_summary"]`), and variable validation (ensure required inputs exist before task execution). We'll show complex examples: chained variables (task C uses outputs from both task A and task B), optional variables, and default values.

#### 8.1.3 Workflow Status Tracking
The `WorkflowExecution` model tracks workflow state: which tasks completed, failed, or are waiting for approval; current task in progress; execution duration; and final outputs. This section explains status types (PENDING, RUNNING, WAITING_APPROVAL, COMPLETED, FAILED, SKIPPED), how to query execution state via CLI (`/workflow status`), and how workflows resume after approval or failure. We'll show example status outputs and explain the state machine.

### 8.2 YAML Workflow Definitions

#### 8.2.1 Workflow Schema Reference
Complete documentation of the workflow YAML schema: metadata (`id`, `name`, `description`, `version`, `author`, `tags`), global settings (`timeout_seconds`, `max_retries`), and task definitions. Each task includes: `id`, `name`, `description`, `agent` (which agent executes it), `inputs` (variable bindings), `outputs` (variable names to publish), `depends_on` (prerequisite tasks), and `requires_approval` (human gate). We'll provide annotated examples showing all fields in use.

#### 8.2.2 Task Configuration Options
Deep dive into task-level configuration: retry strategies (`max_retries`, exponential backoff), timeout enforcement (`timeout_seconds` per task), conditional execution (skip task if condition false), and error handling (fail-fast vs. graceful degradation). This section includes examples of robust task configuration for production workflows (handle network failures, timeout long-running operations, skip optional enhancement tasks on failure).

#### 8.2.3 Human-in-the-Loop Approval Gates
Friday supports blocking approval gates where workflows pause for human review. This section explains the approval mechanism: set `requires_approval: true` on a task, workflow pauses before executing it, user reviews task context via `/workflow status`, and approves (`/workflow approve`) or skips (`/workflow skip`) the task. We'll show use cases: code deployment reviews, sensitive data access, expensive API calls, and explain best practices (clear approval criteria, timeout for approval wait).

### 8.3 Workflow Loader & Execution

#### 8.3.1 Loading Workflows from YAML
How the `WorkflowLoader` discovers and loads workflow definitions from the `workflows/` directory. This section explains the loading process: directory scanning, YAML parsing, validation (schema compliance, cycle detection, agent resolution), caching (reuse parsed workflows), and error reporting (helpful messages for YAML syntax errors or missing agent references). We'll show how to organize workflows in subdirectories and use naming conventions.

#### 8.3.2 Executing Workflows via CLI
Practical guide to running workflows from the memory-chat-v2.py CLI: list available workflows (`/workflow list`), start execution with inputs (`/workflow run newsletter user_topic="AI trends"`), monitor progress (`/workflow status`), and handle approval gates (`/workflow approve`). This section includes complete interaction examples showing the full workflow lifecycle from user perspective.

#### 8.3.3 Workflow Engine Internals
Technical deep dive into the `WorkflowEngine` implementation: task scheduling algorithm (topological sort), agent delegation (how tasks execute via orchestrator), variable resolution (`$var` lookup and substitution), error propagation (failed task handling), and execution resumption (continue after approval or failure recovery). This section is for developers wanting to extend the workflow engine or debug complex workflow issues.

### 8.4 Example Workflows & Templates

#### 8.4.1 Newsletter Generation Workflow
Walkthrough of the included `newsletter.yaml` example: research task (gather information), review gate (human approval), writing task (draft newsletter), and final review gate (publish approval). This section shows the complete workflow definition with explanations for each task configuration and demonstrates end-to-end execution with sample inputs/outputs.

#### 8.4.2 Code Review Workflow
Example workflow for automated code review: analyze task (static analysis), test task (run test suite), security scan task (vulnerability check), and review gate (human accepts/rejects). We'll explain how tasks pass results to each other (test results inform review decision), how to handle partial failures (security scan fails but tests pass), and how to customize for different repositories.

#### 8.4.3 Research & Report Workflow
Example workflow for research automation: web search task (gather sources), summarization task (extract key points), synthesis task (generate report), and fact-check gate (human verification). This section demonstrates variable passing (search results → summarizer → synthesizer), parallel execution (multiple search tasks), and output formatting (generate markdown report).

---

## 9. CLI REFERENCE: memory-chat-v2.py

**Purpose:** Comprehensive command reference for Friday's interactive CLI.

### 9.1 Session Management Commands

#### /exit, /quit
Exits the chat session. Optionally triggers maintenance operations (lifecycle promotion/decay, memory reorganization) if configured with `on_exit: true` in `session` settings. This command saves the session state and releases resources.

#### /clear
Clears conversation history for the current session. This removes episodic memory (turn history) but preserves long-term memories (entities, insights) from prior sessions. Useful for starting a fresh conversation topic without losing learned context.

#### /reset
Complete memory wipe: clears all memory stores (vector, graph, episodic) AND archives all transcripts to CSV backup files. This is the "factory reset" command for starting completely fresh or troubleshooting memory corruption. Requires confirmation to prevent accidental data loss.

### 9.2 Memory Inspection Commands

#### /memory
Displays comprehensive memory statistics: number of entities in graph, relationship count, insights in vector store (by collection: short-term, long-term, decayed), conversation turns in current session, and total token count. Includes breakdown by memory type and health indicators (memory fragmentation, promotion backlog).

#### /context [--debug]
Shows the assembled context payload that would be sent to the LLM for the current turn: system prompt, conversation history, retrieved insights, loaded entities, and injected tools. The `--debug` flag adds detailed token counts per component, helping diagnose context window exhaustion. This is the primary debugging tool for understanding what Friday "sees" when responding.

#### /prompt
Shows the exact formatted messages sent to the LLM, including full tool schemas and variable substitutions. Unlike `/context` which shows the logical payload, `/prompt` shows the final LLM API request structure. This command is essential for troubleshooting tool calling issues or unexpected responses.

#### /prime
Manually triggers session priming (normally automatic on first turn). Loads the priming payload (top entities by hit_count, recent insights, conversation summaries) and displays what was retrieved. Useful for verifying priming configuration or debugging cold-start behavior.

#### /debug
Displays detailed debug information from the last context assembly: retrieval latency per store, token counts by component, knapsack packing efficiency, and any warnings (e.g., context window near limit). This command helps diagnose performance issues or memory retrieval problems.

### 9.3 Memory Store Queries

#### /entities [--limit N]
Lists graph entities with metadata: entity type (Person, Project, Technology, etc.), description, hit count (Hebbian importance), relationships (with edge counts), and last accessed timestamp. The optional `--limit` parameter controls how many entities to display (default 20).

#### /facts [--type TYPE]
Lists all documents from vector store: insights, summaries, and metadata. The `--type` filter limits to specific document types: `insight`, `summary`, or `meta_insight` (from memory synthesis). Shows content preview, confidence score, collection (short-term/long-term/decayed), and provenance.

#### /insights
Filtered view of `/facts` showing only insights (not summaries) with structured metadata: insight type (preference, decision, observation), confidence score, extraction source, and current lifecycle stage. This is the primary way to inspect what Friday has learned about user preferences and patterns.

#### /summaries
Shows conversation turn summaries stored in vector memory: turn IDs, summary text, timestamp, and token count. Turn summaries enable efficient retrieval of past conversations without loading full transcripts.

#### /meta
Displays meta-insights generated by memory synthesis operations: high-level patterns detected across multiple insights (e.g., "User prefers functional programming patterns across Python and JavaScript"), synthesis timestamp, and supporting evidence (which insights contributed to the meta-insight).

### 9.4 Transcript Management

#### /sessions
Lists all stored transcript sessions: session ID, start timestamp, turn count, user ID, and session duration. Useful for finding past conversation sessions for review or export.

#### /transcript [id]
Shows transcript for the current session (if no ID provided) or a specific session ID. Displays full turn-by-turn record: user messages, assistant responses, tool calls with parameters and results, token usage, latency, and timestamps. This is the complete conversation log.

#### /transcript export
Exports the entire transcript database to CSV files: sessions table (session metadata), turns table (turn details), tool calls table (tool execution log), and relationships table (turn linkages). Creates timestamped export in configured directory.

#### /export [format]
Exports current session in specified format: `jsonl` (JSONL for programmatic processing), `markdown` (human-readable formatted transcript), or `training` (JSONL format for fine-tuning). Default is markdown. Files saved to configured export directory.

### 9.5 Advanced Memory Operations

#### /reorganize [options]
Runs memory reorganization operations to optimize memory stores. Options include:
- `--analyze-only`: Show what would be reorganized without making changes
- `--skip-pruning`: Skip removal of low-value memories
- `--skip-synthesis`: Skip meta-insight generation
- `--skip-lifecycle`: Skip lifecycle progression (promotion/decay)
- Default (no flags): Run full reorganization with all operations

This command is typically run periodically (weekly) or on-demand when memory performance degrades.

#### /migrate [options]
Migrates existing memories to new schema versions or adds missing lifecycle metadata. Options:
- `--force`: Overwrite existing metadata (default is add-only)
- `--dry-run`: Show migration plan without executing

Used after Friday upgrades that introduce new memory fields or structures.

#### /lifecycle [options]
Manually triggers memory lifecycle operations (normally run automatically after each turn or on session exit). Options:
- `--stats`: Show current lifecycle statistics (stage distribution, promotion/decay candidates)
- `--promote`: Run promotion scoring and promote eligible memories
- `--decay`: Run decay calculations and downgrade stale memories
- `--reactivate`: Check decayed memories for reactivation opportunities
- Default (no flags): Run full cycle (promote, decay, reactivate)

### 9.6 Tool Management Commands

#### /tools [category]
Lists available tools, optionally filtered by category. Shows: tool name, category, description (first 100 chars), parameter count, and tags. Examples:
- `/tools` - List all 50+ tools
- `/tools filesystem` - Show only filesystem tools
- `/tools web` - Show only web/network tools

#### /run-tool <name> [json]
Executes a tool directly with provided JSON parameters. Useful for testing tools outside of agent loops or debugging tool execution. Example: `/run-tool read_file {"file_path": "/tmp/test.txt"}`. Returns full ToolResult including execution time and any errors.

#### /inject-tools <names>
Injects specified tools into context for the current session, making them available even if not normally selected by the recommendation algorithm. Useful for testing tool workflows or forcing specific tool availability. Example: `/inject-tools git_status,git_diff,git_commit`.

#### /clear-tools
Removes all injected tools, returning to normal tool recommendation behavior. This clears the state set by `/inject-tools`.

#### /recommend-tools <query>
Tests the tool recommendation algorithm for a given query. Shows which tools Friday would include in context and why (relevance scores, category matches, usage patterns). Useful for debugging cases where expected tools aren't available or understanding recommendation logic.

#### /tool-budget
Displays current tool token budget allocation: how many tokens are reserved for tool schemas, how many tools fit in budget at current context utilization, and which tools are currently included. Helps diagnose cases where all tools don't fit in context window.

### 9.7 Agent Orchestration Commands (Phase 3)

#### /switch [agent]
Switches active agent or shows current agent status if no name provided. Example: `/switch researcher` changes to researcher agent, `/switch` displays currently active agent and available options.

#### /agents
Lists all registered agents with capabilities: agent name, role, goal, available tools, model configuration, and status (active/cached/registered). Shows the complete agent roster.

#### /agent [name]
Shows detailed information for a specific agent (or active agent if no name): full configuration (tools, model, memory mode), current state (message count, tool calls), and performance metrics (average latency, token usage).

#### /delegate <agent> <task>
Delegates a task to another agent and returns result to current agent. Example: `/delegate coder Implement the user authentication function`. The delegated agent executes the task with full tool access, then returns control to the calling agent.

#### /status
Shows orchestrator status: active agent, default agent, session ID, message count, cached agents (instantiated and ready), and registered agents (available but not yet loaded).

#### @agent_name <message>
Direct routing syntax for explicitly addressing a specific agent. Example: `@researcher Find papers on transformer architectures` sends the message directly to the researcher agent, bypassing the active agent. The response is attributed to the addressed agent.

### 9.8 Workflow Commands (Phase 4)

#### /workflow list
Lists all available workflows from the `workflows/` directory: workflow name, description, task count, version, and author. Shows which workflows are ready for execution.

#### /workflow run <name> [inputs]
Executes a workflow with optional input variables. Example: `/workflow run newsletter user_topic="AI trends" urgency="high"`. Variables are passed as key=value pairs (supports quoted strings for multi-word values). The command returns execution results or pauses at approval gates.

#### /workflow status
Shows current workflow execution status: workflow name, execution ID, overall status (RUNNING/COMPLETED/FAILED/WAITING_APPROVAL), task breakdown (which tasks completed/failed/pending), current task in progress, and execution duration. Also shows variable values and final outputs if completed.

#### /workflow approve
Approves a pending task at an approval gate and continues workflow execution. Only valid when workflow status is WAITING_APPROVAL. Shows the approved task and next workflow state.

#### /workflow skip
Skips a pending task at an approval gate and continues workflow with remaining tasks. Skipped tasks mark their outputs as null, so dependent tasks must handle missing inputs gracefully.

### 9.9 Configuration & Utility Commands

#### /vars
Displays all scoped variables: session-scoped (current session only), user-scoped (persist across sessions for user), and global-scoped (shared across all users). Shows variable names, values, and scope.

#### /set <key> <value>
Sets a scoped variable. Scope determined by key prefix: `session:` for session scope, `user:` for user scope, no prefix for global scope. Example: `/set user:name "Alice"` stores user name across sessions.

#### /read <path>
Reads a file using Friday's smart file readers with automatic format detection. Supports: text files (UTF-8, Latin-1, auto-detect), PDF, DOCX, Excel, CSV. Shows content with metadata (file size, encoding, line count). Example: `/read /tmp/report.pdf`.

#### /ingest <path>
Ingests file content into vector memory for semantic search. Friday extracts text, chunks it, generates embeddings, and stores in the vector store. Useful for adding documents to Friday's knowledge base. Example: `/ingest /docs/api-reference.pdf`.

#### /help [command]
Shows command reference. Without arguments, displays summary of all commands by category. With command name, shows detailed help including: description, parameters, examples, and related commands. Example: `/help workflow` shows all workflow commands.

---

## 10. CONFIGURATION GUIDE

**Purpose:** Complete reference for Friday's YAML configuration system.

### 10.1 Configuration Architecture

#### 10.1.1 Hierarchical Config Merging
Friday's configuration system merges values from multiple sources in priority order: (1) Code defaults - sensible baseline values, (2) System config file - `config.yaml` in project root, (3) Environment variables - override config for deployment, (4) Runtime overrides - programmatic configuration changes. This section explains the merging algorithm (deep merge for nested dicts, environment variables override matching paths), how to structure config files for different environments (dev, staging, prod), and best practices for secret management (API keys only in environment, never commit to config files).

#### 10.1.2 Configuration Validation
Friday validates configuration on startup using Pydantic models: type checking (ensure ints are ints, enums are valid), range validation (temperature 0-2, token limits within model caps), dependency checks (if feature X enabled, require config Y), and error reporting (clear messages about missing/invalid values). This section explains how to interpret validation errors and common configuration mistakes to avoid.

#### 10.1.3 Environment Variable Mapping
Complete reference for environment variable overrides: naming convention (uppercase with underscore separator), nesting (double underscore for nested keys: `FRIDAY_LLM__MODEL`), type coercion (string "true" → boolean True), and precedence (environment always wins over config file). We'll include a full mapping table showing config path → environment variable for every setting.

### 10.2 LLM Configuration

#### 10.2.1 Provider Setup (OpenAI, Anthropic, Google, Local)
Step-by-step guides for each LLM provider:

**OpenAI:** Set `OPENAI_API_KEY`, configure `model: "gpt-4o"` or `"gpt-4o-mini"`, adjust `temperature` and `max_tokens`. We'll cover organization IDs, API base URL for Azure OpenAI, and retry configuration.

**Anthropic:** Set `ANTHROPIC_API_KEY`, configure `model: "claude-3.5-sonnet"` or `"claude-3-haiku"`, explain the different model tiers (Opus/Sonnet/Haiku) and when to use each, cover beta features (tool use requires header configuration).

**Google Gemini:** Set `GOOGLE_API_KEY`, configure `model: "gemini-2.5-pro"` or `"gemini-2.5-flash"`, explain rate limits and quota management, cover grounding with Google Search (if enabled).

**Local Ollama:** No API key needed, set `base_url: "http://localhost:11434"`, configure `model: "ollama/llama3"` or `"ollama/mistral"`, explain how to install Ollama, pull models, and verify connection. We'll cover resource requirements (RAM, GPU) for different model sizes.

#### 10.2.2 OpenRouter for Multi-Model Access
OpenRouter provides unified API access to 100+ models from various providers. This section explains setup: get API key from openrouter.ai, set `OPENROUTER_API_KEY`, configure models with `openrouter/` prefix (e.g., `"openrouter/anthropic/claude-3.5-sonnet"`), and understand pricing (OpenRouter adds markup to provider costs). We'll show how to switch between providers seamlessly for cost optimization or capability testing.

#### 10.2.3 Model-Specific Settings
Configuration reference for model parameters:
- `temperature` (0-2): Creativity/randomness (0 = deterministic, 1 = balanced, 2 = very creative)
- `max_tokens`: Response length limit (model-specific caps: 4K-128K)
- `top_p`: Nucleus sampling threshold (alternative to temperature)
- `frequency_penalty`/`presence_penalty`: Repetition control (OpenAI-specific)
- `stop_sequences`: Custom stop tokens for response termination

We'll explain when to adjust each parameter and provide recommended values for different use cases (factual Q&A vs. creative writing vs. code generation).

#### 10.2.4 Resilience & Retry Configuration
Friday's resilience layer wraps LLM calls with:
- `max_retries`: Retry attempts with exponential backoff (default 3)
- `timeout_seconds`: Request timeout (default 60s, increase for long generation)
- `circuit_breaker_threshold`: Failures before circuit opens (default 5)
- `circuit_breaker_timeout`: How long circuit stays open (default 60s)

This section explains backoff strategies (exponential with jitter), when retries help (transient errors, rate limits) vs. when they don't (invalid API key, model not found), and how to tune for production reliability.

### 10.3 Memory Configuration

#### 10.3.1 Context Window & Token Budgeting
Friday's token budget configuration determines how tokens are allocated:
- `total_tokens`: Total context window (must match LLM model limit: 8K, 32K, 128K)
- `system_prompt_tokens`: Reserved for system prompt/identity (default 1000)
- `history_tokens`: Reserved for conversation history (default 2000)
- `context_tokens`: Reserved for retrieved memories/tools (default remaining)
- `query_tokens`: Reserved for user query (default 500)

This section explains the knapsack optimization, how to adjust budgets for different workflows (research needs more context_tokens, chat needs more history_tokens), and how to diagnose context window exhaustion.

#### 10.3.2 Priming Configuration
Session priming settings control what's loaded on first turn:
- `enabled`: Enable/disable priming (default true)
- `top_n_entities`: How many entities to load by hit_count (default 10)
- `top_n_insights`: How many recent insights to load (default 20)
- `recency_days`: Only load entities/insights from last N days (optional filter)
- `include_summaries`: Load turn summaries from prior sessions (default true)

We'll explain priming strategies for different agent types (personal assistants prime heavily, ephemeral agents don't prime), and how priming affects cold-start latency.

#### 10.3.3 Lifecycle Settings (Decay, Promotion)
Memory lifecycle configuration:
- `decay_rate`: Lambda value for exponential decay (default 0.01 = ~79% after 24h)
- `promotion_threshold`: Minimum score for promotion (default 0.7)
- `promotion_min_age_hours`: Minimum time in short-term before promotion (default 24)
- `decay_min_age_days`: Minimum age before decay eligible (default 7)
- `decayed_retention_days`: How long decayed memories persist before deletion (default 30)
- `auto_lifecycle`: Run lifecycle after each turn (default true) vs. manual trigger

This section explains how to tune decay rates for different memory types (fast decay for temporary tasks, slow decay for learned preferences) and when to disable auto-lifecycle (performance-critical applications).

#### 10.3.4 Collection Configuration (Multi-Collection Vector Store)
ChromaDB collection settings:
- `collection_names`: Map of stages to collection names (short_term, long_term, decayed)
- `similarity_thresholds`: Minimum similarity score per collection (default 0.7 for all)
- `max_results`: Maximum documents to retrieve per collection (default 10)
- `embedding_function`: Which embedding model to use (local vs. cloud)

We'll explain the multi-collection strategy benefits (separate thresholds per stage, optimized retrieval, logical organization) and how to customize for specific use cases.

### 10.4 Tool Configuration

#### 10.4.1 Tool Registry Setup
Tool system configuration:
- `auto_discover`: Automatically register built-in tools (default true)
- `custom_tool_paths`: Additional directories to search for custom tools
- `disabled_tools`: Explicit blocklist of tool names to disable
- `context_integration`: Include tools in LLM context (default true) vs. external execution

This section explains tool discovery mechanism (module scanning for BaseTool subclasses), how to organize custom tools, and when to disable specific tools (security, cost, or capability constraints).

#### 10.4.2 Security & Sandboxing
Tool security configuration:
- `sandbox_mode`: Enable subprocess isolation (default true for code execution tools)
- `allowed_commands`: Shell command allowlist for execute_command tool
- `blocked_paths`: Filesystem paths to deny access (e.g., /etc, ~/.ssh)
- `timeout_seconds`: Maximum tool execution time (default 30s)
- `resource_limits`: CPU/memory limits for sandboxed execution

We'll cover security best practices (never run untrusted code without sandbox, validate all tool inputs, log tool execution for audit) and the roadmap for Docker-based sandboxing.

### 10.5 Extraction Configuration

#### 10.5.1 Extraction LLM Selection
Configure a separate (typically cheaper) model for entity/relationship extraction:
- `extraction_llm.model`: Model name (default same as main LLM)
- `extraction_llm.temperature`: Lower for extraction (default 0.3 for consistency)
- `extraction_llm.max_tokens`: Shorter for structured output (default 1000)

This section explains cost/quality tradeoffs: using GPT-4o-mini or Claude Haiku for extraction saves ~90% vs. premium models, with minimal quality loss for structured extraction tasks. We'll show cost analysis and quality benchmarks.

#### 10.5.2 Extraction Prompts & Rules
Customize extraction behavior:
- `entity_types`: Which entity types to extract (Person, Project, Technology, etc.)
- `relationship_verbs`: Which semantic relationships to recognize (USES, AUTHORED, etc.)
- `confidence_threshold`: Minimum extraction confidence (default 0.6)
- `extraction_enabled`: Enable/disable extraction (default true, disable for stateless agents)

We'll provide guidance on custom entity types for domain-specific applications (e.g., adding "Drug" and "Symptom" for medical agents) and custom relationship verbs.

### 10.6 Transcript Configuration

#### 10.6.1 Storage Settings
Transcript storage configuration:
- `storage_path`: SQLite database location (default `./transcripts/transcript.db`)
- `export_directory`: Where to save exports (default `./transcripts/exports`)
- `auto_export_on_exit`: Automatically export session on exit (default false)
- `compression`: Enable gzip compression for exports (default true)

#### 10.6.2 Export Formats
Configure default export format and options:
- `default_format`: jsonl, markdown, or training (default markdown)
- `include_tool_results`: Include full tool outputs in exports (default true)
- `include_tokens`: Include token counts in exports (default true)
- `anonymize_user_id`: Replace user IDs with hashes in exports (default false for privacy)

### 10.7 Telemetry & Observability

#### 10.7.1 Logging Configuration
Python logging setup:
- `log_level`: DEBUG, INFO, WARNING, ERROR (default INFO)
- `log_format`: Structured (JSON) vs. human-readable (default structured for production)
- `log_file`: File path for log output (default stderr only)
- `component_levels`: Per-component log levels (e.g., verbose memory, quiet LLM)

#### 10.7.2 Telemetry Integration
Optional telemetry configuration for production monitoring:
- `telemetry_enabled`: Enable telemetry recording (default false)
- `telemetry_provider`: OpenTelemetry, DataDog, custom (extensible via protocol)
- `trace_llm_calls`: Include full LLM request/response in traces (sensitive)
- `metrics_endpoint`: Where to send metrics (Prometheus, StatsD, etc.)

This section explains privacy considerations (telemetry may include user data, configure carefully) and performance impact (minimal with async submission).

---

## 11. ADVANCED TOPICS

**Purpose:** Advanced techniques and architectural deep dives for power users.

### 11.1 Hybrid Cloud-Local Architecture

#### 11.1.1 Cost Optimization Strategies
Architectural patterns for minimizing cloud API costs while maintaining capabilities:
- **Reasoning-in-cloud, Execution-local:** Use cloud models (GPT-4, Claude) for complex reasoning, local models (Llama 3, Mistral) for tool calls and formatting
- **Tiered agent model:** Premium models for critical agents, budget models for routine agents
- **Extraction offload:** Use local models for all extraction, cloud only for main conversations
- **Embeddings local:** Run nomic-embed or similar locally via LM Studio, eliminate embedding API costs

This section includes cost analysis with real examples showing 70-90% cost reduction vs. all-cloud approaches, while maintaining quality for most use cases.

#### 11.1.2 Privacy & Data Residency
Use local models for privacy-sensitive data:
- **PHI/PII handling:** Medical, legal, or financial data never leaves premises
- **Compliance requirements:** GDPR, HIPAA, SOC 2 mandating data residency
- **Air-gapped deployment:** Run Friday entirely on-premises with local LLMs

We'll cover local model setup (Ollama installation, GPU requirements), quality expectations (local models now match older cloud models like GPT-3.5), and hybrid strategies (encrypt and route only non-sensitive data to cloud).

#### 11.1.3 Latency vs. Capability Tradeoffs
When to choose local vs. cloud models based on latency and capability requirements:
- **Local advantages:** <100ms latency, no rate limits, deterministic performance
- **Cloud advantages:** Latest models, larger context windows, specialized capabilities (vision, code)
- **Hybrid solution:** Fast local for interactive turns, cloud for batch operations

This section provides latency benchmarks and a decision matrix for model selection.

### 11.2 Memory Optimization Techniques

#### 11.2.1 Advanced Lifecycle Tuning
Beyond default configuration, advanced tuning for specific memory patterns:
- **Hot-cold memory tiers:** Very fast decay (λ=0.1) for "hot" temporary memory, slow decay (λ=0.001) for "cold" learned preferences
- **Topic-based decay rates:** Different decay per entity type (projects decay fast, people decay slow)
- **Access-based reactivation:** Configurable reactivation thresholds (auto-promote on N accesses within M hours)

We'll show configuration examples for different use cases (research assistant, personal assistant, customer support agent) with rationale for each tuning decision.

#### 11.2.2 Graph Pruning Strategies
Optimizing the associative graph as it grows:
- **Weak edge removal:** Delete relationships with low hit_count after N days
- **Orphan node cleanup:** Remove entities with no relationships
- **Merge duplicate entities:** Fuzzy matching to consolidate similar entities
- **Subgraph extraction:** Isolate specific topic subgraphs for focused agents

This section explains the graph pruning algorithms, when to run them (monthly or at threshold size), and how to preserve important connections.

#### 11.2.3 Vector Store Compaction
Optimizing ChromaDB performance:
- **Reindexing:** Periodic reindexing for faster similarity search
- **Embedding upgrades:** Migrate to better embedding models while preserving documents
- **Quantization:** Reduce vector dimensions for faster search (with quality tradeoff)
- **Collection splitting:** Break large collections into topic-specific subcollections

### 11.3 Custom Protocol Implementations

#### 11.3.1 Implementing Custom LLM Clients
How to implement the `LLMClient` protocol for custom LLM backends:
- Protocol requirements: `chat_completion()`, `streaming_completion()`, `get_model_info()`
- Authentication patterns, error handling, response parsing
- Example: Implementing a client for Hugging Face Inference API
- Example: Implementing a client for self-hosted vLLM deployment

This section includes complete code examples and explains integration with Friday's resilience layer.

#### 11.3.2 Implementing Custom Memory Stores
How to implement the store protocols for custom backends:
- `VectorStoreAdapter`: Requirements for custom vector DB (Pinecone, Weaviate, Qdrant)
- `GraphStoreAdapter`: Requirements for custom graph DB (Neo4j, ArangoDB)
- `EpisodicStoreAdapter`: Requirements for custom transcript storage (PostgreSQL, MongoDB)

We'll show example implementations and explain the protocol contracts (required methods, expected exceptions).

#### 11.3.3 Custom Tool Protocols & Wrappers
Advanced tool patterns:
- **Tool wrappers:** Wrapping external APIs as Friday tools (Slack, GitHub, Database)
- **Streaming tools:** Tools that return results incrementally (long-running operations)
- **Stateful tools:** Tools that maintain connections across calls (database sessions, SSH connections)
- **Composite tools:** Tools that orchestrate multiple sub-tools (CodeGenerationTool example)

### 11.4 Performance Optimization

#### 11.4.1 Context Assembly Optimization
Techniques for faster context assembly:
- **Parallel retrieval:** Query all stores concurrently (episodic + vector + graph)
- **Caching:** Cache assembled context for rapid-fire turns (invalidate on memory update)
- **Lazy loading:** Defer entity/relationship loading until needed
- **Pre-computed factors:** RetrievalFactorComputer for fast inclusion scoring

We'll show benchmarks: optimized assembly <165ms vs. naive sequential 500ms+.

#### 11.4.2 Memory Store Indexing
Database optimization for large deployments:
- **Graph indexes:** Index entities by type, hit_count, created_at for fast queries
- **Vector indexes:** Tune HNSW parameters (M, ef_construction) for speed vs. accuracy
- **Episodic indexes:** Index turns by session_id, timestamp, user_id for fast retrieval

#### 11.4.3 Token Budget Optimization
Maximizing information density in limited context windows:
- **Compression:** Summarize old conversation turns instead of including verbatim
- **Relevance filtering:** Aggressive similarity thresholds to exclude marginal memories
- **Tool schema minimization:** Include only parameter names + types, omit descriptions
- **Dynamic budgeting:** Adjust budget allocation per turn (more context for complex queries)

### 11.5 Deployment Patterns

#### 11.5.1 Docker Deployment
Containerizing Friday applications:
- Multi-stage Dockerfile for minimal image size
- Volume mounting for persistent memory stores
- Environment variable configuration for secrets
- Health checks and monitoring integration
- Example docker-compose.yml for full stack (Friday + Ollama + ChromaDB)

#### 11.5.2 Kubernetes Deployment
Production-grade orchestration:
- Deployment manifests for Friday agent pods
- StatefulSet for memory store persistence
- ConfigMap/Secret for configuration and API keys
- Horizontal pod autoscaling based on request load
- Distributed tracing integration (OpenTelemetry)

#### 11.5.3 Serverless Deployment
Running Friday in serverless environments:
- AWS Lambda packaging considerations (memory stores initialization)
- Cold-start optimization (pre-warmed containers, minimal context priming)
- Stateless mode for ephemeral agents (disable memory persistence)
- API Gateway integration for REST/webhook triggers

---

## 12. USE CASES & EXAMPLES

**Purpose:** Real-world applications demonstrating Friday's capabilities.

### 12.1 Personal Assistant Use Cases

#### 12.1.1 Research Assistant
A Friday agent configured for deep research with long-term memory of sources, topics explored, and findings. This section walks through:
- Agent configuration (tools: web_search, scrape_page, read_file, git_commit for notes)
- Memory configuration (long retention, slow decay for sources)
- Workflow: Search → Extract → Summarize → Store findings
- Example interaction showing cross-session research continuity
- Sample agent YAML and config.yaml

#### 12.1.2 Code Review & Development Assistant
A Friday agent team for software development: coder writes code, reviewer checks quality, tester runs tests. This section demonstrates:
- Multi-agent orchestration (code → review → test workflow)
- Tool usage (git, filesystem, code execution, linting)
- Memory of codebase context, prior reviews, and coding patterns
- Workflow: Feature request → Implementation → Review gate → Test → Commit
- Complete code example with agent definitions and workflow YAML

#### 12.1.3 Project Management Assistant
A Friday agent that tracks project status, deadlines, and dependencies across conversations:
- Entity graph for projects, tasks, and people
- Relationship tracking (DEPENDS_ON, ASSIGNED_TO, BLOCKS)
- Memory of decisions, blockers, and progress
- Workflow: Standup update → Extract updates → Update graph → Generate status report
- Example showing how Friday maintains project state across weeks of conversations

### 12.2 Enterprise Use Cases

#### 12.2.1 Customer Support Agent
A Friday agent for handling customer inquiries with memory of customer history:
- Customer profile in graph (preferences, past issues, product usage)
- Insight memory for common solutions and escalation triggers
- Tool integration (CRM API, knowledge base search, ticket creation)
- Workflow: Query → Search KB → Check history → Respond or escalate
- Privacy considerations (namespace isolation per customer, data retention policies)

#### 12.2.2 Document Analysis & QA Agent
A Friday agent for analyzing large document sets and answering questions:
- Document ingestion pipeline (PDF/DOCX → chunking → embedding → vector store)
- Semantic search for relevant passages
- Graph of document relationships (citations, authorship, topics)
- Multi-hop reasoning across documents ("What does Paper A say about the method from Paper B?")
- Example: Analyzing a corpus of research papers or legal documents

#### 12.2.3 DevOps & Monitoring Agent
A Friday agent for infrastructure monitoring and incident response:
- Tool integration (kubectl, cloud provider APIs, log aggregation)
- Memory of infrastructure topology, past incidents, and resolutions
- Workflow: Alert → Diagnose → Remediate or escalate
- Example: Autonomous response to common issues (restart failing pod, scale up under load)
- Safety boundaries (read-only operations by default, approval gates for destructive actions)

### 12.3 Specialized Domain Examples

#### 12.3.1 Medical History Assistant (PHI-Compliant)
A Friday agent for healthcare with strict privacy requirements:
- Local LLM deployment (no cloud API calls with PHI)
- Custom entity types (Symptom, Medication, Diagnosis, Provider)
- Relationship graph for medical history (Patient HAS Condition, PRESCRIBED Medication)
- Compliance features (audit logging, data residency, access controls)
- Example: Tracking patient history and drug interactions across visits

#### 12.3.2 Legal Research Assistant
A Friday agent for legal professionals:
- Document corpus (case law, statutes, regulations) in vector store
- Entity graph (cases, judges, legal concepts, precedents)
- Citation tracking (which cases cite which, relationship strength by frequency)
- Workflow: Legal question → Find relevant cases → Extract principles → Draft argument
- Example: Researching precedent for a specific legal argument

#### 12.3.3 Financial Analysis Agent
A Friday agent for financial data analysis:
- Tool integration (market data APIs, financial modeling libraries)
- Memory of companies, sectors, and analyst notes
- Time-series aware memory (track metric evolution over time)
- Workflow: Query → Fetch data → Analyze → Generate report
- Example: Tracking portfolio performance and recommending rebalancing

### 12.4 Educational Use Cases

#### 12.4.1 Language Learning Tutor
A Friday agent that adapts to learner's level and remembers progress:
- Memory of vocabulary learned, grammar concepts covered, and error patterns
- Adaptive difficulty (increase complexity as proficiency improves)
- Spaced repetition integration (surface weak areas)
- Workflow: Conversation → Error analysis → Targeted practice → Progress tracking

#### 12.4.2 Study Assistant
A Friday agent that helps students learn and retain material:
- Memory of topics studied, questions asked, and misunderstandings
- Document ingestion (textbooks, lecture notes) for QA
- Quiz generation based on memory gaps (Hebbian learning identifies weak areas)
- Workflow: Study session → Questions → Answers with explanations → Follow-up quizzes

---

## 13. TROUBLESHOOTING & FAQ

**Purpose:** Common issues, debugging strategies, and frequently asked questions.

### 13.1 Common Issues & Solutions

#### 13.1.1 Memory Issues
- **Symptom:** Friday doesn't remember prior conversations
  - **Check:** Verify memory stores are persistent (not in /tmp), check permissions
  - **Check:** Ensure session_id and user_id are consistent across restarts
  - **Debug:** Use `/memory` command to verify store contents

- **Symptom:** Memory retrieval is slow (>1s per turn)
  - **Check:** ChromaDB collection sizes (reindex if >10K documents)
  - **Check:** Graph size (prune if >10K entities)
  - **Solution:** Tune similarity thresholds, limit retrieval count

#### 13.1.2 LLM Issues
- **Symptom:** "API key not found" errors
  - **Solution:** Set environment variables (OPENAI_API_KEY, etc.), verify they're visible to process

- **Symptom:** Tool calls not working
  - **Check:** Tool schemas included in context (`/prompt` to verify)
  - **Check:** Model supports tool calling (older models don't)
  - **Debug:** Use `/run-tool` to test tool directly

#### 13.1.3 Context Window Issues
- **Symptom:** "Context length exceeded" errors
  - **Solution:** Reduce token budgets in config (especially history_tokens)
  - **Solution:** Increase context_format compression (use XML instead of plain)
  - **Debug:** Use `/context --debug` to see token breakdown

### 13.2 Debugging Strategies

#### 13.2.1 Logging & Telemetry
Enable debug logging to diagnose issues:
```bash
export FRIDAY_LOG_LEVEL=DEBUG
python memory-chat-v2.py
```

Key log messages to look for:
- Context assembly: Token counts, retrieval latency, knapsack packing efficiency
- Memory operations: Store writes, lifecycle transitions, extraction results
- LLM calls: Request/response, retries, errors

#### 13.2.2 Interactive Debugging
Use CLI commands for live debugging:
- `/debug` - Last context assembly details
- `/prompt` - Exact LLM input
- `/context` - Logical context payload
- `/memory` - Memory store statistics
- `/status` - Agent orchestrator state

#### 13.2.3 Transcript Analysis
Export and analyze transcripts to understand failures:
```bash
/export jsonl
# Analyze with jq, grep, or custom scripts
```

Look for patterns: repeated tool failures, context misses (relevant memory not retrieved), token budget exhaustion.

### 13.3 Performance Tuning

#### 13.3.1 Latency Optimization
Target latencies:
- Context assembly: <200ms
- LLM call: 1-5s (depends on provider and response length)
- Tool execution: varies (filesystem <100ms, web API 500ms-5s)
- Total turn latency: <10s for typical interactions

If exceeding targets:
- Profile with `time` command or Python profilers
- Check for sequential operations that could be parallel
- Consider local LLMs for latency-sensitive applications

#### 13.3.2 Cost Optimization
Monitor token usage via transcripts:
```bash
# Total tokens across all turns
sqlite3 transcript.db "SELECT SUM(total_tokens) FROM turns"
```

Optimize costs:
- Use cheaper models for extraction and simple agents
- Reduce context token budgets (less memory retrieval)
- Increase similarity thresholds (fewer retrieved documents)
- Compress conversation history (summarize old turns)

### 13.4 FAQ

**Q: Can Friday run completely offline?**
A: Yes, use local LLMs (Ollama) and local embeddings (LM Studio with nomic-embed). No network calls required.

**Q: How much does it cost to run Friday in the cloud?**
A: Highly variable based on usage. Typical ranges: $0.01-0.10 per conversation turn with GPT-4, $0.001-0.01 with budget models. Use extraction offloading and hybrid architecture for 70-90% cost reduction.

**Q: What are the hardware requirements?**
A: Minimum: 4GB RAM, any CPU. Recommended for local LLMs: 16GB+ RAM, GPU with 8GB+ VRAM. ChromaDB and graph stores are lightweight (<1GB for 10K memories).

**Q: How do I migrate from another agent framework?**
A: Friday's protocol-based architecture enables gradual migration. Start with custom LLMClient wrapping your existing LLM integration, migrate memory stores incrementally, adopt Friday tools progressively. No "big bang" rewrite required.

**Q: Is Friday production-ready?**
A: Friday is currently v0.1.0 (early development). Core features (memory, tools, agents) are stable and tested. Orchestration and workflows are new (Phase 3-4). Use for prototypes and pilot projects; production deployment requires additional hardening (error handling, monitoring, scaling).

**Q: How does Friday compare to LangChain / AutoGPT / CrewAI?**
A: Friday focuses on production-ready architecture with enterprise observability, while LangChain targets rapid prototyping. AutoGPT emphasizes autonomy, Friday balances autonomy with human oversight. CrewAI specializes in multi-agent, Friday provides comprehensive agent capabilities (memory, tools, workflows). Friday's protocol-first design enables long-term maintainability and extension.

---

## 14. APPENDICES

### Appendix A: Complete Configuration Reference
(Full config.yaml with all fields documented inline)

### Appendix B: Tool Catalog
(Complete list of all 50+ built-in tools with parameters and examples)

### Appendix C: API Reference
(Python API documentation for using Friday programmatically)

### Appendix D: Protocol Specifications
(Complete interface definitions for all abstract protocols)

### Appendix E: Migration Guides
(Version-to-version upgrade instructions)

### Appendix F: Glossary
(Definitions of key terms: episodic memory, Hebbian learning, knapsack optimization, etc.)

---

## 15. CONTRIBUTING & COMMUNITY

### 15.1 Development Setup
How to contribute to Friday: clone repo, install dev dependencies (`uv sync`), run tests (`pytest`), code style (Ruff), commit conventions.

### 15.2 Architecture Decision Records
Link to ADRs documenting major design decisions and rationale.

### 15.3 Roadmap
Current development priorities and planned features (Phase 5+).

### 15.4 Community Resources
Links to: GitHub repository, Discord/Slack community, issue tracker, documentation site.

---

**End of Outline**

**Total Estimated Length:** 200-250 pages (comprehensive)
**Modular Structure:** Each section can be read independently
**Target Reading Time:** 20-30 hours for complete guide, 2-3 hours for quick start + core concepts

# Friday Agent Framework
## Executive Summary: Why Friday Exists

**Version:** 1.0
**Framework Version:** v0.1.0
**Last Updated:** 2026-01-24

---

## The Problem: AI Agents That Forget

Every conversation with today's AI assistants starts from zero. You explain your preferences. You provide context. You repeat background information you've shared before. The AI responds intelligently—but it doesn't *remember*. It doesn't *learn*. It doesn't *grow* with you over time.

This isn't just inconvenient. It's a fundamental barrier to AI reaching its potential as a genuine cognitive partner. Imagine if every morning, you woke up with amnesia—unable to recall yesterday's work, last week's decisions, or the lessons learned from months of experience. That's the reality of stateless AI assistants. The 'Memento Problem'

The problem runs deeper than simple forgetfulness. Modern AI applications struggle with:
- **Context fragmentation**: Information scattered across disconnected sessions
- **Scalability limits**: Every conversation competes for the same fixed context window
- **Learning impossibility**: No mechanism to improve from experience
- **Collaboration barriers**: Multiple agents can't share knowledge or build on each other's work
- **Deployment rigidity**: Locked into specific vendors, models, or architectures

We built Friday to solve these problems—not with patches or workarounds, but with a fundamentally different architecture.

---

## The Facts: What Friday Is

**Friday is a production-ready Python framework for building AI agents with genuine memory, adaptive learning, and collaborative intelligence.**

At its core, Friday implements a **three-tier memory architecture** inspired by cognitive science:

1. **Episodic Memory** - The raw, chronological record of conversations stored in SQLite via the TranscriptStoreAdapter (what happened, when, and with whom)
2. **Semantic Memory** - Conceptual knowledge extracted from interactions and stored as searchable embeddings via swappable VectorStoreAdapter (ChromaDB by default; supports Pinecone, Weaviate, Qdrant, or enterprise SQL databases)
3. **Associative Memory** - A knowledge graph of entities and relationships via swappable GraphStoreAdapter (NetworkX + JSON by default; supports Neo4j, ArangoDB, or other graph databases)

This isn't a database wrapper. It's a **memory loop**: every conversation feeds learning, every learning informs future conversations, and importance naturally emerges through use. Friday implements **Hebbian learning** ("neurons that fire together wire together")—entities and relationships strengthen with repeated access, while unused memories naturally decay. The result is a system that mirrors human memory: remembering what matters, forgetting what doesn't, and reactivating forgotten knowledge when it becomes relevant again.

**Friday is modular.** The framework consists of eight independent Python packages:

- `friday-core` - Abstract protocols for complete implementation swappability
- `friday-memory` - Three-tier memory system with lifecycle management
- `friday-llm` - Provider-agnostic LLM client (OpenAI, Anthropic, Google, Ollama)
- `friday-agent` - Agent implementations (Re-Act loop, orchestration, workflows)
- `friday-tools` - 50+ tools for filesystem, web, git, code execution, data manipulation
- `friday-transcript` - Complete conversation logging with export (JSONL, Markdown, training data)
- `friday-mcp` - Model Context Protocol integration for external tool systems
- `friday-optimization` - Knapsack algorithms for optimal context packing

You can use the full stack or individual packages. Need just the memory system? Use `friday-memory`. Need provider-agnostic LLM calls? Use `friday-llm`. Every major component is defined as an **abstract protocol**—swap ChromaDB for Pinecone, replace LiteLLM with a custom client, bring your own graph database. Zero vendor lock-in.

**Friday is observable.** Every conversation is captured in SQLite transcripts with complete metadata: user messages, assistant responses, tool calls with parameters and results, token usage, latency, timestamps, and provenance attribution. Export to JSONL for analysis, Markdown for human review, or training format for fine-tuning. The memory system includes built-in lifecycle tracking—see exactly which memories are promoted to long-term storage, which decay from disuse, and which get reactivated when they become relevant again.

**Friday runs anywhere Python runs.** Use cloud models (OpenAI, Anthropic, Google) for cutting-edge capabilities, local models (Ollama, LM Studio) for privacy and cost control, or hybrid architectures that balance both. Friday supports OpenRouter for unified access to 100+ models with a single API key. The same agent definition works with GPT-4, Claude 3.5 Sonnet, Llama 3, or Mistral—change one config line, no code changes required.

**Current status:** v0.1.0 (early development). Core memory, tools, and agent systems are stable and tested. Multi-agent orchestration and workflows are production-ready as of Phase 4. Enterprise deployment requires additional hardening (comprehensive monitoring, autoscaling, distributed tracing).

---

## The Difference: Why Friday

### 1. **Memory That Actually Works**

Most "memory" in AI frameworks is glorified chat history. Friday implements genuine memory with **lifecycle management**—memories move through stages (short-term → long-term → decayed → reactivated) based on access patterns and importance scoring. The system uses **Hebbian learning** where frequently-accessed information naturally becomes more prominent, while unused memories fade but remain recoverable.

The memory system solves the "lost in the middle" problem identified by cognitive research: LLMs pay less attention to content in the middle of long contexts. Friday uses **tail injection**—placing supporting memories immediately before the user's query to maximize attention. Combined with **knapsack optimization** for intelligent token budgeting, Friday packs the maximum relevant information into every context window.

Example: A research assistant remembers every paper it's read, every entity it's encountered, and every conversation you've had—across weeks or months. When you ask "What did that paper by Smith say about transformers?", Friday doesn't just search its vector database. It activates the "Smith" entity in its knowledge graph, follows relationship edges to papers authored by Smith, checks which papers discuss transformers, retrieves relevant passages from semantic memory, and reactivates any decayed memories about your prior interest in that topic. This isn't keyword matching. It's contextual recall.

### 2. **True Multi-Agent Collaboration**

Friday's multi-agent architecture uses a **shared memory model**: all agents access the same memory controller. When a research agent gathers information, an analyst agent automatically sees those findings. When a coder writes functions, a reviewer agent accesses the same context. This "shared intelligence plane, multiple control planes" design eliminates the context handoff overhead that plagues other multi-agent systems.

**Provenance tracking** ensures attribution clarity: every memory includes metadata about which agent created it, when, and from what source. This enables quality filtering (trust high-confidence extractions), debugging (trace why Friday believes something), and agent-specific learning patterns.

The orchestrator supports **explicit routing** (`@agent_name send this message to researcher`), **task delegation** (one agent hands off a subtask and receives results), and **state aggregation** (merge outputs from parallel agents). Unlike frameworks that spawn isolated agent instances, Friday's agents genuinely collaborate—building shared understanding rather than working in silos.

### 3. **Provider-Agnostic Architecture**

Friday's **protocol-first design** means you're never locked into a vendor:

**Storage Layer (All Swappable):**
- **Episodic Memory**: SQLite by default via `TranscriptStoreAdapter` (implement protocol for PostgreSQL, MySQL, or other SQL databases)
- **Semantic Memory**: ChromaDB by default via `VectorStoreAdapter` (swap for Pinecone, Weaviate, Qdrant, or enterprise SQL like Postgres with pgvector, SQL Server, Oracle)
- **Associative Memory**: NetworkX + JSON by default via `GraphStoreAdapter` (swap for Neo4j, ArangoDB, AWS Neptune, or other graph databases)

**LLM & Embedding Layer:**
- Replace LiteLLM with custom inference by implementing `LLMClient` (vLLM, custom API endpoints, enterprise gateways)
- Switch embedding models with zero code changes (OpenAI → local nomic-embed, Cohere, custom models)

**Tool & Telemetry Layer:**
- Implement `ToolDefinition` for custom tool integrations
- Swap telemetry providers via `TelemetryInterface` (OpenTelemetry, DataDog, custom observability)

Every major component is an abstract protocol. This isn't just architectural elegance; it's **strategic independence**. As the AI landscape evolves (new model providers, better vector databases, improved embedding models), your Friday agents evolve with it. No rewrites, no migrations, no vendor negotiations.

### 4. **Production-Ready Observability**

Friday was designed for enterprise deployment from day one:

- **Complete transcripts**: SQLite database with turn-by-turn conversation records, tool execution logs, token usage, latency tracking
- **Structured logging**: JSON-formatted logs with configurable verbosity per component
- **Telemetry hooks**: OpenTelemetry integration for distributed tracing (request → context assembly → LLM call → tool execution → memory storage)
- **Audit trails**: Provenance metadata on every memory (who created it, when, from what source)
- **Export flexibility**: JSONL for programmatic analysis, Markdown for human review, training format for fine-tuning

This isn't debugging infrastructure bolted on afterward. It's foundational. You can reconstruct any conversation, diagnose any memory retrieval issue, audit any agent decision, and analyze costs down to the token.

### 5. **Hybrid Cloud-Local Architecture**

Friday doesn't force an either/or choice between cloud and local deployment:

- **Cost optimization**: Use GPT-4 for complex reasoning, GPT-4o-mini for extraction, local Llama for tool calls
- **Privacy compliance**: Route sensitive data to local models, use cloud for general tasks
- **Latency control**: Local models for real-time interaction, cloud for batch operations
- **Capability matching**: Specialized cloud models (GPT-4 for code, Claude for long context) with local fallbacks

Example hybrid architecture: A legal research assistant uses local Llama 3 to process privileged documents (100% on-premises for compliance), but routes general legal research to GPT-4 (cloud) for superior reasoning. The same agent definition, the same memory system—just different model endpoints.

---

## The Vision: What Friday Enables

### The Future of Human-AI Collaboration

Imagine AI agents that genuinely understand you—not because they've been fine-tuned on your data, but because they've *experienced* working with you. Agents that remember your coding style, your writing voice, your decision-making patterns. Agents that get better at helping you, the more you work together.

This is Friday's north star: **AI agents that learn and grow alongside humans.**

Today's AI assistants are powerful but ephemeral. They're tools you pick up and put down, never quite fitting your hand. Friday agents are **cognitive partners** that adapt to you. The research assistant that remembers you prefer primary sources over summaries. The coding assistant that knows you favor functional patterns and explicit error handling. The project manager that tracks your team's priorities and blockers without being told.

This isn't about training custom models—it's about **emergent personalization** through memory and interaction. Every conversation teaches Friday about you, your preferences, your context, and your goals. Not through explicit fine-tuning or prompt engineering, but through the natural accumulation of experience stored in a three-tier memory architecture.

### Multi-Agent Systems That Actually Work

Most "multi-agent" frameworks spawn independent agents that can't effectively share knowledge. They either duplicate effort (each agent re-learns the same context) or suffer handoff overhead (explicit context passing at every boundary). Neither scales.

Friday's shared memory model enables **genuine team intelligence**: agents that specialize but collaborate. A research team where one agent finds papers, another extracts insights, a third synthesizes findings, and a fourth fact-checks conclusions—all building on shared context, all contributing to collective knowledge.

This unlocks workflow patterns that are currently impractical:

- **Peer review systems**: Coder writes, reviewer critiques, tester validates—with Friday maintaining coherence across all stages
- **Research pipelines**: Multiple specialists gather information in parallel, synthesize independently, cross-validate findings—without manual context consolidation
- **Continuous learning**: Junior agents learn from senior agents by observing their decisions in shared memory—pattern recognition across provenance metadata

The vision: **AI agent teams that function like human teams**—specialized roles, shared understanding, collaborative improvement.

### Enterprise-Grade AI Infrastructure

Friday is designed for the reality of enterprise deployment: hybrid cloud environments, compliance requirements, cost constraints, observability demands, and vendor diversity.

**Compliance-ready architecture**: Run sensitive data through local models while leveraging cloud capabilities for general operations. HIPAA, GDPR, SOC 2—Friday's architecture supports data residency requirements through configurable model routing and memory namespace isolation.

**Cost-optimized execution**: The framework supports tiered model strategies—premium models for critical reasoning, budget models for routine tasks, local models for high-volume operations. A customer support agent might use GPT-4o-mini for classification, Claude Haiku for extraction, and local Mistral for response formatting—achieving 70-90% cost reduction versus all-premium architectures while maintaining quality for most interactions.

**Observable at every level**: Complete request tracing from user input through context assembly, LLM inference, tool execution, and memory storage. When something goes wrong (and in production, things *will* go wrong), you have full visibility: exactly what context was retrieved, which tools were called, what the LLM generated, and what Friday remembered.

**Vendor independence**: As model providers evolve, pricing changes, or better alternatives emerge, Friday agents adapt through configuration—not code rewrites. This isn't just technical flexibility; it's strategic risk mitigation.

The vision: **AI infrastructure that enterprises can actually deploy**—observable, compliant, cost-effective, and adaptable.

### Democratizing Advanced AI Capabilities

Today, building sophisticated AI agents requires deep ML expertise, extensive infrastructure engineering, and significant financial resources. Friday changes the equation.

**For developers**: Building an agent with memory, tools, and multi-turn conversation capability should take hours, not weeks. Friday provides the infrastructure—you provide the domain logic. Define agents in YAML, configure workflows as task graphs, implement custom tools as decorated Python functions. The complexity of memory management, context engineering, LLM integration, and observability is handled by the framework.

**For researchers**: Friday provides a platform for experimenting with agent architectures, memory systems, and collaboration patterns. The protocol-based design enables clean component substitution—test a new retrieval algorithm by implementing `VectorStoreAdapter`, evaluate a new memory lifecycle policy by subclassing the decay model, compare embedding approaches without changing the rest of the stack.

**For enterprises**: Friday offers a path to AI capabilities without vendor lock-in or proprietary dependencies. The entire framework is built on abstract protocols—adopt Friday's architecture while retaining control over implementation choices. Start with Friday's defaults, gradually swap components as needs evolve, maintain strategic independence.

The vision: **Lowering the barrier to sophisticated AI agents** from "requires a specialized team" to "requires Python knowledge and domain expertise."

### The Path Forward

Friday v0.1.0 represents the foundation: memory systems, tool infrastructure, agent primitives, and multi-agent orchestration. The roadmap ahead:

**Phase 5 - Autonomy & Scale**
- Event-driven autonomous agents (goal-based task execution without human-in-the-loop)
- Distributed deployment patterns (agent swarms across multiple machines)
- Advanced workflow patterns (conditional logic, loops, failure recovery)
- Docker-based sandboxing for untrusted code execution

**Phase 6 - Intelligence Enhancement**
- Self-improving agents (automated prompt optimization based on conversation outcomes)
- Meta-learning from memory patterns (identify what makes memories valuable, adjust extraction accordingly)
- Cross-agent knowledge transfer (senior agents teaching junior agents through shared memory observation)
- Adaptive context engineering (learn optimal token budgets per use case)

**Phase 7 - Future Ecosystem Integration**
- Comprehensive MCP server implementations (expose Friday's memory and tools as MCP resources)
- Pre-built agent templates (research assistant, code reviewer, project manager)
- Enterprise integrations (Slack, Microsoft Teams, ServiceNow, Jira)
- Fine-tuning pipelines (export Friday conversations as training data, evaluate fine-tuned models)

But the deeper vision isn't about features—it's about **enabling a new category of AI application**.

Applications where AI doesn't just respond to queries but *maintains context across time*. Where agents don't just execute tasks but *learn from experience*. Where teams of specialized agents *collaborate seamlessly* rather than operate in isolation. Where enterprises can deploy sophisticated AI capabilities *without sacrificing control or independence*.

This is Friday: **a framework for building AI agents that genuinely learn, remember, and grow.**

---

## Why Now

The conditions are aligned for a memory-first agent framework:

1. **LLMs are good enough**: Models like GPT-4, Claude 3.5, and Llama 3 have sufficient reasoning capabilities that memory—not raw intelligence—is the bottleneck for agent performance.

2. **Context windows are too small**: Even 128K-token models can't hold everything. Intelligent retrieval and lifecycle management are essential for long-running agents.

3. **Vector databases are mature**: ChromaDB, Pinecone, Weaviate offer production-ready semantic search. The infrastructure for memory exists.

4. **Local LLMs are viable**: Llama 3, Mistral, and similar models run on commodity hardware with quality approaching cloud models from 2 years ago. Hybrid architectures are practical.

5. **Multi-agent is mainstream**: The industry recognizes that single-agent systems hit capability limits. The question is no longer "should we use multiple agents?" but "how do we make them collaborate effectively?"

6. **Enterprise is ready**: Companies are moving beyond AI experiments to production deployments. They need observability, compliance, and vendor independence—not research prototypes.

Friday was built to address these conditions—not as a research project or a startup experiment, but as **production infrastructure for the next generation of AI applications**.

---

## Who Friday Is For

**Software developers** building AI-powered applications who need memory, tools, and multi-agent capabilities without building memory infrastructure from scratch.

**AI researchers** exploring agent architectures, memory systems, and collaboration patterns who need a flexible platform with swappable components.

**Technical leaders** evaluating AI strategies who need vendor-independent architecture that adapts as the landscape evolves.

**Enterprise teams** deploying AI in production who need observability, compliance support, and cost control.

**AI practitioners** comfortable with Python who want to build sophisticated agents without deep ML expertise or infrastructure engineering.

If you're building AI agents that operate across multiple sessions, accumulate knowledge over time, use tools to interact with systems, or involve multiple specialized agents working together—Friday was built for you.

---

## How To Use This Guide

This guide is structured for progressive learning:

- **Section 2 (Getting Started)**: Get Friday running in 15 minutes. See memory persistence firsthand.
- **Section 3 (Core Concepts)**: Build a mental model of Friday's architecture before diving into specifics.
- **Sections 4-8 (Memory, Tools, Agents, Orchestration, Workflows)**: Deep dives into each major capability.
- **Section 9 (CLI Reference)**: Command-by-command documentation for the interactive CLI.
- **Section 10 (Configuration)**: Complete YAML configuration reference.
- **Section 11 (Advanced Topics)**: Optimization, custom implementations, deployment patterns.
- **Section 12 (Use Cases)**: Real-world examples demonstrating Friday's capabilities.
- **Section 13 (Troubleshooting)**: Common issues and debugging strategies.

Each section is designed to stand alone—jump to what you need. Reference the appendices for complete API documentation, tool catalogs, and protocol specifications.

The fastest path to understanding Friday: **Read sections 1-3, then build your first agent from section 2**. Everything else follows naturally once you've experienced Friday's memory persistence and tool execution firsthand.

---

## The Bottom Line

**Friday is a production-ready Python framework for building AI agents with genuine memory, adaptive learning, and collaborative intelligence.**

It solves the fundamental problems holding back AI agents today: forgetfulness, context limitations, vendor lock-in, collaboration barriers, and deployment complexity.

It enables a new category of AI application: agents that learn from experience, remember what matters, work together seamlessly, and adapt to their users over time.

The technology exists. The infrastructure is ready. The architecture is proven.

**Build AI agents that genuinely grow with you.**

Welcome to Friday.

---

*Ready to start? Jump to [Section 2: Getting Started](02-getting-started.md) and have your first memory-persistent agent running in 15 minutes.*

*Have questions? See [Section 13: Troubleshooting & FAQ](13-troubleshooting.md) or reach out to the community.*

*Want to dive deeper? Continue to [Section 3: Core Concepts & Architecture](03-core-concepts.md) for the full technical foundation.*

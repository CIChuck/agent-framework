---
title: "Friday Framework"
layout: hextra-home
---

{{< friday-hero >}}

## The Memento Problem

Every AI conversation starts from zero.

You explain your preferences. You provide context. You repeat background
information you shared last week. The AI responds intelligently — but it doesn't
*remember*. It doesn't *learn*. It doesn't *grow* with you over time.

This isn't just inconvenient. It's a fundamental barrier to AI reaching its
potential as a genuine cognitive partner.

> "Imagine waking up every morning with complete amnesia — unable to recall
> yesterday's work, last week's decisions, or the lessons learned from months
> of experience. That's the reality of stateless AI assistants."

Friday solves this at the architecture level.

---

## What Friday Gives You

{{< hextra/feature-grid cols="3" >}}

  {{< hextra/feature-card
    title="Persistent Multi-Tier Memory"
    subtitle="Episodic + Semantic + Associative. Hebbian learning ensures what matters rises to the top. Memories decay naturally — and reactivate on demand."
    link="/docs/memory/three-tier/"
  >}}

  {{< hextra/feature-card
    title="Provider-Agnostic LLM"
    subtitle="OpenAI, Anthropic, Ollama, OpenRouter. One config line to switch providers. Same agent code works with GPT-4, Claude, Llama 3, or Mistral."
    link="/docs/configuration/llm/"
  >}}

  {{< hextra/feature-card
    title="Protocol-First Design"
    subtitle="16 packages, each defined by abstract protocols. Swap ChromaDB for Pinecone, replace NetworkX with Neo4j, bring your own LLM client. Zero lock-in."
    link="/docs/concepts/protocols/"
  >}}

  {{< hextra/feature-card
    title="Multi-Agent Collaboration"
    subtitle="Shared memory plane. Provenance tracking. When one agent learns, all agents benefit. No handoff cost, no context duplication."
    link="/docs/multi-agent/architecture/"
  >}}

  {{< hextra/feature-card
    title="Production Observability"
    subtitle="Full conversation transcripts in SQLite. Structured JSON logging. OpenTelemetry hooks. Every tool call, token count, and latency recorded."
    link="/docs/advanced/deployment/"
  >}}

  {{< hextra/feature-card
    title="YAML-First Configuration"
    subtitle="Deterministic, auditable runtime behaviour. HIPAA/GDPR/SOC 2 deployment patterns. Compliance-ready by design."
    link="/docs/configuration/architecture/"
  >}}

{{< /hextra/feature-grid >}}

---

## Architecture at a Glance

```text
┌─────────────────────────────────────────────────────────────┐
│                     Intelligence Plane                       │
│                                                             │
│   MemoryController ◄──────────────► ContextAssembler        │
│         │                                   │               │
│         │  retrieves                        │  assembles    │
│         ▼                                   ▼               │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐    │
│  │ Vector Store│  │ Graph Store │  │  Episodic Store  │    │
│  │ (ChromaDB)  │  │ (NetworkX)  │  │    (SQLite)      │    │
│  │             │  │             │  │                  │    │
│  │  Semantic   │  │ Associative │  │  Conversation    │    │
│  │   search    │  │relationships│  │    history       │    │
│  └─────────────┘  └─────────────┘  └──────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │    Control Plane   │
                    │   CopilotAgent     │
                    │   Re-Act Loop      │
                    │   Tool Registry    │
                    └────────────────────┘
```

Each store implements a swappable abstract protocol. ChromaDB, NetworkX, and
SQLite are the defaults — replace any of them without changing agent code.

[→ Architecture overview](/docs/concepts/architecture/)

---

## Get Running in 5 Minutes

```python
import asyncio
from friday_agent import CopilotAgent
from friday_agent.config import AgentConfig

async def main():
    config = AgentConfig.from_yaml("config.yaml")
    agent  = CopilotAgent(config)

    # First session — agent stores context in memory
    response = await agent.chat("My name is Alex. I'm building a RAG pipeline.")
    print(response.content)

    # Later session — agent remembers without being told again
    response = await agent.chat("What was I building?")
    print(response.content)  # "You were building a RAG pipeline."

asyncio.run(main())
```

[Full quick-start guide →](/docs/getting-started/quick-start/)

---

## How Memory Works

Memories move through a lifecycle:

```text
EPISODIC ──► SHORT_TERM ──► LONG_TERM ──► DECAYED
                                             │
                 ◄───────────────────────────┘
              (reactivated on access — never truly lost)
```

**Decay formula:** `score(t) = score₀ × exp(−λ × hours_since_access)`

The `λ` decay rate is configurable per use case. Memories that are accessed
more often build stronger weights through Hebbian reinforcement and resist decay.

[→ Memory lifecycle deep dive](/docs/memory/lifecycle/)

---

## Real-World Use Cases

{{< hextra/feature-grid cols="3" >}}

  {{< hextra/feature-card
    title="Research Assistant"
    subtitle="Reads papers, extracts facts into the knowledge graph, and answers questions across sessions with provenance citations."
    link="/docs/use-cases/research-assistant/"
  >}}

  {{< hextra/feature-card
    title="Multi-Agent Code Pipeline"
    subtitle="Planner → coder → reviewer → tester agents sharing context. No copy-pasting code between agents. Shared memory handles it."
    link="/docs/use-cases/dev-assistant/"
  >}}

  {{< hextra/feature-card
    title="Compliance-Ready Enterprise"
    subtitle="HIPAA, GDPR, SOC 2. Sensitive data stays local via Ollama. Cloud LLMs for general reasoning. Full audit trail in SQLite."
    link="/docs/use-cases/compliance/"
  >}}

{{< /hextra/feature-grid >}}

---

{{< friday-cta >}}

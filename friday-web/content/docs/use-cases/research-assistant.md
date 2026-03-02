---
title: "Research Assistant"
description: "Build an agent that reads papers, extracts facts, and answers questions across sessions."
weight: 1
---

Build a persistent research assistant that ingests academic papers, extracts structured facts into the memory graph, and answers cross-session questions with citations.

## Overview

A Friday agent configured for deep research with long-term memory of sources, topics explored, and findings. The agent maintains context across weeks of research sessions, tracks which papers have been read, remembers insights from previous explorations, and builds a knowledge graph of research topics.

**Key Capabilities:**
- Web search and document ingestion
- Citation tracking and source management
- Topic clustering and relationship mapping
- Cross-session research continuity
- Automatic insight extraction and summarization

## Agent Configuration

Create `/agents/researcher.yaml`:

```yaml
name: researcher
role: "Research Assistant"
goal: "Conduct thorough research, track sources, and build comprehensive knowledge over time"

system_prompt: |
  You are a research assistant specializing in {{domain}}.

  Your task is to find accurate, relevant information and build a comprehensive
  knowledge base across multiple research sessions.

  Core Responsibilities:
  - Search for and analyze information from multiple sources
  - Always cite sources with URLs when available
  - Track which papers/articles you've already reviewed
  - Distinguish between facts, expert opinions, and speculation
  - Acknowledge uncertainty when information is incomplete or conflicting
  - Build connections between related research topics
  - Summarize findings in clear, structured formats
  - Remember prior research to avoid duplication

  Current research focus: {{focus}}

  When you encounter a topic you've researched before, reference your prior findings
  and explain what's new or different in the current exploration.

tools:
  - web_search
  - scrape_page
  - read_file
  - write_file
  - http_request
  - parse_json

tool_autonomy: auto

model: "gpt-4o"
temperature: 0.3   # Lower temperature for factual accuracy
max_tokens: 4096

memory_config:
  mode: full
  enable_graph: true    # Graph tracks: Papers, Authors, Topics, Concepts
  enable_vector: true   # Vector stores: Insights, summaries, source excerpts
  max_episodic_turns: 50

  priming:
    enabled: true
    top_entities: 30   # Load many entities (papers, topics)
    max_insights: 40   # Rich prior research context
    recency_days: 90   # 3 months of research history

  lifecycle:
    decay_rate: 0.005  # Slow decay — research stays relevant
    promotion_threshold: 0.65
```

## Memory Configuration

Create `config.yaml` with research-optimized settings:

```yaml
llm:
  model: "gpt-4o"
  temperature: 0.3
  max_retries: 3
  timeout_seconds: 120   # Longer timeout for research tasks

extraction:
  model: "gpt-4o-mini"   # Cheaper model for extraction
  temperature: 0.0

  # Custom entity types for research
  entities:
    allowed_types:
      - paper
      - author
      - topic
      - concept
      - organization

  # Research-specific relationship verbs
  relationships:
    allowed_verbs:
      - AUTHORED
      - CITES
      - DISCUSSES
      - APPLIES
      - PUBLISHED_BY
      - EXTENDS

memory:
  collection_name: "research_assistant"
  persist_directory: "./memory/research"

  # Large context window for research
  context_window: 32000
  output_buffer: 2000
  max_history_turns: 30

  # Rich priming for research continuity
  priming:
    enabled: true
    top_entities: 30
    max_insights: 40
    max_summaries: 20
    recency_days: 90
    token_budget: 8000

  context_format: markdown

lifecycle:
  enabled: true
  decay_rate: 0.005      # Slow decay
  access_boost: 0.3      # Strong boost on access
  promotion_threshold: 0.65
  decay_threshold: 0.4
  short_term_min_age_hours: 48  # Require 2 days before promotion
  decayed_retention_days: 60    # Keep decayed research longer
```

## Sample Interaction

The following shows how cross-session memory works in practice.

**Session 1 — Initial Research:**

```text
User: "Find recent papers on transformer architecture improvements since 2023"

Friday: I'll search for recent transformer architecture papers.

[Tool: web_search("transformer architecture improvements 2023 2024")]
[Tool: scrape_page(url_1), scrape_page(url_2), scrape_page(url_3)]

I found 3 significant papers:

1. "Flash Attention 2: Faster Attention with Better Parallelism" (2023)
   - Authors: Dao et al., Stanford
   - Key innovation: Reduces attention computation from O(n²) to O(n log n)
   - URL: https://arxiv.org/abs/2307.08691
   - Finding: 2-4x speedup on A100 GPUs

2. "GQA: Training Generalized Multi-Query Transformer Models" (2023)
   - Authors: Ainslie et al., Google Research
   - Key innovation: Grouped-query attention for inference efficiency
   - Finding: Matches multi-head quality with 10x faster inference

3. "RoFormer: Enhanced Transformer with Rotary Position Embedding" (2023)
   - Key innovation: Rotary position embeddings (RoPE)
   - Finding: Better length extrapolation than absolute position encodings

[Memory stored: 3 papers, 8 authors, 5 concepts, 12 relationships]
```

**Session 2 — One Week Later:**

```text
User: "What were those attention optimization papers you found last week?"

Friday: From my prior research, I found three papers on transformer optimization:

1. Flash Attention 2 (Dao et al., 2023) - O(n log n) attention computation
2. GQA (Google, 2023) - Grouped-query attention for fast inference
3. RoFormer (ZhuiyiAI, 2023) - Rotary position embeddings

[Context: Retrieved from episodic memory - Session from 2026-01-17]

I also noted connections between these works:
- Flash Attention 2 and GQA both focus on inference optimization
- RoPE (from RoFormer) is now used in Llama 2 and other models
- Flash Attention technique applies to GQA's grouped queries
```

**Session 3 — Citation Traversal:**

```text
User: "Find papers that cite Flash Attention 2"

Friday: [Tool: web_search("cite:2307.08691 transformer attention optimization")]

I found 2 significant follow-up papers:

1. "Ring Attention with Blockwise Transformers" (2024) — UC Berkeley
   - Extends Flash Attention to distributed settings for million-token contexts

2. "PagedAttention: Efficient Memory Management for LLM Serving" (2023)
   - Builds on Flash Attention's memory efficiency concepts
   - Used in: vLLM serving framework

[Memory updated: Added 2 new papers, created CITES relationships]

Citation graph:
- Flash Attention 2 → Ring Attention (extends to distributed)
- Flash Attention 2 → PagedAttention (memory management)
```

## Memory Graph After Three Sessions

```text
Papers (5):
  flash_attention_2    (hit_count: 3, connections: 4)
  gqa_google           (hit_count: 2, connections: 2)
  roformer             (hit_count: 2, connections: 3)
  ring_attention       (hit_count: 1, connections: 2)
  paged_attention      (hit_count: 1, connections: 2)

Topics (7):
  attention_optimization   (hit_count: 4, connections: 5)
  position_embeddings      (hit_count: 2, connections: 3)
  distributed_training     (hit_count: 1, connections: 2)

Organizations (3):
  stanford_university  (hit_count: 2)
  uc_berkeley          (hit_count: 3)
  google_research      (hit_count: 1)

Key Relationships:
  dao_tri -> AUTHORED -> flash_attention_2
  ring_attention -> CITES -> flash_attention_2
  ring_attention -> EXTENDS -> flash_attention_2
  uc_berkeley -> PRODUCED -> ring_attention
```

## Key Benefits

1. **Cross-Session Continuity**: Friday remembers all prior research, avoiding duplicate searches
2. **Citation Tracking**: Automatic relationship mapping between papers
3. **Knowledge Accumulation**: Research graph grows over time, revealing connections
4. **Efficient Re-access**: Prior papers are immediately accessible by reference
5. **Research Lineage**: Track how papers build on each other

## Cost Optimization

- Use GPT-4o for research queries (quality matters)
- Use GPT-4o-mini for extraction (90% cost savings)
- Local embeddings for vector storage (zero API cost)
- Workflow approval gates prevent unnecessary LLM calls

## Related Pages

- [Code Development Assistant](/docs/use-cases/dev-assistant/) — Multi-agent code review pipeline
- [Memory Settings](/docs/configuration/memory/) — Tune decay and priming for research workloads
- [Hybrid Cloud-Local](/docs/advanced/hybrid/) — Run extraction locally to cut costs

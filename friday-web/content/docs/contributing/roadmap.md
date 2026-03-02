---
title: "Roadmap"
description: "Planned features, milestones, and the path to Friday v1.0."
weight: 3
---

Planned features, active milestones, and the full path from the current v0.1.0 alpha to the Friday v1.0 stable release.

## Current Status: v0.1.0

Released January 2026. Early alpha — core systems are stable; orchestration and workflows are newly implemented. Suitable for prototypes and internal tools.

**What ships in v0.1.0:**
- Three-tier memory architecture (episodic, semantic, associative)
- Memory lifecycle management (promotion, decay, reactivation)
- CopilotAgent with Re-Act loop (max 10 iterations)
- 50+ built-in tools (filesystem, shell, web, git, data, text, code)
- Multi-agent orchestration with shared memory
- Dynamic workflow engine with YAML definitions
- Provider-agnostic LLM client (OpenAI, Anthropic, Google, Ollama)
- Transcript system with SQLite storage and export
- Interactive CLI (`memory-chat-v2.py`)
- Comprehensive documentation (user guide, specs)

**Repository status:** Private alpha. Will become public at v0.2.0, estimated Q2 2026.

---

## Phase 5: Autonomy and Scale (Q1-Q2 2026)

**Goal:** Enable autonomous agent operation and distributed deployment.

### 5.1 Autonomous Agent

- Event-driven agent architecture (schedule-based and trigger-based)
- Goal-oriented planning and task decomposition
- Confidence-based tool execution (high confidence = autonomous, low = request approval)
- Checkpoint and rollback for error recovery
- Human oversight patterns — notification gates and approval gates

### 5.2 Docker-Based Sandboxing

- Isolated code execution in Docker containers
- Resource limits (CPU, memory, disk, network)
- Security boundaries for untrusted code
- Streaming output from sandboxed execution
- Multi-language support (Python, JavaScript, Shell)

### 5.3 Advanced Workflow Patterns

- Conditional execution (if/else logic in workflow YAML)
- Loops and iteration (process lists, retry-until-success)
- Error handling strategies (continue-on-error, fallback tasks)
- Dynamic task generation (workflows that modify themselves at runtime)
- Workflow composition (nested workflows)

### 5.4 Distributed Deployment

- Agent swarm coordination across multiple machines
- Distributed memory stores (shared Redis/PostgreSQL)
- Load balancing for agent requests
- Health monitoring and automatic failover
- Kubernetes manifests and Helm charts

**Priority:** HIGH — critical for production deployments

---

## Phase 6: Intelligence Enhancement (Q2-Q3 2026)

**Goal:** Self-improving agents through meta-learning and automated optimization.

### 6.1 Self-Improving Agents

- Automated prompt optimization based on conversation outcomes
- A/B testing for different system prompt variants
- Reinforcement learning from human feedback (RLHF integration)
- Automatic adjustment of temperature based on task type
- Performance tracking (latency, quality, cost) with feedback loop

### 6.2 Meta-Learning from Memory Patterns

- Analyze lifecycle patterns to improve extraction prompts
- Identify what makes memories valuable (high promotion rate, frequent reactivation)
- Learn optimal decay rates per entity type
- Automatic graph pruning strategies derived from usage patterns

### 6.3 Cross-Agent Knowledge Transfer

- Senior agents teaching junior agents through shared memory observation
- Pattern recognition across provenance metadata
- Skill transfer (agent A's effective tool usage informs agent B)
- Knowledge distillation — compress experienced agent patterns for onboarding new agents

### 6.4 Adaptive Context Engineering

- Learn optimal token budgets per use case (research vs. chat vs. coding)
- Dynamic similarity thresholds based on retrieval effectiveness
- Personalized memory priming per user
- Query-aware tool selection (learn which tools are actually used for which queries)

**Priority:** MEDIUM — enhances capabilities, not blocking for production

---

## Phase 7: Ecosystem Integration (Q3-Q4 2026)

**Goal:** Integrate Friday with the broader AI and enterprise ecosystems.

### 7.1 Comprehensive MCP Implementation

- Full MCP server (expose Friday memory and tools as MCP resources)
- MCP client enhancements (support more MCP server types)
- Bi-directional integration (Friday as both MCP client and server)
- MCP transport improvements (WebSocket, gRPC in addition to SSE)
- MCP resource discovery and dynamic loading

### 7.2 Pre-Built Agent Templates

- Research Assistant (web search, document analysis, citation tracking)
- Code Reviewer (git integration, linting, security scanning)
- Project Manager (task tracking, dependency management, status reports)
- Customer Support (CRM integration, knowledge base search, ticket creation)
- DevOps Agent (infrastructure monitoring, incident response, deployment)
- Legal Research (case law search, citation extraction, precedent analysis)

### 7.3 Enterprise Integrations

- Slack — conversational agents in Slack channels
- Microsoft Teams — Teams bot with memory
- ServiceNow — ticket automation and knowledge base
- Jira/Confluence — project tracking and documentation
- GitHub — PR review, issue triage, code search
- Salesforce — CRM data access and lead qualification

### 7.4 Fine-Tuning Pipelines

- Export Friday conversations as training data (JSONL for fine-tuning)
- Evaluate fine-tuned models within Friday (A/B test vs. base model)
- Automatic dataset curation (select high-quality conversations)
- Privacy-preserving fine-tuning (on-premises training pipelines)
- Model distillation — create smaller models from Friday interaction patterns

**Priority:** MEDIUM — expands reach, not core functionality

---

## Phase 8: Production Hardening (Q4 2026 - Q1 2027)

**Goal:** Enterprise-grade reliability, security, and observability.

### 8.1 Comprehensive Monitoring

- Metrics dashboard (Grafana/Prometheus integration)
- Real-time memory health monitoring (growth rates, fragmentation)
- LLM call analytics (latency, cost, error rates by model)
- Tool execution tracking (success rates, performance by tool)
- Per-agent performance profiling and bottleneck identification

### 8.2 Advanced Security

- Role-based access control (RBAC) for memory namespaces
- API key rotation and secret management (Vault integration)
- Audit logging for GDPR/HIPAA compliance
- Data encryption at rest and in transit
- Input sanitization and output filtering (prevent injection attacks)
- Enhanced tool execution sandboxing

### 8.3 Distributed Tracing

- OpenTelemetry integration with full request tracing
- Distributed context propagation across agents and stores
- Performance profiling to identify slow operations
- Cost attribution per user and session
- Error tracking and alerting (Sentry/Rollbar integration)

### 8.4 High Availability

- Horizontal pod autoscaling based on load
- Database replication for multi-region memory stores
- Automatic failover with health checks
- Rate limiting and backpressure to prevent overload
- Circuit breakers for all external services

**Priority:** HIGH for v1.0 — required for enterprise production deployments

---

## Version 1.0 Goals (Q1 2027)

Friday v1.0 is the first production-ready release suitable for enterprise deployment.

**v1.0 success criteria:**

**Stability**
- No critical bugs in a 90-day release candidate period
- Test coverage >85% across all packages
- All core APIs stable — no breaking changes without major version bump

**Performance**
- Context assembly <200ms (95th percentile)
- Memory lifecycle operations <5s for 10K memories
- Support 100K+ memories per instance

**Scalability**
- Horizontal scaling tested to 100 concurrent agents
- Distributed memory stores with replication
- Load balancing and automatic failover in production

**Observability**
- Complete distributed tracing (OpenTelemetry)
- Real-time metrics dashboard
- Comprehensive audit logging

**Security**
- RBAC implementation
- Encryption at rest and in transit
- Security audit completed by third-party

**Documentation**
- Complete user guide (all sections)
- Full API reference
- Deployment guides (Docker, Kubernetes, serverless)
- Case studies and tutorials

**Community**
- Public GitHub repository (open-source)
- Active Discord or Slack community
- Contribution guidelines and governance model

**Post-1.0 vision:** Community-driven feature development, plugin marketplace (custom tools, stores, and agents), enterprise support offerings, conference talks, and research publications.

---

## Influence the Roadmap

The roadmap is community-driven. Your input shapes Friday's evolution.

**Ways to contribute:**

1. **GitHub Issues** — File feature requests with clear use cases; upvote issues you care about
2. **GitHub Discussions** — Propose architectural changes and discuss tradeoffs
3. **Pull Requests** — Implement features you need and demonstrate their value
4. **Community Calls** — Monthly calls starting Q2 2026; demo projects and discuss priorities
5. **Sponsorship** — Fund specific features through the enterprise sponsorship program

**Feature request template:**

```markdown
## Feature

[Clear, concise title]

## Use Case

Describe the problem you're solving. Who is affected? Why does it matter?

## Proposed Solution

How would you like this to work? Include examples.

## Alternatives Considered

What other approaches could solve this?

## Additional Context

- Impact on your work: Low / Medium / High
- Willing to contribute: Yes / Maybe / No
- Related issues: [links]
```

**Prioritization criteria:**
1. Impact — how many users benefit?
2. Feasibility — how difficult to implement?
3. Alignment — does it fit Friday's vision and principles?
4. Community demand — upvotes and request frequency
5. Maintainability — can we support it long-term?

## Related Pages

- [Development Setup](/docs/contributing/setup/) — Get your environment ready to contribute
- [Architecture Decisions](/docs/contributing/adrs/) — Why Friday is designed the way it is
- [Deployment Patterns](/docs/advanced/deployment/) — Docker, Kubernetes, serverless

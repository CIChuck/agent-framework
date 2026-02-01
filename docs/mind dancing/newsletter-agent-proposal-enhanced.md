# Newsletter Agent Proposal - Enhanced Plan

## Objective
Build a production-ready Newsletter Agent as a visible differentiator, internal proof point, and client-facing demonstration of Friday's capabilities.

## Core Workflow (Multi-Agent System)

### 1. Research Agent
- Performs web search using SERP API (Google Custom Search for MVP)
- Applies selection criteria (relevance, source credibility, recency, non-duplication)
- Maintains exclusion list (sources, topics, competitors) in shared memory
- Presents 3-5 article options to human for approval

### 2. Writer Agent
- Drafts newsletter content in Markdown using template
- Synthesizes insights from selected articles
- Uses shared memory/knowledge graph for context
- Tags sources and maintains reference list
- Flags potential blocking questions for human input

### 3. Editor Agent
- Performs quality check on draft (brand voice, clarity, technical accuracy, compliance)
- Checks for hallucinations, factual errors, tone issues
- Returns to Writer Agent for revisions if needed
- Maintains style guide in knowledge graph
- Validates against compliance requirements (SOC 2, healthcare privacy)

### 4. Human-in-the-Loop
- Approves topic selection
- Selects final articles
- Answers blocking questions
- Approves final draft
- Authorizes send
- Provides feedback loop to improve agent performance

## Technical Requirements

### Critical Gaps to Address:
- SERP API integration (Google Custom Search for MVP → SerpAPI for scale)
- Shared file system workspace for agent artifact exchange
- Notification mechanism for human intervention (email/slack)
- Async workflow orchestration
- Version control for drafts (track changes across iterations)
- Error handling and retry logic for failed web requests

### Output Formats:
- Primary: Markdown (editable format)
- Secondary: PDF conversion (distribution format)
- HTML output (web publishing option)

### Execution Modes:
- Scheduled (autonomous periodic review)
- On-demand (ad-hoc generation)
- Hybrid mode (scheduled initiation with human approval points)

### Knowledge Graph Enhancements:
- Track topics, selected articles, draft versions, editorial feedback
- Maintain exclusion lists (sources, topics, competitors)
- Store style guide, brand voice parameters
- Capture human feedback for continuous improvement

## Business Value
- Internal proof point for Friday's capabilities
- Visible differentiator in market
- Low-risk deployment
- Recruiting signal
- Demonstrates thought leadership
- Client co-branding opportunity (SunStone partnership)
- Foundation for client-specific newsletters

## Immediate Next Steps
1. Audit existing Friday codebase
2. Define success metrics (quality, speed, accuracy, human intervention rate)
3. Create test plan (unit, integration, end-to-end)
4. Document dependencies
5. Implement MVP with file-based workflow
6. Establish feedback collection mechanism
7. Define versioning strategy for drafts

## Project Phases
- **Phase 1 (MVP):** File-based workflow - read config, retrieve content, synthesize, write draft file
- **Phase 2:** CMS integration (WordPress, HubSpot)
- **Phase 3:** Client portal for co-branded newsletters

## Risk Mitigation
- Start with internal-only distribution
- Human approval required at all critical points
- Maintain audit trail of all decisions
- Implement content review checklist

## Strategic Positioning
Showcases Friday's memory, learning, and flexibility without exposing underlying mechanisms to buyers. Demonstrates "We built Friday for our team, we can customize Friday for you."
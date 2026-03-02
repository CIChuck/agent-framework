---
title: "Example Workflows"
description: "Annotated real-world workflow definitions for common automation scenarios."
weight: 3
---

Annotated, real-world Friday workflow definitions covering common automation scenarios such as data pipelines, code review flows, and document processing.

## Newsletter Generation Workflow

The newsletter generation workflow demonstrates multi-agent collaboration with research, writing, and approval gates.

**Workflow File:** `workflows/newsletter.yaml`

**Complete Definition:**

```yaml
# Newsletter Generation Workflow
# Researches a topic and generates a newsletter article

id: newsletter_generation
name: "Newsletter Generation"
description: "Research a topic and generate a newsletter article with human review"
version: "1.0.0"
author: "friday-team"
tags: ["content", "research", "writing"]

tasks:
  - id: research
    name: "Research Topic"
    description: |
      Research the given topic and gather key information.
      Focus on:
      - Recent developments
      - Key statistics
      - Expert opinions
      - Relevant examples

      Provide a comprehensive research summary.
    agent: researcher
    inputs:
      topic: "$user_topic"
    outputs:
      - research_results
    requires_approval: false

  - id: review_research
    name: "Review Research Results"
    description: |
      Review the research results for accuracy and completeness.

      Research to review:
      {{research}}

      Provide feedback or approve to continue.
    agent: researcher
    inputs:
      research: "$research_results"
    outputs:
      - approved_research
    depends_on:
      - research
    requires_approval: true

  - id: write_draft
    name: "Write Newsletter Draft"
    description: |
      Write a newsletter article based on the approved research.

      Guidelines:
      - Engaging headline
      - Clear introduction
      - Key points with supporting details
      - Call to action
      - 500-800 words
    agent: coder
    inputs:
      research: "$approved_research"
    outputs:
      - newsletter_draft
    depends_on:
      - review_research
    requires_approval: false

  - id: final_review
    name: "Final Newsletter Review"
    description: |
      Review the final newsletter draft.

      Check for:
      - Accuracy
      - Clarity
      - Tone
      - Grammar

      Approve to publish or provide feedback.
    agent: coder
    inputs:
      draft: "$newsletter_draft"
    outputs:
      - final_newsletter
    depends_on:
      - write_draft
    requires_approval: true

timeout_seconds: 7200
max_retries: 2
```

**Execution Example:**

```bash
Friday> /workflow run newsletter user_topic="Quantum Computing Breakthroughs 2025"

Starting workflow: Newsletter Generation

Task: research (Research Topic)
   Researching "Quantum Computing Breakthroughs 2025"...
   Using web_search to find recent articles
   Found 12 relevant sources
   Summarizing key findings...
Completed in 48.3s

Task: review_research (Review Research Results)
   Approval Required

Research Summary (3,850 words):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Quantum Computing Breakthroughs in 2025

Key Developments:
1. IBM's 1000-qubit quantum processor (March 2025)
2. Google's error correction milestone (June 2025)
3. Commercial applications in drug discovery
...
[Full research content displayed]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/workflow approve - Continue    /workflow skip - Skip

Friday> /workflow approve

Task approved, continuing...

Task: write_draft (Write Newsletter Draft)
   Drafting newsletter article...
   Word count: 687
   Tone: Professional, accessible
Completed in 42.1s

Task: final_review (Final Newsletter Review)
   Approval Required

Newsletter Draft:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"Quantum Leap: 2025's Computing Revolution"

The quantum computing landscape transformed dramatically in 2025,
with three major breakthroughs marking a turning point from
laboratory curiosity to practical technology...

[Full newsletter displayed]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/workflow approve - Publish    /workflow skip - Discard

Friday> /workflow approve

Task approved
Workflow completed successfully

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Newsletter Generation - COMPLETED
Duration: 2m 35s
Tasks: 4/4 completed

Output: $final_newsletter
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Use Cases:**

- Content marketing teams generating weekly newsletters
- Internal communications creating company updates
- Educational institutions producing research summaries
- Media organizations drafting news articles

**Customization Options:**

```yaml
# Variation: Skip human review for internal drafts
- id: review_research
  requires_approval: false  # Auto-approve for internal use

# Variation: Add SEO optimization task
- id: optimize_seo
  name: "Optimize for SEO"
  description: "Add meta description, keywords, and optimize headings"
  agent: seo_specialist
  depends_on: [write_draft]
  inputs:
    draft: "$newsletter_draft"
  outputs:
    - optimized_draft

# Variation: Add fact-checking task
- id: fact_check
  name: "Verify Facts"
  description: "Cross-reference all claims with sources"
  agent: fact_checker
  depends_on: [write_draft]
  inputs:
    draft: "$newsletter_draft"
    sources: "$research_results"
  outputs:
    - verified_draft
```

---

## Code Review Workflow

Automated code review workflow with static analysis, testing, and security scanning.

**Complete Definition:**

```yaml
id: code_review
name: "Automated Code Review"
description: "Review code changes with static analysis, tests, and security checks"
version: "1.0.0"
author: "friday-team"
tags: ["code", "review", "testing", "security"]

tasks:
  - id: analyze_code
    name: "Static Code Analysis"
    description: |
      Run static analysis on the codebase.

      Checks:
      - Code style violations (Ruff, ESLint)
      - Type errors (mypy)
      - Complexity metrics
      - Code smells

      Provide summary of issues found.
    agent: coder
    inputs:
      repo_path: "$repository_path"
      files_changed: "$changed_files"
    outputs:
      - analysis_report
    requires_approval: false

  - id: run_tests
    name: "Run Test Suite"
    description: |
      Execute the full test suite.

      Report:
      - Pass/fail status
      - Coverage metrics
      - Failed test details
      - Performance regressions
    agent: coder
    inputs:
      repo_path: "$repository_path"
    outputs:
      - test_results
    requires_approval: false

  - id: security_scan
    name: "Security Vulnerability Scan"
    description: |
      Scan for security vulnerabilities.

      Tools:
      - Bandit (Python)
      - npm audit (JavaScript)
      - Dependency vulnerability checks

      Flag high-severity issues.
    agent: security_specialist
    inputs:
      repo_path: "$repository_path"
    outputs:
      - security_report
    requires_approval: false

  - id: review_gate
    name: "Review Results"
    description: |
      Review all analysis results:

      Static Analysis: {{analysis}}
      Test Results: {{tests}}
      Security Scan: {{security}}

      Approve if all checks pass or issues are acceptable.
      Skip to reject changes.
    agent: coder
    depends_on:
      - analyze_code
      - run_tests
      - security_scan
    inputs:
      analysis: "$analysis_report"
      tests: "$test_results"
      security: "$security_report"
    outputs:
      - review_decision
    requires_approval: true

  - id: merge_changes
    name: "Merge to Main Branch"
    description: |
      Merge approved changes to main branch.

      Executes: git merge --no-ff {branch}
    agent: coder
    depends_on:
      - review_gate
    inputs:
      branch: "$source_branch"
    outputs:
      - merge_result
    requires_approval: false

timeout_seconds: 1800  # 30 minutes
max_retries: 1
```

**Execution Example:**

```bash
Friday> /workflow run code_review repository_path="/project" changed_files="src/main.py,tests/test_main.py" source_branch="feature/auth"

Starting workflow: Automated Code Review

Task: analyze_code (Static Code Analysis)
   Running Ruff on 2 changed files...
   No style violations found
   Running mypy...
   3 type warnings in src/main.py
Completed in 8.4s

Task: run_tests (Run Test Suite)
   Running pytest...
   127 tests passed
   Coverage: 92.3% (+1.2%)
Completed in 23.7s

Task: security_scan (Security Vulnerability Scan)
   Running Bandit...
   No high-severity issues
   1 medium-severity warning (hardcoded secret detection)
Completed in 12.1s

Task: review_gate (Review Results)
   Approval Required

Code Review Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Static Analysis: 3 type warnings
  - Line 45: Argument type mismatch
  - Line 67: Missing return type annotation
  - Line 89: Unreachable code detected

Tests: All passed (127/127)
Coverage: 92.3%

Security: 1 medium-severity issue
  - B105: Possible hardcoded password in config.py:23

Recommendation: Review type warnings and security issue before merging
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/workflow approve - Merge anyway    /workflow skip - Reject

Friday> /workflow skip

Task skipped - changes not approved
Workflow completed

Code review failed - changes not merged
Review the flagged issues and resubmit
```

**Use Cases:**

- Pull request validation in CI/CD pipelines
- Pre-commit hooks with comprehensive checks
- Scheduled code quality audits
- Security compliance scanning

**Diamond Dependency Pattern:**

The code review workflow demonstrates a diamond dependency — `review_gate` waits for three parallel tasks before it can run:

```
analyze_code ──┐
run_tests    ──┤──► review_gate ──► merge_changes
security_scan ─┘
```

This is valid because `review_gate` lists all three as dependencies. When parallel execution is added to the workflow engine, these three tasks will run concurrently, reducing total review time.

---

## Research and Report Workflow

Comprehensive research workflow with multi-source data gathering, synthesis, and report generation.

**Complete Definition:**

```yaml
id: research_report
name: "Research & Report Generation"
description: "Conduct multi-source research and generate a comprehensive report"
version: "1.0.0"
author: "friday-team"
tags: ["research", "analysis", "reporting"]

tasks:
  - id: web_research
    name: "Web Research"
    description: |
      Search the web for information on the topic.
      Use multiple search queries to cover different angles.
      Save relevant URLs and key excerpts.
    agent: researcher
    inputs:
      topic: "$user_topic"
      depth: "$research_depth"  # "quick", "standard", "deep"
    outputs:
      - web_sources
    max_retries: 3

  - id: academic_search
    name: "Academic Literature Search"
    description: |
      Search academic databases for peer-reviewed research.
      Focus on recent publications (last 5 years).
      Prioritize highly-cited papers.
    agent: researcher
    inputs:
      topic: "$user_topic"
    outputs:
      - academic_sources
    requires_approval: false

  - id: scrape_sources
    name: "Scrape and Extract Content"
    description: |
      Scrape content from discovered URLs.
      Extract main text, remove ads and navigation.
      Store full-text versions for analysis.
    agent: researcher
    depends_on:
      - web_research
    inputs:
      urls: "$web_sources"
    outputs:
      - scraped_content
    max_retries: 2

  - id: synthesize
    name: "Synthesize Findings"
    description: |
      Synthesize information from all sources.

      Create:
      - Executive summary
      - Key findings (bullet points)
      - Supporting evidence
      - Conflicting viewpoints
      - Research gaps
    agent: analyst
    depends_on:
      - web_research
      - academic_search
      - scrape_sources
    inputs:
      web: "$web_sources"
      academic: "$academic_sources"
      content: "$scraped_content"
    outputs:
      - synthesis
    timeout_seconds: 600  # 10 minutes for synthesis

  - id: generate_report
    name: "Generate Final Report"
    description: |
      Generate a comprehensive report in markdown format.

      Structure:
      1. Executive Summary
      2. Introduction
      3. Methodology
      4. Findings
      5. Analysis
      6. Conclusions
      7. References

      Include charts and visualizations where appropriate.
    agent: writer
    depends_on:
      - synthesize
    inputs:
      synthesis: "$synthesis"
      format: "$output_format"  # "markdown", "pdf", "html"
    outputs:
      - final_report
    requires_approval: false

  - id: save_report
    name: "Save Report to File"
    description: |
      Save the generated report to the filesystem.
      Create necessary directories.
    agent: coder
    depends_on:
      - generate_report
    inputs:
      report: "$final_report"
      output_path: "$save_path"
    outputs:
      - saved_file_path
    requires_approval: false

timeout_seconds: 3600  # 1 hour
max_retries: 2
```

**Execution Example:**

```bash
Friday> /workflow run research_report user_topic="Impact of AI on Healthcare" research_depth="deep" output_format="markdown" save_path="/reports/ai-healthcare-2025.md"

Starting workflow: Research & Report Generation

Task: web_research (Web Research)
   Searching web sources...
   Found 47 relevant articles
   Extracting key information...
Completed in 52.3s

Task: academic_search (Academic Literature Search)
   Searching PubMed, arXiv, Google Scholar...
   Found 23 peer-reviewed papers
   Prioritizing by citation count...
Completed in 38.7s

Task: scrape_sources (Scrape and Extract Content)
   Scraping 47 URLs...
   Extracted full text from 42 sources (5 failed)
   Total content: 182,500 words
Completed in 67.2s

Task: synthesize (Synthesize Findings)
   Analyzing 42 web sources + 23 academic papers...
   Generating synthesis...
   Cross-referencing findings...
   Identifying consensus and conflicts...
Completed in 145.8s

Task: generate_report (Generate Final Report)
   Writing comprehensive report...
   Adding visualizations...
   Formatting references...
   Final length: 8,750 words
Completed in 89.3s

Task: save_report (Save Report to File)
   Saving to /reports/ai-healthcare-2025.md...
   File saved successfully
Completed in 1.2s

Workflow completed successfully

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Research & Report Generation - COMPLETED
Duration: 6m 34s
Tasks: 6/6 completed

Output: /reports/ai-healthcare-2025.md (8,750 words)
Sources: 42 web + 23 academic
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Use Cases:**

- Market research and competitive analysis
- Academic literature reviews
- Due diligence investigations
- Policy research and briefings

**Future Enhancement — Parallel Research:**

```yaml
# Future enhancement: Parallel execution
tasks:
  - id: web_research
    # No dependencies - can run in parallel

  - id: academic_search
    # No dependencies - can run in parallel

  - id: expert_interviews
    # No dependencies - can run in parallel

  - id: synthesize
    depends_on:
      - web_research
      - academic_search
      - expert_interviews
    # Waits for all parallel tasks to complete
```

When parallel execution is implemented, independent research tasks will run concurrently, reducing total workflow time from 6+ minutes to under 3 minutes.

---

## Related Pages

- [Workflow Engine](/docs/workflows/engine/) — How Friday parses, validates, and executes YAML workflow definitions
- [YAML Schema Reference](/docs/workflows/yaml-reference/) — Complete field documentation
- [Workflow Commands](/docs/cli/workflows/) — CLI commands for running and managing workflows

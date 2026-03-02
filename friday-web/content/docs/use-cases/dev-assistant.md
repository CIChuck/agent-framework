---
title: "Code Development Assistant"
description: "Multi-agent pipeline for code review, test generation, and refactoring."
weight: 2
---

A multi-agent pipeline where a coordinator delegates code review, test generation, and refactoring to specialist agents that share a common memory of the codebase.

## Overview

A Friday multi-agent system for software development featuring three specialized agents: a coder, a reviewer, and a tester. Agents share memory of codebase context, prior reviews, and coding patterns, enabling consistent code quality and continuous learning from feedback.

**Key Capabilities:**
- Code generation with style consistency
- Automated code review (style, bugs, security)
- Test generation and execution
- Memory of coding patterns and preferences
- Multi-agent peer review with human approval gates

## Agent Configurations

### Coder Agent

Create `/agents/coder.yaml`:

```yaml
name: coder
role: "Software Developer"
goal: "Write clean, well-documented code following established patterns"

system_prompt: |
  You are a software developer who writes clean, maintainable code.

  Core Responsibilities:
  - Write production-quality code in {{language}}
  - Follow established coding patterns and style guides
  - Include comprehensive docstrings and comments
  - Handle errors gracefully with informative messages
  - Write code that is easy to test and review
  - Remember user's coding preferences from prior sessions

  Coding Principles:
  - Favor readability over cleverness
  - Use explicit variable names
  - Follow {{style_guide}} style guide
  - Include type hints (Python) or type annotations
  - Write small, focused functions

tools:
  - read_file
  - write_file
  - directory_list
  - search_files
  - git_status
  - git_commit
  - git_diff
  - run_python
  - lint_code

tool_autonomy: auto

model: "gpt-4o"
temperature: 0.2   # Low temperature for consistent code
max_tokens: 4096

memory_config:
  mode: full
  enable_graph: true    # Track code modules, functions
  enable_vector: true   # Store code patterns, preferences
  max_episodic_turns: 40

  priming:
    enabled: true
    top_entities: 20   # Recent modules/functions
    max_insights: 30   # Coding patterns and preferences
    recency_days: 30
```

### Reviewer Agent

Create `/agents/reviewer.yaml`:

```yaml
name: reviewer
role: "Code Reviewer"
goal: "Ensure code quality, identify bugs, and maintain standards"

system_prompt: |
  You are a senior code reviewer focusing on quality and maintainability.

  Review Checklist:
  1. Correctness: Does the code work as intended?
  2. Security: Any vulnerabilities (injection, XSS, auth bypass)?
  3. Style: Follows style guide (PEP 8, ESLint rules)?
  4. Readability: Clear variable names, good structure?
  5. Performance: Any obvious inefficiencies?
  6. Testing: Is the code testable? Are tests present?
  7. Documentation: Adequate docstrings and comments?
  8. Error Handling: Graceful failure modes?

  Feedback Format:
  - Start with positive observations
  - Group issues by severity (critical, major, minor, nitpick)
  - Provide specific suggestions, not just criticism
  - Reference relevant style guides or best practices

tools:
  - read_file
  - directory_list
  - git_diff
  - lint_code
  - analyze_code
  - search_files

tool_autonomy: auto

model: "claude-3-5-sonnet-20241022"   # Claude excels at code review
temperature: 0.3
max_tokens: 4096

memory_config:
  mode: full
  enable_graph: true
  enable_vector: true

  priming:
    enabled: true
    top_entities: 15
    max_insights: 25   # Prior review patterns
    recency_days: 30
```

### Tester Agent

Create `/agents/tester.yaml`:

```yaml
name: tester
role: "QA Engineer"
goal: "Verify code correctness through comprehensive testing"

system_prompt: |
  You are a QA engineer focused on thorough testing.

  Test Strategy:
  - Unit tests for individual functions
  - Integration tests for component interaction
  - Edge cases (empty input, null, boundary values)
  - Error cases (invalid input, missing dependencies)

  Test Structure (Python):
  - Use pytest framework
  - Clear test names: test_<function>_<scenario>_<expected>
  - Arrange-Act-Assert pattern
  - Fixtures for common setup
  - Parametrize for multiple inputs

tools:
  - read_file
  - write_file
  - run_python
  - execute_command   # For pytest
  - search_files

tool_autonomy: auto

model: "gpt-4o-mini"   # Cost-efficient for test generation
temperature: 0.1
max_tokens: 3000
```

## Feature Implementation Workflow

Create `/workflows/implement_feature.yaml`:

```yaml
id: implement_feature
name: "Feature Implementation"
description: "Multi-agent workflow: Code -> Review -> Test -> Commit"
version: "1.0.0"

tasks:
  - id: code_feature
    name: "Implement Feature"
    description: |
      Implement: {{feature_description}}
      Save to the appropriate file.
    agent: coder
    inputs:
      feature_description: "$user_feature"
      target_file: "$user_file"
    outputs:
      - implementation_code
      - file_path
    requires_approval: false

  - id: review_code
    name: "Code Review"
    description: |
      Review code for correctness, security, style, and documentation.
      Provide feedback with severity levels.
    agent: reviewer
    inputs:
      code: "$implementation_code"
      file_path: "$file_path"
    outputs:
      - review_feedback
      - approval_status
    depends_on:
      - code_feature
    requires_approval: false

  - id: approval_gate
    name: "Human Review Gate"
    description: "Review code and reviewer feedback before proceeding."
    agent: reviewer
    inputs:
      code: "$implementation_code"
      feedback: "$review_feedback"
    outputs:
      - approved_code
    depends_on:
      - review_code
    requires_approval: true   # Human gate

  - id: generate_tests
    name: "Generate Test Suite"
    description: |
      Generate unit tests, edge case tests, and error handling tests.
      Use pytest framework with clear test names.
    agent: tester
    inputs:
      code: "$approved_code"
      file_path: "$file_path"
    outputs:
      - test_code
      - test_file_path
    depends_on:
      - approval_gate
    requires_approval: false

  - id: run_tests
    name: "Execute Test Suite"
    description: |
      Run generated tests and report results.
      Include pass/fail counts, coverage, and failure details.
    agent: tester
    inputs:
      test_file: "$test_file_path"
    outputs:
      - test_results
      - coverage_report
    depends_on:
      - generate_tests
    requires_approval: false

  - id: commit_changes
    name: "Git Commit"
    description: |
      Commit the implementation and tests following Conventional Commits:
      feat(module): Brief description
    agent: coder
    inputs:
      code_file: "$file_path"
      test_file: "$test_file_path"
      results: "$test_results"
      review: "$review_feedback"
    outputs:
      - commit_sha
    depends_on:
      - run_tests
    requires_approval: true   # Human approves commit

timeout_seconds: 1800
max_retries: 2
```

## Sample Interaction

```text
User: "I need to implement user authentication with JWT tokens"

Friday Orchestrator: I'll delegate this to our development team.
Starting multi-agent workflow...

[CODER AGENT]

I'll implement JWT-based authentication. Let me check existing patterns first.

[Tool: search_files("authentication", "*.py")]
[Memory: Retrieved prior coding preferences — User prefers Flask, PyJWT library]

[Tool: write_file("src/auth/jwt_auth.py", ...)]

I've implemented JWT authentication with token generation, validation, and
a Flask decorator for protected routes. Features: type hints throughout,
comprehensive docstrings, proper error handling for JWT exceptions.

[Tool: git_commit("feat(auth): Add JWT authentication module")]

Code committed. Passing to reviewer...

---

[REVIEWER AGENT]

[Tool: read_file("src/auth/jwt_auth.py")]
[Tool: lint_code("src/auth/jwt_auth.py")]

Code Review Feedback:

Positive Observations:
- Clean, well-structured code following PEP 8
- Excellent documentation with comprehensive docstrings
- Good use of type hints

Critical Issues:
1. Security: Weak Secret Key Handling (CRITICAL)
   - No validation that secret key is strong enough
   - Suggestion: Add minimum length check (32+ bytes)

2. Security: Algorithm Vulnerability (MAJOR)
   - Allows arbitrary algorithm specification
   - Vulnerable to algorithm confusion attacks
   - Fix: Hardcode safe algorithms or use strict allowlist

Minor Issues:
3. No token refresh mechanism
4. No audit logging for auth events

Recommendation: APPROVE with required fixes for issues 1 and 2.

[Memory: Stored review pattern — User's security awareness needs improvement]
```

## Key Benefits

1. **Specialization**: Each agent is optimized for its role — coder uses GPT-4o for quality, reviewer uses Claude for nuanced analysis, tester uses GPT-4o-mini to minimize cost
2. **Shared Memory**: All agents see the same codebase context and prior patterns
3. **Human Gates**: `requires_approval: true` pauses the workflow for human review at critical points
4. **Learning**: Review feedback is stored in memory and informs future coding sessions

## Cost Optimization

| Agent | Model | Cost | Rationale |
|-------|-------|------|-----------|
| Coder | GPT-4o | $2.50/1M | Code quality matters |
| Reviewer | Claude 3.5 Sonnet | $3.00/1M | Nuanced review |
| Tester | GPT-4o-mini | $0.15/1M | Structured output, repetitive |
| Extraction | GPT-4o-mini | $0.15/1M | Background task |

## Related Pages

- [Research Assistant](/docs/use-cases/research-assistant/) — Long-term cross-session memory
- [Custom Protocol Implementations](/docs/advanced/custom-protocols/) — Write custom tools for CI/CD integration
- [Hybrid Cloud-Local](/docs/advanced/hybrid/) — Run tester agent locally to reduce costs

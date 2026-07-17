# Friday Lab: Environment Evolution & Testing Infrastructure

**Date:** February 11, 2026  
**Status:** Draft  
**Reference:** `phase-1-build-plan.md`, `comprehensive-agent-framework-design.md`, `technical-specifications.md`

---

## 1. Executive Summary

Friday Lab is the dedicated testing and development environment for agent validation. It provides isolated sandboxes where agents can be instantiated, tasked, monitored, and destroyed without risk to production systems. This document defines the evolutionary roadmap of the Lab environment—from basic single-turn execution to complex multi-agent, multi-turn research workflows with full workspace manipulation capabilities.

The Lab environment is not merely a testing harness; it is the primary interface through which developers interact with the agent framework during construction. Its capabilities must evolve in lockstep with the core framework phases.

---

## 2. Lab Environment Evolution Roadmap

### Phase 1: Baseline Execution (Current Focus)
**Core Capability:** Single-turn task execution with read-only workspace access

**Test Flow:**
```
create_agent(config) → AgentHandle
start_task(handle, prompt) → TaskState=PENDING
poll get_task_state() → RUNNING → COMPLETED|FAILED|CANCELLED
destroy_agent(handle) → cleanup
```

**Constraints:**
- Workspace access: READ-ONLY (per Phase 1 Build Plan Section 7)
- Task scope: Single-turn execution with explicit termination
- Embodiment: Software-only, no external tool binding
- Deliverables: Returned via `TaskResult.output` field only

**Verification Scenarios:**
- Agent instantiation with valid/invalid configurations
- State transition validation (PENDING → RUNNING → COMPLETED)
- Timeout handling and forced cancellation
- Resource cleanup verification post-destruction

---

### Phase 1.5: Workspace Writing & Multi-Turn Research
**Core Capability:** Multi-turn research tasks with document output

**Rationale:** Even single-agent research workflows require persistent output. An agent conducting multi-turn research must produce documents, store intermediate findings, and maintain state across turns.

**New Capabilities:**
- Workspace WRITE access (scoped to agent-specific directories)
- Document creation and appending
- Multi-turn task state persistence
- Intermediate result checkpointing

**Tool Requirements:**
- `file_write`: Create new documents
- `file_append`: Add to existing documents
- `directory_create`: Organize output structure
- `checkpoint_save`: Persist intermediate state

**Safety Requirements:**
- Path sandboxing (all paths resolved relative to agent workspace)
- Size quotas (max file size, max files per agent)
- Write auditing (every mutation logged with agent ID, timestamp, checksum)

---

### Phase 2: Multi-Agent Arbitration Lab
**Core Capability:** Test conflict resolution and resource contention

**New Capabilities:**
- Multiple simultaneous agents in shared workspace
- Memory proposal conflict simulation
- Arbitration outcome verification
- Deadlock detection and recovery

**Tool Requirements:**
- `file_lock`: Cooperative locking for shared resources
- `conflict_simulate`: Inject artificial contention scenarios
- `arbitration_trace`: Record arbitration decisions for analysis

---

### Phase 3: Full Workspace Manipulation
**Core Capability:** Complete file lifecycle management

**New Capabilities:**
- File move, rename, directory operations
- Scoped deletion with confirmation
- Workspace organization and cleanup
- Cross-directory linking (hard constraints)

**Tool Requirements:**
- `file_move`: Relocate files within workspace
- `file_delete`: Remove files (with guardrails)
- `directory_list`: Enumerate contents
- `directory_delete`: Remove directories (recursive with limits)

---

### Phase 4: Code Generation & Execution Sandbox
**Core Capability:** Safe code execution within controlled environment

**New Capabilities:**
- Code generation validation
- Sandboxed execution environment
- Resource-constrained execution (CPU, memory, time)
- Output capture and analysis

**Safety Architecture:**
- Containerized execution (isolated processes)
- Network egress blocking
- Filesystem chroot to agent workspace
- Resource limits enforcement (cgroups/limits)

---

## 3. Workspace Tool Specifications

### Core File Operations

#### `file_read`
**Status:** Phase 1 (Existing)  
**Purpose:** Read file contents from workspace

```yaml
input:
  path: string          # Relative to workspace root
  offset: int           # Optional: start position
  limit: int            # Optional: max bytes to read
output:
  content: string
  size: int
  encoding: string
errors:
  - PATH_VIOLATION      # Path escapes workspace
  - FILE_NOT_FOUND
  - PERMISSION_DENIED
```

#### `file_write`
**Status:** Phase 1.5 (New)  
**Purpose:** Create or overwrite files

```yaml
input:
  path: string          # Relative to workspace root
  content: string
  encoding: string      # default: utf-8
  create_dirs: boolean  # Auto-create parent directories
output:
  bytes_written: int
  checksum: string      # SHA-256 for audit
errors:
  - PATH_VIOLATION
  - QUOTA_EXCEEDED      # File size or count limit
  - DIRECTORY_REQUIRED  # Path component is file
```

#### `file_append`
**Status:** Phase 1.5 (New)  
**Purpose:** Append to existing files

```yaml
input:
  path: string
  content: string
output:
  new_size: int
  checksum: string
errors:
  - PATH_VIOLATION
  - FILE_NOT_FOUND
  - QUOTA_EXCEEDED
```

#### `file_search`
**Status:** Phase 1.5 (New)  
**Purpose:** Search for content within files

```yaml
input:
  pattern: string       # Regex or literal
  path: string          # File or directory
  recursive: boolean    # Search subdirectories
  case_sensitive: boolean
output:
  matches: []
    - file: string
      line: int
      column: int
      context: string   # Surrounding lines
errors:
  - PATH_VIOLATION
  - INVALID_PATTERN
```

### Advanced File Operations

#### `file_edit`
**Status:** Phase 1.5 (New)  
**Purpose:** Surgical file modifications

```yaml
input:
  path: string
  operations: []
    - type: REPLACE     # Replace range with content
      start: int
      end: int
      content: string
    - type: INSERT      # Insert at position
      position: int
      content: string
    - type: DELETE      # Delete range
      start: int
      end: int
output:
  operations_applied: int
  checksum: string
errors:
  - PATH_VIOLATION
  - FILE_NOT_FOUND
  - INVALID_RANGE
```

#### `file_move`
**Status:** Phase 3 (New)  
**Purpose:** Relocate files within workspace

```yaml
input:
  source: string        # Source path
  destination: string   # Destination path
  overwrite: boolean    # Allow overwriting existing file
output:
  new_path: string
errors:
  - PATH_VIOLATION
  - SOURCE_NOT_FOUND
  - DESTINATION_EXISTS
```

#### `file_delete`
**Status:** Phase 3 (New)  
**Purpose:** Remove files with confirmation

```yaml
input:
  path: string
  confirmation_token: string  # Required for destructive ops
output:
  deleted: boolean
  bytes_freed: int
errors:
  - PATH_VIOLATION
  - FILE_NOT_FOUND
  - CONFIRMATION_REQUIRED
```

---

## 4. Safety and Sandboxing Architecture

### Path Sandboxing
All file operations resolve paths relative to the agent's assigned workspace root. Any path containing `..` or absolute paths outside the workspace is rejected with PATH_VIOLATION.

**Resolution Rules:**
1. Strip leading `/` or `./` from input paths
2. Reject paths containing `..` components
3. Resolve against workspace root
4. Verify final path is within workspace boundary

### Destructive Operation Guardrails
- **Delete Confirmation:** All delete operations require explicit confirmation token
- **Quota Enforcement:** Max file size (10MB default), max files per agent (100 default)
- **Audit Logging:** Every mutation logged with agent ID, timestamp, before/after checksums

### Workspace Boundaries
Agents cannot access:
- Parent directories outside assigned workspace
- Other agents' workspaces (unless explicitly shared)
- System files or sensitive paths
- Network resources (Phase 4 excepted with explicit allowlist)

---

## 5. Integration with Friday Ecosystem

### Friday-Tools Evolution
The workspace toolset extends `friday-tools` with sandboxed variants:

| Tool | Package | Phase | Description |
|------|---------|-------|-------------|
| file_read | friday-tools | 1 | Existing, no changes |
| file_write | friday-tools | 1.5 | New, with sandbox wrapper |
| file_append | friday-tools | 1.5 | New |
| file_search | friday-tools | 1.5 | New |
| file_move | friday-tools | 3 | New, sandboxed |
| file_delete | friday-tools | 3 | New, with confirmation |
| checkpoint_* | friday-memory | 1.5 | Integration with episodic memory |

### Friday-Memory Integration
Checkpoints store agent state to episodic memory, enabling:
- Task resumption after interruption
- Multi-turn context preservation
- Rollback to previous states

---

## 6. Open Questions

1. Should Phase 1.5 be rolled into Phase 2, or is workspace writing critical enough to warrant its own sub-phase?
2. What are the quota defaults? Should they be configurable per-agent or per-lab-instance?
3. Does code execution sandbox (Phase 4) belong in the Lab spec or in a separate code-execution service?
4. How does the Lab integrate with Friday-telemetry for execution tracing?

---

**Next Steps:** Define tool schemas in `friday-tools` package, then implement sandbox layer in `friday-runtime`.

---

## 7. Lab Infrastructure Setup

### 7.1 Environment Requirements

#### Minimum Hardware (Local Development)
- **CPU:** 4 cores (8 recommended for multi-agent testing)
- **Memory:** 8GB RAM (16GB for Phase 2+ multi-agent scenarios)
- **Disk:** 10GB free space (SSD recommended for checkpoint I/O)
- **Network:** Localhost only (egress blocked for Phase 4 code execution)

#### Containerized Deployment (Recommended for Beta Testing)
```yaml
# docker-compose.lab.yml
version: '3.8'
services:
  friday-lab:
    image: friday/agent-lab:latest
    volumes:
      - ./workspaces:/lab/workspaces:rw
      - ./fixtures:/lab/fixtures:ro
      - ./logs:/lab/logs:rw
    environment:
      - LAB_MODE=isolated
      - MAX_AGENTS=10
      - WORKSPACE_QUOTA_MB=100
      - LOG_LEVEL=debug
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
```

### 7.2 Dependency Installation

#### System Dependencies
```bash
# Ubuntu/Debian
sudo apt-get install -y python3.11 python3-pip docker.io cgroup-tools

# macOS
brew install python@3.11 docker colima

# Verify installations
python3 --version  # >= 3.11
docker --version   # >= 24.0
```

#### Python Environment
```bash
python3 -m venv .venv
source .venv/bin/activate

# Core packages
pip install friday-agent==0.1.0-alpha
pip install friday-runtime==0.1.0-alpha
pip install friday-tools==0.1.0-alpha
pip install friday-memory==0.1.0-alpha

# Lab testing utilities
pip install pytest-asyncio==0.21.0
pip install pytest-timeout==2.1.0
pip install hypothesis==6.82.0
```

### 7.3 Configuration Files

#### Lab Configuration (lab-config.yaml)
```yaml
lab:
  version: "1.0.0"
  mode: isolated  # isolated | shared | production
  
workspace:
  root: "./workspaces"
  quota_mb: 100
  max_files: 100
  allowed_extensions: [".md", ".txt", ".json", ".yaml", ".py"]
  
agent:
  default_timeout_seconds: 300
  max_concurrent: 5
  memory_budget_mb: 512
  
sandbox:
  path_enforcement: strict
  audit_logging: true
  destructive_confirmation: true
  
phases:
  enabled: [1, 1.5]  # Enable specific phases for testing
  
logging:
  level: debug
  format: json
  output: "./logs/lab-{timestamp}.jsonl"
  retention_days: 30
```

#### Environment Variables (.env.lab)
```bash
# Core paths
FRIDAY_LAB_ROOT=/lab
FRIDAY_WORKSPACE_ROOT=/lab/workspaces
FRIDAY_LOG_PATH=/lab/logs

# Phase flags
ENABLE_PHASE_1=true
ENABLE_PHASE_1_5=true
ENABLE_PHASE_2=false
ENABLE_PHASE_3=false
ENABLE_PHASE_4=false

# Security
LAB_CONFIRMATION_TOKEN_SALT=changeme-in-production
AUDIT_LOG_ENCRYPTION_KEY=${AUDIT_KEY}

# Model configuration
DEFAULT_MODEL_PROVIDER=openai
DEFAULT_MODEL=gpt-4
OPENAI_API_KEY=${OPENAI_API_KEY}
```

### 7.4 Workspace Initialization

#### Automated Setup Script
```bash
#!/bin/bash
# init-lab.sh

set -e

LAB_ROOT=${1:-"./friday-lab"}
echo "Initializing Friday Lab at $LAB_ROOT..."

# Create directory structure
mkdir -p $LAB_ROOT/{workspaces,fixtures,logs,configs}
mkdir -p $LAB_ROOT/fixtures/{agents,tasks,expected}

# Initialize sample workspaces
for phase in 1 1.5 2 3; do
    mkdir -p $LAB_ROOT/workspaces/phase-${phase}/{agent-a,agent-b,shared}
done

# Create fixture files
cat > $LAB_ROOT/fixtures/agents/basic-researcher.json << 'EOF'
{
  "agent_id": "test-researcher-001",
  "config": {
    "model": "gpt-4",
    "timeout_seconds": 300,
    "memory_budget_mb": 512,
    "workspace_access": "read-only"
  },
  "capabilities": ["file_read", "web_search"]
}
EOF

cat > $LAB_ROOT/fixtures/tasks/single-turn-prompt.txt << 'EOF'
Research the impact of artificial intelligence on software development 
workflows. Provide a summary of key findings in 3-5 bullet points.
EOF

# Set permissions
chmod -R 755 $LAB_ROOT/workspaces
chmod -R 644 $LAB_ROOT/fixtures

echo "Lab initialization complete."
```

### 7.5 Cleanup Procedures

#### Between Test Runs
```python
def cleanup_workspace(agent_id: str = None, preserve_logs: bool = True):
    """Clean specific agent workspace or all test workspaces."""
    pass
```

#### Full Lab Reset
```bash
#!/bin/bash
# reset-lab.sh - Nuclear option for clean slate
read -p "Delete ALL lab data? (yes/no): " confirm
[ "$confirm" = "yes" ] && rm -rf ./workspaces/* ./logs/*
```
